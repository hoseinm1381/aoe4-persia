# Persia Keep — original healthy source draft

Drafted 2026-10-27. **Only one existing body: A3**. Actor `ps_building_defense_keep_control_sul`; native primary `art/civilizations/sultanate/structures/keep/sul_keep_control_age03/sul_keep_control_age03.rgm`. No extra Age IV body is invented merely because the defensive building remains available later.

## Design, anatomy and historical certainty

Use [ordinary building guide, Keep](../../../../research/persia_buildings/history/ORDINARY_BUILDING_REFERENCE_GUIDE.md). [UNESCO Bam](https://whc.unesco.org/en/list/1208) is a fortified earthen-settlement comparator with restoration/earthquake reconstruction history; it is not proof of a pristine unchanged medieval elevation. The guide's cited [Iranica fortifications survey](https://www.iranicaonline.org/articles/fortifications/) supports site-dependent defensive relationships. This draft is an original compact fortification, not a copy or miniature of Bam or the separately planned named landmark.

Primary anatomy: thick curtain base and walk; controlled arched through-gate; two low chamfered gate-flank platforms; one taller offset occupied guard/store hall; real narrow high guard/light slit; grounded access to the curtain and strong-hall roof. Strong hall is a lofty single occupied volume, not a box falsely implying an inaccessible second floor. Gate and curtain dominate the lower silhouette; a limited stepped parapet gives defensive identity without needle turrets, mosque dome, minarets or automatic European bastions. Original A3 visual date band is approximately 1256–1501 only as game art discussion; masonry methods and upper defenses were not invented in that interval.

Anatomy/proportion choices are original: whole ground envelope 13.9×13.9; strong hall 5.4×4.4×7.7 above source floor, wall thickness .60; curtains 1.1 thick/4.2 high with .18 walk caps; gatehouse 4.0×2.0, 1.85 clear arched opening and shared front/back axis. Low octagonal/chamfered flanks have radius1.30 and retain two actual walk junction gaps. These dimensions are not archaeological measurements or measured stock doorways.

Access is functional source geometry: 29 grounded masonry steps rise from court to `WALK_Z=4.46`; solid landing joins curtain and a 1.10-wide parallel upper walk; 24 further steps rise to strong roof Z7.96; a rear landing ends exactly at the roof edge and matches the omitted west parapet Y2.6–3.3. Broad access podium and taller landing form an intentionally heavy defensive buttress, not floating stone balconies. Butt surfaces were trimmed to avoid coplanar walk caps/exposed faces. A cistern, a few guard chests and concentrated gateway/stair traffic wear communicate occupation; no piles of copied weapons replace the architecture.

## Exact measured envelope and coordinate space

All points are **measured native stamp space**. Resource-to-stamp is approximately `x_s=y_r; y_s=-x_r; z_s=z_r`, no translation. Full floating-point matrix/inverse remain in anchors; inverse `x_r=-y_s; y_r=x_s; z_r=z_s` must be applied exactly once if parent exports resource-space geometry. Preserve native origin; F=.08 is an original provisional source bearing plane, not a recenter from buried stock Z minimum.

Native healthy primary stamp bounds are (-7.44140625,-7.44140625,-3.0) to (7.5546875,7.5546875,13.5625). Chosen envelope is (-6.95,-6.95,-.08) to (6.95,6.95,11.60); actual source architecture is lower. Native healthy LOD0 interval116,532–138,124 is inventory evidence, not a target to fill. Possible complete default compound extends roughly X-10.94..10.46, Y-10.08..9.92 because of conditional props; it grants no extra building clearance. `outskirt_a` categories with no measured body bounds remain distinct evidence, not guessed geometry.

Native dependency: `art/civilizations/common/layouts/archetypes/layout_keep/layout_keep.rgm`, its official owner graph/skeleton and `starting_position` marker retained in anchors. That marker is bone-local; raw translation (6.1626,-4.4235,0) is **not** a proved world exit coordinate. Native defensive attack/weapon mechanism and actual garrison clearance must be reviewed separately; this recipe neither replaces nor animates them.

## Draft plan/checkpoint

- [x] Exact A3 source-use and measured-bound metadata retained.
- [x] Original foundation → first strong room → defensive architecture/access → props → detail stages authored.
- [x] Offline test: **157 unique tagged objects, 129 contact equations**, chosen/native-envelope containment and matrix inverse pass.
- [x] Roof-bearing list corrected to exclude low slit sill; walk/podium/platform/roof joins trimmed at shared boundaries.
- [ ] Parent serial Blender build, six-direction review, real topology/contact inspection and state/LOD/native gates.

## Shared source contract and evidence limits

The recipe reads the actual `PRIMARY_BODY_HANDOFF.json`, `HEALTHY_REST_BOUNDS.json`, `SOURCE_CATEGORY_COMPOUND_BOUNDS.json` and `MECHANISM_DEPENDENCIES.json`. Anchors preserve exact model/geometry hashes, native graph paths, triangle interval, measured matrix/inverse, full `source_uses` and evidence classes, private compiled uses, official-parent candidates, native dependencies/skeleton/markers and complete-category bounds. The definite primary body is the conservative architecture limit; a larger possible compound includes conditional props and is not free building space.

Default/campaign are current private compiled source uses in this handoff. Candidate `cordoba`/`xp3` inheritance rows are retained as evidence, not admitted as new runtime consumers. Parent's separately evidenced consumer contract owns final admission, including any `3hre_brawl` branches. Native gameplay, footprint, attack/weapon rigs, material states, stamp/layout/interaction/exit markers, selection and lifecycle ownership remain unchanged external contracts. No new clip, rig, tier or gameplay behavior is introduced.

House-compatible API: `root(key,state='healthy',lod=0)`, `foundation(key)`, `first_room()`, `architecture()`, `props()`, `detail()`, `build_body(key)`, `write_anchors()`; `ANCHORS`, `CONTRACTS`, `ASSEMBLIES` are available. Healthy LOD0 is the authored checkpoint. Arbitrary state/LOD collection names do not implement those states. Every repeated mesh is individually created and tagged with body, construction stage, role and structural group. Parent adapters own state/LOD derivation and subsequent inspection.

Original family atlas inputs are declared as 2048-square `textures/{albedo,normal,roughness,metalness,owner_mask}.png`. No textures were copied, generated or written here. Shared material creation will require those future inputs. No helper or other family source was edited.

Offline checking executes the actual shared runner's geometry formulas for block/extrude/arch/vault/lathe through an AST-extracted subset and a fake mesh/collection registry. No Blender process or Blender Python module ran. Checks cover syntax, unique names, required tags, positive boxes, chosen/native bounds, recorded contact equations and inverse-matrix identity. Bounding-box equations do not prove face contact, manifold/normal correctness, concave-cap triangulation, marker clearance or visual quality. Contracts with `local_seat` also record the stair ledge/tread planes, but their actual topology must be checked after build.

Parent must serially build and review six directions, openings, bearing joints, access routes/parapet gaps, native mechanisms and full compounds, terrain/water interface, material mapping and every real state/LOD before scoring the family. No 90/100 or source acceptance is claimed. Garrison cook/readback, Content Editor, owning archive, client import, runtime, repair, save/load and multiplayer remain separate unverified gates.

## Family LOD source draft, 2026-10-27

The family hook in `recipe.py` loads `lods.py` by source hash. It coarsens intact stair flights to9/8 major risers at LOD1 and5/4 at LOD2, complete merlon courses to fewer broad distant crenels, intact arches/vaults to8/10 and4/6 segments, and the complete grounded cistern to one distant vessel. Landings, curtain/roof bearings and the through-gate remain. Exact source polygon fingerprints disable healthy proxies after any geometry alteration; missing step indices split flights, and altered masonry steps request an exact union of the actual survivors.

Offline formula counts are2192→1348/1144 triangles (.615/.522). These exceed the desired .5/.25; this source is already low poly, and bearing/support walls remain. No triangles were added to LOD0 to improve ratios. Healthy raw edge incidence, bounds, existing scalar contacts and unique proxy IDs pass, as do seven deliberate missing/altered-part cases across the three families. **Actual BMesh/Boolean output, every damage/ruin ratio, saved/cold readback and visual review remain unverified.** See `evidence/lod-offline-receipt.json` and the reproducible `evidence/verify_family_lod_formulas.py`.
