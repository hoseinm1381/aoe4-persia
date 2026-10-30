# Persia Barracks — original healthy source draft

Draft checkpoint, 2026-10-27. Existing bodies are exactly A1/A2/A3/A4; no Blender/render/cook was performed. The actor recorded by inventory is `ps_building_unit_infantry_control_sul`. Resource filenames are `sul_barracks_combined_age01` through `age04`, with each exact path and SHA-256 retained dynamically from the handoff.

## Architectural intent and chronology

Use the [ordinary family guide](../../../../research/persia_buildings/history/ORDINARY_BUILDING_REFERENCE_GUIDE.md) and [Divan of War evidence](../../../../research/persia_buildings/history/DIVAN_OF_WAR.md). Documented military administration establishes military institutions, not an excavated standard Persian barracks plan. This building is an original infantry preparation/lodging court. It must differ from the Divan's pay/register/dispatch office and from a compact residential House even without props. Regional brick, plaster, thick wall and vault vocabulary follows the guide's cited Saljuq architectural evidence; the military layout and room sizes are interpretations.

| Existing age | Original programme and silhouette | Why the composition changes |
|---|---|---|
| A1 | Broad low rear earthen lodging block, separate east guard room, open west preparation shelter | A modest military compound has many practical doors and a wide unroofed approach. |
| A2 | Three separately constructed barrel-vaulted lodging cells, west masonry guard room and east equipment shelter | Repeated occupied bays replace the single rear block; masonry/roof anatomy changes as well as finish. |
| A3 | Long west lodging range turned 90 degrees, joined to a taller rear guard hall, east court shelter | Useful asymmetric expansion moves the major mass and opens a different court axis. |
| A4 | Broad lower lodging/preparation hall, east guard room and west upper duty room accessed from a grounded stair podium/landing | A command/duty programme adds genuine occupied height with explicit support and access. |

The guide's I~934–1040, II~1040–1256, III~1256–1501, IV~1501–1629 bands are art discussion only. Vaults and upper rooms were available earlier; this is a selected game progression, not an invention timeline. The A3 guard hall is lower than an upper-storey proposal in the initial guide to keep the court/bearing programme conservative; A4 carries the actual upper room. No royal iwan, minarets, palace dome or wall of decorative weapons is required.

Original equipment includes a footed preparation bench, timber rack with suspended practice boards, chests and ceramic water jar. Bench/chests are kept clear of the paved approach. Wear concentrates on the court entrance/handling path. Static boards are original props and do not replace native weapon/armor rigs.

## Measured coordinate and envelope evidence

**All authored points are native measured stamp-space coordinates.** Current resource-to-stamp matrix is `diag(-1,-1,1)` plus translation `(0,-3.5,0)`: `x_s=-x_r`, `y_s=-y_r-3.5`, `z_s=z_r`. Its inverse is the same. Parent must apply this inverse exactly once before resource-space export, or explicitly author the adapter to consume stamp space. Do not apply the stock stamp a second time to already transformed points.

Source terrain origin is unchanged; `F=.08` is a provisional top bearing surface, not a Z recenter using a native buried minimum. Ground extends only to Z=-.06. The stock negative minimum is not evidence that terrain should be lowered.

| Body | Native primary stamp bounds min → max | Chosen draft envelope min → max | Analytic actual maximum Z |
|---|---|---|---:|
| A1 | (-4.3242,-4.7939,-1.2002) → (4.3242,4.4414,4.6992) | (-3.95,-4.35,-.06) → (3.95,4.05,4.45) | 2.97 |
| A2 | (-4.6367,-5.1309,-1.3428) → (4.6367,4.9375,5.9023) | (-4.10,-4.65,-.06) → (4.10,4.45,5.50) | 3.43 |
| A3 | same native bounds as A2 | same chosen envelope as A2 | 3.90 |
| A4 | (-4.7305,-5.1973,-1.5137) → (4.8008,5.1016,8.0625) | (-4.20,-4.65,-.06) → (4.20,4.55,7.40) | 5.90 |

Height is conservatively below the measured native body; unused height is not a request for decorative towers. Native primary healthy triangle counts are 58,912 / 59,119 / 62,607 / 80,491. These are inventory references, not mesh-fill targets. The possible complete category extends farther than the chosen envelope because it includes conditional props; no clearance is claimed from that extra space.

