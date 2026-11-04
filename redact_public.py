#!/usr/bin/env python3
"""Produce PUBLIC copies of the verdict files with upstream text redacted.

WHY THIS EXISTS. The pre-registration states: "The original repository carries no licence file, so
this study redistributes none of its contents." The paper separately promises to release the
per-judge verdict files "with every individual sample and its raw text". Those two commitments are
in conflict, because a judge's raw output routinely quotes the question and the candidate answers
back verbatim, and those are upstream text. Releasing the raw samples as they stand would
redistribute unlicensed content and break the registration.

WHAT THIS DOES. For every sample's raw text, it finds each MAXIMAL run of consecutive words that
also appears verbatim in the upstream corpus, and replaces any run of at least THRESHOLD words with

    [upstream span redacted, sha256:<first 16 hex of the span>]

The hash lets a reader who already holds the upstream corpus confirm what was removed without us
publishing it. Originals stay local and unpublished; only the redacted copies are released.

WHAT THIS MUST NOT DO. Change any number in the paper. Every statistic is computed from the
UNREDACTED files, and --assert-stats recomputes the published quantities from both the originals
and the redacted copies and fails if any differ. Redaction touches `raw` only, never `verdict`,
`parsed`, `order`, `qid`, `arm`, `template` or any other analysed field.

Usage:
    python3 redact_public.py                 # write results-public/, report at 8 and 12 words
    python3 redact_public.py --assert-stats   # also prove no statistic moved
    python3 redact_public.py --selftest       # behavioural tests
"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Reviewer 1 (#142, 2026-11-04) could not run this without editing the module: the input
# root was hard-coded. It is now configurable, default unchanged so existing invocations work.
#   --inputs <path>   on the command line, or   P10_INPUTS=<path>   in the environment
def _input_root():
    import sys as _s
    if "--inputs" in _s.argv:
        i = _s.argv.index("--inputs")
        if i + 1 < len(_s.argv):
            return os.path.abspath(os.path.expanduser(_s.argv[i + 1]))
    return os.path.abspath(os.path.expanduser(
        os.environ.get("P10_INPUTS", "~/.cache/p10-inputs/FairEval")))
INPUTS = _input_root()
OUTDIR = os.path.join(HERE, "results-public")
THRESHOLD = 8                      # the released threshold; 12 is reported for comparison
PLACEHOLDER = "[upstream span redacted, sha256:%s]"


def upstream_texts(root=INPUTS):
    """Every question and candidate answer text from the upstream corpus."""
    out = []
    qp = os.path.join(root, "question.jsonl")
    if os.path.exists(qp):
        for line in open(qp):
            line = line.strip()
            if line:
                d = json.loads(line)
                for k in ("text", "question", "turns"):
                    v = d.get(k)
                    if isinstance(v, str):
                        out.append(v)
                    elif isinstance(v, list):
                        out.extend(x for x in v if isinstance(x, str))
    for ap in sorted(glob.glob(os.path.join(root, "answer", "*.jsonl"))):
        for line in open(ap):
            line = line.strip()
            if line:
                d = json.loads(line)
                for k in ("text", "answer", "output"):
                    v = d.get(k)
                    if isinstance(v, str):
                        out.append(v)
    return out


def _norm_words(s):
    """Lowercased word tokens, with the character span of each kept for exact replacement."""
    return [(m.group(0).lower(), m.start(), m.end()) for m in re.finditer(r"\S+", s)]


def build_index(texts, threshold):
    """Set of lowercased word-tuple n-grams of exactly `threshold` length, plus a joined corpus
    for extending a match beyond the threshold."""
    grams = set()
    joined = []
    for t in texts:
        ws = [w for w, _, _ in _norm_words(t)]
        joined.append(" ".join(ws))
        for i in range(len(ws) - threshold + 1):
            grams.add(tuple(ws[i:i + threshold]))
    return grams, "\n".join(joined)


def redact(text, grams, corpus, threshold):
    """Replace every maximal >=threshold-word upstream run. Returns (new_text, n_spans)."""
    toks = _norm_words(text)
    words = [w for w, _, _ in toks]
    n = len(words)
    out, i, spans = [], 0, 0
    last_char = 0
    while i < n:
        if i + threshold <= n and tuple(words[i:i + threshold]) in grams:
            # extend greedily while the longer phrase still occurs upstream
            j = i + threshold
            while j < n and (" ".join(words[i:j + 1]) in corpus):
                j += 1
            start_char = toks[i][1]
            end_char = toks[j - 1][2]
            span = text[start_char:end_char]
            out.append(text[last_char:start_char])
            h = hashlib.sha256(span.encode("utf-8")).hexdigest()[:16]
            out.append(PLACEHOLDER % h)
            last_char = end_char
            spans += 1
            i = j
        else:
            i += 1
    out.append(text[last_char:])
    return "".join(out), spans


def count_affected(threshold, texts=None):
    """How many samples contain at least one >=threshold-word upstream span, per judge file."""
    texts = texts or upstream_texts()
    grams, corpus = build_index(texts, threshold)
    per = {}
    for f in sorted(glob.glob(os.path.join(HERE, "results", "verdicts_*.json"))):
        d = json.load(open(f))
        tot = hit = 0
        for v in d["verdicts"]:
            for s in v.get("samples", []):
                tot += 1
                _, k = redact(s.get("raw", ""), grams, corpus, threshold)
                if k:
                    hit += 1
        per[os.path.basename(f)] = (hit, tot)
    return per


def write_public():
    texts = upstream_texts()
    grams, corpus = build_index(texts, THRESHOLD)
    os.makedirs(OUTDIR, exist_ok=True)
    written, spans_total, samples_touched = [], 0, 0
    for f in sorted(glob.glob(os.path.join(HERE, "results", "verdicts_*.json"))):
        d = json.load(open(f))
        for v in d["verdicts"]:
            for s in v.get("samples", []):
                new, k = redact(s.get("raw", ""), grams, corpus, THRESHOLD)
                if k:
                    s["raw"] = new
                    spans_total += k
                    samples_touched += 1
        d["_redaction"] = {
            "reason": "the upstream corpus carries no licence; the pre-registration states this "
                      "study redistributes none of its contents",
            "rule": "every maximal run of >=%d consecutive words occurring verbatim in the upstream "
                    "questions or candidate answers is replaced by a placeholder carrying the "
                    "sha256 prefix of the removed span" % THRESHOLD,
            "fields_touched": ["verdicts[].samples[].raw"],
            "fields_untouched": ["verdict", "parsed", "order", "qid", "arm", "template", "k",
                                 "seed_block", "temperature", "r1_sha", "r2_sha"],
            "statistics_unaffected": "every number in the paper is computed from the UNREDACTED "
                                     "files; redact_public.py --assert-stats proves equality",
        }
        out = os.path.join(OUTDIR, os.path.basename(f))
        json.dump(d, open(out, "w"), indent=1)
        written.append(os.path.basename(f))
    return written, samples_touched, spans_total


def assert_stats():
    """Recompute the published quantities from the originals and from the redacted copies and
    require exact equality. Redaction must be statistically invisible."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("am", os.path.join(HERE, "analyze_mec.py"))
    am = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(am)

    def snapshot(results_dir):
        real, am.HERE = am.HERE, results_dir
        try:
            h = {k: round(v["stat"], 12) for k, v in am.h2(verbose=False).items()}
            cb = [(r[0], r[1], round(r[3], 12), round(r[4], 12))
                  for r in am.content_blind(verbose=False)]
            cs = [(r[0], r[1], r[2], round(r[5], 12)) for r in am.cs_intervals(verbose=False)]
        finally:
            am.HERE = real
        return h, cb, cs

    # analyze_mec globs HERE/results, so point HERE at a dir whose results/ is the redacted set
    import tempfile
    shadow = tempfile.mkdtemp()
    os.symlink(OUTDIR, os.path.join(shadow, "results"))
    a = snapshot(HERE)
    b = snapshot(shadow)
    names = ("H2 signed", "content-blind gaps", "c-s")
    bad = [n for n, x, y in zip(names, a, b) if x != y]
    for n, x, y in zip(names, a, b):
        print("  %-20s identical: %s" % (n, x == y))
    return 0 if not bad else 1


