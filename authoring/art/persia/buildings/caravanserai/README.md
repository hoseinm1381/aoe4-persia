# Small Persian Caravanserai — original healthy source draft

Drafted2026-10-27. Existing body **A2 only**; actor `ps_building_carvansarai_economy_persia` (existing spelling retained), native resource `art/civilizations/sultanate/structures/wonder_siri_fort/sul_siri_fort_control_age02/sul_siri_fort_control_age02.rgm`. This ordinary inn is not the Grand Caravanserai landmark and does not create new gameplay tiers.

## Evidence and selected anatomy

[Deep dossier](../../../../research/persia_buildings/history/SMALL_CARAVANSERAI.md), [original functional diagram](../../../../research/persia_buildings/history/diagrams/small_caravanserai_original_typology.svg). Neither is a surveyed plan of this original asset. [UNESCO Persian Caravanserai](https://whc.unesco.org/en/list/1668/) supports varied shelter/food/water/security roles and regional forms. [Kiani/Kleiss, Iranica](https://www.iranicaonline.org/articles/caravansary/) distinguishes types, inward guest rooms, raised thresholds and rear stable passages; reported60–100cm raised guest anterooms in discussed Safavid examples are not a universal prescribed platform height. The original game's threshold here is .25 above court, selected for legibility/constraints. No building is claimed to preserve one unchanged medieval elevation.

Choose the modest plateau courtyard type: six inward guest bays, raised side walks, deeper rear stable/service band, one secure through-gate, low enclosing frontage and a meaningful empty unloading court. Ribat-e Sharaf is only a brick-craft comparator, not a miniature plan for this small inn. No circular fort, open Gulf pavilion, royal garden, minarets, blue dome, giant animal sculpture or modern hotel sign is mixed into the type.

Building outline is approximately11.0×9.85, kept low. Three separately constructed vaulted guest rooms line each side (local bay2.10, depth1.60, wall2.40 above raised base); west/east actual doors face the court through opposite90° transforms. Each room sits on its own .25 stone plinth, with an inward .50-wide raised walk and a broad middle step. Rear stable is11.0×2.0×2.65, with two real1.30-wide arched passages and low feed divisions. Single front gate is2.60×1.10×3.65, with a1.78 clear through-opening and parked leaves beside the passage. The frontal wall remains lower than the guest range; no landmark pishtaq or invented upper floor dominates.

The clear court between guest walks is6.80×6.75, roughly42% of the11.0×9.85 building area. A genuinely open trough, one jar and three small traveler chests serve the inn without covering the court in clutter. Trough dark interior is an original damp-material patch, not a validated native water shader. Wear follows gate unloading and stable approaches. Covered hierarchy and negative space differentiate it from an ordinary Market and from a military Keep.

## Native envelope, coordinates and Grand comparison gap

Native stamp transform is180° aboutZ, no translation: `x_s=-x_r; y_s=-y_r; z_s=z_r`; inverse is the same and must be applied exactly once for resource export. All source positions are stamp space. Native terrain origin is retained, F=.08 is a provisional original source floor; no terrain or native footprint edits.

Native healthy primary stamp bounds (-6.921875,-5.730469,-2.0) → (6.921875,5.925781,7.460938). Chosen source envelope (-5.95,-5.30,-.08) → (5.95,5.30,6.60). Actual highest gate roof top is3.91; unused native height is intentionally not filled. Native primary LOD0 is67,806 triangles, an inventory reference rather than a fill target.

**Lower hierarchy than Grand is a design intent, not yet measured acceptance.** The current inventory handoff contains this ordinary actor, not a qualified same-camera Grand projected-area/occupied-volume comparison. Before acceptance, parent must compare existing Grand and new small inn at the same camera/scale. Reduce secondary accommodation/portal ambition if needed; do not silently enlarge footprints or label a guessed percentage as verified. Native marker/interaction/animal/exit routes also remain unqualified.

Private compiled source uses in this family are **default/campaign/hre_brawl**, distinct from inherited official-parent candidates. Native layout-market dependency `art/civilizations/common/layouts/archetypes/layout_market/layout_market.rgm` remains a separate official graph/skeleton/marker contract. Source economic/lodging meaning does not authorize replacing or moving the layout/attachment owner.

## Checkpoint

- [x] Qualified dossier/diagram read; exact single body, hashes, private/evidence-class rows and dependency retained.
- [x] Foundation → first raised guest room → original service/guest/gate architecture → props/detail authored.
- [x] Offline checks pass **124 unique tagged objects /107 contacts**, chosen/native bounds and inverse matrix.
- [x] Front return walls trimmed at guest plinth boundaries; adjacent vault shells conservatively stop inside their bay width.
- [ ] Parent Blender/atlas/state/LOD inspection, native compound/route qualification and actual small-vs-Grand visual comparison.

## Shared source contract and evidence limits

The recipe reads the actual `PRIMARY_BODY_HANDOFF.json`, `HEALTHY_REST_BOUNDS.json`, `SOURCE_CATEGORY_COMPOUND_BOUNDS.json` and `MECHANISM_DEPENDENCIES.json`. Anchors preserve exact model/geometry hashes, native graph paths, triangle interval, measured matrix/inverse, full `source_uses` and evidence classes, private compiled uses, official-parent candidates, native dependencies/skeleton/markers and complete-category bounds. The definite primary body is the conservative architecture limit; a larger possible compound includes conditional props and is not free building space.

Default/campaign are current private compiled source uses in this handoff. Candidate `cordoba`/`xp3` inheritance rows are retained as evidence, not admitted as new runtime consumers. Parent's separately evidenced consumer contract owns final admission, including any `3hre_brawl` branches. Native gameplay, footprint, attack/weapon rigs, material states, stamp/layout/interaction/exit markers, selection and lifecycle ownership remain unchanged external contracts. No new clip, rig, tier or gameplay behavior is introduced.

House-compatible API: `root(key,state='healthy',lod=0)`, `foundation(key)`, `first_room()`, `architecture()`, `props()`, `detail()`, `build_body(key)`, `write_anchors()`; `ANCHORS`, `CONTRACTS`, `ASSEMBLIES` are available. Healthy LOD0 is the authored checkpoint. Arbitrary state/LOD collection names do not implement those states. Every repeated mesh is individually created and tagged with body, construction stage, role and structural group. Parent adapters own state/LOD derivation and subsequent inspection.

Original family atlas inputs are declared as 2048-square `textures/{albedo,normal,roughness,metalness,owner_mask}.png`. No textures were copied, generated or written here. Shared material creation will require those future inputs. No helper or other family source was edited.

Offline checking executes the actual shared runner's geometry formulas for block/extrude/arch/vault/lathe through an AST-extracted subset and a fake mesh/collection registry. No Blender process or Blender Python module ran. Checks cover syntax, unique names, required tags, positive boxes, chosen/native bounds, recorded contact equations and inverse-matrix identity. Bounding-box equations do not prove face contact, manifold/normal correctness, concave-cap triangulation, marker clearance or visual quality. Contracts with `local_seat` also record the stair ledge/tread planes, but their actual topology must be checked after build.

Parent must serially build and review six directions, openings, bearing joints, access routes/parapet gaps, native mechanisms and full compounds, terrain/water interface, material mapping and every real state/LOD before scoring the family. No 90/100 or source acceptance is claimed. Garrison cook/readback, Content Editor, owning archive, client import, runtime, repair, save/load and multiplayer remain separate unverified gates.

## Family LOD source draft, 2026-10-27

The `recipe.build_lod` hook delegates by source hash to `lods.py`. Exact intact vaults/gables coarsen together to10/4 segments and one longitudinal span; arches use8/4. All six inward guest openings, both stable passages, raised walks/plinths and the through-gate remain distinct. The complete trough becomes an exact closed hollow union with a separate water patch; a missing wall disables reconstruction. The service jar has10/6 sides when retained.

Exact polygon fingerprints prevent rebuilding altered vaults from healthy parameters, including a tested internal-vertex change with unchanged outer bounds. Fractured curves retain actual surviving meshes and core UVs; native dependencies are cloned unchanged. Offline formula counts5048→2584/1736 (.512/.344), so the far intact profile is now within the current .25+.10 numerical band, while damaged/ruined ratios remain unresolved. No LOD0 inflation or loss of court/door/support structure was used. Healthy raw edge incidence, envelopes, existing contacts, unique proxy IDs and deliberate missing/altered-part cases pass. Actual BMesh/Boolean output, state-specific ratios, triangulated saved/cold readback and six-direction/native comparison remain unverified.

Owner quick-completion steering freezes this source draft after the matched far-vault/gable coarsening. The parent baseline report had11 ratio-only errors, including higher damaged/ruined ratios. This offline healthy improvement does not clear those unrebuilt states or imply visual acceptance.
