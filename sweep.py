"""Stale-claim sweep.

Checks every corrected claim in the project against:
  - the draft sources (RESULTS-DRAFT.md, SECTIONS-DRAFT.md, DEVIATIONS.md), and
  - the text a reader actually sees, extracted from build/p10.pdf.

Written after review found two live errors this sweep had missed, and extended after
D-P10-33 found a third that lived only in the built appendix and not in the files being swept.

WHITELIST. A dated register entry in DEVIATIONS.md is allowed to contain a superseded claim, but
ONLY if it carries a bracketed superseded note. That exemption is deliberately narrow and is tested
in both directions by `--selftest`: the noted form must pass, and the bare form must still fail.

Usage:
    python3 sweep.py             # sweep sources + built PDF
    python3 sweep.py --selftest  # prove the whitelist accepts the noted form and rejects the bare one
Exit 0 only if no stale claim survives anywhere.
"""
import os
import os
import re
import subprocess
import sys

SOURCES = ["RESULTS-DRAFT.md", "SECTIONS-DRAFT.md", "DEVIATIONS.md"]
PDF = "build/p10.pdf"

# (label, pattern that MUST NOT appear)
BANNED = [
    # D-P10-39 INVERTED THIS PATTERN. Under D-12, "all three not evaluable" is the CORRECT claim,
    # so the old banned phrasing is now required. What is banned instead is the SUPERSEDED
    # classification: H2 presented as evaluated, or as a registered inconclusive result.
    ("superseded: H2 evaluated / inconclusive as a registered result",
     r"the third is inconclusive"
     r"|H2 is inconclusive(?! there under)"
     r"|two of the three (?:pre-registered )?hypotheses cannot be evaluated"
     r"|H2, evaluated under D-8"
     r"|H2 names no arm in the registration, so it was evaluated"
     r"|no registered hypothesis test was performed"),
    ("three strategies, not two", r"two calibration strategies"),
    # Only catch US claiming a BPC figure. References to the ORIGINAL's MEC+BPC quantity are
    # legitimate: H3 genuinely compares it, and D-9/D-10 must be able to name it.
    ("BPC misnomer (our figures)", r"our MEC ?\+ ?BPC|order-averaged MEC accuracy"),
    # The prevalence/bias-index check was REMOVED, deliberately. The distinction that matters is
    # semantic - claiming the indices are reported versus quoting the requirement to explain why
    # they are not - and a regex cannot draw it. It misfired twice on D-13, which must quote the
    # registration to document the gap. What replaced it is the narrow, literal compliance claim
    # the paper actually used to make.
# Pre-D-16 (frame-error) figures. Any reappearance means uncorrected numbers are back.
    # Pre-D-16 figures are BANNED as live values but REQUIRED where a correction is disclosed
    # ("An earlier version ... reported 0.429"). Excused when the sentence names the correction,
    # the same treatment the dated superseded note gets. Tested both ways in --selftest.
    ("pre-D-16 figures used as live values",
     r"(?<!reported )(?<!reported 0\.429, )\b0\.429 \[|by 0\.30 to 0\.41|order-averaged MEC accuracy"),
# A conflict rate c is never zero for these cells; it is the NET order-dependence c - s that is
    # zero. This phrasing survived three ad-hoc greps because it wraps across a line break in the
    # source and my greps did not normalise whitespace; the sweep does, so it belongs here.
    ("conflict rate called zero",
     r"(?:zero|0\.000) conflict rate|conflict rate (?:is|of) (?:zero|0\.000)"),
# A duplicated sentence survived four literal-match attempts because line breaks fell inside the
    # phrases being matched. The sweep normalises whitespace before matching, so it catches what
    # hand-written greps miss - which is the whole argument for putting checks here rather than ad hoc.
("duplicated venue sentence",
     r"(author guidelines are the source for the venue requirements we follow).{0,200}\1"),
    ("false kappa-compliance claim",
     r"alongside the label marginals and PABAK, never as a bare number\."),
    ("bare 313-of-320 parser claim",
     r"could not reach for 313 of 320|313 of 320 records, because it emitted"),
    ("'substantively correct' scores", r"produced substantively\s*correct scores"),
    ("debiasing-sentence rationale", r"imported the code's debiasing sentence"),
    ("six CONSUMED files", r"all six consumed files"),
    ("determinism extended to all 3 judges",
     r"these three locally served 7-8B judges, a temperature-0"),
    ("temp-0 used to explain a temp-1 arm",
     r"compared record by record, for the\s*same reason this paper documents"),
    ("Zheng over-credited",
     r"Vicuna benchmark that the original study reuses|documented\s*position bias among other"),
    ("unqualified 'MEC arms are clean'",
     r"MEC arms on the authors' own released prompt are clean:"),
    ("H2 test called McNemar", r"registered tests were exact McNemar per judge"),
    ("every question in both orders", r"Every question is judged in both presentation orders"),
    # draft scaffolding that must never reach a reader (D-P10-35)
    ("workflow 'at the time of writing'", r"at the time of writing"),
    ("workflow 'NOT FOR BUILD'", r"NOT FOR BUILD"),
    ("workflow 'open with the reviewer'", r"with the reviewer"),
    ("stale 'once the remaining'", r"once the remaining"),
    ("arms described as still running", r"temperature-1 arms, running"),
]

