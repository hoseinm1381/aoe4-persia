# Persia 0.1.4 unit art

The Castle Savar has a shaped cloth hem, woven diamonds, and a brass-rimmed shield. The Imperial Savar has bronze horse armor, gilt rosettes, and an embossed shield. The Assassin and both Zamburak variants now carry more dynamic player color on cloth. UV repairs cover the mounted models and Zamburak cannon. Savar cloth and shield UVs follow the new texture bakes at all three LODs.

| Equipped unit | LOD 1 | LOD 2 | LOD 3 |
| --- | ---: | ---: | ---: |
| Assassin | 23.36% | 20.82% | 19.36% |
| Zamburak | 11.49% | 11.58% | 11.94% |
| Upgraded Zamburak | 13.45% | 13.37% | 13.76% |
| Castle Savar | 36.03% | 28.92% | 24.64% |
| Imperial Savar | 29.96% | 30.21% | 27.13% |

Coverage is sampled from the red channel of the packed owner mask at 1,024 barycentric points per triangle, weighted by the area of the equipped mesh. LOD 1 is highest detail. Native texture mip chains, skin and hair masks, and original triangle connectivity and skinning passed offline verification. Garrison recipe validation, full SGA member readback, and ZIP CRC passed. In-game appearance and LOD transitions await a native match test.

The playable archive changes 14 art members and adds 22 textures. All other 0.1.3 members were read back with identical sizes, TOCs, and SHA-256 digests. The exact local 0.1.3 ZIP is under `archives/units_014_baseline/`.

The normal project builder consumes the verified native inputs. Editable maps are under `authoring/units_014/`. The rebake scripts in `tools/update_014/` use the original assemblies, a scoped snapshot of 0.1.3 native inputs, and the installed Garrison SDK. See the rebake instructions there for command order.
