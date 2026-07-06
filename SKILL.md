---
name: panorama
description: Generate interactive project diagrams as self-contained HTML (in-house renderer, no Mermaid, no CDN). Three variants. (1) flow, a status-and-dependency map where nodes carry done/in_progress/planned/blocked states, blockers, hover tooltips with the stack, dashed arrows for future/gated work, and a clickable dependency cone. (2) table, a comparison or equivalence matrix with ++/-- intensity badges. (3) pipeline, a horizontal 2D graph with vertical branches (parallel tracks, merges, tools that join mid-process) that explains what each tool does, where its data comes from, and what travels between steps, labeled on each arrow. Built to show a project to a manager, client, or teammate, or to keep your own agent sessions oriented. Use it when the user wants a project map, asks where a project stands, needs to compare options in a matrix, or wants to explain how a system works end to end. Works for in-flight projects and for day-zero planning. Triggers - "panorama", "project map", "architecture diagram", "where are we at", "diagram the stages", "dependency map", "comparison table", "compare X vs Y", "mental model", "how does this project work", "what does each tool do", "tool chain", "explain my project to someone".
---

# Panorama

Turn the state or structure of a project into one interactive, self-contained HTML file: no dependencies, no CDN, opens anywhere. It replaces hand-drawn schemas and Mermaid attempts. Three variants, selected by `type` in the spec: **`flow`** (status map, the default), **`table`** (comparison matrix) and **`pipeline`** (tool-chain mental model).

## Which mode

Pick by the question you are answering, not by the topic. `flow` and `pipeline` overlap on purpose: they can describe the same system.

| Question | Mode |
|---|---|
| Where are we? What is stuck? What depends on what? | `flow` |
| How does it work end to end? Where does each piece of data come from? | `pipeline` |
| Which of these options do I pick? | `table` |

- **`flow`**: status and dependencies of a system under construction: code, tool connections, planned work with blockers. Builder-facing. It keeps you oriented across many prompts, and it keeps an agent oriented when several sessions or several people advance stages of the same repo. Supports custom statuses and a `live` toggle (below).
- **`table`**: you are choosing between two or more options and want to compare their properties to decide. Also for equivalence: mapping which metric on one platform corresponds to which on another.
- **`pipeline`**: the whiteboard replacement. A schema where stacks feed each other, loop back, and feed again, with dependencies, limits and variants, defining what each tool or process step does and where each piece of data comes from. Explanatory: for presenting the system to someone, or for reminding yourself how it works.

## What it produces

- **Nodes as stages or pieces**, laid out in horizontal **lanes** (sources, ingestion, storage, interface, or whatever fits).
- **Status on each node** (`done`, `in_progress`, `planned`, `blocked`), editable per spec.
- **Hover tooltip** with the tech stack, a note, and the blocker when one exists.
- **Dashed arrows** for `aspirational` edges: future or gated work that the diagram should show without claiming it happens today.
- **Click a node** to highlight its dependency cone (everything it needs upstream plus everything that depends on it downstream) while the rest dims.
- **Clickable legend** to filter by status, a light/dark theme toggle, and a Reset button.
- **Edit button**: in-place editing of every text (titles, card fields, arrow labels, captions). Edits write through to the embedded spec JSON, and **Save .html** downloads the updated file under the same name, still fully interactive and re-editable. Handy for renaming things without a re-render; for structural changes (new nodes, new edges), edit the spec and re-render.
- The `pipeline` variant renders compact cards by default: type + name + role. Hover shows the hidden detail, click opens a side panel with the full card plus its incoming and outgoing arrows, and a "Details" button expands every card inline for printing or static export.

## Workflow

1. **Gather the real state.** For an in-flight project: read the repo and docs. Do not infer progress from the repo alone; verify it. A workflow can be live in a cloud service while the repo only holds a template. When you cannot confirm a piece, mark it with a blocker like "confirm real status" instead of guessing. For day-zero planning: model stages, dependencies and candidate stack from what the user describes.
2. **Write the spec JSON** following the schemas below.
3. **Render:**
   ```bash
   python3 render.py <spec.json> -o <out.html> --open
   ```
   Omitting `-o` writes next to the spec with an `.html` extension.