# Patterns checked ONLY in the built PDF: internal process identifiers are allowed to live in the
# dated register source, but must not reach a reader.
# sweep.py and build_paper.py are EXCLUDED from the process-language scan, and only from that
# scan. Both must contain the very strings they search for or rewrite - a linter necessarily names
# what it lints - so scanning them produces permanent noise rather than findings. The exclusion is
# deliberately narrow: these two files are still scanned by every other pattern, and the four files
# that carry the study's logic are scanned by all of them.
CODE_FILES = ["run_replication.py", "analyze_mec.py", "relaxed_parse.py",
              "pc4_retest.py", "hydrate_faireval.py"]

# Project-internal PROCESS LANGUAGE. These read as ordinary English, so no identifier pattern
# catches them; review found two such phrases in the manuscript after the sweep was believed
# complete. Checked over the extracted PDF AND the released code.
# Hits are read by eye, never auto-deleted: "internally" can be legitimate in some sentences.
PROCESS_LANGUAGE = [
    ("process language",
     r"accepted internally|internal decision|our earlier internal|pending a ruling"
     r"|\ba ruling\b|\bthe ruling\b|watchdog|coordinator|paperReview|inbox|handoff|hand-off"),
]

PDF_ONLY = [
    ("internal ruling IDs in the PDF", r"D-P10-?\d*"),
    ("project-internal 'ruling' wording", r"\bruling\b"),
    ("inbox seq references", r"paperReview seq \d+"),
    # D-P10-38: drafting-file names a reader cannot open. DEVIATIONS.md is rendered as Appendix A.
    ("drafting file names in the PDF",
     # DEVIATIONS.md is REMOVED from this list: the register is now a released repository file
     # cited as such in section 6, which is exactly the exception D-P10-38 carved out. The
     # others remain drafting files a reader cannot open.
     r"DECISION-LOG\.md|RESULTS-DRAFT\.md|SECTIONS-DRAFT\.md|PREREGISTRATION-DRAFT\.md"),
]

