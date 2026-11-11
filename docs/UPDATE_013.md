# Persia 0.1.3 landmark art

Six private landmarks have separate layered texture bakes for weathered masonry, timber grain, glazed motifs, and dyed panels. Each uses a native sRGB albedo with linear-light mips and dedicated normal, surface, and dynamic owner maps. Owner-color panels use neutral pigment. Finished paving and earth remain outside the painted zones.

| Landmark | LOD 1 | LOD 2 | LOD 3 |
| --- | ---: | ---: | ---: |
| Ali Qapu Palace | 9.20% | 9.64% | 9.72% |
| Assassin Brotherhood | 8.89% | 8.61% | 7.88% |
| Grand Caravanserai | 9.53% | 8.25% | 8.92% |
| Gundeshapur | 13.04% | 7.96% | 8.95% |
| Samarkand Bazaar | 11.65% | 9.98% | 10.32% |
| Shah Abbas Siege Factory | 11.38% | 11.47% | 11.80% |

Values are area-weighted samples of the decoded native mask on finished geometry. Heavy Gundeshapur damage can remove much of the tinted roof, so certain damaged LODs fall below 5%. Construction, damage, and ruin geometry and selectors retain their original bytes. Blender material previews simulate the tint. Native match appearance remains pending.

The update changes six RRMaterials and adds 24 textures. Garrison validation and full archive readback passed, including preservation of all other original members. The exact 0.1.2 rollback is stored under archives/landmarks_013_baseline.

Editable PNG maps are in authoring/landmarks_013. Run the normal BUILD.cmd to rebuild from the pinned native inputs. To regenerate the texture bake into an empty staging directory, run tools/bake_landmarks.py with the repository path and staging path using Python 3.13, Pillow, NumPy, and the installed Garrison SDK. The recipe reads the preserved original materials and original native textures.