def selftest():
    ok = True
    texts = ["the quick brown fox jumps over the lazy dog and keeps running onward"]
    grams, corpus = build_index(texts, 8)
    cases = [
        ("a judge echoing the quick brown fox jumps over the lazy dog and keeps running onward here",
         True, "long verbatim echo is redacted"),
        ("the quick brown fox", False, "a 4-word echo is below threshold and kept"),
        ("Assistant 1 scored higher because its answer was more complete and accurate overall",
         False, "the judge's own prose is untouched"),
    ]
    for txt, want_redacted, lbl in cases:
        new, k = redact(txt, grams, corpus, 8)
        got = k > 0
        print("  %-46s %s" % (lbl, "PASS" if got == want_redacted else "FAIL"))
        ok &= (got == want_redacted)
    # D-P10-91w: the planted-hit test the reply mentions is now part of --selftest, so the claim
    # "it fails on a file that does carry upstream text" is checked on every run rather than once.
    import json as _j, glob as _g, subprocess as _sp, tempfile as _tf
    planted = None
    for f in _g.glob(os.path.join(HERE, "results", "verdicts_*.json")):
        d = _j.load(open(f))
        if "_redaction" in d:
            continue
        g8, c8 = build_index(upstream_texts(), 8)
        for v in d["verdicts"]:
            for smp in v.get("samples", []):
                if redact(smp.get("raw", ""), g8, c8, 8)[1] >= 1:
                    planted = smp["raw"]; break
            if planted: break
        if planted: break
    if planted:
        tmp = os.path.join(_tf.mkdtemp(), "planted.txt")
        open(tmp, "w").write(planted)
        r = _sp.run([sys.executable, os.path.abspath(__file__), "--scan", tmp],
                    capture_output=True, text=True)
        fired = r.returncode == 1
        print("  %-46s %s" % ("--scan fires on a planted upstream span", "PASS" if fired else "FAIL"))
        ok &= fired
    else:
        print("  %-46s SKIP (no unredacted sample available)" % "--scan planted-hit test")
    r0 = _sp.run([sys.executable, os.path.abspath(__file__), "--scan"], capture_output=True, text=True)
    refused = r0.returncode == 2
    print("  %-46s %s" % ("--scan refuses an empty file list", "PASS" if refused else "FAIL"))
    ok &= refused
    _env = dict(os.environ); _env["P10_INPUTS"] = "/nonexistent-corpus"
    r1 = _sp.run([sys.executable, os.path.abspath(__file__), "--scan", os.path.abspath(__file__)],
                 capture_output=True, text=True, env=_env)
    refused2 = r1.returncode == 2
    print("  %-46s %s" % ("--scan refuses an empty upstream corpus", "PASS" if refused2 else "FAIL"))
    ok &= refused2

    # the placeholder must carry a hash and must not leak the span
    new, _ = redact(texts[0] + " tail", grams, corpus, 8)
    leaked = "quick brown fox jumps over the lazy dog" in new
    print("  %-46s %s" % ("redacted output does not leak the span", "PASS" if not leaked else "FAIL"))
    ok &= not leaked
    print("  %-46s %s" % ("placeholder carries a sha256 prefix",
                          "PASS" if re.search(r"sha256:[0-9a-f]{16}", new) else "FAIL"))
    ok &= bool(re.search(r"sha256:[0-9a-f]{16}", new))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    if "--scan" in sys.argv:
        # Reviewer 1 (#142) asked us to show, not assert, that a released file carries no upstream
        # text. Scan any file or directory and report spans at both thresholds. Exit 1 on any hit.
        import glob as _g
        args = sys.argv[sys.argv.index("--scan") + 1:]
        paths = []
        for a in args:
            if os.path.isdir(a):
                paths += [p for p in _g.glob(os.path.join(a, "**", "*"), recursive=True)
                          if os.path.isfile(p)]
            else:
                paths += _g.glob(a)
        if not paths:
            # D-P10-91w: with no arguments this printed "scanning 0 file(s)" and then CLEAN, exit 0.
            # A scan of nothing must never report clean: a false zero from a safety check is worse
            # than no check, because it is indistinguishable from a real pass.
            print("REFUSED: no files given. A scan of zero files is not a pass.")
            print("usage: redact_public.py --scan <path> [path ...]")
            raise SystemExit(2)
        texts = upstream_texts()
        # D-P10-93w M6: with no upstream corpus loaded this reported CLEAN, exit 0, which is
        # meaningless - every comparison is against an empty set. A safety check must refuse when
        # EITHER side is empty: zero files to scan, or zero texts to scan against.
        if not texts:
            print("REFUSED: 0 upstream texts loaded from %s" % INPUTS)
            print("A scan against an empty corpus is not a pass. Pass --inputs <path> or set")
            print("P10_INPUTS to a verified FairEval checkout; see the README.")
            raise SystemExit(2)
        bad = 0
        print("scanning %d file(s) against %d upstream text(s)" % (len(paths), len(texts)))
        for th in (8, 12):
            grams, corpus = build_index(texts, th)
            for p in paths:
                try:
                    blob = open(p, errors="replace").read()
                except Exception as e:
                    print("  %-56s UNREADABLE (%s)" % (p, e)); continue
                _, n = redact(blob, grams, corpus, th)
                if n:
                    bad += 1
                print("  >=%2d words  %-50s %d span(s)" % (th, os.path.basename(p), n))
        print("\n%s" % ("CLEAN: no upstream spans at either threshold" if not bad
                         else "HITS: %d file/threshold combinations carry upstream text" % bad))
        raise SystemExit(1 if bad else 0)
    print("upstream texts: %d" % len(upstream_texts()))
    for th in (8, 12):
        per = count_affected(th)
        tot_h = sum(h for h, _ in per.values())
        tot_n = sum(n for _, n in per.values())
        print("\nsamples containing a >=%d-word verbatim upstream span:" % th)
        for k, (h, n) in per.items():
            print("  %-46s %4d / %4d" % (k, h, n))
        print("  %-46s %4d / %4d" % ("TOTAL", tot_h, tot_n))
    w, touched, spans = write_public()
    print("\nwrote %d public file(s) to results-public/" % len(w))
    print("  samples redacted: %d   spans removed: %d  (threshold %d words)"
          % (touched, spans, THRESHOLD))
    if "--assert-stats" in sys.argv:
        print("\nstatistics computed from originals vs redacted copies:")
        raise SystemExit(assert_stats())
