# The Grand Caravanserai — editable source art

Persia's other Feudal landmark. Original compact Seljuk-informed courtyard caravanserai, using Robat-e Sharaf as a principal medieval reference. This is a game-art interpretation of a building type, not a measured reconstruction of a named historical site.

All work remains in `F:/aoe_4_temp/Temp_before_github_push/art/persia/grand_caravanserai`. Research and the original design board are in `F:/aoe_4_temp/Temp_before_github_push/research/grand_caravanserai`. Read `RESEARCH_AND_DESIGN.md` there for linked historical evidence, visual observations, alternatives, deliberate simplifications and chronology limits. No photographs were copied into textures or distributed with the source.

## Open and edit

Open `grand_caravanserai.blend`, scene **PS_Caravanserai**. The original default **Scene**, Cube, Camera and Light are retained. Only **healthy_LOD0** is visible initially. Top-level lifecycle, construction and LOD collections are mutually exclusive compositions; show one at a time. Nested collections group architecture, vaults, ground, trim, brick detail, owner areas, cargo, cart, water, tally and surface wear. Every mesh is single-user with applied transforms and UVMap/UVMap1. Presentation cameras, lights and ground are separate in **Presentation_Caravanserai**; anchors are hidden in **Guides_Caravanserai**.

`state-manifest.json` records every part, original healthy source, role, stage, triangle count and quantized geometry/UV digest. `anchors.json` names the recipe's principal interfaces and activity locations. Construction finish restores the exact healthy mesh/UV composition. Damaged parts retain healthy source identities so future native repair integration can select the recorded composition.

## Model content

Deep recessed pointed gateway, nested geometric brick frame, low enclosure with four rounded corner buttresses, four raised pointed-vault lodging bays on each side, lower rear iwan and two small rear rooms. The single axial entrance and middle court stay readable. West unloading uses wrapped bales, tied/slatted crates, a two-wheel handcart and a short supported awning. East work includes thick stone trough, jars and fodder baskets. Rear merchant work has a tally table, ledger, chests and carpet rolls. These are static art props, without gameplay entities.

Neutral warm brick and earthen roof surfaces, limited plaster maintenance, a narrow stone footing, worn paving, dusty doorways, loading ground, drainage and damp water-area wear. Geometric brick detail is original ornament, without invented readable calligraphy. No minaret or glazed dome is used.

## Source states

| Composition | Treatment |
|---|---|
| Construction foundation | Earthen base, raised platforms, entry sill and footings |
| Construction walls | Enclosure, piers and corner buttresses |
| Construction vaults | Pointed vaults, gateway roof/coping, exposed masonry |
| Construction finish | Exact healthy composition including paving, wear, textiles and cargo |
| Healthy | Complete maintained inn with visible use |
| Damage 1–2 | Coping chips, localized impacts, textile fraying |
| Damage 3 | Broken southeast coping/cap, grounded masonry debris |
| Damage 4 | Fractured subsidiary east vault, larger local loss |
| Damage 5 | Partial east wing collapse; principal gateway remains readable |
| Ruins | Low broken piers/wall stubs, fallen vault fragments, scattered cargo remains and one small owner-coloured fragment |

No native HP percentages, lifecycle selector names, collapse animation or gameplay replacement has been invented. The ruined height is roughly 30% of healthy height. Healthy and all five damaged states plus ruins have 100%, approximately 50% and approximately 25% source geometry variants. Decimation is baked, owner regions and primary planar structures are retained, and carried UVs preserve brick scale. The lowest source variant substitutes a simple central paving strip for individual pavers.

## Textures and owner colour

`textures/` contains the shared 2048×2048 albedo, tangent normal, roughness, metalness and owner_mask PNGs plus atlas-layout.json. They are used across all states/LODs. `make_atlas.py` is the original deterministic editable texture generator, with no external photo dependency. The master uses relative `//textures/` paths. There is no packed duplicate texture bank.

The editable **PS_Caravanserai_SharedAtlas** node tree uses a separate **OWNER_COLOUR** RGB node and owner-mask R channel for portal panels, wing fascia and supported short fabric. The albedo is neutral within owner regions. Red, blue and yellow previews use the same mask. This node tree demonstrates source mask intent; native Garrison material adoption and structure shader binding need qualification during the later mod build. Non-albedo maps use Non-Color data.

## Sizing and geometry budget

