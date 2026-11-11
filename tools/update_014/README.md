# Reproduce the 0.1.4 unit art

The ordinary project build uses the pinned resources in inputs/native.
This recipe regenerates those resources into a fresh staging directory.
Use Python 3.13 with Pillow and NumPy, Blender 5.2 with Pillow and NumPy on
its Python path, and the installed Garrison extension. Set GARRISON_EXTENSION
if it is installed outside Blender's usual extension directory.

Run from the standalone repository. Create the empty staging directory first.
Replace the two placeholder paths with absolute paths. Blender's saved equipped
assemblies are read in background mode with embedded scripts disabled.

    python -B tools/update_014/unit_review.py REPOSITORY STAGE
    python -B tools/update_014/stage_unit_art.py REPOSITORY STAGE
    python -B tools/update_014/style_savar_textures.py REPOSITORY STAGE
    blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python tools/update_014/style_savar_geometry.py -- REPOSITORY STAGE
    python -B tools/update_014/verify_coverage.py REPOSITORY STAGE
    python -B tools/update_014/verify_overlay.py REPOSITORY STAGE

The 0.1.3 snapshot in docs/update_014/native-baseline.zip holds only the
original resources the recipes edit. Original textures and rigs are still
in the source tree. The art recipe reads native UV layouts and material
channels, preserves unrelated BC texture blocks, and retains original
skinning when UV seams split a vertex. Assorted .blend preview scenes and
intermediate renders are unnecessary to reproduce the staged assets.
Compare the regenerated member hashes with docs/update_014/asset-verification.json
before accepting an unchanged rebuild. For an intentional edit, remeasure color
coverage and update the input manifest after approval.
