# Persia editable building sources

This is the owner-requested temporary source-art workspace. The permanent mod,
its gameplay, six age-up landmarks and releases are preserved. No integration,
cooking, package, version change, promotion, push or cleanup belongs to this set.

The latest owner priority is quick completion of all20 families, reuse of existing
research and proven helpers, batch state/LOD generation, one visual review per
family and fixes for visible defects. Exhaustive audits and native validation
are deferred. Saved sources and numerical QA acceptance are separate statuses.

## Open and edit

Each family folder contains its current named `.blend`, original five-map2048²
atlas textures, recipe, anchors, native contracts, state profiles, state manifest
and evidence. The original objects remain individually editable. Show the named
body/state/LOD collection; all other composition collections are hidden to avoid
superimposing source alternatives. Construction uses four source assemblies;
five damage levels are authored compositions and do not invent native HP gates.

`state-manifest.json` maps each consumer/body/state/LOD and retained dependency.

Outpost also has `outpost/equipment/outpost_configurations.blend`: eight legal
basic/fortified equipment choices, each with31 editable source assemblies. Its
separate configuration manifest records active original arrow guards, retained
native mechanism inputs and source-only collapse choices. Original native arrow
housing stays inspectable as an inactive reference where incompatible with the
new architecture. Configuration motion, native marker frames and LOD performance
are deferred validation gates.

`native-contracts.json` distinguishes actual private consumers from inherited
parent candidates. Review the family README for its architectural programme and
particular mechanisms. `_shared` owns reusable geometry/material helpers only.

Manual mesh edits are protected by saved-file SHA guards. Do not overwrite a
manually changed master with a recipe rebuild. Reconcile the edit into its recipe
or preserve it as an explicit retained input before rebuilding. No script edits
or saves an unrelated live Blender scene.

## Rebuild a source checkpoint

Use a dedicated factory Blender process, one at a time. From the temporary root:

    & 'E:\Blender5.2\blender.exe' --background --factory-startup --threads 2 --python-exit-code 1 --python art/persia/buildings/_shared/fast_checkpoint.py -- FAMILY

The retained process logs record the exact commands used.
House uses its preserved pilot `build_source.py` pipeline. The strict generic
builder is `_shared/build_family.py`; quick checkpoints deliberately retain failed
numerical checks rather than converting them into successful QA receipts.

Render with `_shared/render_quick_review.py` after opening the intended saved
master in a background Blender process; generate sheets with `quick_sheets.py`.
The renderer never saves a source master. Red/blue/yellow owner previews are source
shader checks; native owner rendering remains unverified.

## Review and limitations

The current completion ledger lives at
`research/persia_buildings/COMPLETION_LEDGER.md`. It reports authored sets, one-pass
visual reviews, unresolved numerical checks and provisional LOD fallbacks. A
checkpoint does not imply the old90/100 exhaustive acceptance gate has passed.
Source readback/cold reconstruction, LOD ratios, contact/UV/normal audits and exact
attachment closure not completed under the quick scope remain explicitly open.

All Garrison/native export, cook, admission/binding, colour, mechanisms, state
transitions, destruction/repair, package/import and multiplayer are unverified.
Original rigs, graph/marker inputs and native resource provenance are retained;
inspectable rest poses do not prove game animation. No new animation clips exist.
