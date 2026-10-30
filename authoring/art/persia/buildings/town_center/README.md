# Town Center source recipe — revised civic draft, parent rebuild pending

Authoring scope: `recipe.py` and these notes only. No Blender access, scene generation, renders, native export/cook/build or mod changes were performed. No asset acceptance is claimed. The parent built an earlier healthy draft; the revised source below requires a fresh serial build and review. Existing previews/master describe the earlier geometry until that rebuild. No Blender was run by this source author.

## Architectural choice

This is an **original Persian civic meeting and administration compound**, not a scaled House and not a reconstruction of a universal medieval town hall. It uses an open public hall, a meaningful assembly court and unequal low service ranges. The body should read publicly accessible even with the props removed. It must remain distinct from the fiscal Divan, War Divan, inn, mosque and Wonder.

The historical basis is the [ordinary-building research guide](../../../../research/persia_buildings/history/ORDINARY_BUILDING_REFERENCE_GUIDE.md), especially civic/gateway organization and the relative hierarchy of occupied offices, covered public space and service rooms. Reference dates remain explicit: Ali Qapu's recognizable timber talar was added in 1643–44, outside the main 934–1629 band. The Age-IV broad porch borrows that **later qualified regional vocabulary**, not an exact claimed 1629 elevation. No minarets, monumental prayer dome, palace reflecting pool or fake calligraphy are proposed.

| Existing age/body | Architectural programme | Geometry that changes |
|---|---|---|
| A1 | Open civic meeting hall and a working public court | Front timber posts/beam/joists and quiet flat clay roof; substantial low west store and small east service room |
| A2 | More regular covered public hall | Three real masonry arcade openings and separate barrel-vaulted bays; shifted service ranges and a wider regular central approach |
| A3 | Expanded administration over the meeting frontage | Broad east-expanded reception office with two actual windows, fixed west landing, bracket-supported hood and longer stair; lower public hall retained, west service range shifted clear |
| A4 | Broad inhabited council range with a public upper porch | Broad council range with paired rear/side windows, four pier-aligned porch posts, explicit front/rear beam load paths, visible upper owner cloth and notched-deck turn landing |

These are artistic age choices rather than a claim that timber, vaults or upper rooms were invented in the respective game ages. Decoration is restrained and subordinate to the changes in programme and massing.

## Actual native mapping: four bodies, shared capital/secondary

The current `PRIMARY_BODY_HANDOFF.json` identifies exactly **four primary Town Center bodies**, reused by both `ps_building_town_center_capital_sul` and `ps_building_town_center_sul`. Its `source_uses` explicitly distinguishes existing private compiled variants from official-parent inheritance candidates. Default/campaign records are private evidence; cordoba/xp3 candidate records are **not separately serialized private runtime consumers and do not authorize automatic authoring scope**. The parent supplies the final native consumer contract, including any separately evidenced `3hre_brawl` branches. `consumer_evidence()` retains the original source-use classes without hardcoding all candidate names as approved consumers. Current availability/unlocks stay unchanged. This recipe creates no extra capital tier and no new secondary-only appearance.

`A1` through `A4` map respectively to:

`art/civilizations/sultanate/structures/towncenter/sul_towncenter_combined_age0N/sul_towncenter_combined_age0N.rgm`

The existing visual attachment choice is:

`attachments/attachment_lists/civilizations/sultanate/buildings/town_center_sul/tierN_town_center_control_sul`

N=1..4 only. Existing age requirements/actions are recorded in the inventory. No actor source files are edited by this recipe.

## Measured envelope and transform

Source: `research/persia_buildings/inventory/HEALTHY_REST_BOUNDS.json`. The measured bounds are **healthy primary-body rest geometry**, with exact current source/collection membership, then the recorded stamp matrix. They are not a full compound maximum, engine footprint, native ground plane, doorway measurement or unit-clearance measurement. Outskirts and native bell dependencies are separate.

| Age | Stamp-space min x/y/z | Stamp-space max x/y/z | Primary healthy LOD0 triangles |
|---|---|---|---:|
| I | -7.991406, -7.563672, -1.613281 | 7.856250, 8.004687, 5.796875 | 43,003 |
| II | -7.909375, -7.778516, -1.599609 | 7.754688, 8.098437, 6.757813 | 43,877 |
| III | -7.909375, -7.778516, -1.599609 | 7.754688, 8.098437, 6.757813 | 45,718 |
| IV | -7.941654, -7.699280, -1.599609 | 7.863034, 8.029236, 9.460938 | 55,886 |

The authored review plan lies inside x[-6.85,6.85], y[-6.55,6.45], with foundation bottom -.08 and a chosen ground surface F=.16. Height caps are 5.30 / 6.20 / 6.30 / 8.35; geometry may be substantially lower than these caps. Caps are conservative containers, not instructions to use the whole height. `foundation()` records arithmetic side/top margins, and the parent must measure the actual built geometry before calling it fitted.

