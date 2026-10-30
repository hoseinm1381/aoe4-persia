# Persia Archery Range — original healthy source draft

Draft checkpoint, 2026-10-27. Existing bodies are exactly A2/A3/A4; there is no A1 resource to invent. The actor recorded by inventory is `ps_building_unit_ranged_control_sul`. Resource filenames are `sul_archery_range_control_age02`, `age03`, `age04`, with exact paths/hashes retained from the handoff. No Blender/render/cook was performed.

## Architectural intent and chronology

The [ordinary family guide](../../../../research/persia_buildings/history/ORDINARY_BUILDING_REFERENCE_GUIDE.md) links practice activity to historical discussion of Ali Qapu; that does not establish a surviving standard Persian range plan. This is an original narrow side service range beside a long open target lane, with restrained regional masonry/wood vocabulary. The practice lane and supported target end should identify the building after decorative owner cloth is removed.

| Existing age | Original programme and silhouette | Functional distinction |
|---|---|---|
| A2 | Small north-west gear room, long open western equipment shade, two target trestles and low backstop | Most space is visibly open practice ground. |
| A3 | Long west gear range with a transverse vault profile, separate taller rear staff cell, small south equipment-work shade and three targets | Major occupied mass rotates into a service spine rather than enlarging the A2 box. |
| A4 | Taller north staff/store range joined to low gear arcade, transverse southern covered firing line, three targets | The firing shelter gives a new widthwise roof and a clear sheltered start to the lane. |

The broad age II/III/IV discussion bands are c.1040–1256 / 1256–1501 / 1501–1629. They are art direction, not dates when the respective roof or target type was invented. No unqualified post-1629 palace talar or modern competition target graphic is used. A4 has a taller occupied staff room, not an unsupported spectator balcony. The donor does not require an upper floor, and a speculative access staircase would unnecessarily narrow this envelope.

Target faces are original closed circular meshes, backed by two posts, a rail, two rear braces and grounded feet; they are not floating signs. Plain small impact centers avoid modern colored scoring rings. Three late targets face a clear lane; local soil wear stays at practice/target areas. The low backstop/buttresses are source silhouettes, not a physically validated arrow-catch system. Compressed shooting distance makes no historical range-length or gameplay claim. Shafts have a grounded rack; the A4 rack is positioned inside the open firing shelter rather than embedded in the gear-room end wall. A2/A3 equipment benches are sheltered; no native archery rig or new animation is manufactured.

## Measured coordinate and envelope evidence

**All authored points are native measured stamp-space coordinates.** Current resource-to-stamp rotation/translation is approximately `x_s=y_r+2.6`, `y_s=-x_r+.3`, `z_s=z_r`; the full measured floating-point matrix is retained in anchors. Inverse: `x_r=.3-y_s`, `y_r=x_s-2.6`, `z_r=z_s`. This is a 90-degree mapping, unlike the Barracks/TC 180-degree mapping. The parent adapter must apply this inverse exactly once before resource-space export or explicitly consume stamp space.

Native terrain origin is preserved. `F=.08` is a provisional source bearing surface; ground extends to -.06. Native buried minima are not an instruction to shift the building vertically.

| Body | Native primary stamp bounds min → max | Chosen draft envelope min → max | Analytic actual maximum Z |
|---|---|---|---:|
| A2 | (-.6285,-3.8133,-1.1992) → (5.0531,4.2922,6.8281) | (-.35,-3.50,-.06) → (4.85,4.05,6.20) | 2.97 |
| A3 | same native bounds as A2 | same chosen envelope as A2 | 3.47 |
| A4 | (-.9508,-3.9070,-1.1992) → (5.2738,5.2453,7.9141) | (-.50,-3.55,-.06) → (5.05,4.60,7.20) | 4.07 |

The shifted positive-X envelope follows measured stock placement, not an accidental recenter. Native healthy primary triangle counts are 38,423 / 36,867 / 53,065. These are inventory references, not targets to fill with unnecessary divisions. Much larger possible category bounds contain conditional props; they are not guaranteed open space for the new building.

Recorded native dependencies include `art/civilizations/common/props/wall_stone_low_segment/wall_stone_low_segment.rgm`, `art/civilizations/common/props/stone_bench/stone_bench.rgm`, `art/civilizations/common/banners/banner_archery/banner_archery.rgm`, and `art/civilizations/common/layouts/archetypes/layout_archery/layout_archery.rgm`. Preserve their paths, transforms/pivots, ownership and native material/animation mechanisms in the eventual adapter. A new source stone boundary or bench is not automatic permission to delete the native dependency. Bone-local marker values are not world coordinates; exact sweep/marker qualification remains open.

Offline totals: A2 **78 objects / 61 contacts**; A3 **101 / 73**; A4 **101 / 71**. All recorded contacts and chosen-envelope checks passed in the analytic checkpoint. Contacts include each target's rear-face-to-post surface, brace-to-rear-foot and post-to-front-foot. End-cap triangulation, shading, actual target stand appearance and passage clearance still require parent Blender review.

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
