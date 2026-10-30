# Persia Codex crash investigation, 2026-10-30

Observed game build: 17.0.12182. The captured warnings log opens
CodexModalPage.xaml at 20:11:35 and records the application crash at 20:11:48.
The native dump records 0xC0000005, instruction address 0x7ff7ee0af633,
read address 0xffffffffffffffff (RelicCardinal!0349e633).

The actual installed 0.1.0-trial.1 Persia Codex contained age-column values up
to 31, row positions up to 17 and background heights up to 19. The official
English tree and installed creator Persians example use age columns -1..3,
rows 0..11 and backgrounds no higher than 11. The former generator assigned
producer indexes to age columns and five-row bands to ages. Those assignments
are inconsistent with both working native references.

The 0.1.1 generator derives age columns from each referenced blueprint and
fits every row inside the four native bands. The same exporter defect existed
in Korea/Vietnam. Berbers' original graph is retained; only its invalid age
columns and background height are corrected. No production/gameplay is granted
or removed. Actual old native trees are retained as failing regression fixtures.

The defect is fixed in source and packaged data. No native debugger stack or
in-game reproduction has established that it is the sole crash cause. The
owner must retest opening, browsing and reopening the tree from menu and match.
The local captured dump/XML/warnings remain in archives/diagnostics_011 (see CRASH_EVIDENCE.json); they were
not uploaded or published. Runtime, save/load and multiplayer are unqualified.