The native **resource → stamp** transform has x/y inversion and translation:

- Ages I–III: x'=-x-2.2999999523, y'=-y-5.3000001907, z'=z.
- Age IV: x'=-x-2.3166539669, y'=-y-5.2207641602, z'=z.

The source is intentionally authored in stamp space for a centered review. `ANCHORS` records the transform and inverse. Since this 180-degree matrix is its own inverse when z translation is zero, the same x/y equations convert to resource coordinates. **The future adapter must apply that inverse exactly once**, retaining the correct native pivot/markers; no implicit transform is applied in this draft. Passing an already transformed source through the matrix again would be wrong.

The rectangular source bed and native ground-origin interpretation require review. None of the above is proof of clearance from the full native bell, moving geometry, exits, targeting markers, repair or rally locations. Opening dimensions such as 2.05 m are **original proposed source dimensions**, not invented “measured stock doorway” values.

## Stage/API contract

The recipe matches the House-facing callable surface:

1. `foundation('A1')`: selects an owned body, creates the court's source bearing planes and records the native mapping/envelope proposal.
2. `first_room()`: creates the main civic hall's back/side walls and floor. No roof or finish detail is added here.
3. `architecture()`: creates actual arcade/door gaps, main roofs, unequal service rooms, the age-specific upper programme/access and low civic boundary.
4. `props()`: adds protected clerk/records, water provision, received supplies and public notice board, keeping the central court open.
5. `detail()`: adds supported owner textile, selective useful masonry detail and bedded approach pavers.

`build_body('A1')` runs those stages for a future parent-controlled draft build and calls `show()`. It logs **uninspected**, not accepted. `root(key,state,lod)`, `ANCHORS`, `CONTRACTS`, `write_anchors()`, tags/stages/roles/structural groups, and explicit `reset_owned(key=None)` are supplied. Reset never runs on import and filters only this family or an explicitly requested body.

Each `B`, arch, vault, lathe or timber element creates a separate mesh through the common runner; no linked instances or copied House mesh are used. Contacts include roof/wall bearings, post/beam/deck/joist seating, stair ground planes and supported clerk furniture. Contacts can be numerically evaluated by the parent, but contact arithmetic alone is not an inspected assembly. The recipe contains no new mechanism, rig, animation or scripted behavior.

## Town bell and other native dependencies

The existing actor has a separate bell-arch attachment group:

`attachments/attachment_lists/civilizations/common/buildings/building_town_center_bell_arch`

The base layout is:

`art/civilizations/common/layouts/archetypes/layout_towncenter/layout_towncenter.rgm`

Outskirts use the existing early and later `sul_towncenter_01` / `sul_towncenter_03` attachment paths. The broad native bell attachment contains conditional civilization alternatives; do not activate unrelated alternatives or assume its entire menu is visible for Persia. Preserve whichever existing native path, pivot, marker, graph and rig actually owns the active bell mechanism. **No replacement bell or dummy animation is authored here.**

The primary-body mechanism inventory exposes native damage physics actions; that does not qualify the bell's pivot or moving swept volume. Bell/marker clearance is a declared adapter gap. The parent must identify the active bell chain and compare it with the new roofs before source acceptance. Do not silently treat this empty mechanism inventory as proof that Town Center has no functional mechanism.

## Original texture inputs

The recipe references this family's `textures/albedo.png`, `normal.png`, `roughness.png`, `metalness.png`, and `owner_mask.png`, all intended as original 2048×2048 atlas sources. No stock pixels or House texture images were copied. Only paths/specification are supplied under this narrow two-file authoring scope; the parent has generated the family atlas for the earlier draft. This refinement edits no texture pixels and still deliberately requires the declared inputs. Parent must inspect the new coping, reveal, tile-band and paper/owner semantics against that original atlas.

Use quiet plaster/clay, selected brick/stone edges, dark timber and a limited readable textile owner area. Tile density must remain far below the mosque/Wonder. Do not fill the native triangle allowance with invisible subdivisions.

## Revised architecture and LOD checkpoint — 2026-10-27

Owner/parent requested substantive civic refinements after independent inspection of the earlier healthy renders. Changed files in this pass are only `recipe.py`, `lods.py`, `state-profiles.json` and this README. Utility door leaf bottoms retain the parent's existing sill-height correction and their contacts still pass.

The revised A3 office anchors its west facade atX-2.95 and expands east toX2.25; two deep actual reception windows replace the tiny solitary square. Timber reveals, a partially shuttered opening, a real interior counter and four closed triangular brackets bearing a shallow hood make occupation readable. West stair now runsY-1.0..2.95 with22 steps; the west service block moved forward to keep the longer stair clear. Rear hall parapet/coping omits the occupied office interval instead of passing through its back wall.

