---
name: draw-layered-engineering-diagrams
description: Draw source-grounded engineering architecture and I/O diagrams using nested ownership boundaries, numbered flows, and a separate control plane. Export 2000×1400 PNGs and preserve requested interactive HTML delivery. Use for architecture, storage-engine, recovery, lifecycle and request-path diagrams, especially “按参考图画”“结构清晰、层次分明”“不要只是框框加文字”.
---

# Draw Layered Engineering Diagrams

Create a task-specific diagram generator instead of manually painting a one-off image.

## Workflow

1. Inspect the published composition references: [通用存储服务架构](assets/reference-style.png) for an overview, and [写入请求示例](assets/reference-io.png) for a request path. These are generic teaching examples. Use both for overview/detail sets; adapt nesting, proportions, data shapes and line routing to the actual source.
2. Read `references/style-spec.md` for the visual grammar and validation checklist.
3. Audit the source, tests, or supplied facts. Separate verified behavior from inference and risk.
4. Write one sentence for the diagram's teaching goal. Every layer and arrow must support it.
5. Copy or import primitives from `scripts/layered_diagram.py`; create the task generator with `apply_patch`.
6. Render a 2000×1400 PNG. Inspect it at original resolution and iterate until text, arrows, and grouping are unambiguous. If HTML is requested, use the same diagram data for the interactive page and PNG export; preserve the requested navigation and animation behavior.
7. If replacing a document image, insert the new image first, fetch to verify both blocks, delete only the old block, then fetch again.

## Required visual grammar

- Use a white rounded outer plate, centered title, short subtitle, and thin divider.
- Lay out ownership before flow: system → process/reactor → component → concrete state/buffer/file. Put child components inside their actual parent boundary, and label every meaningful boundary.
- Tell the story top-to-bottom: caller/request → interface/index → execution → persistence/output.
- Use a right-side column only for control plane, comparison, warnings, or key conclusions.
- Use blue for requests, green for index/query, orange for persistence, purple for control/recovery, and red only for verified risks. Choose solid or dashed strokes by the path's role, as defined below.
- Put the diagram before prose. Prefer concrete examples, exact fields, offsets, ranges, and buffer slots over abstract definitions.
- Make data transformations visible: draw logical ranges and coverage, queue slots, buffer regions, index rows, live/dead records, old/new pages, publication pointers or drain counters as appropriate. Function-name boxes connected by arrows are not a substitute for showing what enters, changes and leaves. Keep long explanations outside the main figure.
- Show branching as branching. Never connect independent lanes in series merely to fill space.
- For a diagram set, start with the whole-system overview. Give each detailed request path its own diagram with finer internal components and only the dependencies it uses.
- Number each step exactly once per figure, on its main arrow. Additional arrows belonging to that step use short action labels when needed, never duplicate numbers. Use solid lines for the normal path, dashed lines for conditional/control/retry paths and early returns; label their condition or destination clearly.
- End with a compact legend and a one-sentence conclusion.

## Quality gates

- No body text below 12 px; prefer 14–16 px. Titles should be 18–24 px inside the canvas.
- Avoid awkward English-token wrapping such as `re` / `name`; shorten text, widen the card, or insert an intentional line break.
- Choose each figure's ownership topology first; vertical stages are optional. Use compact, unequal-sized nested modules, field strips, buffer slots, shard/partition rows and file ranges. Do not reduce the preferred references to equal-height full-width bands, repeated two-column tables or identical flat grids. Split a complex story when necessary.
- Size cards to their content. Full-size workflow cards need source-backed inputs, state, completion conditions or outputs below the heading; label-only nodes use compact strips. Check card completeness and actual result semantics using the style specification.
- Apply the same composition to every flow and to its animated HTML version, not only to the overview or PNG exports. Continuous motion follows existing arrows and must leave the hierarchy, text and step numbers readable.
- Distinguish actual implementation, caller responsibility, and proposed solution with color and line style.
- Verify arrow direction, arrow labels, units, range endpoints, and whether each value is data or an address.
- Choose the flow direction per page. Prefer downward progress for sequential work; reserve side lanes for actual branches or control. Put early-return exits near their decision. Check every page visually for a traceable main path, minimal turns, even lane spacing and clear arrowheads, and geometrically for wire crossings, overlaps and collisions with text or badges. A geometric pass alone is insufficient.
- Do not add decorative icons, gradients, shadows, or dense paragraphs.

When changing primitives, use the bundled demo as a rendering smoke test. Production composition comes from the two screenshots above:

```powershell
python scripts/layered_diagram.py --demo --output demo.png
```
