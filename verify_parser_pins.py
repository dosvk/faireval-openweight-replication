#!/usr/bin/env python3
"""Verify the parser pins printed in the article (Methods, secondary-parser subsection).

WHY THIS EXISTS
---------------
Reviewer 1 on ReScience #142 (2026-11-04) reported that the four sha256 prefixes printed in the
manuscript "could not be reproduced from the current AST source segments, compiled pattern strings
or `inspect.getsource` variants checked", and asked us either to specify the exact hashed bytes or
to ship a verifier.

We tried 26 plausible conventions against the released source -- the compiled `.pattern` string,
with and without a trailing newline, the full assignment line, the right-hand side alone, stripped
and unstripped, `repr()` of the pattern, and for the function: `inspect.getsource`, the body after
the `def` line, the dedented body, the source with the docstring removed, and the stripped body.
NONE reproduced any of the four printed prefixes.

So the original hashing convention is NOT RECOVERABLE from what was recorded. The reviewer is right
that the convention was underspecified. Two points matter and are stated in the deviations register
as well:

  * This does NOT establish that the parser changed after registration, and we do not claim it did.
    An unreproducible hash is evidence about the hashing convention, not about the hashed object.
  * The pins are therefore REPLACED with pins under the explicit convention below, which this script
    recomputes. The superseded values are kept in the register.

THE CONVENTION, STATED EXACTLY
------------------------------
For each of the three regex constants: hash the UTF-8 bytes of the compiled pattern string, i.e.
`re.compile(...).pattern.encode("utf-8")`, with no trailing newline and no surrounding quotes.

For `parse_verdict`: hash the UTF-8 bytes of `inspect.getsource(parse_verdict)` exactly as returned,
including the `def` line, the docstring and the trailing newline, with no dedenting.

Report the first 16 hex characters of each sha256. First 16 is a display convention; the full digest
is printed by `--full`.

USAGE
-----
    python3 verify_parser_pins.py            # print the pins
    python3 verify_parser_pins.py --full     # full 64-hex digests
    python3 verify_parser_pins.py --check    # compare against PINS below; exit 1 on any mismatch
"""
import hashlib
import importlib.util
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Pins under the convention documented above, computed 2026-11-04 from the released source.
# These SUPERSEDE the four prefixes printed in earlier versions of the manuscript, whose
# convention could not be recovered. See DEVIATIONS.md, D-22.
PINS = {
    "SCORE_LINE":     "3731d07991798867",
    "SCORE_LABELLED": "4889ac20478acbd0",
    "COMPARE_LINE":   "225bfde4c0c754e0",
    "parse_verdict":  "e6e373cf6113f98b",
}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass          # the harness exits when run without arguments; the module is still loaded
    return mod


def compute():
    rr = _load("rr_pins", os.path.join(HERE, "run_replication.py"))
    out = {}
    for name in ("SCORE_LINE", "SCORE_LABELLED", "COMPARE_LINE"):
        obj = getattr(rr, name)
        pattern = obj.pattern if hasattr(obj, "pattern") else str(obj)
        out[name] = hashlib.sha256(pattern.encode("utf-8")).hexdigest()
    src = inspect.getsource(getattr(rr, "parse_verdict"))
    out["parse_verdict"] = hashlib.sha256(src.encode("utf-8")).hexdigest()
    return out


def main():
    full = "--full" in sys.argv
    got = compute()
    width = 64 if full else 16
    print("parser pins (sha256, %s hex; convention in this file's docstring)" % width)
    bad = []
    for name in ("SCORE_LINE", "SCORE_LABELLED", "COMPARE_LINE", "parse_verdict"):
        d = got[name][:width]
        line = "  %-16s %s" % (name, d)
        if "--check" in sys.argv:
            want = PINS[name]
            ok = got[name][:16] == want
            line += "   %s" % ("OK" if ok else "MISMATCH, expected %s" % want)
            if not ok:
                bad.append(name)
        print(line)
    if "--check" in sys.argv:
        if bad:
            print("\nFAIL: %d pin(s) do not match: %s" % (len(bad), ", ".join(bad)))
            print("A mismatch means the hashed object changed, OR this script's convention was edited.")
            return 1
        print("\nPASS: all four pins reproduce.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
