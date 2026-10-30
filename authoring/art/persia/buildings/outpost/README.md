# Original Persian Outpost â€” unbuilt healthy architecture drafts

This folder supplies `recipe.py` and a native evidence/configuration contract. **No Blender source has been generated, rendered or accepted by this worker.** No weapons, animations, new gameplay tiers, source lifecycle assemblies or LODs are manufactured here. Parent source/compound verification is still required.

## Two existing bodies

`BODY_KEYS = ('A1Basic', 'A1Fortified')` matches the shared `family.json` source keys. Exact authored→native mapping is `A1Basic`→`wood`/`default`, `A1Fortified`→`fortified`/`stone_upgrade`. They are upgrade alternatives, not four age bodies or a third fortified tier.

| Source key | Native category/stamp | Original massing | Authored bounds before stamp |
|---|---|---|---|
| `A1Basic` | `default`; `art/stamps/civ_sul/sul_outpost.bin` | Battered earthen/brick entrance shaft, open supported timber fighting gallery, upper shaded lookout with clay roof and substantial roof joists. | X/Y within Â±1.98; ground âˆ’.03; roof 8.52. |
| `A1Fortified` | `stone_upgrade`; `art/stamps/civ_sul/sul_outpost_stone.bin` | Compact thicker masonry shaft, protected entrance approach, true splayed arrow slits/lower embrasures, brick-pier fighting gallery, accessible upper platform and restrained chunky crenellation. | X within Â±1.66; Y âˆ’3.20..1.66; ground âˆ’.03; merlons 9.14. |

Both retain the effective default/campaign gameplay `footprint_scale` **4Ã—4**. These gameplay values are not a promise that all donor visual extents lie inside Â±2; the fortified donor has a projecting front approach. No gameplay fields are changed.

The bodies use the measured donor envelopes in `configuration.json`. Basic definite healthy bounds are X/Y Â±2.021484375, Z âˆ’1.599609375..8.5859375; the possible bound expands to X âˆ’2.3515625..2.41796875, Y âˆ’2.228515625..2.392578125, Z max9.2109375. Fortified definite bounds are X Â±1.69140625, Y âˆ’3.345703125..1.69140625, Z âˆ’1.5986328125..9.375, with possible X max1.7080078125. Negative donor extents include native geometry; they are not an instruction to sink the occupied room below terrain.

These measurements are **projected cooked model-local rest geometry** with B(native)=(-x,-z,y). The retained stamp is the exact 180-degree matrix diag(âˆ’1,âˆ’1,1,1), zero translation, for both alternatives. Apply it exactly once after source fit; the fortified front approach then changes side. `ANCHORS` explicitly declares `authored_space='model-space'`: no half-turn stamp is baked into recipe vertices. Source coordinates, stamp space and world/posed bone coordinates are distinct. Exact stamp matrices, hashes and native paths are retained in the JSON.

## Standard legal configurations

The eight source-preview proposals are:

| Body | No emplacement | Arrowslits | Springald | Cannon |
|---|---|---|---|---|
| `wood` | `wood__none` | `wood__arrowslits` | `wood__springald` | `wood__cannon` |
| `fortified` | `fortified__none` | `fortified__arrowslits` | `fortified__springald` | `fortified__cannon` |

These follow the four actually offered upgrades on the private Persian actor and **complete ordered native requirement trees**, not a powerset assumption. A bounded reachable-state calculation confirms eight standard states for default and campaign, with independent stone fortification. Arrowslits requires Feudal, springald Castle, cannon Imperial; stone fortification requires Feudal. Campaign cannon additionally requires any one of common/Sultanate/Mongol Chemistry. Other completed or queued emplacements prevent ordinary combinations; exact queued/completed and parenting flags are preserved in the JSON.

Default/cordoba native requirements contain an **Armed to the Teeth** exception. The scoped Persian actor does not offer or grant that upgrade. It is preserved as an explicit conditional exception, not assigned to standard Persia. An external system granting it would require reevaluating legality. `cordoba`/`xp3` are retained official-parent inheritance candidates; only default/campaign are separately confirmed private compiled variants here.

The earlier inventory `OUTPOST_CONTRACT.json` requirement summarizer overwrites repeated same-key siblings in a dictionary. Its legal count remains correct for this standard scope, but its compact campaign/expansion requirements must not be treated as complete. This folder's requirement arrays retain every sibling and nested any/all relationship.

## Garrison shooting is separate

