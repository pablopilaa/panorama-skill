#!/usr/bin/env python3
"""Render a panorama spec (JSON) into a standalone interactive HTML file.

Usage:
    python3 render.py <spec.json> [-o out.html] [--open]

Templates live next to this script and contain the token __DIAGRAM_DATA__,
which is replaced with the spec verbatim. Python 3 standard library only.
"""
import argparse
import base64
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request
import webbrowser

HERE = pathlib.Path(__file__).resolve().parent
TOKEN = "__DIAGRAM_DATA__"
FAVICON_TOKEN = "__FAVICON__"

TEMPLATES = {
    "flow": HERE / "template.html",
    "table": HERE / "template-table.html",
    "pipeline": HERE / "template-pipeline.html",
}
# Full-color brand SVGs from gilbarbara/logos. Slugs = its filenames
# (e.g. "nextjs", "supabase", "postgresql", "vercel-icon").
LOGO_CDN = [
    "https://cdn.jsdelivr.net/gh/gilbarbara/logos@main/logos/{slug}.svg",
    "https://cdn.jsdelivr.net/gh/gilbarbara/logos@master/logos/{slug}.svg",
]
_LOGO_MIME = {"svg": "image/svg+xml", "png": "image/png", "jpg": "image/jpeg",
              "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif"}


def _data_uri(raw: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")


_LOGO_NAMES = {
    "nextjs": "Next.js", "nextdotjs": "Next.js", "react": "React", "supabase": "Supabase",
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "python": "Python", "fastapi": "FastAPI",
    "hubspot": "HubSpot", "youtube": "YouTube", "googlesheets": "Google Sheets",
    "google-sheets": "Google Sheets", "n8n": "n8n", "backblaze": "Backblaze B2",
    "backblaze-icon": "Backblaze B2", "slack": "Slack", "slack-icon": "Slack", "notion": "Notion",
    "zendesk": "Zendesk", "git": "Git", "git-icon": "Git", "vercel": "Vercel", "vercel-icon": "Vercel",
    "openai": "OpenAI", "openai-icon": "OpenAI", "anthropic": "Anthropic", "claude": "Claude",
    "googlebigquery": "BigQuery", "bigquery": "BigQuery", "metabase": "Metabase",
}


def _prettify(slug: str) -> str:
    return " ".join(w[:1].upper() + w[1:] for w in re.split(r"[-_]+", slug) if w)


def _svg_title(raw: bytes) -> str:
    """The human tool name from an SVG's <title>, if any."""
    try:
        m = re.search(r"<title[^>]*>(.*?)</title>", raw.decode("utf-8", "ignore"), re.I | re.S)
    except Exception:  # noqa: BLE001
        return ""
    return m.group(1).strip() if m else ""


def _resolve_logos(spec: dict, fetch: bool):
    """Map every node `logo` slug to an inlined data URI + a display name (deduped).

    Order per slug: a data: URI verbatim -> an explicit file path -> a cached
    logos/<slug>.svg -> (only with fetch) download from LOGO_CDN and cache.
    The display name comes from the SVG's <title> when present. A missing or
    bad logo is warned and skipped, never fatal.
    """
    slugs = {n["logo"] for n in spec.get("nodes", []) if n.get("logo")}
    if not slugs:
        return {}, {}
    cache = HERE / "logos"
    assets, names = {}, {}
    for slug in sorted(slugs):
        if slug.startswith("data:"):
            assets[slug] = slug
            continue
        raw = None
        p = pathlib.Path(slug)
        if p.suffix and p.exists():
            raw = p.read_bytes()
            assets[slug] = _data_uri(raw, _LOGO_MIME.get(p.suffix.lstrip(".").lower(), "image/svg+xml"))
        else:
            hit = cache / f"{slug}.svg"
            if hit.exists():
                raw = hit.read_bytes()
                assets[slug] = _data_uri(raw, "image/svg+xml")
            elif not fetch:
                print(f"logo '{slug}' not cached - run with --fetch-logos", file=sys.stderr)
                continue
            else:
                for tpl in LOGO_CDN:
                    try:
                        url = tpl.format(slug=urllib.parse.quote(slug))
                        req = urllib.request.Request(url, headers={"User-Agent": "panorama-skill"})
                        with urllib.request.urlopen(req, timeout=15) as r:
                            raw = r.read()
                        break
                    except Exception:  # noqa: BLE001 - try the next candidate URL
                        raw = None
                        continue
                if raw is None:
                    print(f"logo '{slug}' skipped: not found in any source", file=sys.stderr)
                    continue
                cache.mkdir(parents=True, exist_ok=True)
                hit.write_bytes(raw)
                assets[slug] = _data_uri(raw, "image/svg+xml")
        if raw is not None:
            names[slug] = _LOGO_NAMES.get(slug) or _svg_title(raw) or _prettify(slug)
    return assets, names


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


def render(spec_path: pathlib.Path, out_path: pathlib.Path, fetch_logos: bool = False) -> pathlib.Path:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))  # validate it parses
    template = TEMPLATES.get(spec.get("type", "flow"), TEMPLATES["flow"])
    logos, logo_names = _resolve_logos(spec, fetch_logos)
    if logos:
        spec["logoAssets"] = logos
    if logo_names:
        spec["logoNames"] = logo_names
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
    ap.add_argument("--fetch-logos", action="store_true",
                    help="download any node `logo` slugs from gilbarbara/logos and cache in logos/")
    args = ap.parse_args()

    spec_path = pathlib.Path(args.spec).resolve()
    if not spec_path.exists():
        print(f"spec not found: {spec_path}", file=sys.stderr)
        return 1
    out_path = pathlib.Path(args.out).resolve() if args.out else spec_path.with_suffix(".html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    render(spec_path, out_path, fetch_logos=args.fetch_logos)
    print(out_path)
    if args.open:
        webbrowser.open(out_path.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
