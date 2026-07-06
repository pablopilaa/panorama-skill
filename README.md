# panorama-skill

One-file interactive diagrams for your projects: status maps, comparison tables, and tool-chain pipelines. Built for AI builders and AI enthusiasts who want to see where a project stands, decide between options, or explain a system to someone else without opening a design tool.

It ships as an [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code, and the engine (`render.py` plus three HTML templates) runs anywhere with Python 3. Any agent or chat AI that can write JSON can drive it: the AI writes a small spec, the renderer turns it into a self-contained HTML file. No Mermaid, no CDN, no build step.

## Three modes

Pick by the question you are answering, not by the topic.

| `type` | Question it answers | Shape |
|---|---|---|
| `flow` (default) | Where are we? What is stuck? What depends on what? | 2D graph with lanes, status colors, blockers, clickable dependency cone |
| `table` | Which of these options do I pick? What maps to what? | comparison matrix with ++/-- intensity badges |
| `pipeline` | How does it work end to end? Where does each piece of data come from? | horizontal graph with branches, merges, payload-labeled arrows, detail panel |

## Quick start

```bash
git clone https://github.com/pablopilaa/panorama-skill
cd panorama-skill
python3 render.py examples/rag-pipeline.json --open
```

That renders a pipeline diagram of a RAG docs assistant and opens it in your browser. Try the other two examples for the `flow` and `table` modes.

## Install as a Claude Code skill

Symlink the repo into your skills folder:

```bash
ln -s "$PWD" ~/.claude/skills/panorama
```

Then ask Claude Code for "a panorama of this project", "compare X vs Y in a table", or "diagram how this pipeline works". Claude reads your repo, writes the spec, renders it, and keeps the spec versioned under `docs/panorama/` so the diagram evolves with the project. A `live` mode keeps a diagram current on every turn that changes project state; `SKILL.md` documents it.

## Use with any other AI

The renderer has no Claude dependency. Give your assistant the spec schemas from [`SKILL.md`](SKILL.md), ask it to produce the JSON, and run:

```bash
python3 render.py my-spec.json --open
```

## The spec is the source of truth

The JSON spec is what you version; the HTML is a derived artifact you can regenerate or delete. Keep specs in the project they describe (suggested: `docs/panorama/<name>.json`) and re-render as the project moves.

## Share a diagram as a link

```bash
./share.sh out.html
```

Uploads to a secret gist and prints a `gist.githack.com` link that renders in any browser. Needs the [GitHub CLI](https://cli.github.com/) authenticated with the `gist` scope. The gist is unlisted; anyone with the link can view it.

## En español

Diagramas interactivos de proyecto en un solo archivo HTML: mapas de estado (`flow`), tablas de comparación (`table`) y cadenas de herramientas (`pipeline`). La IA escribe un spec JSON y `render.py` lo convierte en HTML autocontenido, sin dependencias.

Para instalarlo como skill de Claude Code: `ln -s "$PWD" ~/.claude/skills/panorama`, y después pedile "un panorama de este proyecto", "una tabla comparando X vs Y" o "un pipeline de cómo funciona el sistema". El spec queda versionado en tu repo; el HTML se regenera cuando quieras. Los esquemas completos están en `SKILL.md` (en inglés).

## License

MIT. See [LICENSE](LICENSE).
