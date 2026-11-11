"""Independently sample the emitted meshes and block-compressed masks."""
import json
from pathlib import Path
import sys

import numpy as np

from unit_review import BODIES, ROOT, mv, normalize, parts, pixels, rgba

repo, stage = map(Path, sys.argv[1:])
native = repo / "inputs/native"
overlay = stage / "overlay"
report = json.loads((stage / "coverage.json").read_bytes())
equipped = {
    "assassin": ("abb_shamshir",),
    "zamburak": ("jpn_cannon_ozutsu",),
    "zamburak_upgrade": ("jpn_cannon_ozutsu",),
    "savar_castle": ("byz_shield_ovalspearman", "mace_flanged"),
    "savar_imperial": ("byz_shield_teardrop", "mace_flanged"),
}
rng = np.random.default_rng(1701)
points = rng.dirichlet(np.ones(3), size=1024)


def path(name):
    changed = overlay / name
    return changed if changed.is_file() else native / name


def measure(stem):
    material = mv.material_slots(path(stem + ".rrmaterial").read_bytes())["textures"]
    maskname = normalize(material["patternTex"]) if material.get("patternTex") else ""
    texture = path(maskname)
    mask = rgba(texture.read_bytes())[:, :, 0] if maskname and texture.is_file() else None
    sums = np.zeros((3, 2))
    for lod, _, _, xyz, uv, faces in parts(path(stem + ".rrgeom").read_bytes()):
        pt = xyz[faces]
        areas = np.linalg.norm(np.cross(pt[:, 1] - pt[:, 0], pt[:, 2] - pt[:, 0]), axis=1) / 2
        sums[lod, 1] += areas.sum()
        if mask is not None:
            coords = np.einsum("sa,fad->fsd", points, uv[faces], optimize=True)
            amounts = (mask[pixels(coords, mask.shape)] >= 128).mean(1)
            sums[lod, 0] += np.dot(areas, amounts)
    return sums


def percent(sums):
    return np.round(sums[:, 0] / sums[:, 1] * 100, 2).tolist()


verified = {}
for key, (family, asset) in BODIES.items():
    body = measure(f"{ROOT}/{family}/{asset}/model")
    full = body.copy()
    for equipment in equipped[key]:
        full += measure(f"{ROOT}/{family}/{equipment}/model")
    conservative = np.column_stack((body[:, 0], full[:, 1]))
    row = {
        "unit_and_mount": percent(body),
        "equipped": percent(full),
        "equipped_if_all_equipment_untinted": percent(conservative),
    }
    verified[key] = row
    print(key, row)
(stage / "verified-coverage.json").write_text(json.dumps(verified, indent=2) + "\n")
assert all(10 <= coverage <= 50 for row in verified.values() for col in row.values() for coverage in col)
