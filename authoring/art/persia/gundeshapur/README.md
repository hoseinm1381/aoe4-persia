# Gundeshapur editable source art

Status: complete source-art review set. **Native game integration is deferred.** This folder is retained in `Temp_before_github_push` while the other landmarks are developed. No 0.9.1 build, version change, mod integration, GitHub promotion/push or temp cleanup is part of this milestone.

## Open and inspect

Open `gundeshapur.blend`, scene **PS_Gundeshapur**. The original default `Scene` and its three objects are retained. Healthy LOD0 is the default visible source composition. Expand the named state collections in the Outliner. Show exactly one state/LOD or construction collection at a time; hide the others. The `Presentation_Gundeshapur` and hidden `Guides_Gundeshapur` collections are helpers and never part of asset triangle counts.

For scripted selection inside Blender:

```python
import sys
sys.path.insert(0, r'F:/aoe_4_temp/Temp_before_github_push/art/persia/gundeshapur')
import asset_runner as R
R.show_state('healthy', 0)  # damage_1 ... damage_5, ruins; LOD 0, 1 or 2
```

The `OWNER_COLOUR` node in `PS_Gundeshapur_SharedAtlas` changes the Blender owner-colour preview. Red, blue and yellow all use **the same mask**. Masonry stays neutral. The mask is original source data, not a claim that a native AoE4 shader binding has been installed.

## Design

Research basis: `../../../research/gundeshapur/GUNDESHAPUR_RESEARCH_AND_DRAFT.md` from the temp root (actual research folder is `Temp_before_github_push/research/gundeshapur`). This is an informed Sasanian architectural interpretation; the exact historical academy layout is unknown.

The compound uses a deep elliptical masonry iwan, two low four-bay vaulted wings, a modest unglazed rear reading dome, low entrance walls and a clear central approach. Three activity groups contain documents/mats/writing furniture, medical herb drying/jars/baskets, and compact entrance supplies. Wear follows maintenance, storage, thresholds and drainage. Healthy plaster-loss pieces are intentional thin surface layers; damage states contain structural breaks.

All geometry fits inside the measured current Imperial Academy source envelope. The effective inherited default/campaign `site_ext/footprint_scale` remains **8 x 8**. These are native attribute values, not an asserted conversion to metres. Current visual owners were traced through the existing Persian first-tier Qutub Minar and second-tier Imperial Academy attachments. No owner, marker, footprint, gameplay or tuning file was edited. Native placement and clearance remain a later game validation gate.

## Sources retained

- `gundeshapur.blend`: canonical current editable source, seven health/ruin compositions, four cumulative construction assemblies, two reduced-detail levels for each health/ruin state, shared editable shader nodes.
- `textures/`: shared 2048 x 2048 albedo, normal, roughness, metalness and owner-mask PNGs, plus named tile layout. Relative Blender paths. Original texture-generation source is `make_atlas.py`; no external bitmap dependency.
- `gundeshapur_recipe.py`, `asset_runner.py`: staged architecture, detail, working activity and wear operations. Named guide positions are also recorded in `anchors.json`.
- `states_recipe.py`, `finalize_source.py`, `lod_recipe.py`: construction/damage/ruin composition, explicit contact/topology refinements and selective LOD reduction. Structural walls, owner areas and healthy paving are preserved in the LODs. Secondary roof and basket relief is removed first. The smallest ruin LOD uses a closed simplified paving plate.
- `state-manifest.json`: every source part, collection, surface, construction stage, healthy-source reference and mesh/UV digest. The completed construction composition matches the healthy source exactly. No invented HP thresholds or native selector assignments.
- `source_checks.py`, `contact_checks.py`, `handoff.py`: acceptance checks, measured bearing/contact interfaces, state restoration and original-scene preservation receipts.
- `previews/01-states.png` through `07-atlas.png`: compact comparison sheets. Individual current views and the lit healthy/ruin renders are retained alongside them.
- `evidence/`: stock source measurements, protection baseline, check results and compact step diagnostics. Existing stock decodes are read-only reference inputs retained for this unpromoted milestone.

## Source states

| Composition | Treatment |
| --- | --- |
| Construction foundation | Plinth, court bed, paving, floors and steps |
| Construction walls | Walls/piers plus temporary scaffold |
| Construction vaults | Supported vaults and dome plus scaffold |
| Construction finish | Exact healthy composition, scaffold removed |
| Healthy | Maintained weathered compound, complete working groups |
| Damage 1-2 | Localized plaster loss, chipped caps, frayed short textiles |
| Damage 3 | Broken subsidiary upper band/cornice and matching debris |
| Damage 4 | Fractured subsidiary vault and exposed masonry |
| Damage 5 | Partial east-wing collapse; the main iwan stays identifiable |
| Ruins | Ragged thick wall stubs, broken piers, grounded vault/dome fragments, one small owner fragment; maximum height about 29% of healthy |

## Budget and checks

Healthy complete visible source: **57,996 triangles**, including the active ground and working props. Reduced levels target 50% and 25%; exact current counts and all state ratios are in `evidence/lod-budget.json`. Mutually exclusive states and presentation helpers are excluded.

The installed stock Imperial Academy, Dome of Faith and Council Hall were traced through attachment/stamp sources and native healthy selectors. Their conservative complete-compound healthy lower counts are 59,652, 70,506 and 52,142 respectively: median target **59,652**, conservative cap **70,506**. Some small-prop numeric selectors remain bounded rather than exactly solved by the decoder; upper intervals and exclusions are explicit in `evidence/stock-budget.json`. Terrain splats and non-mesh marker resources are excluded from this authored-mesh metric. This is offline source evidence, not a measured native GPU draw capture.

Passing source checks cover closed topology, outward volume, UVs, relative image dependencies, 2048 atlas sizes, identity transforms, single-user meshes, state/LOD budgets, source envelope, low ruin height, 26 measured bearing/prop contacts, exact healthy restoration and recorded default-scene fields. Six solid orthographic views and courtyard/contact details are included.

## Reproduction

The current `.blend` is the editable master, including any future manual changes. Running the recipe regenerates its owned output; it is not an update merge for hand edits. `rebuild_source.py` requires an explicit `reset_owned=True` to replace generated Gundeshapur objects in an existing scene. It never removes unrelated objects, writes tuning, launches a cook or builds a mod. `verify_rebuild.py` is a cold in-memory recipe smoke test and does not overwrite the saved master.

After approved source changes, regenerate the relevant previews with `presentation_recipe.py`. `capture_set()` uses the Blender viewport and is the portable preview route; lit `render()` uses the local OptiX-capable GPU and restores render-device preferences afterward. assemble sheets using `make_contact_sheets.py` with Pillow. Use `source_checks.run()`, `contact_checks.run()` and `handoff.write()` before saving. Keep the whole texture/recipe/manifest closure with the blend.

## Deferred native gates

Garrison export/cook/readback, native owner-colour shader behavior, ordered construction transitions, damage selector thresholds, collapse effects, persistent selectable ruins, repair restoring the exact healthy compound, native placement/clearance, import and multiplayer are **unverified and deferred** until the combined landmark mod build is authorized. No native gameplay success is claimed by this source-art handoff.
