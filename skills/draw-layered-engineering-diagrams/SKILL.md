---
name: draw-layered-engineering-diagrams
description: Create consistent 2000×1400 layered engineering architecture, I/O, storage-engine, transaction, recovery, and lifecycle diagrams as PNG files, matching the bundled clean reference style. Use when users ask to draw or redraw technical diagrams, compare components or execution boundaries, or request “按之前图片样式”“结构清晰、层次分明、一目了然”“不要只是框框加文字”.
---

# Draw Layered Engineering Diagrams

Create a task-specific diagram generator instead of manually painting a one-off image.

## Workflow

1. Inspect `assets/reference-style.png` with the image viewer before drawing.
2. Read `references/style-spec.md` for the visual grammar and validation checklist.
3. Audit the source, tests, or supplied facts. Separate verified behavior from inference and risk.
4. Write one sentence for the diagram's teaching goal. Every layer and arrow must support it.
5. Copy or import primitives from `scripts/layered_diagram.py`; create the task generator with `apply_patch`.
6. Render a 2000×1400 PNG. Inspect it at original resolution and iterate until text, arrows, and grouping are unambiguous.
7. If replacing a document image, insert the new image first, fetch to verify both blocks, delete only the old block, then fetch again.

## Required visual grammar

- Use a white rounded outer plate, centered title, short subtitle, and thin divider.
- Tell the story top-to-bottom: caller/request → interface/index → execution → persistence/output.
- Use a right-side column only for control plane, comparison, warnings, or key conclusions.
- Use solid blue for the primary path, green for index/query, orange for persistence, purple dashed lines for control/recovery, and red only for verified risks.
- Put the diagram before prose. Prefer concrete examples, exact fields, offsets, ranges, and buffer slots over abstract definitions.
- Show branching as branching. Never connect independent lanes in series merely to fill space.
- End with a compact legend and a one-sentence conclusion.

## Quality gates

- No body text below 12 px; prefer 14–16 px. Titles should be 18–24 px inside the canvas.
- Avoid awkward English-token wrapping such as `re` / `name`; shorten text, widen the card, or insert an intentional line break.
- Use at most four major vertical layers and three to five cards per layer. Split a complex story into multiple figures.
- Distinguish actual implementation, caller responsibility, and proposed solution with color and line style.
- Verify arrow direction, arrow labels, units, range endpoints, and whether each value is data or an address.
- Do not add decorative icons, gradients, shadows, or dense paragraphs.

Run the bundled demo when changing primitives:

```powershell
python scripts/layered_diagram.py --demo --output demo.png
```