Inherited `combat_ext` defines upgrade hardpoints 0=arrows, 1=springald, 2=cannon, 3=murder hole; these do not initialize on creation. Baseline garrison arrow weapons occupy distinct hardpoints 4 onward: five default garrison slots and three campaign slots, with their respective native hold-event trees. They can coexist with the selected upgrade without becoming an additional visible emplacement configuration. Preserve these native owners, firing markers and hold behavior; this source recipe creates no archers or fake shooting mechanism. Default/campaign marker/origin differences are preserved verbatim in JSON and are not reinterpreted as world positions.

## Native moving parts: actual source gate

The recipe authors **only original architecture**, not the Sultanate shell. Native upgrade members may include architectural frames as well as actual moving components, so retaining every `upgrade_*` member without inspection could reintroduce donor architecture. Parent must isolate the proven mechanism while preserving its native source names, hierarchy, pivots, sockets and owning graph.

- Basic RGM has seven named upgrade helper bones and seven exact MSCL rigid-parent bindings. Their original binary and the complete qualified binding-header evidence remain in `research/persia_buildings/inventory/RIGID_MECHANISM_BINDINGS.json`.
- Fortified RGM has no SKLN and its MSCL parent-bone names are empty. That does not prove an absence of functional motion: native graph-driven parts/child entities remain separate dependencies.
- Arrow/springald weapon entities resolve to an empty weapon-template attachment; their visible body members are important. Cannon additionally references `art/civilizations/common/weapons/ranged/cannon_tower/cannon_tower.rgm` through its native weapon attachment. Its retained native inspectable source pose and sweep are not provided by this draft.
- Exact per-source cooked rest AABBs and grouped reference unions are retained. They include frames and alternative members; they are **not** sums of simultaneously active parts, precise collision volumes, rotation pivots or animation sweeps.
- Fortified source geometry appears around Z5.60â€“7.72 while its separate model-root cannon/springald muzzle records project to about Z4.39/4.50. Keep these distinct until native pose/binding comparison explains the relationship. Do not move a mechanism or marker merely to make those two record classes agree.
- The architecture intentionally supplies broad fighting openings. This is a practical draft reservation, **not verified clearance**. AABB unions can overlap structural corners even where actual mesh shapes do not; inspect actual retained source geometry and its supported motion before accepting or fitting the shell. No rigged compatibility, sampled sweep or world socket pose is claimed.

All eight preview rows are initially `preview_ready=false` and have no retained native collection assigned as present. `preview_configuration(id)` returns the intended body and expected native collection name but performs no import or weapon substitution. Parent should fill/qualify those inputs in its own serialized pipeline, then inspect every legal compound. No new clips or invented playback are authorized.

## Anatomy, contacts and original regional direction

The [ordinary-building guide](../../../../research/persia_buildings/history/ORDINARY_BUILDING_REFERENCE_GUIDE.md) grounds the compact watch platform in regional brick/earth defensive language, with a qualified Nishapur watchtower reference and regional fortification context. These are original functional game designs, not claimed reconstructions of complete excavated elevations. Timber basic and masonry fortified massing remain distinct without a mosque balcony, dome, miniature Keep compound or borrowed Sultanate silhouette.

The shaft is actually hollow; tapered closed panels meet at mitered corner faces. Door/slit/embrasure voids have physical reveals, with wider internal splays. Internal fixed ladders align to real .62Ã—.70 floor hatches. The basic roof uses six supported transverse joists; posts and gallery rails carry the occupied upper lookout. Fortified access reaches both fighting gallery and upper parapet platform. Contacts identify plinth/earth, step/earth, posts/decks, rails/posts, joists/bearings, roof/joists, platform/pier and merlon/parapet planes. Nonvertical joinery is recorded as named numerical interfaces and must be inspected beyond bounding-box tests.

`foundation`, `first_room`, `architecture`, `props`, `detail`, `root`, `build_body`, `ANCHORS`, `CONTRACTS` and `write_anchors` follow the House recipe API. All generated mesh objects carry construction stage, role, structural group and body key. Each mesh call creates unique editable data. No source scene is reset or saved automatically; existing owned geometry causes an explicit stop rather than deletion.

Material helper paths are the original per-family 2048Ã—2048 atlas inputs `textures/{albedo,normal,roughness,metalness,owner_mask}.png`. **Those files are pending**, so calling the real runner before parent supplies them will fail. Small useful supplies and restrained entry/plinth wear are the intended detail level; there is no random scatter, human figure or pretend static cannon.

## Remaining verification

Parent must generate both bodies serially, inspect six sides/entry/access/bearing contacts, preserve qualified native mechanisms and source poses, resolve collisions for every legal configuration, paint the original atlas, establish compound budgets, and author applicable lifecycle/preview/targeting/LOD assemblies. Native selector state names remain in the inventory contracts; no new lifecycle strings or health thresholds are invented here. Cook, package/import and native testing remain later distinct gates. This draft does not claim any of them passed.
