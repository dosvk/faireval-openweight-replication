"""Relaxed SCORING parser: SECONDARY analysis only, per DEVIATIONS.md D-5 and a documented review decision.

This lives in its own module so that run_replication.py is not modified at all. The registered
`parse_verdict` and the registered `SCORE_LINE` regex are imported UNCHANGED from it, which is the
strongest available guarantee that every registered-parser number stays computable exactly as registered.

The rule, deliberately narrow and nothing broader (a documented review decision):
  - skip leading lines that consist ONLY of a markdown heading or emphasis label
    (e.g. '**Overall Scores:**', '## Scores')
  - then apply the UNCHANGED SCORE_LINE to the FIRST REMAINING non-empty line
  - do NOT skip bullets, prose, or any other kind of line
  - applied ONLY where the SCORING template is used

The rule was chosen after seeing the outputs, and the recovered count was known before it was
written. Both facts are recorded in D-5. Results are exploratory and are always reported beside the
registered figure, never instead of it.
"""
import importlib.util
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rr", os.path.join(_HERE, "run_replication.py"))
rr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rr)

SCORE_LINE = rr.SCORE_LINE          # imported unchanged, not redefined

# A line that is ONLY a markdown heading or emphasis label. No digits, no sentence punctuation,
# no bullet markers: '- x' and '* x' both fail because of the space after the marker.
LABEL_ONLY = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:\*{1,3}|_{1,3})?[A-Za-z][A-Za-z ]*:?\s*(?:\*{1,3}|_{1,3})?\s*$"
)


def parse_verdict_relaxed(text):
    """Returns (verdict, parsed_flag) for the SCORING template only.

    Identical to the registered rule except that leading label-only lines are skipped first.
    """
    if not text or not text.strip():
        return None, False
    for line in text.strip().splitlines():
        if not line.strip():
            continue                      # blank
        if LABEL_ONLY.match(line):
            continue                      # a bare markdown label: skip it
        m = SCORE_LINE.match(line)        # first remaining non-empty line, one attempt only
        if not m:
            return None, False
        a, b = float(m.group(1)), float(m.group(2))
        return ("A" if a > b else "B" if b > a else "TIE"), True
    return None, False


if __name__ == "__main__":
    cases = [
        ("**Overall Scores:**\n8.5 9.0\n\nexplanation", ("B", True), "label then scores"),
        ("## Scores\n7 7", ("TIE", True), "heading then scores"),
        ("9 8", ("A", True), "bare scores, same as registered"),
        ("- Assistant 1 is better\n9 8", (None, False), "BULLET must not be skipped"),
        ("* Assistant 2 wins\n8 9", (None, False), "bullet with asterisk must not be skipped"),
        ("Both were helpful overall.\n9 8", (None, False), "PROSE must not be skipped"),
        ("I cannot score these.", (None, False), "no scores at all"),
        ("", (None, False), "empty"),
    ]
    bad = 0
    for text, want, why in cases:
        got = parse_verdict_relaxed(text)
        ok = got == want
        bad += (not ok)
        print("  %-4s %-44s got=%-13s want=%s" % ("OK" if ok else "FAIL", why, got, want))
    print("\n%d of %d guard cases behaved as specified" % (len(cases) - bad, len(cases)))
    raise SystemExit(1 if bad else 0)
