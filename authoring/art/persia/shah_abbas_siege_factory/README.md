# Shah Abbas Siege Factory: editable source art

An original Safavid workshop interpretation with vaulted production bays, a cold casting recess and clay mould/core, low furnace, lifting tackle, carriage assembly, bored gun props and a swivel-gun saddle cradle. No exact historic building plan is claimed.

## Scope and evidence

This is source artwork only. It does not activate a model in the mod. Native export/cook, construction transitions, dynamic team colour, persistent ruin selection/repair, package/import, solo gameplay, save/load and multiplayer are deferred.

The approved research/design and shared reference attribution are retained at `../../../research/persia_imperial/IMPERIAL_RESEARCH_AND_DESIGN.md` and its `references` folder. The permanent repository, Normal and original Persia donor are unchanged. No version change, push or temp cleanup occurred.

- Master: `shah_abbas_siege_factory.blend`; dedicated asset scene and preserved original default scene.
- Seven healthy/damage/ruin compositions, each with LOD0/1/2, plus four construction assemblies: **25 compositions**.
- Five original 2048 texture maps in `textures`: albedo, tangent normal, roughness, metalness and owner mask. Relative paths; editable shader nodes; red/blue/yellow source previews.
- Healthy triangles: **14,532 / 7,254 / 3,618** at LOD0/1/2. Complete-composition cap: 122,469; props included.
- **65** measured bearing contacts. Source checks cover topology, transforms, UVs, bounds, dependency resolution, LOD budgets and exact final-construction restoration.
- `anchors.json` records numerical support planes; `state-manifest.json` records parts, mesh/UV hashes, states and restoration identity.

## Edit and reconstruct

Edit this master in Blender, preserving the named source collections, or edit `healthy_recipe.py`, `states_recipe.py` and `lod_recipe.py` and regenerate explicitly. Repeated source parts have individual mesh data. Material and texture authoring inputs are retained in `asset_runner.py` and `make_atlas.py`.

Verify reconstruction in a fresh process (never on the live master):

```powershell
& 'E:/Blender5.2/blender.exe' --background --factory-startup --python 'F:/aoe_4_temp/Temp_before_github_push/art/persia/shah_abbas_siege_factory/rebuild_source.py' -- --verify
```

The default verification compares against the retained manifest and preserves the canonical master bytes. It refuses a populated asset scene. A deliberate recipe replacement uses `--rebuild-and-save` instead of `--verify`; it replaces only this owned generated asset. Manual edits must be preserved and reconciled with the recipes before choosing that replacement. Do not use regeneration as a silent reset of an edited master.

`verify_saved.py` opens/audits this saved asset in its own process and verifies texture closure. `review_views.py` and `presentation.py` generate source-review images; cameras, lights and ground helpers are outside source geometry counts.

## Review files

- `previews/healthy.png`: main source-art preview.
- `previews/01-states.png`: healthy, five damage states and ruins.
- `previews/02-construction.png`: ordered construction assemblies.
- `previews/03-owner-lods.png`: owner colours, reduced detail and rear view.
- `previews/04-six-solid-views.png`: orthographic construction inspection.
- `evidence/source-checks.json`, `contact-checks.json`, `cold-rebuild.json` and `saved-readback.json`: objective receipts. A missing receipt is an outstanding gate, not a pass.

Actual historical buildings are larger and structurally richer than these compressed game assets. Construction/damage are static authored compositions with no invented HP thresholds, particles, animated collapse or native selectors. Keep native acceptance separate from source checks and any provisional visual score.
