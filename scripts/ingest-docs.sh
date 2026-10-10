#!/usr/bin/env bash
# Convert PDFs / .tex / .pptx / .docx from outside the repo into markdown under vault/ so graphify indexes text.
# Idempotent (skips files whose markdown is newer than the source). Originals are never modified.
# Add `put <dest-subdir> <source-file>` lines at the bottom. Needs `pdftotext` (brew install poppler) for PDFs.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
D="$HOME/Downloads"
n=0
put() { # dest-subdir source
  local dest="$REPO/vault/$1" src="$2"; mkdir -p "$dest"
  [ -e "$src" ] || { echo "skip (missing): $src"; return; }
  local base; base="$(basename "$src")"; base="${base%.*}"; base="$(echo "$base" | sed -E 's/[^A-Za-z0-9._-]+/-/g; s/-+/-/g; s/^-|-$//g')"
  local out="$dest/$base.md"
  [ "$out" -nt "$src" ] && return
  case "$src" in *.pdf) command -v pdftotext >/dev/null || { echo "skip (no pdftotext; brew install poppler): $src"; return; } ;; esac
  {
    printf -- "---\ntitle: %s\ntype: document\nsource_path: %s\nupdated: %s\n---\n\n" "$(basename "$src")" "${src/#$HOME/~}" "$(date +%F)"
    case "$src" in
      *.pdf)  pdftotext -layout "$src" - 2>/dev/null ;;
      *.tex)  cat "$src" ;;
      *.zip)  unzip -p "$src" '*.tex' 2>/dev/null ;;
      *.pptx) python3 - "$src" <<'PY'
import sys, zipfile, re
z = zipfile.ZipFile(sys.argv[1])
slides = sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml', n)], key=lambda s: int(re.findall(r'\d+', s)[0]))
for i, s in enumerate(slides, 1):
    txt = re.findall(r'<a:t>([^<]*)</a:t>', z.read(s).decode('utf8', 'ignore'))
    print(f"\n## Slide {i}\n" + "\n".join(t for t in txt if t.strip()))
PY
      ;;
      *.docx) python3 - "$src" <<'PY'
import sys, zipfile, re
x = zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode('utf8', 'ignore')
for p in re.findall(r'<w:p[ >].*?</w:p>', x, flags=re.S):
    t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))
    if t.strip(): print(t)
PY
      ;;
      *) cat "$src" ;;
    esac
  } > "$out"
  n=$((n+1)); echo "wrote vault/$1/$base.md"
}

# ---- your documents (examples; uncomment and edit) ----
# put sources/docs "$D/some-report.pdf"
# for f in "$D"/*.pdf; do put sources/docs "$f"; done

echo "converted $n file(s)"
