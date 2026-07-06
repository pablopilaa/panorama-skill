#!/usr/bin/env bash
# Share a diagram as a browsable link, no deploy needed.
# Uploads the HTML to a SECRET gist (unlisted, private by URL) and prints a
# gist.githack.com link that opens the rendered HTML in any browser.
#
#   ./share.sh <file.html>      # share an already-rendered HTML
#   ./share.sh <spec.json>      # render first, then share
#
# Requires: gh authenticated with the 'gist' scope (gh auth status).
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
in="${1:?usage: ./share.sh <file.html | spec.json>}"
[ -f "$in" ] || { echo "not found: $in" >&2; exit 1; }

if [[ "$in" == *.json ]]; then
  out="${in%.json}.html"
  python3 "$here/render.py" "$in" -o "$out" >/dev/null
  in="$out"
fi

base="$(basename "$in")"
gist_url="$(gh gist create "$in" --desc "panorama · $base" | tail -1)"
id="${gist_url##*/}"
user="$(gh api user -q .login)"

echo "secret gist : $gist_url"
echo "open link   : https://gist.githack.com/$user/$id/raw/$base"
echo
echo "The githack link opens the rendered diagram in any browser."
echo "The gist is unlisted, but anyone with the link can view it."