A4 now has two rear and two openings in each side wall, actual sill/head/jamb/reveal parts, and three complete front modules spanning the full council width. Upper/lower porch supports derive from the actual three-bay ground arcade piers: X[-4.785,-1.633333,1.633333,4.785]. No post remains on the central public/council axis. Front beams, lower wall ledger, rear roof ledger, joists and deck retain explicit bearing equations. Capital collars sit at actual beam bearings. One supported owner cloth is now on the visible upper-front beam, atY.495, rather than behind the porch; actual RGB/readability must be rechecked in fresh renders.

The west A4 stair/turn landing was also repaired:22 steps fromY-2.8 to1.2 reach a .9×.8 landing; an actual six-vertex deck notch butts the landing atX-4.55 with no overlapping flat floor faces. The left floor joist shortens into that landing; the other joists bear on the wall ledger. A named `numerical_interfaces` surface point(-4.55,1.60,3.54) checks the actual concave deck edge, rather than pretending the overall deck bounding box represents its notch. No native worker route or clearance claim is made.

Useful authored detail includes separate30cm-proposal coping units seated on parapets, brick voussoir rings against real arcade faces, timber capitals/reveals, clear notice-board marks, a larger protected clerk/register/ink station and localized handling/rain wear. Coping end courses stop at side-course faces to avoid top-plane overlap. The court remains an open public apron. These are original source dimensions and patterns, not a claimed measured historic town-hall kit or a requirement to fill the native triangle budget. Existing atlas pixels remain the parent's original inputs.

`build_lod(H,key,state,source,destination,level,profile)` delegates to the TC-owned `lods.py`. Parent must call this hook from `family_states` when present; the older generic path will not apply this authored reduction. Policy:

- LOD1 groups contiguous intact coping units into3-unit runs (4 forA1); LOD2 uses each surviving continuous run. Missing units, fractured units and gaps larger than mortar split runs. No every-other-brick omission or healthy cap regeneration across damage.
- True original arch/vault profiles reduce to fewer segments only when actual bounds remain intact. Clipped geometry is cloned from the damaged source. Door/room holes, primary walls, roofs, posts, beams, ledgers and structural groups remain.
- Complete intact stairs become closed6/3-step profiles with the same run, final height and landing. Missing, shortened or fractured stair sets are not regenerated. Joists retain end/middle bearings, with5/3 representative members.
- Fine trim/wear and distant small props reduce separately. LOD2 retains the architectural clerk platform while omitting its small furnishings. Native retained dependencies bypass all reduction. All generated proxy names include body/state/LOD to avoid cross-composition collisions.
- No ratio is forced by deleting structural bearings or filling a missing bay. Actual final ratios and visual reads remain parent checks. Small independent curved props may use Blender DECIMATE; the offline test deliberately did not execute that modifier.

The TC-owned state profiles now cap office/council stairs and porch supports during heavy failure/ruins, keeping elevated access/deck assemblies from surviving as intact unsupported geometry. Native lifecycle ownership/thresholds remain unchanged.

### Fresh offline evidence

The test evaluates actual shared runner geometry formulas via AST plus an in-memory mesh registry, not Blender. All scalar equations include projected overlap checks; all body bounds stay inside the chosen/native envelope. The named notch point lies on both authored interface faces analytically; actual Blender BVH verification remains pending. Structural groups survive all tested healthy LOD proxies.

|Body|LOD0 parts|Contacts|Formula triangles LOD0|Mock LOD1 ratio|Mock LOD2 ratio|Actual maximumZ|
|---|---:|---:|---:|---:|---:|---:|
|A1|262|219|3,456|.5313|.2222|3.615|
|A2|205|110|4,368|.4863|.2308|4.070|
|A3|378|282|5,060|.5186|.2458|6.295|
|A4|412|374 +1 surface interface|5,492|.5062|.2790|6.775|

Total1,257 parts and985 scalar contacts pass. Syntax/JSON parse pass. A same-registry preview build checks state-specific names; simulated missing-coping, protected-fracture and incomplete-stair cases confirm the intended anti-healing branches. These are tests of authored formulas/policy, not actual boolean/native-state or Blender modifier results. Triangle formulas are diagnostic and actual Blender triangulation/budgets remain the parent's gate.

Parent must rebuild all124 source compositions, inspect healthy A3/A4 and owner colors before the full visual rubric, then review damage/ruins/construction/LODs in multiple directions and cold-save/readback. The previous healthy renders and71/85 inspected subtotal do not score this revision. No90/100, source acceptance, Garrison cook, native color/placement/mechanism, Content Editor, package/import or runtime result follows from these offline checks. Native bell/layout/outskirt clearance remains explicitly open.