Current private actor: `assets/attrib/instances/ebps/persia/ps_building_landmark_age1_trade_persia.xml` in the permanent repository. Native owner trace resolves Ottoman **ott_landmark_a_01** / its Han Caravanserai stamp and the separate Rus outskirt tier. The parent is **building_wonder_age1**. Default/campaign effective footprint values remain **8×8**; those values are not asserted to be metres.

`evidence/current-visual-envelope.json` records the installed main model's decoded bounds (including alternate lifecycle/LOD geometry) and the smaller chosen art envelope. It is sizing evidence, not an active-only native frame capture or a placement/production-clearance test. Functional markers, construction stamp, gameplay, identity and visual bindings were not altered.

The previous Gundeshapur stock survey is reused in place with path/hash in `evidence/stock-budget.json`: Council Hall 52,142, Imperial Academy 59,652, Dome of Faith 70,506 triangles. Their conservative median target is 59,652 and maximum cap 70,506. The source asset uses about 39,000 healthy triangles, below that median, because this compact layout is readable without filling the allowance with extra tessellation. Complete active mesh surroundings are counted; exclusive states and presentation helpers are excluded. Original bounded stock prop-selector limits remain explicit in the linked evidence. Exact current composition counts are in source-checks.json and lod-budget.json.

## Rebuild and verify

Main steps: `caravanserai_recipe.py` supplies anatomy and staged modeling; `asset_runner.py` supplies generic primitives, materials, UVs and collections. `caravan_states.py` supplies independent lifecycle compositions. `caravan_finalize.py` supplies broken-edge refinement and topology audit. `caravan_lods.py` creates reduced sources. `rebuild_source.py` orchestrates these in memory and only clears its own generated namespace when explicitly called with `reset_owned=True`. It never saves, cooks, exports or changes the mod automatically.

In Blender, add this source folder to sys.path, load `rebuild_source.py` by absolute path, and call `build(reset_owned=True, preview_setup=True)`. Save explicitly after review. Do not run destructive reset against a scene containing hand edits you have not saved; the default scene and unowned objects are protected. The recipe intentionally rebuilds the procedural asset, not an arbitrary later hand-edited mesh.

Configured Windows verification commands:

```powershell
& 'E:/Blender5.2/blender.exe' --background --factory-startup --python-exit-code 1 --python 'F:/aoe_4_temp/Temp_before_github_push/art/persia/grand_caravanserai/verify_rebuild.py'
& 'E:/Blender5.2/blender.exe' --background 'F:/aoe_4_temp/Temp_before_github_push/art/persia/grand_caravanserai/grand_caravanserai.blend' --python-exit-code 1 --python 'F:/aoe_4_temp/Temp_before_github_push/art/persia/grand_caravanserai/verify_saved.py'
```

The cold check compares all 25 composition part maps and geometry/UV digests quantized to five decimal places; it does not overwrite the saved master. The fresh saved-file check verifies the actual master, visibility, contacts, topology, UVs, image sizes and relative dependencies. `final_receipt.py` checks syntax, PNG readability, repository HEAD/status and protected file hashes, and prior Gundeshapur source hashes. Read final receipts for actual gate outcomes; intermediate failed diagnostics are retained.

`prepare.py` is an optional read-only installed-native-owner inventory. Run it with Blender's Python 3.13 because the installed Garrison decoder is compiled for that ABI. It reuses the small original Gundeshapur preflight helper and its stock evidence in place, without copying the stock media bank. That evidence is an advisory measurement input; the editable model recipe and textures are self-contained in this folder. `prepare.py` never compiles the mod.

`caravan_presentation.capture_states()` and `capture_extras()` create portable viewport previews. `render()` creates optional lit Cycles images using this machine's OptiX device temporarily, restoring device preferences afterward. Presentation setup follows modeling. `make_contact_sheets.py` assembles one current compact set from these PNGs. These are source previews, not native-game screenshots.

## Deferred acceptance gates

This milestone is **source art only**. No 0.9.1 build, art export/cook, Content Editor burn, private binding edits, mod integration, release metadata change, repository promotion, commit/push or temp cleanup occurred. Gundeshapur's editable master and the permanent repository are preserved.

Later combined landmark work must validate native construction transitions, material adoption and team colour, damage selector mapping, collapse, persistent selectable ruins, repair restoration, placement/production clearance, native appearance, save/load and multiplayer. Source checks cannot establish those outcomes.

## Verified full-detail counts

| State | Triangles |
|---|---:|
| healthy | 38980 |
| damage_1 | 39124 |
| damage_2 | 39196 |
| damage_3 | 39116 |
| damage_4 | 38472 |
| damage_5 | 34364 |
| ruins | 7576 |
