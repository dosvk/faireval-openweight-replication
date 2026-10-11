"""Hydrate the FairEval inputs locally (the originals are NOT redistributable).

The original repository https://github.com/i-Eval/FairEval carries NO licence (GitHub API
`license: null`; no LICENSE file at the pinned commit), so this replication's Zenodo artefact
ships only our own code, our regenerated candidate answers and our own judge verdicts. The
original question set, candidate answers and the 80 human win/tie/lose labels are FETCHED BY THE
READER at run time from the original public repository, pinned by commit and verified by checksum.
Pattern follows paper6-c7/artifact/rehydrate_asap.py (D-P10-02, 2026-10-09).

1. Clone the pinned commit:
     git clone https://github.com/i-Eval/FairEval.git
     cd FairEval && git checkout 453c117a69159fd7b7de2f4e0519bac57bee21f4
2. Verify and report:
     python hydrate_faireval.py path/to/FairEval
3. Every file must verify before any judge run. A mismatch is a hard stop, not a warning:
   it means the upstream artefact changed and the replication's inputs are no longer the ones
   the pre-registration named.

Checksums were computed on 2026-10-09 from the pinned commit, which was also the remote HEAD on
that date (`git ls-remote https://github.com/i-Eval/FairEval.git HEAD` ->
453c117a69159fd7b7de2f4e0519bac57bee21f4).
"""
import sys
import os
import hashlib

PIN = "453c117a69159fd7b7de2f4e0519bac57bee21f4"

EXPECTED = {
    "question.jsonl":
        ("32b519315704d3da88accb0cab4fd44622ff530fe49e450c1553030ce3e0f962", 12884,
         "80 Vicuna-benchmark questions (question_id/text/category)"),
    "answer/answer_gpt35.jsonl":
        ("c6545739b0738eba5f9348e77f680031aec076a72ecba71b3014e7b1b0dfe099", 107603,
         "ChatGPT candidate answers, 80 records"),
    "answer/answer_vicuna-13b.jsonl":
        ("d1a4b3a5d2e3ca90d2d55084ee25d4d90e63e65ac647bf50359da8633e16d0b8", 131904,
         "Vicuna-13B candidate answers, 80 records"),
    "answer/answer_alpaca-13b.jsonl":
        ("50a6a9274da00cc74e8b3a8e3e92be2ba23ed6f2bf6ae9bbcc3082424acea540", 57071,
         "Alpaca-13B candidate answers, 80 records"),
    "answer/answer_gpt-4.jsonl":
        ("3b554c1a9d9f3c9df105f6f04a3c4890705cfab10f854cc010f4fa550874d7c3", 176138,
         "GPT-4 candidate answers, 80 records"),
    "review/review_gpt35_vicuna-13b_human.txt":
        ("929f14e6582a7d14b1a3d189d29bc1319200588298e4b5429f7ac56bf847d224", 633,
         "the 80 human win/tie/lose labels: CHATGPT 41 / TIE 14 / VICUNA13B 25"),
}


def main(root):
    print("FairEval hydration check")
    print("  pinned commit: %s" % PIN)
    print("  root:          %s" % root)
    bad = []
    for rel, (want, size, what) in sorted(EXPECTED.items()):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            print("  MISSING  %-44s %s" % (rel, what))
            bad.append(rel)
            continue
        blob = open(path, "rb").read()
        got = hashlib.sha256(blob).hexdigest()
        ok = (got == want and len(blob) == size)
        print("  %-8s %-44s %s" % ("OK" if ok else "MISMATCH", rel, what))
        if not ok:
            print("           expected %s (%d bytes)" % (want, size))
            print("           got      %s (%d bytes)" % (got, len(blob)))
            bad.append(rel)
    if bad:
        raise SystemExit(
            "HARD STOP: %d file(s) failed verification: %s\n"
            "The upstream artefact is not the one the pre-registration named. Do not run judges.\n"
            "Check out the pinned commit %s, or if the repository has changed or disappeared, stop "
            "and escalate (D-P10-02 names falling back to target C3 in that case)."
            % (len(bad), ", ".join(bad), PIN))
    print("all %d input files verified against the pinned commit" % len(EXPECTED))
    print("REMINDER: these files stay where they are. They are read, never copied into our "
          "artefact, and never redistributed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
