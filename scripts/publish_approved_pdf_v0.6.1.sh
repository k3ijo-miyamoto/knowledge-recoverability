#!/usr/bin/env bash
# One-time, author-approved PDF-only GitHub release.
# Run inside a clean clone of k3ijo-miyamoto/knowledge-recoverability.
# This script does not publish to Zenodo and never accesses private research Git history.
set -euo pipefail

EXPECTED_SHA256="053b228058438412c36f9e51022cabd7f7f41652afe57b726feca04a49394d06"
EXPECTED_BYTES="149865"
FILENAME="knowledge_recoverability_v0.6.1.pdf"
DEST="paper/$FILENAME"
SRC="$HOME/Project/AssuredKnowledgeEvolution/paper/knowledge_recoverability_manuscript_v0.6.1_PRINT_PREVIEW_V2.pdf"
if [ "$#" -gt 1 ]; then
  echo "Usage: bash scripts/publish_approved_pdf_v0.6.1.sh [exact-approved-pdf-path]" >&2
  exit 2
fi
if [ "$#" -eq 1 ]; then SRC="$1"; fi

cd "$(git rev-parse --show-toplevel)"
URL="$(git remote get-url origin)"
case "$URL" in
  https://github.com/k3ijo-miyamoto/knowledge-recoverability|https://github.com/k3ijo-miyamoto/knowledge-recoverability.git|git@github.com:k3ijo-miyamoto/knowledge-recoverability.git) ;;
  *) echo "STOP: Not the approved public destination: $URL" >&2; exit 2;;
esac
[ "$(git branch --show-current)" = "main" ] || { echo "STOP: expected main branch" >&2; exit 2; }
[ -z "$(git status --porcelain)" ] || { echo "STOP: public checkout has local changes; inspect before proceeding" >&2; exit 2; }
[ -f "$SRC" ] || { echo "STOP: source PDF not found: $SRC" >&2; exit 2; }
ACTUAL_HASH="$(sha256sum "$SRC" | awk '{print $1}')"
[ "$ACTUAL_HASH" = "$EXPECTED_SHA256" ] || { echo "STOP: source checksum differs: $ACTUAL_HASH" >&2; exit 2; }
ACTUAL_BYTES="$(wc -c < "$SRC" | tr -d '[:space:]')"
[ "$ACTUAL_BYTES" = "$EXPECTED_BYTES" ] || { echo "STOP: source size differs: $ACTUAL_BYTES" >&2; exit 2; }
if command -v pdfinfo >/dev/null 2>&1; then
  PAGES="$(pdfinfo "$SRC" | awk '/^Pages:/ {print $2}')"
  [ "$PAGES" = "19" ] || { echo "STOP: expected 19 pages; got $PAGES" >&2; exit 2; }
fi

git fetch origin main
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || {
  echo "STOP: checkout main differs from origin/main; inspect and fast-forward first" >&2
  exit 2
}
[ ! -e "$DEST" ] || { echo "STOP: release PDF already exists; inspect manually" >&2; exit 2; }

# All readme edits are part of the SAME public PDF release commit.
python3 - <<'PY'
from pathlib import Path
import sys

readme = Path("README.md")
scope = Path("PUBLICATION_SCOPE.md")
citation = Path("CITATION.cff")
original = {
    readme: readme.read_text(encoding="utf-8"),
    scope: scope.read_text(encoding="utf-8"),
    citation: citation.read_text(encoding="utf-8"),
}
sha = "053b228058438412c36f9e51022cabd7f7f41652afe57b726feca04a49394d06"
pdf = "paper/knowledge_recoverability_v0.6.1.pdf"

def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise ValueError(f"STOP: {label} template mismatch; no files updated")
    return text.replace(old, new)

r = replace_once(
    original[readme],
    "**Pending author-approved release**; not yet added to this repository",
    f"**Released** — [v0.6.1 manuscript PDF]({pdf}) (19 pages, CC BY 4.0)",
    "README release row",
)
r = r.replace(
    "## Citation and licensing",
    f"**PDF SHA-256:** \x60{sha}\x60. No Zenodo DOI has been assigned.\n\n## Citation and licensing",
    1,
)
p = replace_once(
    original[scope],
    "The PDF is **not yet in this public repository**.",
    f"The author-approved [v0.6.1 manuscript PDF]({pdf}) has been publicly released in this repository; its SHA-256 is \x60{sha}\x60.",
    "PUBLICATION_SCOPE status",
)
p = p.replace(
    "publication rights clearance remain separate matters.",
    "third-party/software rights and independently certified proof remain separate matters. The author approved the exact PDF for public GitHub release.",
    1,
)
c = original[citation]
if "\nurl:" in c:
    raise ValueError("STOP: citation already contains a URL")
c = replace_once(
    c,
    'version: "0.6.1"',
    'version: "0.6.1"\nurl: "https://github.com/k3ijo-miyamoto/knowledge-recoverability/blob/main/paper/knowledge_recoverability_v0.6.1.pdf"',
    "CITATION.cff version",
)
readme.write_text(r, encoding="utf-8")
scope.write_text(p, encoding="utf-8")
citation.write_text(c, encoding="utf-8")
PY

mkdir -p paper
cp -- "$SRC" "$DEST"
[ "$(sha256sum "$DEST" | awk '{print $1}')" = "$EXPECTED_SHA256" ] || {
  echo "STOP: copy checksum mismatch; do not commit" >&2
  exit 2
}

git add -- "$DEST" README.md PUBLICATION_SCOPE.md CITATION.cff
echo "=== APPROVED STAGED PATHS ==="
git diff --cached --name-only
git diff --cached --stat
git commit -m "paper: publish approved recoverability v0.6.1 PDF"
git push origin main
echo "=== PUBLISHED ==="
echo "PDF: https://github.com/k3ijo-miyamoto/knowledge-recoverability/blob/main/$DEST"
echo "COMMIT: $(git rev-parse HEAD)"
echo "SHA256: $(sha256sum "$DEST" | awk '{print $1}')"
