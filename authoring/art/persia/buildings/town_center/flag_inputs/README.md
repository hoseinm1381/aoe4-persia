# Native rectangle flag source input

Parent-run preparation; no Blender has been executed by this worker. This is the
exact 304-triangle / 414-vertex native rest geometry with its original Sails
material, atlas/normal/alpha references, complete material parameters, native
RGM/RGO/RRGeom/RRMaterial, raw wave mask and model-root wind marker retained.
There is no native skeleton or SKMS skin. No armature or clip is invented.

Run `native_flag.py` in a dedicated factory Blender process. It uses the retained
cached plan directly and needs no Garrison extension or additional decode. It
writes `native_flag_inputs.blend` plus a bounded compile receipt after checking
actual topology, positions, UVs, raw/custom normals and material identity. The
Blender Sails rest preview connects only original primary albedo, normal and
maskAlpha red; layered Sails/owner/damage appearance is explicitly unqualified.
All original maps/parameters remain inspectable nodes/metadata, including unused
layers. No source image or native binary is changed/copied.

Cold factory API: import this file and call
`attach(collection, projected_model_to_authored_matrix, label, selection_note)`.
It appends unique editable mesh data and creates a root/child wind-marker
hierarchy without baking vertices. Every call rechecks original hashes and the
compiled library fingerprint. The caller chooses the original placement and
source-view visibility explicitly. `source-contract.json` retains all actor,
variant, category and stamp alternatives; do not sum mutually exclusive tiers.
The retained native stamp inventory contains two flag instances in age I and
four in ages II–IV (indices 74–77 for ages II/III, 84–87 for age IV). Authored
source slots may differ and must be reconciled explicitly. Each selected instance
costs exactly 304 source triangles; two cost 608, four cost 1216.

Native graph `va_act_set_material_moving_state` calls `set_sails_anim_state`
with `state=moving,time=0.01`. Motion is material/stream driven:
`SailsPositionDataStream`, not a skeletal action. Full raw stream bytes remain
in the hashed original RRGeom; the public projection is explicitly
`sail_surface_without_deformation`.

The retained wave mask is internal RRTex format 28, hash
`c123c762b6be4e26016932411785b89b722864822518eb24621245b7ebbc6c52`.
The current decoder cannot project it (`g_masksTex` projection is null). Its
pixel encoding/dimensions are not inferred. Original native source preservation
is supported; native wind playback and moving sweep remain unverified. Finite
numeric build/health predicates remain raw, without invented visibility wiring.
Actual rest-atlas visual inspection, source joins/placement and saved/cold
readback remain parent gates. Full Sails/native-game proof is separate.
