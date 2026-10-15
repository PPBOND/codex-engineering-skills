# Layered engineering diagram style

## Preferred reference compositions

- [通用存储服务架构](../assets/reference-style.png): teaching overview with nested caller/execution/data boundaries, a record buffer, storage objects, and a separate maintenance lane.
- [写入请求示例](../assets/reference-io.png): request acceptance, encoding, persistence and completion inside their corresponding boundaries. Keep arrows near endpoints and return completion to the caller.

These generic screenshots replace project-specific references in the public export. Reuse their nesting and routing grammar, not their demonstration behavior; obtain component names, ownership and behavior from the target system's source. Apply the numbering and line-style rules below.

Place parent regions first and lay out children inside them. A diagram should show where an object lives and which boundary an action crosses, in addition to naming the object. Use small concrete field/slot structures inside components when those structures explain the flow. Reserve the right column for control, lifecycle or critical conclusions; put the detailed ordered explanation below the main figure.

For interactive sets, use an overview followed by focused diagrams. Give each figure its own compact ownership layout, based on the same preferred references. A large horizontal-band comparison table is not an equivalent rendering of the nested reference. Keep the selected page and explanatory text stable until user navigation; animate only the flow when continuous playback is requested. The HTML and static export must share the same nested geometry and numbered edges.

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

Caller → interface → nested execution/index state → I/O abstraction → media. Draw process and reactor boundaries only where they exist in the implementation. Shared services belong outside the instances that borrow them. Put low-frequency control components in the right column and connect them with dashed purple arrows.

### Read/write workflow

Start with one concrete request. Show field decomposition, independent branches, and exact result/output positions. Use a separate card for the implementation boundary.

Label the main arrow of each step once. Use blue for requests, green for index/lookup or completion, orange for persistence, and purple for control/recovery. Normal flow uses solid lines; conditional/control/retry paths and early returns use dashed lines with a clear condition or endpoint. Place early exits beside their decision, and route a sequential flow downward when that makes the path easier to follow. Side lanes are optional and must represent an actual branch or control dependency.

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
- Inspect every full-size card body. Request cards show their input; task cards show the relevant state or trigger; callback/completion cards show the result and completion condition. Choose fields, ranges, slots or a small table according to the data, and use compact strips for label-only nodes.
- Name results by the actual API contract and retain essential fields: for example, a mapping list includes logical positions as well as physical locations. A generic address label must not replace a richer returned object.
- Confirm independent branches do not appear sequential.
- Confirm child components remain within their owning boundary, and shared dependencies are outside borrower-specific boundaries.
- Confirm each step number appears exactly once and agrees with the explanation, and completion reaches the correct caller.
- Confirm arrows avoid component text and boundary titles; numbered badges remain readable throughout animation.
- Check wire-to-wire crossings, shared segments, close parallel lanes and crowded arrowheads. Visually follow every main path and branch: minimize turns and detours, keep lane spacing consistent and make return destinations obvious. Repeat for PNG and HTML; passing geometry checks does not prove visual clarity.
- Confirm dashed paths are control, recovery, optional, or external responsibility.
- Confirm the footer conclusion is consistent with the arrows.
- When the diagram is inserted at 900 px width, the layer titles and main field values must remain readable.
