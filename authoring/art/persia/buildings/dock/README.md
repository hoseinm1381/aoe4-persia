# Persia Dock — original healthy source draft

Drafted 2026-10-27. **Existing bodies A2/A3/A4 only**. Actor `ps_building_unit_naval_sul`; native primary resources are Ottoman `ott_dock_control_age02/03/04.rgm` under their respective `art/civilizations/ottoman/structures/dock/` directories. Exact paths/hashes and source-use evidence are retained dynamically. No Age I body is invented from the historical discussion.

## Design, anatomy and historical certainty

Use [ordinary building guide, Dock](../../../../research/persia_buildings/history/ORDINARY_BUILDING_REFERENCE_GUIDE.md). Its [Khakzad et al. Siraf maritime survey](https://www.ancientportsantiques.com/wp-content/uploads/Documents/PLACES/IndOc-Gulf/Siraf-Khakzad2015.pdf) distinguishes inferred shipwright activity from what contemporary texts actually name. The guide retains the verified reference URL; this draft does not claim a standardized excavated Persian dock plan. Source form is an original warehouse/working-quay interpretation in restrained masonry and timber, without palace domes, dry-dock gates or a modern crane.

| Existing body | Distinct major programme | Functional silhouette |
|---|---|---|
| A2 | Small landward masonry store, eastern open work shelter and broad forward loading apron | Lowest/most open roof organization; two enclosed/open halves. |
| A3 | Long western vaulted warehouse rotated90°, rear goods shelter | Strong lengthwise service spine and lateral goods doors leave a different open loading route. |
| A4 | Broad two-door warehouse, small upper counting room and supported timber stair/landing | A real working upper room and access replace the earlier long shed arrangement. |

Date bands II~1040–1256, III~1256–1501, IV~1501–1629 are selected art discussion, not invention dates. Dock identity must read from warehouse/quay/shelter anatomy without decorative cloth. Original goods crates, compact rope/tool bench, mooring posts and a small static handling A-frame reinforce work. The frame has real feet, closed diagonal supports, crossbar, suspended rope and wooden block; it is not a new animated lifting mechanism or substitute native rig. Wear is localized timber loading traffic, not an earth patch placed at sea.

## Deck, access and unresolved shoreline evidence

No full earth rectangle crosses hypothetical water. Nine piers plus a landward masonry abutment bear on an original proposed bottom at-1.15 and top at.50; four transverse beams span them (.50–.64); twelve individual planks form deck .64–.80. Every plank has four recorded beam bearings. **F=.80 and negativeY as working edge are original proposals, not measured native waterline or boat-exit conclusions.** Terrain origin is unchanged and no water/terrain/ship geometry is created. The parent must qualify native shoreline/exit direction before adopting this orientation.

A4 counting floor bears on the lower warehouse roof. A supported landing reaches it with a .08 threshold; 20 timber steps use two closed stepped stringers derived from the same local ledge planes as the treads. Landing posts/feet/beams have explicit contacts; front rail leaves an .90 arrival opening. Relative bounding-box checks on stepped stringers are accompanied by `local_seat` data and do not substitute for actual mesh inspection. Doorways, handling area and loading axis require a native-clearance review.

## Exact measured envelope and coordinate space

Current Dock stamp matrix is identity; authored stamp coordinates equal resource coordinates. Retain this evidence rather than borrowing another family's rotation. Native origin stays unchanged; the proposed elevated working deck does not establish native sea level.

| Body | Native primary healthy stamp bounds min → max | Chosen source envelope min → max | Native LOD0 triangles |
|---|---|---|---:|
| A2 | (-3.404297,-3.458984,-1.602539) → (3.4375,3.322266,7.394531) | (-3.25,-3.25,-1.15) → (3.25,3.20,7.00) |66,277|
| A3 | same native bounds as A2 | same source envelope as A2 |58,992|
| A4 | (-3.404297,-3.458984,-1.602539) → (3.511719,3.322266,8.375) | (-3.25,-3.25,-1.15) → (3.25,3.20,7.90) |102,426|

Triangle counts are native references, not fill targets. Possible complete categories extend approximately±6.125 for A2/3 and±6.012 for A4 due to conditional attachments; that does not authorize a larger quay or prove space for ship movement.

Native dependency: `art/civilizations/common/layouts/archetypes/layout_docks/layout_docks.rgm` plus official graph/skeleton/nine markers. Anchors retain full marker data and frame qualification. Marker `starting_position` raw translation (.97494,-3.98865,0) and the road-point ring are bone-local values, not projected world-space boat/worker routes. No new animation or removal of native dock owners is authorized by this architecture draft.

## Draft plan/checkpoint

- [x] Exact A2/A3/A4 bodies, private source uses/candidate evidence and native dependency retained.
- [x] Foundation piles/beams/deck → first warehouse → distinct per-body architecture → practical props/detail authored.
- [x] Offline test: A2 **95 objects/117 contacts**, A3 **94/117**, A4 **122/147**; all unique tagged parts, recorded equations, chosen/native envelopes and inverse matrices pass.
- [ ] Parent shoreline/exit qualification, serial Blender mesh/visual review, atlas, full compound and every state/LOD gate.

## Shared source contract and evidence limits

The recipe reads the actual `PRIMARY_BODY_HANDOFF.json`, `HEALTHY_REST_BOUNDS.json`, `SOURCE_CATEGORY_COMPOUND_BOUNDS.json` and `MECHANISM_DEPENDENCIES.json`. Anchors preserve exact model/geometry hashes, native graph paths, triangle interval, measured matrix/inverse, full `source_uses` and evidence classes, private compiled uses, official-parent candidates, native dependencies/skeleton/markers and complete-category bounds. The definite primary body is the conservative architecture limit; a larger possible compound includes conditional props and is not free building space.

Default/campaign are current private compiled source uses in this handoff. Candidate `cordoba`/`xp3` inheritance rows are retained as evidence, not admitted as new runtime consumers. Parent's separately evidenced consumer contract owns final admission, including any `3hre_brawl` branches. Native gameplay, footprint, attack/weapon rigs, material states, stamp/layout/interaction/exit markers, selection and lifecycle ownership remain unchanged external contracts. No new clip, rig, tier or gameplay behavior is introduced.

House-compatible API: `root(key,state='healthy',lod=0)`, `foundation(key)`, `first_room()`, `architecture()`, `props()`, `detail()`, `build_body(key)`, `write_anchors()`; `ANCHORS`, `CONTRACTS`, `ASSEMBLIES` are available. Healthy LOD0 is the authored checkpoint. Arbitrary state/LOD collection names do not implement those states. Every repeated mesh is individually created and tagged with body, construction stage, role and structural group. Parent adapters own state/LOD derivation and subsequent inspection.

Original family atlas inputs are declared as 2048-square `textures/{albedo,normal,roughness,metalness,owner_mask}.png`. No textures were copied, generated or written here. Shared material creation will require those future inputs. No helper or other family source was edited.

Offline checking executes the actual shared runner's geometry formulas for block/extrude/arch/vault/lathe through an AST-extracted subset and a fake mesh/collection registry. No Blender process or Blender Python module ran. Checks cover syntax, unique names, required tags, positive boxes, chosen/native bounds, recorded contact equations and inverse-matrix identity. Bounding-box equations do not prove face contact, manifold/normal correctness, concave-cap triangulation, marker clearance or visual quality. Contracts with `local_seat` also record the stair ledge/tread planes, but their actual topology must be checked after build.

Parent must serially build and review six directions, openings, bearing joints, access routes/parapet gaps, native mechanisms and full compounds, terrain/water interface, material mapping and every real state/LOD before scoring the family. No 90/100 or source acceptance is claimed. Garrison cook/readback, Content Editor, owning archive, client import, runtime, repair, save/load and multiplayer remain separate unverified gates.

## Family LOD and stringer correction draft, 2026-10-27

The family `build_lod` hook loads `lods.py` by its current source hash. Twelve actual boards coarsen to2/4-board strips, complete canopy runs retain5/3 supported rafters, intact arches/vaults use8/10 and4/6 segments, complete mooring posts become closed distant profiles, and the complete counting stair uses7/4 matched treads with both stringers. Missing/altered members disable whole-unit proxies; actual deck gaps split strips, and damaged curved solids keep their surviving fracture geometry and masonry-core UVs. Piles, abutment and beams remain.

The original A4 stringer lower chord crossed the upper tread ledges. LOD0 now uses a parallel underside .35 below the tread-bottom slope, clipped at deckZ=.80 until its actual knee. The same construction is used at LOD1/2. The actual function AST regression reproduces10/2/2 proper outline crossings before correction and0/0/0 after, while every tread bottom equals its stringer ledge and original XY/Z extrema remain. Run ordinary Python on `evidence/verify_stringer_profiles.py`; exact coordinates, hashes and results are in `evidence/stringer-polygon-regression.json`. This proves the planar formula, not triangulated Blender solids.

Offline triangle counts LOD0→LOD1/2: A2 1140→840/708 (.737/.621), A3 1720→1084/856 (.630/.498), A4 1980→1292/1052 (.653/.531). The .5/.25 targets are not met by all bodies; useful bearing/clearance geometry remains and LOD0 was not inflated. Healthy raw edge incidence, bounds, existing scalar contacts and unique identities pass; deliberate missing/changed-part cases pass. Actual modifiers/triangulation, damage/ruin ratios, saved/cold readback and visual review remain parent gates.