4. **Keep the spec in the project repo** (suggested: `docs/panorama/<name>.json`) so it stays versioned and re-renderable as the project moves. The HTML is a derived artifact.
5. **Share by link** when asked: `./share.sh <out.html>` uploads to a secret gist and prints a browsable link. That publishes content outside the machine, so confirm with the user before running it.

## Live mode (the `"live"` field)

A panorama can be **on-demand** (generated when asked) or **live** (kept current on every turn that changes project state). The `"live"` field in the spec is the switch:

- `"live": true`: on EVERY output that changes project state (new feature, phase finished, blocker resolved or added, dependency added), before closing the turn: (1) edit the spec and its `updated` date, (2) re-render to the same path, (3) say so in one line ("panorama updated").
- `"live": false` or absent: update only when asked. This is the default; it saves tokens.

One honest caveat about where the rule has to live: a SKILL.md instruction is only guaranteed to be in context while the skill is active in the session, so on its own it cannot make the auto-update fire on every turn of every session. When you set `"live": true`, also add a line to the project's `CLAUDE.md`:

```
- Live panorama: docs/panorama/<name>.json (live:true). Keep it current on every
  turn that changes project state (edit the spec + re-render with render.py).
```

The project `CLAUDE.md` loads in every session of that repo, which is what makes the rule persist. Turning auto off means removing that line and setting `"live": false`. Trivial edits (a typo, a copy tweak that moves no stage) do not warrant a re-render; the trigger is a change of *state*.

## Flow spec

```jsonc
{
  "title": "string",
  "project": "short name (optional)",     // browser tab: "<Type> · <project||title>"
  "live": false,                          // optional: true = keep current every turn; false/absent = on-demand
  "subtitle": "string (optional)",
  "updated": "YYYY-MM-DD (optional)",
  "lanes": ["Sources", "Ingestion", "…"], // optional: one label per layer, top to bottom
  "statuses": {                           // optional: override labels/colors, or add custom ones
    "done": {"label": "Shipped", "color": "#E8E4D8"}
  },
  "nodes": [{
    "id": "unique-slug",
    "label": "Visible name",
    "status": "done | in_progress | planned | blocked",
    "layer": 0,             // row (0 = top). Omit everywhere to compute from dependencies.
    "order": 0,             // optional: position within the row
    "stack": ["tech", "…"], // chips in the tooltip
    "note": "one line of context (optional)",
    "blocker": "what it waits on (optional, short phrase)"
  }],
  "edges": [{
    "from": "id", "to": "id",
    "label": "label (optional)",
    "style": "aspirational"  // optional: dashed (future/gated). Solid by default.
  }]
}
```

## Table spec (`type: "table"`)

For comparisons and equivalences. Same renderer, same palette, same theme toggle.

```jsonc
{
  "type": "table",
  "title": "string", "subtitle": "…", "updated": "YYYY-MM-DD",
  "rowHeader": "Axis",          // corner label (the row-header column)
  "columns": [{
    "id": "a", "label": "Option A", "sub": "optional subtitle",
    "accent": true              // highlights the column (border + tint)
  }],
  "rows": [{
    "label": "Quality", "sub": "…", "group": null,  // group: section divider row
    "status": "done",           // optional: status dot on the row header
    "cells": {
      "a": {                    // rich cell; or a plain string, or an array of chips
        "text": "main text",
        "chips": ["field_1", "field_2"],
        "emphasis": "++",       // ++ / + / ~ / - / -- badge; brightness follows magnitude
        "note": "clarification",// info marker with a tooltip
        "color": "#…"           // optional badge color override
      }
    }
  }],
  "caption": "footnote (optional)"
}
```

Color rule: `emphasis` is **directional, never evaluative** (more/less, never good/bad). That is why badges render bright or dimmed instead of green or red.

## Pipeline spec (`type: "pipeline"`)

