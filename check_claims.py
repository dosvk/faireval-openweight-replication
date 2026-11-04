#!/usr/bin/env python3
"""Stated-once checker: no released text may carry a superseded wording of a canonical claim.

WHY THIS EXISTS
---------------
On ReScience #142, three claims were each corrected in one place and left wrong in another, and the
reply to the reviewer then asserted the correction was complete. All three were caught by a second
reader, not by me:

  * the secondary parser's skip rule was fixed in a code comment while the module DOCSTRING kept the
    false version, and the manuscript carried two adjacent sentences contradicting each other;
  * the per-arm halt was described as the registration's rule in three places while the disclosure
    that the registration says two different things lived only in the register;
  * hydrate_faireval.py was corrected in the README and still called a fetcher in four other places.

A human proofread does not reliably find the second occurrence. A list does.

Exit 1 if any superseded wording appears outside a dated correction. Exit 0 with a count otherwise.

    python3 check_claims.py            # check
    python3 check_claims.py --selftest # prove it fires, and prove it does not fire on the register
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "claims.json")

# A superseded wording quoted INSIDE a dated correction is documented history, not a live claim.
# This is the same distinction the redaction register uses for its bracketed notes.
CORRECTION_MARKERS = ("superseded", "was FALSE", "was false", "earlier wording",
                      "we quoted only one side", "which was false", "earlier versions",
                      "the earlier docstring", "the earlier alternative",
                      "which was wrong", "was wrong", "corrected after",
                      "still wrong", "WHAT WAS STILL WRONG", "the manuscript carried")
WINDOW = 400


def _exempt(text, idx):
    lo, hi = max(0, idx - WINDOW), min(len(text), idx + WINDOW)
    return any(m in text[lo:hi] for m in CORRECTION_MARKERS)


def check(verbose=True, extra_files=None):
    spec = json.load(open(SPEC))
    files = list(spec["scope"]["files"]) + list(extra_files or [])
    hits = []
    for claim in spec["claims"]:
        for bad in claim["superseded"]:
            for fn in files:
                p = fn if os.path.isabs(fn) else os.path.join(HERE, fn)
                if not os.path.exists(p):
                    continue
                t = open(p, errors="replace").read()
                for m in re.finditer(re.escape(bad), t):
                    if _exempt(t, m.start()):
                        continue
                    line = t[:m.start()].count("\n") + 1
                    hits.append((claim["id"], fn, line, bad))
    if verbose:
        print("stated-once check: %d claim(s), %d file(s)" % (len(spec["claims"]), len(files)))
        for cid, fn, line, bad in hits:
            print("  LIVE SUPERSEDED WORDING  %-26s %s:%d  %r" % (cid, fn, line, bad))
        print("\n%s" % ("PASS: no superseded wording outside a dated correction"
                        if not hits else "FAIL: %d live superseded wording(s)" % len(hits)))
    return hits


def selftest():
    ok = True
    hits = check(verbose=False)
    print("  %-52s %s" % ("clean tree has no live superseded wording", "PASS" if not hits else "FAIL"))
    ok &= not hits

    # non-vacuity: plant one and confirm it fires.
    # C1 (D-P10-93w) was a README overwritten in place. This selftest used to write the REAL
    # README and restore it in a finally, which would have left it damaged if interrupted - the
    # same failure. It now works on a temp copy and never touches a released file.
    import shutil as _sh, tempfile as _tf2
    _d = _tf2.mkdtemp()
    target = os.path.join(_d, "README.md")
    _sh.copy(os.path.join(HERE, "README.md"), target)
    orig = open(target).read()
    try:
        open(target, "w").write(orig + "\n\nThis script fetches and verifies the inputs.\n")
        planted = check(verbose=False, extra_files=[target])
        fired = any(b == "fetches and verifies" for _, _, _, b in planted)
        print("  %-52s %s" % ("fires on a planted superseded wording", "PASS" if fired else "FAIL"))
        ok &= fired
    finally:
        open(target, "w").write(orig)

    # and the exemption works: the same wording inside a correction must NOT fire
    try:
        open(target, "w").write(orig + "\n\nThe earlier docstring said it fetches and verifies; that was false.\n")
        exempted = check(verbose=False, extra_files=[target])
        quiet = not any(b == "fetches and verifies" for _, _, _, b in exempted)
        print("  %-52s %s" % ("quiet when quoted inside a dated correction", "PASS" if quiet else "FAIL"))
        ok &= quiet
    finally:
        open(target, "w").write(orig)
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(1 if check() else 0)
