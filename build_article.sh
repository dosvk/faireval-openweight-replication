#!/bin/bash
# Reproducible build of the ReScience C article.
#
# WHY THIS EXISTS, AND WHY IT CHECKS CONTENT RATHER THAN BYTES
#
# 1. LuaTeX stamps the build time into the PDF, so rebuilding byte-identical sources gave a
#    different sha every time. SOURCE_DATE_EPOCH below pins that.
#
# 2. Even with the timestamp pinned, the raw bytes still differ between two directories:
#
#        clean build in the working tree   0355a0ef30bb49e2
#        clean build in a fresh clone      2cec15b048cbf0af
#
#    Both are 17 pages and their extracted text is byte-identical (sha c977d432ad496787, 60,705
#    characters). The difference is build-environment detail, not content. So a raw-byte pin cannot
#    be satisfied from a clone, and pinning one would have told every reader their build was wrong.
#    --check therefore verifies the PAGE COUNT and a hash of the normalised text, which is what a
#    reader is actually trying to confirm and which does reproduce across locations.
#
# 3. The residue matters. An article.bbl three weeks stale sat in the working tree and every build
#    silently used it, which is how an 18-page PDF came to be shipped when the sources produce 17.
#    This script deletes the residue before building, so a build here is the same build as a clone's.
#
#     ./build_article.sh          # clean build, then print page count and content hash
#     ./build_article.sh --check  # build and fail if either differs from the pins below
set -u

EPOCH=1762300000                      # fixed; part of the build definition
PINNED_PAGES=17
PINNED_TEXT_SHA=c977d432ad496787      # sha256 prefix of the whitespace-normalised text

cd "$(dirname "$0")/rescience-build" || exit 2

# Build residue, removed so this build cannot inherit a stale bibliography. Scoped to this
# directory by name: a bare *.log once removed the released PC-4 evidence log.
rm -f article.aux article.bbl article.bcf article.blg article.fdb_latexmk article.fls \
      article.log article.out article.run.xml article.toc article.pdf

env -i HOME="$HOME" PATH=/Library/TeX/texbin:/usr/bin:/bin:/usr/sbin:/sbin \
    SOURCE_DATE_EPOCH="$EPOCH" FORCE_SOURCE_DATE=1 \
    latexmk -pdflua -interaction=nonstopmode article.tex >/dev/null 2>&1
rc=$?
if [ ! -f article.pdf ]; then
  echo "BUILD FAILED (latexmk rc=$rc); see rescience-build/article.log"
  exit 1
fi

read -r PAGES TEXTSHA <<EOF
$(python3 - <<'PY'
import pymupdf, hashlib, re
d = pymupdf.open("article.pdf")
t = re.sub(r"\s+", " ", "".join(p.get_text() for p in d)).strip()
print(d.page_count, hashlib.sha256(t.encode()).hexdigest()[:16])
PY
)
EOF

BYTES=$(shasum -a 256 article.pdf | cut -d' ' -f1)
echo "article.pdf  pages $PAGES   text sha $TEXTSHA"
echo "             bytes $BYTES"
echo "             (byte hash varies by build directory; the text hash does not)"

if [ "${1:-}" = "--check" ]; then
  ok=1
  [ "$PAGES" = "$PINNED_PAGES" ] || { echo "MISMATCH pages: expected $PINNED_PAGES, got $PAGES"; ok=0; }
  [ "$TEXTSHA" = "$PINNED_TEXT_SHA" ] || { echo "MISMATCH text: expected $PINNED_TEXT_SHA, got $TEXTSHA"; ok=0; }
  if [ "$ok" = "1" ]; then
    echo "REPRODUCIBLE: $PAGES pages and the pinned text hash"
    exit 0
  fi
  echo "Either a source changed, or the toolchain differs from TeX Live 2026 / biber 2.21."
  exit 1
fi
