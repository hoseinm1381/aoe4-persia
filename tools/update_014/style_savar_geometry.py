"""Reshape the Savar's hanging hem and align the new cloth and shield UVs."""
import json
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
from stage_unit_art import fix_uv, uv_area
from style_savar_textures import SHIELDS
from savar_pose import mount_trees, match_mount
from unit_review import baseline_member, BODIES, ROOT, parts, rc

tile = np.array([2, 1])
samples = np.array([[1, 1, 1], [2, 1, 1], [1, 2, 1], [1, 1, 2]]) / np.array([3, 4, 4, 4])[:, None]


def cloth_reference(high):
    xyz, face_rows, tile_rows = [], [], []
    count = 0
    for _, _, _, points, uv, faces in high:
        xyz.extend(points.tolist())
        face_rows.extend((faces.astype(int) + count).tolist())
        tile_rows.extend((np.floor(uv[faces] * 8) == tile).all((1, 2)).tolist())
        count += len(points)
    tree = BVHTree.FromPolygons(xyz, face_rows, all_triangles=True)
    return tree, tile_rows


def signed_area(uv):
    a, b = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
    return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]


def cloth_uv(triangles):
    u = np.clip((triangles[:, :, 2] + 1.0) / 1.98, .024, .976)
    v = np.clip((triangles[:, :, 1] - .35) / 1.21, .024, .976)
    side_uv = np.stack((.25 + u / 8, .125 + v / 8), axis=2)
    # Fold the front and back onto the sewn edge rather than stretching the
    # mid-panel artwork across faces perpendicular to the flank.
    x = np.clip(triangles[:, :, 0] * .11 + .045, .018, .082)
    near = triangles[:, :, 2].mean(1) > 0
    u_end = np.where(near[:, None], .99 - x, x)
    edge_uv = np.stack((.25 + u_end / 8, .125 + v / 8), axis=2)
    side_area = abs(signed_area(side_uv))
    edge_area = abs(signed_area(edge_uv))
    use_edge = (side_area < edge_area * 4) & (abs(triangles[:, :, 2].mean(1)) > .59)
    return np.where(use_edge[:, None, None], edge_uv, side_uv).astype("<f2")


def select_cloth(tree, flags, lod, xyz, uv, faces, mount):
    tris = xyz[faces]
    old = (np.floor(uv[faces] * 8) == tile).all((1, 2))
    coords = np.einsum("sa,fad->fsd", samples, tris)
    layout = cloth_uv(tris)
    valid = (abs(signed_area(layout.astype(np.float32))) > 1.4e-7) & mount[faces].all(1)
    picked = {}
    for i in np.flatnonzero(valid):
        center = coords[i, 0]
        if old[i]:
            picked[int(i)] = layout[i]
        elif lod != 0 and abs(center[0]) > .145 and .33 < center[1] < 1.55:
            score = 0
            for point in coords[i]:
                _, _, nearest, distance = tree.find_nearest(Vector(point))
                score += flags[nearest] and distance <= (.075 if lod == 2 else .046)
            if score >= (2 if lod == 2 else 3):
                picked[int(i)] = layout[i]
    return picked


def sculpt_hem(xyz, faces, selected, imperial):
    if not selected:
        return xyz
    changed = xyz.copy()
    ids = np.unique(faces[list(selected)])
    points = xyz[ids]
    good = (abs(points[:, 0]) > .21) & (points[:, 1] < .86) & (points[:, 1] > .29)
    if not good.any():
        return changed
    hem = {tuple(pt) for pt in points[good]}
    mark = np.array([tuple(pt) in hem for pt in xyz])
    x, y, z = xyz[mark].T
    lower = np.clip((.86 - y) / .43, 0, 1) ** 1.4
    raised_ends = np.clip(abs(z) / .91, 0, 1) ** 1.7
    if imperial:
        lift = .034 + .108 * raised_ends + .026 * np.cos((z + .1) * 9)
        flare = .018 + .023 * (1 - raised_ends)
    else:
        lift = .060 + .126 * raised_ends
        flare = .014 + .012 * (1 - raised_ends)
    changed[mark, 0] = x + np.sign(x) * lower * flare
    changed[mark, 1] = y + lower * lift
    return changed


def shield_uv(xyz, imperial):
    center, radius = (.123, .69) if imperial else (.112, .71)
    u = np.clip(.5 + (xyz[..., 0] - center) / radius, .034, .966)
    v = np.clip(.5 + (xyz[..., 1] - .005) / .69, .034, .966)
    return np.stack((.75 + .25 * u, .75 + .25 * v), axis=-1).astype("<f2")


def select_shield(xyz, uv, faces, imperial):
    original = (np.floor(uv[faces].mean(1) * 2) == (1, 1)).all(1)
    projected = shield_uv(xyz[faces], imperial)
    valid = abs(signed_area(projected.astype(np.float32))) > 1.4e-7
    return {int(i): projected[i] for i in np.flatnonzero(original & valid)}


def sculpt_boss(xyz, faces, selected, imperial):
    changed = xyz.copy()
    ids = np.unique(faces[list(selected)])
    vertices = {tuple(p) for p in xyz[ids]}
    mark = np.array([tuple(p) in vertices for p in xyz])
    x, y, z = xyz[mark].T
    radius = np.hypot(x - (.123 if imperial else .112), y - .005)
    bump = (.042 if imperial else .021) * np.clip((.17 - radius) / .17, 0, 1) ** 1.35
    changed[mark, 2] = z - bump
    return changed


