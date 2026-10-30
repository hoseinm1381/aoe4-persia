# Persian House — source-art pilot

Passed source-art QA at 90/100. Covers four native ages and all three native house body categories (12 combinations), with 372 verified compositions. See `evidence/acceptance.json` for the exact master, rubric and bound evidence. Owner promotion approval and native validation remain deferred.

The proposed low courtyard / L-shaped vaulted home / upper domestic wing / shaded upper residence progression is an original game-art progression. It is not a historical assertion that upper floors or elaborate domestic rooms first appeared in these ages. See `research/persia_buildings/history/HOUSE_PILOT_EVIDENCE.md` for the evidence and chronology limits.

Sources and previews remain in temp. Permanent source/gameplay, all six landmark families and release metadata are read-only. No cooking, mod integration, pushing or cleanup is included.

## Editing and reconstruction

- Open `house.blend`, scene `PSB_house`. The original factory `Scene` remains intact.
- The twelve native alternatives are A1a..A4a, A1b..A4b and A1c..A4c. Alternatives are independent compositions, never a combined placement. Use `recipe.show(key,state,lod)` in this folder's Python context to show exactly one body.
- Each body has 31 top-level compositions: healthy, five damage levels, grounded ruins, preview and targeting at three LODs, plus four full-detail construction assemblies. `construct_finish` is geometry/UV-identical to healthy. Exact native construction labels are grouped only as a source proposal; no thresholds or runtime wiring are invented.
- `recipe.py` owns original domestic plans, stage ordering, anchors, material roles and named bearing contacts. `states.py` owns structural damage/collapse and readable LOD omissions. `fit.py` applies one retained per-body affine transform to all states; native actor, stamp, footprint and sockets are not edited.
- The five original 2048-square PNGs in `textures/` are retained source inputs. `make_textures.py` and `_shared/atlas_source.py` document their original painting. No stock photographs or game textures were used. Owner colour is a preview shader input driven by the red owner mask, not painted blue/red/yellow into albedo.
- Every repeated mesh has its own editable mesh datablock. There are no linked repeated meshes, library links or new animation clips. House has no moving mechanism requiring a donor rig.
- The narrow A4c has a real internal stairwell and upper-side opening; the wider A4a/b use an exterior solid stair. A4a's side-roof/porch join is partitioned into non-overlapping source slabs, rather than hidden by a render patch.

From a fresh Blender factory process, run `build_source.py -- A1a A2a A3a A4a A1b A2b A3b A4b A1c A2c A3c A4c`. Use `--probe` for an in-memory subset check without replacing the master. A saved-master SHA guard refuses to overwrite a manual/external edit. Preserve that edit and reconcile it into the recipe before updating the ownership hash; do not bypass the guard.

Open the saved master in a fresh process and run `verify_saved.py`; run `verify_rebuild.py` from factory startup for cold reconstruction without saving. These checks use retained original textures and compact measurement contracts; they do not require the multi-gigabyte stock decoder cache. `state-manifest.json` retains per-part geometry/UV digests and consumer/state proposals. `native-contracts.json` records donor bounds and exact source provenance. Family-specific readback/rebuild receipts are acceptance evidence only when current and passing.

## Inspection and limits

`qa_render.py -- solid` produces six orthographic directions for every body. `-- materials` produces current textured ages/alternatives, two complete damage/construction sequences, representative LODs and red/blue/yellow owner previews. These cameras are source inspection views; they are not native in-game screenshots. `presentation.py` frames measured source bounds to avoid cropped roofs and never saves its cameras/lights into the master.

`qa_render.py -- coverage` and `qa_sheets.py coverage` retain all 372 source-composition frames and twelve complete body sheets. The accepted checkpoint has 490 hash-verified inspection frames in total. All twelve coverage sheets were reviewed after the independent rubric audit; no further objective defect was found.

The checks cover positive closed mesh volume, normals, transforms, bounded UVs, individually editable meshes, resolvable atlas images, named Z bearings with XY overlap, exact construction restore, placement-source equivalence, per-state native envelopes, stock triangle caps and approximately half/quarter LODs. The roof detector is deliberately scoped to upward rectangular roof/deck faces; buried structural joinery is not an error merely because it intersects. This is not a complete CAD collision solver or native walkability proof.

Historical scale evidence includes roughly 1.9-unit unposed villager geometry and a conditional actor animator-scale field of122. Neither proves native doorway passage or posed/world height. Existing native transforms and gameplay footprints are preserved; native clearance remains a later gate. Research distinguishes archaeological evidence, later regional comparators and original age progression.

Visual acceptance requires the task rubric and all objective gates. A generated file, a passing source check or a provisional score is not family completion. See `research/persia_buildings/COMPLETION_LEDGER.md` for current roster status.
