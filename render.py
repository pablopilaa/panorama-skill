#!/usr/bin/env python3
"""Render a panorama spec (JSON) into a standalone interactive HTML file.

Usage:
    python3 render.py <spec.json> [-o out.html] [--open]

Templates live next to this script and contain the token __DIAGRAM_DATA__,
which is replaced with the spec verbatim. Python 3 standard library only.
"""
import argparse
import json
import pathlib
import sys
import urllib.parse
import webbrowser

HERE = pathlib.Path(__file__).resolve().parent
TOKEN = "__DIAGRAM_DATA__"
FAVICON_TOKEN = "__FAVICON__"

TEMPLATES = {
    "flow": HERE / "template.html",
    "table": HERE / "template-table.html",
    "pipeline": HERE / "template-pipeline.html",
}


def _favicon() -> str:
    """Small node-graph glyph on a dark tile, as a self-contained data URI."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
        "<rect width='64' height='64' rx='10' fill='#0a0a0b'/>"
        "<g stroke='#56565e' stroke-width='3'>"
        "<line x1='17' y1='32' x2='32' y2='17'/><line x1='17' y1='32' x2='32' y2='47'/>"
        "<line x1='32' y1='17' x2='47' y2='32'/><line x1='32' y1='47' x2='47' y2='32'/></g>"
        "<circle cx='17' cy='32' r='6' fill='#ffffff'/><circle cx='32' cy='17' r='6' fill='#ffffff'/>"
        "<circle cx='32' cy='47' r='6' fill='#ffffff'/><circle cx='47' cy='32' r='6' fill='#f04838'/></svg>"
    )
    return "data:image/svg+xml," + urllib.parse.quote(svg)


def render(spec_path: pathlib.Path, out_path: pathlib.Path) -> pathlib.Path:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))  # validate it parses
    template = TEMPLATES.get(spec.get("type", "flow"), TEMPLATES["flow"])
    # re-dump so the embedded JSON is clean and </script> can't break out of the tag
    data = json.dumps(spec, ensure_ascii=False).replace("</", "<\\/")
    html = template.read_text(encoding="utf-8")
    html = html.replace(FAVICON_TOKEN, _favicon()).replace(TOKEN, data)
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="path to the diagram spec JSON")
    ap.add_argument("-o", "--out", help="output HTML path (default: <spec>.html)")
    ap.add_argument("--open", action="store_true", help="open the result in the default browser")
    args = ap.parse_args()

    spec_path = pathlib.Path(args.spec).resolve()
    if not spec_path.exists():
        print(f"spec not found: {spec_path}", file=sys.stderr)
        return 1
    out_path = pathlib.Path(args.out).resolve() if args.out else spec_path.with_suffix(".html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    render(spec_path, out_path)
    print(out_path)
    if args.open:
        webbrowser.open(out_path.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