Recorded dependency model paths are `art/civilizations/common/banners/banner_barracks/banner_barracks.rgm` and `art/civilizations/common/layouts/archetypes/layout_barracks/layout_barracks.rgm`; native paths/hashes/owner graphs are kept in anchors. Bone-local layout marker data is not an untransformed world-space position. No dependency is moved or deleted by this recipe.

Offline totals: A1 **84 objects / 63 contacts**; A2 **97 / 69**; A3 **81 / 59**; A4 **95 / 53**. All recorded contacts and chosen envelope checks passed in the analytic checkpoint. The upper duty floor meets the lower roof; the stair reaches a solid landing and parapets leave the access gap. Visual/mesh execution remains pending.

## Consumer evidence and protected native behavior

The recipe reads `research/persia_buildings/inventory/PRIMARY_BODY_HANDOFF.json` and keeps every `source_uses` row and its `variant_evidence_class`. It records existing private compiled default/campaign uses separately from official-parent candidate rows. Candidate `cordoba`/`xp3` evidence is not permission to create private consumers. Final admission, including any separately established `3hre_brawl` branches, belongs to the parent's current consumer contract. No gameplay tiers are invented by an architectural age discussion.

`HEALTHY_REST_BOUNDS.json` supplies the actual measured stamp matrix. `SOURCE_CATEGORY_COMPOUND_BOUNDS.json` supplies complete-category definite/possible bounds, retained in anchors for the existing private uses. Possible compound bounds include conditional models and are not additional guaranteed building space. `MECHANISM_DEPENDENCIES.json` supplies dependency hashes, owner graphs and explicit pose/sweep caveats. Native marker, selector, stamp, layout, attachment, weapon/armor, construction/ruin, motion and gameplay ownership remain external contracts. No new animation or clip is authored. This source is not a replacement for a rig simply because the replacement geometry fits a static box.

## Authoring contract

API: `root(key, state='healthy', lod=0)`, `foundation(key)`, `first_room()`, `architecture()`, `props()`, `detail()`, `build_body(key)`, `write_anchors()`; `ANCHORS`/`CONTRACTS`/`ASSEMBLIES` expose evidence. This checkpoint authors healthy LOD0 architecture only. Arbitrary state/LOD collection names do not constitute state/LOD implementations. Parent adapters must supply/qualify the lifecycle. Use `R.configure(ROOT, FAMILY)` through `activate()` to avoid cross-family mutable runner configuration. Cleanup is restricted to the literal family prefix.

Every repeated mesh is individually created and tagged with body, stage, role and structural group. Stages intentionally separate first occupied room, major additions, roof structures, working equipment and restrained finish. Room openings are holes bounded by jamb/head or genuine arched masonry; a recessed timber leaf is a fitting. Roofs bear on walls, shelters have foot/post/beam/rafter/cap chains, and props have feet or explicit suspension. No stock doorway size was measured; all source door dimensions are original proposals.

Family material input paths are `textures/albedo.png`, `normal.png`, `roughness.png`, `metalness.png`, `owner_mask.png`, each 2048 square and original. No image was generated or copied for this draft; shared material creation deliberately requires those future inputs. No common helper or another family source was edited.

## Verification and remaining gates

Syntax plus an offline analytic test were run with the actual shared runner's `block`, `extrude_xz`, `archwall`, `vault`, and `lathe` geometry formulas extracted by AST and a fake mesh/collection registry. No Blender process or Blender Python module ran. The test checks unique names, required tags, positive box dimensions, measured-envelope containment and each recorded numeric contact. Bounding-box contact equality does not prove face adjacency, a manifold mesh, a valid triangulation of a concave cap, visual quality, collision clearance or native motion.

Parent must serially build and inspect roof/end-cap triangulation, openings, repeated wall joints, useful passage widths, terrain origin, selection/repair/exit/layout markers, exact native mechanism sweeps, atlas mapping and each actual state/LOD in multiple directions. Reevaluate complete compounds rather than treating body-only rest bounds as complete clearance. No visual score or 90/100 acceptance is claimed. Cook, Content Editor, owning archive, client import and native-game results remain unverified.