def write_stream(vertex, index, xyz, new_xyz, uv, original_faces, mapping):
    n, _, stride, _ = struct.unpack_from("<4I", vertex.payload)
    assert stride == 28
    buffers = [vertex.payload[16 + i * stride:16 + (i + 1) * stride] for i in range(n)]
    # A split only duplicates a vertex where an existing material seam needs
    # distinct UVs. Normals, original bone IDs, and normalized weights follow it.
    edited = original_faces.copy()
    source = list(range(n))
    allocated = {}
    usage = {}
    for face_id, face in enumerate(original_faces):
        corners = mapping.get(face_id)
        for c, i in enumerate(face):
            raw = (uv[i] if corners is None else corners[c]).astype("<f2").tobytes()
            available = usage.setdefault(int(i), [])
            if raw not in available:
                available.append(raw)
    for i, row in enumerate(buffers[:n]):
        possible = usage.get(i)
        if not possible:
            continue
        original_uv = row[12:16]
        if original_uv in possible:
            possible = [original_uv] + [p for p in possible if p != original_uv]
        pos = new_xyz[i].astype("<f2").tobytes()
        for count, coords in enumerate(possible):
            data = pos + row[6:12] + coords + row[16:]
            if count == 0:
                target = i
                buffers[i] = data
            else:
                target = len(buffers)
                buffers.append(data)
                source.append(i)
            allocated[i, coords] = target
    for face_id, face in enumerate(original_faces):
        corners = mapping.get(face_id)
        for c, i in enumerate(face):
            raw = (uv[i] if corners is None else corners[c]).astype("<f2").tobytes()
            edited[face_id, c] = allocated[int(i), raw]

    assert len(buffers) <= np.iinfo(original_faces.dtype).max
    assert np.array_equal(np.array(source)[edited], original_faces)
    for row, i in zip(buffers, source, strict=True):
        ref = vertex.payload[16 + i * stride:16 + (i + 1) * stride]
        assert row[6:12] == ref[6:12] and row[16:] == ref[16:]
    return (struct.pack("<I", len(buffers)) + vertex.payload[4:16] + b"".join(buffers),
            index.payload[:16] + edited.tobytes(), source)


def style_geometry(native, overlay, asset, imperial, shield, trees=None):
    rel = f"{ROOT}/savar/{asset}/model.rrgeom"
    source = baseline_member(native.parent.parent, rel)
    clean, micro = fix_uv(source, 4 if shield else 8)
    parsed = rc.parse(clean)
    decoded = list(parts(clean))
    references = cloth_reference([row for row in decoded if row[0] == 0]) if not shield else None
    patches = {}
    report = []
    for lod, _, vertex, xyz, uv, faces in decoded:
        if shield:
            edits = select_shield(xyz, uv, faces, imperial)
            deformed = sculpt_boss(xyz, faces, edits, imperial)
        else:
            edits = select_cloth(*references, lod, xyz, uv, faces, match_mount(trees[lod], xyz))
            deformed = sculpt_hem(xyz, faces, edits, imperial)
        geom = next(g for g in rc.walk(parsed.roots) if g.tag == b"GEOM" and
                    any(c.offset == vertex.offset for c in g.children))
        _, index = [c for c in geom.children if c.tag == b"GEOB"]
        vdata, idata, source_ids = write_stream(vertex, index, xyz, deformed, uv, faces, edits)
        patches[vertex.offset] = vdata
        patches[index.offset] = idata
        report.append({"lod": lod + 1, "faces_reprojected": len(edits),
                       "vertex_splits": len(source_ids) - len(xyz),
                       "sculpted_vertices": int(np.count_nonzero((xyz != deformed).any(1))),
                       "max_vertex_displacement": float(np.linalg.norm(xyz - deformed, axis=1).max()),
                       "original_vertex_index": source_ids})
    edited = rc.rebuild(parsed, lambda node: patches.get(node.offset))
    for a, b in zip(decoded, parts(edited), strict=True):
        assert a[:2] == b[:2] and len(a[5]) == len(b[5])
        assert np.isfinite(b[4]).all() and ((b[4] >= 0) & (b[4] <= 1)).all()
        assert (abs(uv_area(b[4], b[5])) > 1e-10).all()
    output = overlay / rel
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(edited)
    print(asset, [{k: v for k, v in r.items() if k != "original_vertex_index"} for r in report], flush=True)
    return report


def main(repo, stage):
    results = {}
    for key, shield in SHIELDS.items():
        native, overlay = repo / "inputs/native", stage / "overlay"
        body = BODIES[key][1]
        imperial = key == "savar_imperial"
        assembly = repo / "authoring/art/persia/units/savar/assemblies" / body / "assembly.blend"
        bpy.ops.wm.open_mainfile(filepath=str(assembly), load_ui=False)
        trees = [mount_trees(bpy.context.scene, body, lod) for lod in range(3)]
        results[body] = style_geometry(native, overlay, body, imperial, False, trees)
        results[shield] = style_geometry(native, overlay, shield, imperial, True)
    (stage / "savar-model-changes.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main(*map(Path, sys.argv[sys.argv.index("--") + 1:]))
