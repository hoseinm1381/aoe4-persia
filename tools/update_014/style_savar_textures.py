"""Bake Savar embroidery, plate accents, and shield relief into native atlases."""
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from stage_unit_art import OUT, merge_blocks, tile_region
from unit_review import baseline_member, BODIES, ROOT, encode, mv, normalize, rgba

SHIELDS = {
    "savar_castle": "byz_shield_ovalspearman",
    "savar_imperial": "byz_shield_teardrop",
}


def coordinates(dim):
    points = (np.arange(dim) + .5) / dim
    return np.meshgrid(points, points)


def paint(colors, relief, rough, metal, where, rgb, height, roughness, metallic):
    colors[where] = rgb
    relief[where] = height
    rough[where] = roughness
    metal[where] = metallic


def rosette(x, y, x0, y0, radius, petals):
    dx, dy = (x - x0) / radius, (y - y0) / radius
    theta = np.arctan2(dy, dx)
    r = np.hypot(dx, dy)
    profile = .61 + .28 * np.cos(theta * petals)
    return r, abs(r - profile) < .075, r < profile


def textile(dim, imperial):
    x, y = coordinates(dim)
    rng = np.random.default_rng(100 + imperial)
    grain = rng.normal(0, 1.7, (dim, dim))
    warp = 2.2 * np.cos(x * np.pi * dim * .89) + 1.5 * np.cos(y * np.pi * dim * .71)
    folds = 8 * np.cos((x + .03 * np.sin(7 * y)) * 8 * np.pi) + 5 * np.sin(y * 13 + x * 3)
    tone = (182 if imperial else 164) + grain + warp + folds
    colors = np.repeat(tone[:, :, None], 3, axis=2)
    owner = np.full((dim, dim), 245, dtype=np.uint8)
    relief = .1 * (warp + grain) + .14 * folds
    rough, metal = np.full((dim, dim), 177.), np.full((dim, dim), 12.)
    d = np.minimum.reduce((x, y, 1 - x, 1 - y))
    edge = (d < .082) | (y > .807)
    gold = (201, 148, 69) if imperial else (168, 126, 67)
    edge_color = (66, 29, 31) if imperial else (31, 49, 49)
    secondary = (48, 102, 102) if imperial else (112, 51, 43)
    paint(colors, relief, rough, metal, edge, edge_color, .6, 185, 12)
    owner[edge] = 0
    stripe = (abs(d - .062) < .012) | (abs(y - .816) < .010) | (abs(y - .971) < .011)
    paint(colors, relief, rough, metal, stripe, gold, 3.8, 143, 69)
    owner[stripe] = 0
    # A large, repeating border motif remains distinct at strategy-camera distance.
    repeat = abs((x * (7 if imperial else 6) + .5) % 1 - .5)
    leaf = (repeat * .095 + abs(y - .894) < .047) & (x > .075) & (x < .925)
    core = (repeat * .14 + abs(y - .894) < .022) & leaf
    paint(colors, relief, rough, metal, leaf, gold, 3.5, 143, 76)
    paint(colors, relief, rough, metal, core, secondary, 2.0, 161, 19)
    for center in (.29, .72):
        if imperial:
            r, thread, inside = rosette(x, y, center, .58, .155, 8)
            ring = abs(r - 1.03) < .058
            inner = (r < .24) | (abs(r - .4) < .045)
        else:
            r = (abs(x - center) + abs(y - .59) * .9) / .128
            ring = (abs(r - 1) < .09) | (abs(r - .65) < .08)
            inside = r < .64
            thread = (abs(x - center) < .015) & (r < .63)
            inner = r < .29
        paint(colors, relief, rough, metal, inside, secondary, 2.0, 168, 16)
        paint(colors, relief, rough, metal, ring | thread | inner, gold, 4.0, 138, 78)
        owner[inside | ring | thread | inner] = 0
    colors += (grain + warp + .55 * folds)[:, :, None] * .68
    return colors, owner, relief, rough, metal


def shield_design(dim, imperial):
    x, y = coordinates(dim)
    dx, dy = (x - .50) * 2.16, (y - .50) * 2.20
    theta, r = np.arctan2(dy, dx), np.hypot(dx, dy)
    grain = np.sin(x * 164 + y * 8) * 2 + np.sin(y * 119) * 1.8
    burnish = 13 * np.cos(theta - .8) * np.minimum(r, 1) + 5 * np.sin(x * 32)
    base = np.array([41, 78, 91] if imperial else [82, 56, 42])
    colors = np.broadcast_to(base, (dim, dim, 3)).astype(float).copy()
    relief = np.zeros((dim, dim))
    rough, metal = np.full((dim, dim), 141.), np.full((dim, dim), 76.)
    rim = (r > .79) & (r < .99)
    gold = (220, 164, 84) if imperial else (184, 151, 87)
    steel = (154, 178, 185) if imperial else (152, 164, 159)
    paint(colors, relief, rough, metal, rim, gold, 3, 106, 201)
    outer = (abs(r - .94) < .019) | (abs(r - .81) < .015)
    paint(colors, relief, rough, metal, outer, steel, 5, 86, 225)
    angle = abs((theta * (16 if imperial else 12) / (2 * np.pi) + .5) % 1 - .5)
    stud = ((angle / .135) ** 2 + ((r - .875) / .046) ** 2) < 1
    paint(colors, relief, rough, metal, stud, (238, 204, 139), 6, 89, 221)
    rr, petals, leaves = rosette(x, y, .5, .5, .385, 8 if imperial else 4)
    trim = (abs(rr - .9) < .021) | petals
    paint(colors, relief, rough, metal, leaves, (111, 42, 38) if imperial else (42, 86, 80), 1.8, 155, 48)
    paint(colors, relief, rough, metal, trim, gold, 3.4, 115, 186)
    boss = r < (.205 if imperial else .177)
    paint(colors, relief, rough, metal, boss, steel, 5, 100, 213)
    paint(colors, relief, rough, metal, r < .095, (224, 197, 137), 7, 91, 222)
    colors += (grain + burnish)[:, :, None]
    return colors, np.zeros((dim, dim), dtype=np.uint8), relief, rough, metal