# A superseded claim is tolerated only immediately followed by a bracketed dated note.
SUPERSEDED_NOTE = re.compile(r"\[\d{4}-\d{2}-\d{2}, superseded ")
# A disclosed correction is also an excuse: "An earlier version ... reported X", "X -> Y".
CORRECTION_CTX = re.compile(r"An earlier version|earlier version of this paper|->|was an\s+artefact")
# The register's own convention: a historical claim stays as written, with a DATED BRACKET after
# it carrying the correction. Any banned phrasing followed by such a bracket is documented history,
# not a live claim. Without this, restoring an original verbatim (which the register rules require)
# would make the sweep fail for doing the right thing.
DATED_BRACKET = re.compile(r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z[,:]")


def norm(t):
    return re.sub(r"\s+", " ", t)


def pdf_text():
    try:
        import pymupdf
        return "".join(p.get_text() for p in pymupdf.open(PDF))
    except Exception as e:
        print("  (could not read %s: %s)" % (PDF, e))
        return ""


def excused(text, end):
    """True if a bracketed dated superseded note opens within 500 chars.

    We match the note OPENING only. Requiring its closing bracket was brittle: a note longer
    than the window could not complete the match, which produced a false HIT on D-5.
    """
    window = text[max(0, end - 300):end + 500]
    return (bool(SUPERSEDED_NOTE.search(text[end:end + 500]))
            or bool(CORRECTION_CTX.search(window))
            or bool(DATED_BRACKET.search(text[end:end + 400])))


def check(name, text):
    bad = 0
    for lbl, pat in BANNED:
        hits = [m for m in re.finditer(pat, text, re.IGNORECASE)]
        live = [m for m in hits if not excused(text, m.end())]
        if live:
            bad += len(live)
            print("  HIT  %-40s %s" % (lbl, name))
            for m in live[:2]:
                print("        ...%s..." % text[max(0, m.start() - 55):m.end() + 55])
        elif hits:
            print("  ok*  %-40s %s  (%d excused by dated superseded note)"
                  % (lbl, name, len(hits)))
        else:
            print("  ok   %-40s %s" % (lbl, name))
    return bad


def selftest():
    """The whitelist must accept the noted form and reject the bare form."""
    pat = dict(BANNED)["superseded: H2 evaluated / inconclusive as a registered result"]
    bare = "The third is inconclusive, so two of the three hypotheses cannot be evaluated."
    noted = bare + " [2026-10-10, superseded for H2 by D-8: H2 is evaluated and INCONCLUSIVE.]"
    ok = True
    m = re.search(pat, bare)
    r1 = bool(m) and not excused(bare, m.end())
    print("  bare stale line is still caught        : %s" % ("PASS" if r1 else "FAIL"))
    ok &= r1
    m = re.search(pat, noted)
    r2 = bool(m) and excused(noted, m.end())
    print("  noted register line is excused         : %s" % ("PASS" if r2 else "FAIL"))
    ok &= r2
    for lbl, pat in [("scaffolding 'at the time of writing'", r"at the time of writing"),
                     ("internal ID D-P10-29", r"D-P10-?\d*")]:
        hit = re.search(pat, "Pending at the time of writing. Under ruling D-P10-29 we did x.")
        print("  %-38s : %s" % (lbl, "PASS" if hit else "FAIL"))
        ok &= bool(hit)
    # process-language selftest, both directions
    pl = dict(PROCESS_LANGUAGE)["process language"]
    for txt, want in [("it was accepted internally before any number", True),
                      ("see the watchdog note", True),
                      ("the judge scored internally consistent answers", False),
                      ("we report the conflict rate per judge", False)]:
        got = bool(re.search(pl, txt, re.IGNORECASE))
        print("  process-lang %-46s caught=%-5s want=%-5s %s"
              % (repr(txt)[:46], got, want, "PASS" if got == want else "FAIL"))
        ok &= (got == want)
    # dated-bracket selftest: a restored original WITH a dated bracket is excused; without one it is not
    cz = dict(BANNED)["conflict rate called zero"]
    bare_cz = "the conflict rate is 0.000, which follows arithmetically."
    noted_cz = ("the conflict rate is 0.000, which follows arithmetically. "
                "[2026-10-11T06:00:00Z, corrected: c is 0.018; it is c - s that is zero.]")
    for txt, want_live, lbl in [(bare_cz, True, "bare 'conflict rate is 0.000' still caught"),
                                (noted_cz, False, "dated-bracket version excused")]:
        m = re.search(cz, txt, re.IGNORECASE)
        live = bool(m) and not excused(txt, m.end())
        print("  %-44s %s" % (lbl, "PASS" if live == want_live else "FAIL"))
        ok &= (live == want_live)
    neither = "None of H1, H2 or H3 is evaluable as registered."
    r3 = re.search(pat, neither) is None
    print("  corrected wording is not matched at all: %s" % ("PASS" if r3 else "FAIL"))
    ok &= r3
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    total = 0
    blocks = 0
    failed = []
    for f in SOURCES:
        try:
            total += check("src:" + f, norm(open(f).read()))
            blocks += 1
        except Exception as e:                      # one broken block must not hide the others
            failed.append(("src:" + f, repr(e)))
    try:
        t = pdf_text()
    except Exception as e:
        failed.append(("pdf", repr(e))); t = ""
    if t:
        nt = norm(t)
        total += check("PDF:" + PDF, nt)
        blocks += 1
        for lbl, pat in PDF_ONLY + PROCESS_LANGUAGE:
            hits = list(re.finditer(pat, nt, re.IGNORECASE))
            if hits:
                total += len(hits)
                print("  HIT  %-40s PDF-only" % lbl)
                for m in hits[:2]:
                    print("        ...%s..." % nt[max(0, m.start() - 55):m.end() + 55])
            else:
                print("  ok   %-40s PDF-only" % lbl)
    for cf in CODE_FILES:
        if not os.path.exists(cf):
            continue
        blocks += 1
        ct = norm(open(cf).read())
        for lbl, pat in PROCESS_LANGUAGE:
            hits = list(re.finditer(pat, ct, re.IGNORECASE))
            if hits:
                total += len(hits)
                print("  HIT  %-40s code:%s" % (lbl, cf))
                for m in hits[:2]:
                    print("        ...%s..." % ct[max(0, m.start() - 50):m.end() + 50])
    print()
    # Status and hit count are printed SEPARATELY and on purpose. An exit code alone cannot
    # distinguish "found problems" from "the checker broke"; a crash in one scan block used to
    # surface as exit 1 and read like a finding. CHECKER STATUS says whether the sweep itself
    # completed; TOTAL STALE HITS says what it found. Exit 2 means the checker failed, 1 means
    # it ran and found something, 0 means it ran and found nothing.
    if failed:
        print("CHECKER STATUS: FAILED - %d scan block(s) did not run:" % len(failed))
        for where, err in failed:
            print("  %s: %s" % (where, err))
        print("TOTAL STALE HITS: %d (INCOMPLETE - do not treat as clean)" % total)
        sys.exit(2)
    print("CHECKER STATUS: OK (all %d scan blocks completed)" % blocks)
    print("TOTAL STALE HITS: %d" % total)
    sys.exit(1 if total else 0)
