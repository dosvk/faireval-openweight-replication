#!/usr/bin/env python3
"""Two release gates asked for by D-P10-92w, both proven to discriminate before being shipped.

1. ORPHAN LINE. A short line that ends a sentence AND whose previous line also ends a sentence.
   Hard-wrapped prose produces short final lines constantly ("load.", "used.", "figures."), which is
   why a naive short-line check gives 12 false positives on this manuscript. But wrapped prose never
   has a period at the end of the PREVIOUS line, because the previous line is mid-sentence. That one
   extra condition takes the check from 12 clean / 13 planted to 0 clean / 1 planted.

   This is the check that would have caught "marginal distribution." on page 7, which an earlier
   noisy attempt did surface and which I then dismissed as a table artefact while arguing the check
   did not work.

2. INVENTORY LISTING. DATA-AVAILABILITY.md is headed "Our own code, all of it". That claim is
   checkable: every *.py in the release must be named in that file, and every .py named must exist.
   `verify_parser_pins.py` was shipped and left out of the inventory, and the reply then said the
   inventory was reconciled.

    python3 check_release.py            # both gates; exit 1 on any finding
    python3 check_release.py --selftest # prove each one fires and is quiet when it should be
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP_PREFIX = ("#", "|", "-", "*", ">")


def orphan_lines(text):
    """Short sentence-ending lines whose previous line also ends a sentence."""
    out, lines = [], text.split("\n")
    for i in range(1, len(lines)):
        cur, prev = lines[i].strip(), lines[i - 1].strip()
        if not cur or not prev:
            continue
        if cur.startswith(SKIP_PREFIX) or prev.startswith(SKIP_PREFIX):
            continue
        if 1 <= len(cur.split()) <= 3 and cur.endswith(".") and prev.endswith("."):
            out.append((i + 1, cur))
    return out


def inventory_mismatch(inv_path=None, root=None):
    """Scripts present but unlisted, and scripts listed but absent."""
    inv_path = inv_path or os.path.join(HERE, "DATA-AVAILABILITY.md")
    root = root or HERE
    if not os.path.exists(inv_path):
        return ["DATA-AVAILABILITY.md not found"], []
    inv = open(inv_path, errors="replace").read()
    on_disk = sorted(os.path.basename(p) for p in glob.glob(os.path.join(root, "*.py")))
    unlisted = [s for s in on_disk if s not in inv]
    import re
    # names may be hyphenated (yaml-to-latex.py) and may live in a subdirectory
    # (rescience-build/article.py), so match the full token and search the whole tree.
    listed = sorted(set(re.findall(r"\b([a-z0-9_][a-z0-9_\-]*\.py)\b", inv)))
    present = set()
    for dirpath, _dirs, files in os.walk(root):
        if "/.git" in dirpath:
            continue
        present.update(files)
    missing = [s for s in listed if s not in present]
    return unlisted, missing


README_REQUIRED = [
    ("title line", "# Does positional bias"),
    ("OSF DOI", "10.17605/OSF.IO/JW59C"),
    ("what-is-here section", "## What is here"),
    ("licence section", "## Licence"),
]


def readme_missing(path=None):
    """C1: the README was once overwritten rather than extended, losing the title, the OSF DOI,
    the licence and four other sections. The reviewer's first click is this file. These four
    anchors must be present."""
    path = path or os.path.join(HERE, "README.md")
    if not os.path.exists(path):
        return [("README.md absent", "")]
    t = open(path, errors="replace").read()
    return [(lbl, tok) for lbl, tok in README_REQUIRED if tok not in t]


def tracked_not_in_inventory(root=None):
    """m9: compare the inventory against git ls-files, not ls *.py, so build inputs and data files
    are covered too."""
    import subprocess
    root = root or os.path.join(HERE, "release-tree")
    inv_p = os.path.join(root, "DATA-AVAILABILITY.md")
    if not os.path.exists(inv_p):
        return []
    inv = open(inv_p, errors="replace").read()
    # split on NEWLINES, not whitespace: the bundled font licences are named
    # "SIL Open Font License.txt" and whitespace splitting turned each into three phantom files.
    out = [l for l in subprocess.run(["git", "ls-files"], cwd=root, capture_output=True,
                                     text=True).stdout.split("\n") if l.strip()]
    ignore = {".gitignore", "DATA-AVAILABILITY.md", "LICENSE", "README.md", "DEVIATIONS.md",
              "metadata.yaml", "article/article.pdf", "claims.json"}
    missing = []
    for f in out:
        if f in ignore:
            continue
        base = os.path.basename(f)
        if base in inv or f in inv:
            continue
        # a directory named in the inventory covers the files inside it: the font bundles are
        # listed as roboto/, source-code-pro/ and so on rather than file by file.
        parent = os.path.dirname(f)
        covered = False
        while parent:
            if (parent + "/") in inv or os.path.basename(parent) + "/" in inv:
                covered = True
                break
            parent = os.path.dirname(parent)
        if not covered:
            missing.append(f)
    return missing


def check(verbose=True):
    findings = []
    for lbl, tok in readme_missing():
        findings.append(("README missing a required anchor", "README.md", "%s (%r)" % (lbl, tok)))
    for f in tracked_not_in_inventory():
        findings.append(("released file not in inventory", "DATA-AVAILABILITY.md", f))
    built = os.path.join(HERE, "build", "p10.md")
    if os.path.exists(built):
        for line, text in orphan_lines(open(built, errors="replace").read()):
            findings.append(("orphan line", "build/p10.md:%d" % line, text))
    elif verbose:
        print("  note: build/p10.md absent, orphan check skipped (run build_paper.py first)")
    unlisted, missing = inventory_mismatch()
    for s in unlisted:
        findings.append(("script not in inventory", "DATA-AVAILABILITY.md", s))
    for s in missing:
        findings.append(("inventory names a missing script", "DATA-AVAILABILITY.md", s))
    if verbose:
        for kind, where, what in findings:
            print("  %-34s %-26s %r" % (kind, where, what))
        print("%s" % ("PASS: no orphan lines, inventory matches the tree"
                      if not findings else "FAIL: %d finding(s)" % len(findings)))
    return findings


def selftest():
    ok = True
    print("  %-52s %s" % ("clean tree passes both gates",
                          "PASS" if not check(verbose=False) else "FAIL"))
    ok &= not check(verbose=False)

    built = os.path.join(HERE, "build", "p10.md")
    if os.path.exists(built):
        orig = open(built, errors="replace").read()
        planted = orig.replace("look-alike number.", "look-alike number.\nmarginal distribution.", 1)
        fired = len(orphan_lines(planted)) > len(orphan_lines(orig))
        print("  %-52s %s" % ("orphan gate fires on a planted fragment",
                              "PASS" if fired else "FAIL"))
        ok &= fired
        # and quiet on ordinary wrapped prose, which is what the naive version failed
        quiet = len(orphan_lines(orig)) == 0
        print("  %-52s %s" % ("orphan gate quiet on wrapped prose", "PASS" if quiet else "FAIL"))
        ok &= quiet

    import tempfile
    d = tempfile.mkdtemp()
    open(os.path.join(d, "ghost.py"), "w").write("# a script no inventory mentions\n")
    open(os.path.join(d, "DATA-AVAILABILITY.md"), "w").write("nothing listed here\n")
    unlisted, _ = inventory_mismatch(os.path.join(d, "DATA-AVAILABILITY.md"), d)
    hit = "ghost.py" in unlisted
    print("  %-52s %s" % ("inventory gate fires on an unlisted script",
                          "PASS" if hit else "FAIL"))
    ok &= hit
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(1 if check() else 0)
