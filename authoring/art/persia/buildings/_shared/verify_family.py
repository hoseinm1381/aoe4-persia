"""Fresh saved readback or cold source reconstruction; never saves a master.

Blender --background --factory-startup --python-exit-code 1 --python THIS -- SLUG
Add --rebuild to reconstruct all geometry from pinned source without opening it.
"""
from pathlib import Path
import sys, json, traceback
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_family as B


def compare(H, expected):
    errors = []
    wanted_names = B.expected_names(H.R.PREFIX, expected['expected_body_keys'])
    scene = bpy.data.scenes.get(H.R.SCENE)
    actual_names = {c.name for c in scene.collection.children if c.name.startswith(H.R.PREFIX)} if scene else set()
    if actual_names != wanted_names or set(expected['compositions']) != wanted_names:
        errors.append({'coverage_missing': sorted(wanted_names - actual_names), 'coverage_extra': sorted(actual_names - wanted_names), 'manifest_coverage_exact': set(expected['compositions']) == wanted_names})
    count = 0
    for name, row in expected['compositions'].items():
        col = bpy.data.collections.get(name)
        if col is None:
            continue
        wanted = {p['name']: p for p in row['parts']}
        got = {o.name: B.part_record(o) for o in B.meshes(col)}
        if got != wanted:
            changed = sorted(n for n in set(got) | set(wanted) if got.get(n) != wanted.get(n))
            errors.append({'composition': name, 'changed_parts': changed[:30], 'changed_part_count': len(changed)})
        count += 1
    return errors, count


def main(slug, rebuild=False, requalify=False):
    B.factory_guard()
    root = B.family_root(slug)
    master = root / (slug + '.blend')
    manifest_path = root / 'state-manifest.json'
    receipt = json.loads((root / 'evidence/build-receipt.json').read_text())
    expected = json.loads(manifest_path.read_text())
    pinned = B.fingerprints(root)
    before, manifest_sha = B.sha(master), B.sha(manifest_path)
    if not receipt.get('passed') or receipt.get('saved_file_sha256') != before or receipt.get('state_manifest_sha256') != manifest_sha:
        raise RuntimeError('Current master/manifest lack a matching successful full-source receipt')
    original_inputs = receipt.get('geometry_input_sha256', {})
    if expected.get('saved_file_sha256') != before or expected.get('geometry_input_sha256') != original_inputs:
        raise RuntimeError('Original build and manifest disagree')
    changed = sorted(k for k in set(original_inputs) | set(pinned) if original_inputs.get(k) != pinned.get(k))
    if requalify:
        allowed={'_shared/build_family.py','_shared/mesh_checks.py','_shared/verify_family.py'}
        if not changed or not set(changed)<=allowed or set(original_inputs)!=set(pinned):
            raise RuntimeError('Requalification admits only existing checker helpers, never changed/missing/new art inputs: '+str(changed))
    elif changed:
        raise RuntimeError('Retained source inputs differ from the saved master build')
    family, native, profiles, keys = B.source_contracts(root)
    if keys != expected['expected_body_keys']:
        raise RuntimeError('Expected body keys differ from current family contract')
    if rebuild:
        H, checks, actual_manifest = B.generate(root)
        errors = list(checks['errors'])
    else:
        bpy.ops.wm.open_mainfile(filepath=str(master))
        H = B.load_recipe(root)
        H.ANCHORS.update(expected['source_anchors'])
        # Import/configuration does not construct a room or change saved objects.
        checks, unused = B.assess(H, root, native, profiles, keys, expected['resource_contact_contracts'], expected['resource_interface_contracts'])
        errors = list(checks['errors'])
    differences, count = compare(H, expected)
    errors += differences
    if count != len(keys) * 31:
        errors.append({'checked_compositions': count, 'expected_compositions': len(keys) * 31})
    if B.sha(master) != before or B.sha(manifest_path) != manifest_sha or B.fingerprints(root) != pinned:
        errors.append('Master, manifest or retained inputs changed during verification')
    doc = {'passed': not errors, 'family': slug, 'saved_file_sha256': before, 'state_manifest_sha256': manifest_sha,
           'geometry_input_sha256': pinned, 'checked_compositions': count, 'expected_compositions': len(keys) * 31,
           'saved_master': False, 'method': 'Factory cold reconstruction from retained inputs' if rebuild else 'Fresh saved-file readback with actual mesh/UV/contact/state checks',
           'errors': errors, 'compound_budget_qualified': checks['compound_budget_qualified'],
           'triangle_cap_scope': checks['triangle_cap_scope'], 'native_gates': B.NATIVE_GATES}
    if requalify:
        doc.update({'checker_requalification_only':True,'changed_checker_paths':changed,
            'original_build_receipt_sha256':B.sha(root/'evidence/build-receipt.json'),
            'original_geometry_input_sha256':original_inputs,'geometry_and_rig_manifest_comparison_passed':not differences,
            'master_and_manifest_unchanged':B.sha(master)==before and B.sha(manifest_path)==manifest_sha,
            'scope':'Original art inputs and saved master preserved. Actual current checks and exact original manifest comparison; cold reconstruction separately required.'})
    name = ('checker-requalification-cold.json' if rebuild else 'checker-requalification-readback.json') if requalify else ('rebuild-verification.json' if rebuild else 'saved-file-readback.json')
    B.write(root / 'evidence' / name, doc)
    print('FAMILY_VERIFY', slug, 'cold' if rebuild else 'readback', doc['passed'], count, flush=True)
    if errors:
        raise RuntimeError(str(errors[:8]))
    return doc


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    try:
        if not args: raise ValueError('Expected family slug')
        main(args[0], '--rebuild' in args, '--requalify' in args)
    except Exception:
        if args:
            try:
                failed_root = B.family_root(args[0])
                if (failed_root / 'evidence').is_dir():
                    diagnostic = traceback.format_exc()
                    (failed_root / 'evidence/verification-error.txt').write_text(diagnostic)
                    path = failed_root / (failed_root.name + '.blend')
                    manifest_path = failed_root / 'state-manifest.json'
                    failed_name = ('checker-requalification-cold.json' if '--rebuild' in args else 'checker-requalification-readback.json') if '--requalify' in args else ('rebuild-verification.json' if '--rebuild' in args else 'saved-file-readback.json')
                    B.write(failed_root / 'evidence' / failed_name,
                            {'passed': False, 'family': args[0], 'saved_file_sha256': B.sha(path) if path.exists() else None,
                             'state_manifest_sha256': B.sha(manifest_path) if manifest_path.exists() else None,
                             'saved_master': False, 'errors': [diagnostic], 'compound_budget_qualified': False, 'native_gates': B.NATIVE_GATES})
            except (ValueError, OSError):
                pass
        raise
