"""Assemble build/p10.md from the sources, then build the PDF.

One transformation is applied to the APPENDIX ONLY: internal process identifiers (D-P10-nn ruling
numbers, and "ruling" phrasing that only means something inside this project) are rewritten into
plain dated internal-review wording. A ReScience reader cannot resolve "D-P10-29"; the date and the
substance are what matter to them.

DEVIATIONS.md itself is NEVER modified. It stays the dated register. Only the built text differs,
which is why this lives in the build step and not in an edit to the source.
"""
import re
import os
import subprocess
import sys

def deproject(text):
    """Strip internal ruling IDs from appendix text, keeping dates and substance."""
    t = text
    t = re.sub(r",? ?under ruling D-P10-\d+ item \(?[A-Za-z0-9]+\)?,?", "", t)
    t = re.sub(r",? ?under ruling D-P10-\d+ following review finding [A-Za-z0-9-]+", " following a referee finding", t)
    t = re.sub(r",? ?under ruling D-P10-\d+", "", t)
    t = re.sub(r"ruling D-P10-\d+ item \d+", "an internal review decision", t)
    t = re.sub(r"ruling D-P10-\d+", "an internal review decision", t)
    t = re.sub(r"D-P10-\d+ item [A-Za-z0-9()]+", "an internal review decision", t)
    t = re.sub(r"D-P10-\d+", "internal review", t)
    t = re.sub(r"paperReview seq \d+", "internal review", t)
    t = re.sub(r"\bthe ruling\b", "that decision", t)
    t = re.sub(r"\bruling\b", "internal review decision", t)
    # D-P10-38: drafting-file names must not reach a reader. DEVIATIONS.md is the register and is
    # reproduced as Appendix A, so self-reference by that name is replaced with the appendix.
    # DEVIATIONS.md is now a RELEASED repository file, not an inlined appendix, so it is
    # named directly - which D-P10-38 permits for files DATA-AVAILABILITY.md releases.
    # (Before the register was relocated, this rewrote it to "Appendix A".)
    t = re.sub(r"as recorded in DECISION-LOG\.md,?\s*", "", t)
    t = re.sub(r"\bDECISION-LOG\.md\b", "our internal decision record", t)
    t = re.sub(r"PREREGISTRATION-DRAFT\.md l\.[\d-]+", "the registered pre-registration", t)
    t = re.sub(r"\bPREREGISTRATION-DRAFT\.md\b", "the registered pre-registration", t)
    t = re.sub(r"RESULTS-DRAFT\.md section ", "section ", t)
    t = re.sub(r"\bRESULTS-DRAFT\.md\b", "the results section", t)
    t = re.sub(r"\bSECTIONS-DRAFT\.md\b", "the methods section", t)
    return t

def strip_filenames(t):
    """Drafting-file names must not reach a reader (D-P10-38). Applied to the WHOLE document,
    unlike the identifier transform, which is appendix-only."""
    # DEVIATIONS.md is now a RELEASED repository file, not an inlined appendix, so it is
    # named directly - which D-P10-38 permits for files DATA-AVAILABILITY.md releases.
    # (Before the register was relocated, this rewrote it to "Appendix A".)
    t = re.sub(r"as recorded in DECISION-LOG\.md,?\s*", "", t)
    t = re.sub(r"\bDECISION-LOG\.md\b", "our internal decision record", t)
    t = re.sub(r"PREREGISTRATION-DRAFT\.md l\.[\d-]+", "the registered pre-registration", t)
    t = re.sub(r"\bPREREGISTRATION-DRAFT\.md\b", "the registered pre-registration", t)
    t = re.sub(r"\bRESULTS-DRAFT\.md\b", "the results section", t)
    t = re.sub(r"\bSECTIONS-DRAFT\.md\b", "the methods section", t)
    return t


def main():
    sec = open("SECTIONS-DRAFT.md").read()
    sec = sec[sec.index("# 1 Introduction"):]
    intro = sec[:sec.index("# 5 Discussion")]
    disc = sec[sec.index("# 5 Discussion"):]
    res = open("RESULTS-DRAFT.md").read()
    ab = res.split("# Abstract (draft, conservative)")[1]
    ab = re.sub(r"^.*?is stated as a test of a hypothesis\.\s*", "", ab, flags=re.S)
    body = res[res.index("## 4.1"):res.index("\n---\n\n# Abstract")]
    dev = open("DEVIATIONS.md").read()
    dev = deproject(dev[dev.index("## D-1"):])          # appendix only
    hdr = ('---\ntitle: "Does positional bias in LLM-as-judge evaluation, and its calibration fix, hold for open-weight judges? A pre-registered replication halted by its own determinism control"\n'
           'author: "Veerendra Kumar Sunkavalli (Independent Researcher)"\n'
           'date: "2026-10-11"\ndocumentclass: article\nclassoption: [11pt]\n'
           'geometry: [margin=1in]\ncolorlinks: true\n---\n')
    doc = "\n".join([
        hdr,
        # m7 (D-P10-93w): a submitted article must not say it is not a submission. The banner is
        # now opt-in via P10_DRAFT_BANNER=1 for internal copies; the submission build omits it.
        ("**DRAFT, NOT A SUBMISSION.** " if os.environ.get("P10_DRAFT_BANNER") else "")
        + "Pre-registration: https://osf.io/jw59c/ "
        + "(DOI 10.17605/OSF.IO/JW59C).\n",
        "# Abstract\n\n" + ab.strip() + "\n",
        intro.strip() + "\n",
        "# 4 Results\n\n" + body.strip() + "\n",
        disc.strip() + "\n",
        "# Deviations from the registered plan\n\n"
        "Every departure from the pre-registered plan is recorded, with its date and its\n"
        "reasoning, in `DEVIATIONS.md` in the project repository released with this article\n"
        "(see Code and data availability). The register is the authoritative record: it\n"
        "holds each deviation in full, including those that correct earlier entries of its\n"
        "own, with the original wording left intact beside every correction. It is kept in\n"
        "the repository rather than inlined here so that this article stays close to the\n"
        "length of a ReScience C replication while the record itself remains complete and\n"
        "auditable.\n"])
    # Reviewer 1 (#142) found the documented build path unusable. In a fresh clone there is no
    # build/ directory, so this used to die with FileNotFoundError on the line below.
    os.makedirs("build", exist_ok=True)
    open("build/p10.md", "w").write(strip_filenames(doc))
    r = subprocess.run(["pandoc", "build/p10.md", "-o", "build/p10.pdf",
                        "--citeproc", "--bibliography=rescience-build/bibliography.bib",
                        "--pdf-engine=tectonic", "--toc"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        # A build script that reports success it did not achieve is worse than no build script.
        err = [l for l in (r.stderr or "").splitlines() if l.lower().startswith("error")][:4]
        print("BUILD FAILED, pandoc exit %d" % r.returncode)
        for l in err:
            print("  " + l)
        raise SystemExit(r.returncode)
    print("built build/p10.pdf")

if __name__ == "__main__":
    main()
