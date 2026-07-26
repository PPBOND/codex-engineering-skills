# Layered engineering diagram style

## Canvas and layout

- Canvas: 2000×1400 px, RGB PNG.
- Outer plate: margin 24 px, 30 px corner radius, white fill, `#D8DEE5` border.
- Header: title around y=45, subtitle around y=98, divider at y=145.
- Content: x=70..1930, y=165..1240. Keep 35–50 px between major layers.
- Footer legend: y=1295..1362.
- Default main column: x=90..1450. Optional side column: x=1500..1910.

## Palette

| Meaning | Fill | Border | Text |
|---|---|---|---|
| Primary/API | `#E5F2FC` | `#1976C5` | `#0B5D9A` |
| Index/query/success | `#EAF6E7` | `#3D9140` | `#28732E` |
| Persistence/file | `#FFF1DC` | `#EF7D00` | `#B85B00` |
| Control/MVCC/recovery | `#F3E6F7` | `#8635B5` | `#6D278F` |
| Warning/risk | `#FDEBEC` | `#E33D48` | `#A82530` |
| Neutral/caller | `#F1F3F5` | `#7E8B98` | `#4F5C67` |

Use pale fills and 2–3 px borders. Reserve red for facts verified in source or tests.

## Structure patterns

### Architecture

Caller → interface → managers/indexes → I/O abstraction → media. Put low-frequency control components in the right column and connect them with dashed purple arrows.

### Read/write workflow

Start with one concrete request. Show field decomposition, independent branches, and exact result/output positions. Use a separate card for the implementation boundary.

### MVCC/version search

Draw the sorted version timeline once. Branch from the same predecessor result into exact-match and prefix/predecessor semantics. Show tombstone filtering as a final visibility step.

### Two-hop address

Use distinct colors and labels for:

1. the address of a serialized mapping inside the database;
2. the decoded business-data address;
3. the caller buffer position.

Never label an address as the payload itself.

## Visual QA

- Inspect at original resolution.
- Confirm no text touches borders and no card looks like a paragraph dump.
- Confirm independent branches do not appear sequential.
- Confirm dashed paths are control, recovery, optional, or external responsibility.
- Confirm the footer conclusion is consistent with the arrows.
- When the diagram is inserted at 900 px width, the layer titles and main field values must remain readable.