Mental model of a process's **tool chain**: what each piece does, where it comes from, why it is there, and what data travels between steps. A 2D graph with a horizontal main axis (left to right by column) and branches hanging below: parallel tracks, merges, tools that join mid-process, dependent subprocesses. Each arrow carries its data payload as a label.

Difference from `flow`: `flow` encodes *status and dependencies* (to track progress); `pipeline` encodes *function and provenance* (to explain the system). If the focus is "how it works / where each thing comes from", use `pipeline`; if it is "where are we / what is stuck", use `flow`.

```jsonc
{
  "type": "pipeline",
  "title": "string", "subtitle": "…", "updated": "YYYY-MM-DD",
  "project": "short project name",   // optional, all 3 modes: browser tab reads "<Type> · <project>"
  "lanes": ["Extraction", "Consolidation", null, "…"],  // optional: band label per column (index = col). null = none
  "nodes": [{
    "id": "crm",
    "label": "CRM",
    "col": 0,                  // column (main axis, left to right). Omit to compute from dependencies.
    "row": 0,                  // position within the column (0 = top). Use for parallel tracks / branches.
    "kind": "source",          // source|script|tool|sheet|store|crm|dashboard|api|output → type tag
    "role": "What it does and which part of the process it covers (visible sentence).",
    "why": "Why it is used / where it comes from (optional, dimmed).",
    "in": "what enters (optional)",
    "out": "what leaves (optional)",
    "stack": ["tech", "…"],    // chips
    "manual": true,            // optional: red "Manual" badge (where human work happens)
    "owner": "Ana",            // optional: who operates it
    "note": "extra detail (optional, hover only)",
    "status": "in_progress"    // optional: tints the border (in_progress/blocked = red, planned = dimmed)
  }],
  "edges": [{
    "from": "crm", "to": "consolidator",
    "payload": "which data travels (arrow label)",  // optional
    "style": "aspirational"                          // optional: dashed arrow (future/gated)
  }],
  "caption": "footnote (optional)"
}
```

Pipeline conventions:

- **Layout**: columns align to the top, so the main thread (`row: 0`) reads as a top line and branches hang below. Place a source at `col` greater than 0 with no incoming edges to represent a tool that joins mid-process; its outgoing edges are its dependent subprocesses. Two nodes in the same `col` with different `row` are parallel tracks; several edges pointing at the same `to` are a merge.
- **Information density**: cards render compact (type + name + role). Hover shows why, in/out, stack and owner. Click highlights the dependency cone and opens a detail panel with the full card and its arrows. The "Details" button expands everything inline; use it before printing or exporting a static image, where hover and click do not exist. The mobile stack layout always shows everything inline for the same reason.
- **No audience labels** ("For: CEO") in the spec: those are internal annotations, and the artifact is what the audience sees.
- `manual` marks steps with human intervention. `payload` is the data that travels, never an action.

## Design

- Dark command-center palette by default, with a light theme toggle: near-black ink, a gray ramp, a red accent (`#f04838`) for blocked and alerts, and a green accent (`#3fb950`) for in-progress, so the two states never share a color.
- Color encodes *status*, never *value*. No semantic red/green in data cells.
- System font stack, subtle 4px corners, 1px hairlines. The HTML stays self-contained and small.

## Conventions

- **Statuses**: use `blocked` only when something concrete is waited on (set the `blocker`). `planned` means not started. `in_progress` means started, not yet productive.
- **`aspirational`**: for arrows that describe the goal but do not happen yet (a future integration, a gated write). It keeps the diagram honest about what is real.

## Examples

- `examples/ai-assistant-flow.json`: flow. Build status of an internal AI support assistant, with a blocked guardrails node, dashed edges for the unshipped delivery path, and all four statuses in use.
- `examples/chat-vs-agentic.json`: table. Chat assistant vs agentic workflow, axis by axis, with ++/-- intensity badges and grouped rows.
- `examples/rag-pipeline.json`: pipeline. How a docs assistant answers a question, from raw sources through a manual curation gate to a cited answer, with a feedback edge flowing back into the eval set.