def convert_tile(maps, region, pattern):
    rgb, owner, height, rough, metal = pattern
    albedo = maps["albedoTexture"][region]
    mask = maps["patternTex"][region]
    surface = maps["metalTex"][region]
    normal = maps["normalMap"][region]
    albedo[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    mask[:, :, 0] = owner
    dx, dy = np.gradient(height)
    normal[:, :, 3] = np.clip(128 - dy * 11, 28, 226).astype(np.uint8)
    normal[:, :, 1] = np.clip(128 + dx * 11, 28, 226).astype(np.uint8)
    surface[:, :, 0] = np.clip(metal, 0, 255).astype(np.uint8)
    surface[:, :, 3] = np.clip(rough, 0, 255).astype(np.uint8)


def plate_material(maps, tiles, imperial):
    tint = {
        "iron": ((94, 107, 110), .24 if imperial else .31),
        "mail": ((118, 127, 123), .32),
        "bronze": ((198, 141, 65), .54 if imperial else .26),
        "lamellar": ((167, 120, 61), .47 if imperial else .18),
    }
    for key, (color, mix) in tint.items():
        region = tile_region(maps["albedoTexture"].shape, 8, tiles[key])
        albedo = maps["albedoTexture"][region][:, :, :3]
        metal = maps["metalTex"][region]
        tone = albedo.astype(float) @ np.array([.21, .72, .07])
        ref = tone[:, :, None] * .46 + np.array(color)[None, None, :] * .59
        albedo[:] = np.clip(albedo * (1 - mix) + ref * mix, 0, 255).astype(np.uint8)
        metal[:, :, 0] = np.maximum(metal[:, :, 0], int(136 + imperial * 31))
        metal[:, :, 3] = np.minimum(metal[:, :, 3], 152 - imperial * 18)


def stage_texture(repo, stage, key, asset, shield):
    native, overlay = repo / "inputs/native", stage / "overlay"
    stem = f"{ROOT}/savar/{asset}/model"
    original_material = baseline_member(repo, stem + ".rrmaterial")
    srcs = mv.material_slots(original_material)["textures"]
    originals = {slot: (native / normalize(srcs[slot])).read_bytes()
                 for slot in ("albedoTexture", "patternTex", "normalMap", "metalTex")}
    baseline = {slot: rgba(raw) for slot, raw in originals.items()}
    edited = {slot: a.copy() for slot, a in baseline.items()}
    imperial = key == "savar_imperial"
    if shield:
        grid, tile = 4, (3, 0)
        pattern = shield_design(edited["albedoTexture"].shape[0] // grid, imperial)
        prefix = f"{OUT}/{key}/shield"
    else:
        layout = repo / "authoring/art/persia/units/savar/textures" / asset / "sources.json"
        tiles = json.loads(layout.read_bytes())["tiles"]
        grid, tile = 8, tiles["horse_owner"]
        pattern = tuple(layer[::-1] for layer in textile(edited["albedoTexture"].shape[0] // grid, imperial))
        prefix = f"{OUT}/{key}"
        plate_material(edited, tiles, imperial)
    convert_tile(edited, tile_region(edited["albedoTexture"].shape, grid, tile), pattern)

    paths = {}
    src_out = stage / "editable" / key / ("shield" if shield else "armor")
    src_out.mkdir(parents=True, exist_ok=True)
    filenames = {"albedoTexture": "albedo", "patternTex": "owner", "normalMap": "normal", "metalTex": "surface"}
    for slot, name in filenames.items():
        raw, old, new = originals[slot], baseline[slot], edited[slot]
        path = f"{prefix}/{name}.rrtex"
        change = (new != old).any(2)
        srgb = slot == "albedoTexture"
        pixels = new[:, :, :3] if srgb else new
        template = (native / "art/persia/landmarks_013/ali_qapu_palace/albedo.rrtex").read_bytes() if srgb else raw
        merged = merge_blocks(raw, encode(template, path, pixels, srgb), change, 8 if srgb else 16,
                              preserve_owner_channels=(slot == "patternTex"))
        outfile = overlay / path
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_bytes(merged)
        actual = rgba(merged)
        if slot == "patternTex":
            assert np.array_equal(actual[:, :, 1:], old[:, :, 1:])
        Image.fromarray(actual[::-1]).save(src_out / f"{name}.png")
        paths[slot] = path
    new_mat = mv.rewrite_material(original_material, {k: p.replace("/", "\\") for k, p in paths.items()}, {})
    dst = overlay / (stem + ".rrmaterial")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(new_mat)
    return {"stem": stem, "textures": paths}


def run(repo, stage):
    path = stage / "coverage.json"
    records = json.loads(path.read_bytes())
    for key, shield in SHIELDS.items():
        body = BODIES[key][1]
        records[key].update(stage_texture(repo, stage, key, body, False))
        records[key]["shield"] = stage_texture(repo, stage, key, shield, True)
    path.write_text(json.dumps(records, indent=2) + "\n")
    print("Baked two caparisons and two shield designs with native albedo, owner, normal, and roughness/metal maps.")


if __name__ == "__main__":
    run(*map(Path, sys.argv[1:]))
