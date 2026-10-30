# Samarkand Bazaar: editable source art

Status: source-art milestone. Native export/cook, bindings, package and game validation are deferred. No version change, GitHub promotion/push or temp cleanup.

## Open and review

Open `samarkand_bazaar.blend`, scene **PS_SamarkandBazaar**. Healthy LOD 0 is the intended opening view. Keep exactly one source state/LOD or construction collection visible. `Guides_` and `Presentation_` are authoring/review helpers, excluded from triangle counts.

A central trading dome, four rooflit vaulted arms and eight front/back shop pairs (sixteen rooms). Raised benches, textile and packaged-goods stalls, a weighing desk and restrained tile accents make its economic role readable.

The model is a historically informed interpretation. Exact completed layouts, proportions, room assignments and decorative arrangements are authored game-art decisions. See `references/SOURCES.md`, photographic attribution files and `evidence/anatomy.json`.

## Source contents

- Canonical `.blend`, with healthy, five static damage states and ruins at LOD 0/1/2.
- Four cumulative construction assemblies: foundation, walls, vaults and exact healthy finish. Scaffolding is absent at finish.
- Five original editable 2048 PNG maps in `textures/`: albedo, tangent-space normal, roughness, metalness and owner mask. Relative paths; no photograph or stock bitmap is sampled into these textures.
- `bazaar_recipe.py`, `asset_runner.py`, `states_recipe.py` and `lod_recipe.py`: deterministic staged authoring and reduction. Named anchors are recorded separately.
- `source_checks.py`, `handoff.py`, `verify_saved.py`, `rebuild_source.py`: independent geometry, contacts, dependency, state and reconstruction evidence.
- `state-manifest.json`: exact part/mesh/UV digests, collection ownership and healthy restoration contract. No native HP thresholds or selectors are assigned.
- `previews/`: actual Blender views, labeled sheets and final lit renders.

The current blend is the editable master. Future manual edits must be preserved; a recipe rebuild is a deliberate replacement of generated output, not a merge with manual art.

## Review facts

Healthy LOD 0: **46,484 triangles**. Healthy LOD 0/1/2: **46484 / 23234 / 11654**. Three installed Castle Age stock compounds were traced through native attachment/stamp and healthy-selector graphs: conservative counts 39,811, 52,029, 77,267. Median detail target 52,029; cap 77,267. Some prop visibility remains bounded; this is source geometry evidence, not a GPU capture. This smaller source model is not padded with unnecessary triangles to meet the target.

Default/campaign effective native footprint scalars remain 8 x 8. Their units are not assumed to be metres. Current visual-owner bounds, source hashes and preservation limits are in `evidence/fit-contract.json` and `native-owners.json`. No gameplay, marker, ability or lifecycle resource was edited.

All source checks cover every health/ruin LOD and construction assembly: outward closed geometry, UV0/UV1, transforms, single-user meshes, material/image closure, measured fit and stock cap. Construction finish restores the exact healthy mesh/UV composition. Contacts, LOD ratios and ruin-height limits are recorded separately.

Owner-colour previews use a red-channel source mask and editable `OWNER_COLOUR` node. Native AoE4 shader behaviour is unverified.

## Reconstruct and verify

Use installed Blender 5.2.2 or a compatible version. A fresh process is mandatory for reconstruction.

```powershell
blender --background --factory-startup --python-exit-code 1 --python rebuild_source.py -- --verify
```

This regenerates in memory and compares against the retained manifest, writing compact check evidence. It does not overwrite the master blend. `--rebuild-and-save` is an explicit replacement operation for deliberately regenerating the master; protect hand edits first. `build_all(reset_owned=True)` likewise explicitly replaces only recipe-owned objects.

The retained texture PNGs are source inputs. `make_atlas.py` can recreate the original atlas using Python, NumPy and Pillow; regenerating it replaces painted edits. Geometry reconstruction requires no sibling custom asset folder, disposable stock decode or permanent mod checkout.

Inside Blender, after adding this folder to Python's path:

```python
import asset_runner as R
R.show_state('healthy', 0)  # damage_1 ... damage_5, ruins; LOD 0/1/2
```

## Deferred native gates

Garrison export/cook/readback, Content Editor burn, private visual integration, runtime owner colour, construction/damage transitions, selectable persistent ruins, repair, package/import, lobby selection, save/load and multiplayer are not established by this source-art delivery.
