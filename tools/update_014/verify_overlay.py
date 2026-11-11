"""Verify exact overlay scope, skinning and topology, and packed texture mip chains."""
from dataclasses import replace
from io import BytesIO
import json
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image

from unit_review import baseline_member, BODIES, ROOT, digest, mv, normalize, parts, rc, rr
from stage_unit_art import mip_records, uv_area

repo, stage = map(Path, sys.argv[1:])
native, overlay = repo / "inputs/native", stage / "overlay"
covered = json.loads((stage / "verified-coverage.json").read_bytes())
main = json.loads((stage / "coverage.json").read_bytes())
sculpt = json.loads((stage / "savar-model-changes.json").read_bytes())
records = list(main.values()) + [r["shield"] for r in main.values() if "shield" in r]
expected = set()


def triangles_area(xyz, faces):
    tri = xyz[faces]
    return np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)


def compare_geo(path, design):
    old, new = baseline_member(repo, path), (overlay / path).read_bytes()
    a_chunks, b_chunks = [list(rc.walk(rc.parse(data).roots)) for data in (old, new)]
    for a, b in zip(a_chunks, b_chunks, strict=True):
        assert (a.tag, a.kind, a.name, a.version) == (b.tag, b.kind, b.name, b.version)
        if not a.children and a.tag != b"GEOB":
            assert a.payload == b.payload
    for stream, (a, b) in enumerate(zip(parts(old), parts(new), strict=True)):
        lod, names, vb, xyz, uv, faces = a
        _, _, vnew, pnew, unew, fnew = b
        n, _, stride, _ = struct.unpack_from("<4I", vb.payload)
        assert vb.payload[4:16] == vnew.payload[4:16] and names == b[1] and lod == b[0]
        assert np.isfinite(unew).all() and ((unew >= 0) & (unew <= 1)).all()
        assert (abs(uv_area(unew, fnew)) > 1e-10).all()
        assert not ((triangles_area(xyz, faces) > 1e-8) & (triangles_area(pnew, fnew) <= 1e-8)).any()
        ref = np.array(design[stream]["original_vertex_index"]) if design is not None else np.arange(n)
        assert np.array_equal(ref[fnew], faces)
        old_rows = np.frombuffer(vb.payload[16:], dtype=np.uint8).reshape(n, stride)
        new_rows = np.frombuffer(vnew.payload[16:], dtype=np.uint8).reshape(-1, stride)
        assert np.array_equal(old_rows[ref, 6:12], new_rows[:, 6:12])
        assert np.array_equal(old_rows[ref, 16:], new_rows[:, 16:])
        deviation = np.linalg.norm(xyz[ref] - pnew, axis=1).max()
        assert deviation <= (.188 if design else 0)
        if not design:
            assert np.array_equal(xyz, pnew)


def compare_mat(path, textures):
    old = mv.material_slots(baseline_member(repo, path))
    new = mv.material_slots((overlay / path).read_bytes())
    assert old["parameters"] == new["parameters"]
    for slot, native_path in old["textures"].items():
        if slot not in textures:
            assert new["textures"][slot] == native_path
            continue
        assert normalize(new["textures"][slot]) == textures[slot]
        base = (native / normalize(native_path)).read_bytes()
        changed = (overlay / textures[slot]).read_bytes()
        a, b = mip_records(base), mip_records(changed)
        assert [(r.width, r.height) for r in a] == [(r.width, r.height) for r in b]
        if slot == "patternTex":
            for x, y in zip(a, b, strict=True):
                rx, ry = [
                    np.asarray(Image.open(BytesIO(rr._dds([replace(r, level=0)], 77))).convert("RGBA"))
                    for r in (x, y)
                ]
                assert np.array_equal(rx[:, :, 1:], ry[:, :, 1:])


for record in records:
    stem = record["stem"]
    asset = stem.split("/")[-2]
    design = sculpt.get(asset)
    if record.get("uv_fixes") or design:
        geo = stem + ".rrgeom"
        expected.add(geo)
        compare_geo(geo, design)
    else:
        for _, _, _, _, uv, faces in parts((native / (stem + ".rrgeom")).read_bytes()):
            assert np.isfinite(uv).all() and ((uv >= 0) & (uv <= 1)).all()
            assert (abs(uv_area(uv, faces)) > 1e-10).all()
    textures = record.get("textures")
    if textures:
        mat = stem + ".rrmaterial"
        expected.add(mat)
        expected.update(textures.values())
        compare_mat(mat, textures)
actual = {p.relative_to(overlay).as_posix() for p in overlay.rglob("*") if p.is_file()}
assert actual == expected, (actual - expected, expected - actual)
assert len(covered) == len(BODIES)
assert all(10 <= rate <= 50 for row in covered.values() for vals in row.values() for rate in vals)
print(f"Verified {len(actual)} staged assets, all 15 body LODs, original triangle connectivity and skinning, and all texture mip chains.")
(stage / "final-overlay-verification.json").write_text(
    json.dumps({"coverage": covered, "members": {p: digest((overlay / p).read_bytes()) for p in sorted(actual)}}, indent=2) + "\n"
)
