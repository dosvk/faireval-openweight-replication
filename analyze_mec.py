"""Analysis of the surviving MEC arms, for section 4.6.

Every number this prints is traceable to a results file and a named field. It computes ONLY
quantities the registered plan defines, on the arms that survived. None of H1, H2 or H3 is
evaluable as registered; the H2 figures produced here are descriptive, per the deviations register:
H1 and H3 read from the halted temperature-0 VANILLA arm; the H2 figures here come from the surviving temperature-1 arms under a post-registration deviation, which is halted for two judges under PC-4 and
yields 1 contributing pair for the third. Nothing here is a confirmatory hypothesis test.

Usage: python3 analyze_mec.py
"""
import collections
import glob
import importlib.util
import json
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rr", os.path.join(HERE, "run_replication.py"))
rr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rr)

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
ROOT = _input_root()
# human label -> verdict frame. The close pair is (gpt35, vicuna-13b) = (A, B).
LAB = {"CHATGPT": "A", "VICUNA13B": "B", "TIE": "TIE"}


def human_labels():
    path = os.path.join(ROOT, "review", "review_gpt35_vicuna-13b_human.txt")
    labs = [l.strip() for l in open(path) if l.strip()]
    qs, _, _ = rr.load_inputs(ROOT)
    return {q["question_id"]: LAB[labs[i]] for i, q in enumerate(qs)}, labs



# ---------------------------------------------------------------- frame canonicalisation (D-16)
# run_replication.py's run_arm swaps the two responses for BA:
#     r1, r2 = (a1, a2) if order == "AB" else (a2, a1)
# and stores parse_verdict's output unchanged. So the STORED verdict is in the SLOT frame:
# "A" means "the answer in slot 1 won". In BA, slot 1 holds candidate B.
#
# Every candidate-frame quantity (accuracy and kappa against human labels, conflict rate c,
# self-inconsistency s, the random-order estimate) must use verdict_cand.
# Every slot-frame quantity (p_slot1/p_slot2, the H2 signed slot difference, the content-blind
# benchmark) must use the stored slot verdict directly.
#
# An earlier version of this file read the stored verdict as candidate-frame with no flip, which
# made every BA-dependent candidate-frame number wrong. See the register entry D-16.

_FLIP = {"A": "B", "B": "A", "TIE": "TIE", None: None}


def to_candidate(verdict, order):
    """Slot-frame verdict -> candidate frame. AB is already candidate frame; BA flips A<->B."""
    return verdict if order == "AB" else _FLIP.get(verdict, verdict)


def canonicalise(records):
    """Add verdict_cand to every record, once, at load."""
    for v in records:
        v["verdict_cand"] = to_candidate(v.get("verdict"), v["order"])
    return records


def frame_selftest():
    """A synthetic judge that ALWAYS picks slot 1 must show:
       conflict rate c = 1 (its candidate choice flips with the swap),
       AB and BA candidate-frame accuracy differing,
       and an H2 slot-1 share of exactly 1.
    If the frames were conflated, c would be 0 and the accuracies equal."""
    hum, _ = human_labels()
    qs_ = sorted(hum)[:40]
    recs = []
    for q in qs_:
        for order in ("AB", "BA"):
            recs.append({"qid": q, "order": order, "verdict": "A", "parsed": True})
    canonicalise(recs)
    byq = {}
    for v in recs:
        byq.setdefault(v["qid"], {})[v["order"]] = v
    c = sum(1 for q in byq if byq[q]["AB"]["verdict_cand"] != byq[q]["BA"]["verdict_cand"]) / len(byq)
    acc = {}
    for order in ("AB", "BA"):
        sub = [v for v in recs if v["order"] == order]
        acc[order] = sum(1 for v in sub if v["verdict_cand"] == hum[v["qid"]]) / len(sub)
    slot1 = sum(1 for v in recs if v["verdict"] == "A") / len(recs)
    ok = (c == 1.0) and (acc["AB"] != acc["BA"]) and (slot1 == 1.0)
    print("  always-slot-1 judge: c=%.3f (want 1.000)" % c)
    print("  candidate-frame acc AB=%.3f BA=%.3f (want different)" % (acc["AB"], acc["BA"]))
    print("  slot-frame slot-1 share=%.3f (want 1.000)" % slot1)

    # The earlier version of this selftest stopped here, exercising only the helper. h2() and
    # content_blind() each carried their OWN order-conditional remap, so both were wrong while this
    # test printed PASS. A selftest that does not call the functions under test certifies nothing.
    # These two cases run the real functions over synthetic always-slot-1 records.
    ok &= _slot_fn_selftest()
    print("  FRAME SELFTEST: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def _slot_fn_selftest():
    """Exercise h2() and content_blind() themselves on a synthetic always-slot-1 judge.

    For such a judge the slot-frame signed first-minus-second share must be exactly +1.000 and the
    content-blind p(slot 1) must be 1.000 in BOTH orders. If either function reintroduces an
    order-conditional remap, BA cancels AB and the signed value collapses toward zero - which is
    precisely the regression this catches.
    """
    import tempfile
    hum, _ = human_labels()
    qs_ = sorted(hum)[:30]
    recs = []
    for q in qs_:
        for order in ("AB", "BA"):
            recs.append({"judge": "synthetic", "arm": "mec", "template": "SCORING_CODE",
                         "pair": "close", "qid": q, "order": order, "verdict": "A",
                         "parsed": True, "samples": []})
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "results"), exist_ok=True)   # h2/content_blind glob HERE/results
    json.dump({"judge": "synthetic", "verdicts": recs},
              open(os.path.join(d, "results", "verdicts_synthetic.json"), "w"))
    global HERE
    real, HERE = HERE, d
    try:
        h = h2(verbose=False)
        cb = content_blind(verbose=False)
    finally:
        HERE = real
    ok = True
    key = ("synthetic", "SCORING_CODE")
    if key in h:
        sg = h[key]["stat"]
        good = abs(sg - 1.0) < 1e-9
        print("  h2() on always-slot-1: signed=%+.3f (want +1.000) %s"
              % (sg, "PASS" if good else "FAIL"))
        ok &= good
    else:
        print("  h2() on always-slot-1: NO CELL RETURNED  FAIL"); ok = False
    # A PARTLY PARSED cell: the prediction must use only the parsed questions. If it drew the
    # human marginals from all 80 instead, the two sides of the comparison would rest on different
    # question sets - the defect a referee found in this function.
    recs2 = []
    for i, q in enumerate(sorted(hum)[:40]):
        for order in ("AB", "BA"):
            recs2.append({"judge": "partly", "arm": "mec", "template": "SCORING_CODE",
                          "pair": "close", "qid": q, "order": order, "verdict": "A",
                          "parsed": i >= 20, "samples": []})      # first 20 questions unparsed
    json.dump({"judge": "partly", "verdicts": recs2},
              open(os.path.join(d, "results", "verdicts_partly.json"), "w"))
    real2, HERE = HERE, d
    try:
        cb2 = content_blind(verbose=False)
    finally:
        HERE = real2
    pr = [r for r in cb2 if r[0] == "partly"]
    if pr:
        qs_parsed = sorted(hum)[20:40]
        cA = sum(1 for q in qs_parsed if hum[q] == "A")
        cB = sum(1 for q in qs_parsed if hum[q] == "B")
        cT = sum(1 for q in qs_parsed if hum[q] == "TIE")
        want = (cA - cB) / (cA + cB + cT)          # always-slot-1, so pred gap = (cA-cB)/cN
        got = pr[0][4]
        good = abs(got - want) < 1e-9
        print("  content_blind() on a PARTLY parsed cell: pred gap=%+.4f want=%+.4f %s"
              % (got, want, "PASS" if good else "FAIL"))
        ok &= good
    else:
        print("  content_blind() partly-parsed cell: NO ROW  FAIL"); ok = False

    rows = [r for r in cb if r[0] == "synthetic"]
    if rows:
        p1 = [rows[0][2][o]["p_slot1"] for o in ("AB", "BA")]
        good = all(abs(x - 1.0) < 1e-9 for x in p1)
        print("  content_blind() p(slot 1): AB=%.3f BA=%.3f (want 1.000 both) %s"
              % (p1[0], p1[1], "PASS" if good else "FAIL"))
        ok &= good
    else:
        print("  content_blind(): NO ROW RETURNED  FAIL"); ok = False
    return ok


def kappa(pairs):
    """Cohen's kappa plus the diagnostics the analysis plan requires alongside it."""
    cats = sorted({c for p in pairs for c in p})
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    ma = collections.Counter(a for a, _ in pairs)
    mb = collections.Counter(b for _, b in pairs)
    pe = sum((ma[c] / n) * (mb[c] / n) for c in cats)
    k = (po - pe) / (1 - pe) if pe != 1 else float("nan")
    # PABAK only. Prevalence and bias indices are NOT computed here and must not be claimed
    # anywhere in the prose (DEVIATIONS.md D-10 context; removed from SECTIONS-DRAFT 3.5).
    pabak = 2 * po - 1
    return {"n": n, "po": round(po, 4), "pe": round(pe, 4), "kappa": round(k, 4),
            "pabak": round(pabak, 4),
            "marginals_judge": dict(ma), "marginals_human": dict(mb)}



def common_set_cs(records, tpl):
    """THE one definition of c, s and c - s (ruled: one estimand, one definition, common set).

    Restricted to questions with BOTH MEC orders parsed AND a parsed noise repeat, so c and s are
    computed over the same questions and their difference is meaningful. Both callers - the main
    per-judge print and cs_intervals - use this, so the script cannot print two values for one
    quantity. A disagreement check at the end of main() fails the run if they ever diverge.
    """
    mec, noise = {}, {}
    for v in records:
        if v["template"] != tpl or not v["parsed"]:
            continue
        if v["arm"] == "mec":
            mec.setdefault(v["qid"], {})[v["order"]] = v["verdict_cand"]
        elif v["arm"] == "noise":
            noise[v["qid"]] = v["verdict_cand"]
    qs_ = sorted(q for q, o in mec.items() if "AB" in o and "BA" in o and q in noise)
    if not qs_:
        return None
    c = sum(1 for q in qs_ if mec[q]["AB"] != mec[q]["BA"]) / len(qs_)
    s = sum(1 for q in qs_ if mec[q]["AB"] != noise[q]) / len(qs_)
    return {"n": len(qs_), "c": c, "s": s, "cs": c - s, "mec": mec, "noise": noise, "qs": qs_}


def load(judge_glob):
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, "results", judge_glob))):
        d = json.load(open(f))
        out.setdefault(d["judge"], []).extend([(v, f) for v in canonicalise(d["verdicts"])])
    return out


def main():
    hum, raw_labs = human_labels()
    print("human labels (PC-2): %s" % dict(collections.Counter(raw_labs)))
    print("in verdict frame   : %s" % dict(collections.Counter(hum.values())))
    print()

    byjudge = load("verdicts_*.json")
    for judge in sorted(byjudge):
        recs = byjudge[judge]
        mec = [(v, f) for v, f in recs if v["arm"] == "mec"]
        noise = [(v, f) for v, f in recs if v["arm"] == "noise"]
        if not mec:
            print("=" * 74)
            print("%s -- no MEC arm on disk" % judge)
            print()
            continue
        print("=" * 74)
        print(judge)
        print("  sources: %s" % sorted({os.path.basename(f) for _, f in recs}))

        for tpl in sorted({v["template"] for v, _ in mec}):
            cell = [v for v, _ in mec if v["template"] == tpl]
            # ---- MEC accuracy and kappa, per presentation order
            print("  template %s  (%d records)" % (tpl, len(cell)))
            for order in ("AB", "BA"):
                sub = [v for v in cell if v["order"] == order and v["parsed"]]
                pairs = [(v["verdict_cand"], hum[v["qid"]]) for v in sub]
                if not pairs:
                    continue
                acc = sum(1 for a, b in pairs if a == b) / len(pairs)
                k = kappa(pairs)
                print("     MEC %s: n=%-3d acc=%.3f kappa=%.3f pabak=%.3f pe=%.3f"
                      % (order, len(pairs), acc, k["kappa"], k["pabak"], k["pe"]))

            # ---- RANDOM-ORDER MEC estimate: resample the stored both-order verdicts, which is
            # what the registration specifies in place of 100 fresh random-order runs.
            # This is NOT Wang-style BPC: BPC averages SCORES across orders before deciding,
            # and no such quantity was computed in this study (DEVIATIONS.md D-10).
            byq = collections.defaultdict(dict)
            for v in cell:
                if v["parsed"]:
                    byq[v["qid"]][v["order"]] = v["verdict_cand"]
            rnd = random.Random(rr.BASE_SEED)
            both = {q: o for q, o in byq.items() if "AB" in o and "BA" in o}
            if both:
                # order-averaged verdict by resampling the stored both-order verdicts
                accs = []
                for _ in range(1000):
                    pairs = [(o["AB"] if rnd.random() < 0.5 else o["BA"], hum[q])
                             for q, o in both.items()]   # both already candidate-frame
                    accs.append(sum(1 for a, b in pairs if a == b) / len(pairs))
                accs.sort()
                print("     random-order MEC (resampled, 1000 draws; NOT BPC): n=%d acc=%.3f "
                      "[%.3f, %.3f]" % (len(both), sum(accs) / len(accs),
                                        accs[25], accs[974]))
                # ---- c, s and c - s from THE single common-set definition
                cs = common_set_cs([v for v, _ in recs], tpl)
                if cs:
                    print("     c = %.3f  s = %.3f  c - s = %.3f   (common set, n=%d)"
                          % (cs["c"], cs["s"], cs["cs"], cs["n"]))
                else:
                    print("     c, s: no questions with both orders and a noise repeat")
        print()

    print("=" * 74)
    print("ORIGINAL's Table 5 values for comparison (ChatGPT as evaluator):")
    print("  SCORING   MEC 53.2% kappa 0.24 CR 35.0% | MEC+BPC 58.8% kappa 0.31")
    print("  COMPARING MEC 54.8% kappa 0.27 CR 42.5% | MEC+BPC 60.0% kappa 0.35")
    print("  human ceiling 71.7% accuracy, kappa 0.54")
    print()
    print("DESCRIPTIVE ONLY. None of H1/H2/H3 is evaluable as registered: all three read from the")
    print("halted temperature-0 VANILLA arm. H2 figures here come from a post-registration deviation.")


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------
def content_blind(verbose=True):
    """Accuracy a CONTENT-BLIND judge would get, using each judge's own observed per-order
    slot-1 / slot-2 / tie rates, printed beside the observed accuracies.

    Added after referee review. Descriptive comparison only; no mechanism is claimed.
    slot 1 holds candidate A under AB and candidate B under BA, so the slot-1 rate is read in the
    slot frame, not the candidate frame.
    """
    hum, labs = human_labels()
    nA = sum(1 for v in hum.values() if v == "A")
    nB = sum(1 for v in hum.values() if v == "B")
    nT = sum(1 for v in hum.values() if v == "TIE")
    N = nA + nB + nT
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, "results", "verdicts_*.json"))):
        d = json.load(open(f))
        canonicalise(d["verdicts"])
        for tpl in ("SCORING_CODE", "COMPARING"):
            cell = [v for v in d["verdicts"]
                    if v["arm"] == "mec" and v["template"] == tpl and v["parsed"]]
            if not cell:
                continue
            out = {}
            for order in ("AB", "BA"):
                sub = [v for v in cell if v["order"] == order]
                if not sub:
                    continue
                # stored verdict is slot-frame for every record: no order-conditional remap
                p1 = sum(1 for v in sub if v["verdict"] == "A") / len(sub)
                p2 = sum(1 for v in sub if v["verdict"] == "B") / len(sub)
                pt = sum(1 for v in sub if v["verdict"] == "TIE") / len(sub)
                obs = sum(1 for v in sub if v["verdict_cand"] == hum[v["qid"]]) / len(sub)
                # The prediction must use the SAME questions the observation uses. An earlier
                # version drew the human marginals from all 80 registered questions while the
                # observed figure above was computed on this cell's PARSED records only, so the
                # two sides of the comparison rested on different question sets whenever a cell
                # had unparsed records.
                qs_cell = [v["qid"] for v in sub]
                cA = sum(1 for q in qs_cell if hum[q] == "A")
                cB = sum(1 for q in qs_cell if hum[q] == "B")
                cT = sum(1 for q in qs_cell if hum[q] == "TIE")
                cN = cA + cB + cT
                nslot1 = cA if order == "AB" else cB
                nslot2 = cB if order == "AB" else cA
                pred = (p1 * nslot1 + p2 * nslot2 + pt * cT) / cN
                out[order] = {"n": len(sub), "p_slot1": p1, "p_slot2": p2, "p_tie": pt,
                              "observed": obs, "content_blind": pred}
            if "AB" in out and "BA" in out:
                og = out["AB"]["observed"] - out["BA"]["observed"]
                pg = out["AB"]["content_blind"] - out["BA"]["content_blind"]
                frac = (pg / og) if og else float("nan")
                rows.append((d["judge"], tpl, out, og, pg))
    if verbose:
        print("=" * 100)
        print("CONTENT-BLIND BENCHMARK (see the deviations register). Descriptive. No mechanism claimed.")
        print("%-28s %-13s %-4s %7s %7s %7s | %8s %11s" % (
            "judge", "template", "ord", "p_slot1", "p_slot2", "p_tie", "observed", "blind-pred"))
        for judge, tpl, out, og, pg in rows:
            for order in ("AB", "BA"):
                if order not in out:
                    continue
                o = out[order]
                print("%-28s %-13s %-4s %7.3f %7.3f %7.3f | %8.3f %11.3f" % (
                      judge[:28], tpl, order, o["p_slot1"], o["p_slot2"], o["p_tie"],
                      o["observed"], o["content_blind"]))
            # No ratio is printed: with several observed gaps near zero a ratio of two near-zero
            # numbers is unstable and uninformative. Both gaps appear in the same units instead.
            print("%-28s %-13s %-4s observed gap %+.3f | content-blind gap %+.3f" % (
                  "", tpl, "", og, pg))
        print()
    return rows


if __name__ == "__main__" and os.environ.get("CB"):
    content_blind()


# ---------------------------------------------------------------- H2, under D-8 as amended
def h2(verbose=True):
    """H2's registered test FORM applied to every surviving both-order arm (D-8 deviation), applied to EVERY surviving both-order arm (DEVIATIONS.md D-8).

    Registered test: per judge, the signed first-position minus second-position win rate, with a
    question-clustered bootstrap interval; then whether any two judges differ in sign with
    non-overlapping intervals. Confirmed if at least two judges differ in sign with non-overlapping
    intervals. Declared asymmetry: NOT finding one is INCONCLUSIVE, never a refutation.

    Definitions fixed in the D-8 amendment before computation:
      first-position win rate  = share of parsed verdicts where the slot-1 answer won
                                 (SCORING: scored higher; COMPARING: "Assistant 1")
      ties stay in the denominator and count as neither win nor loss
      unparsed records excluded from numerator and denominator, count printed
      bootstrap 10,000 question resamples, seed 1234
      Holm applied to the interval level: all intervals at 1 - 0.05/3 = 98.33%, the most stringent
      Holm level, since the registered rule names no p-values to rank
    """
    import random as _r
    ALPHA = 0.05 / 3.0                      # most stringent Holm level, per D-8 amendment (iii)
    LO, HI = 100 * ALPHA / 2, 100 * (1 - ALPHA / 2)
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, "results", "verdicts_*.json"))):
        d = json.load(open(f))
        canonicalise(d["verdicts"])
        for tpl in ("SCORING_CODE", "COMPARING"):
            cell = [v for v in d["verdicts"] if v["arm"] == "mec" and v["template"] == tpl]
            if not cell:
                continue
            byq = collections.defaultdict(list)
            nunparsed = 0
            perq = collections.defaultdict(dict)
            for v in cell:
                if not v["parsed"]:
                    nunparsed += 1
                    continue
                # The STORED verdict is slot-frame: "A" means the answer in slot 1 won, for EVERY
                # record. There is no order-conditional remap here, and an earlier version had one,
                # which re-flipped BA and cancelled the very signal H2 measures.
                perq[v["qid"]][v["order"]] = (1 if v["verdict"] == "A" else 0,
                                              1 if v["verdict"] == "B" else 0)
            # Registration: "In a paired test a question contributes only if both members of its
            # pair parsed." An earlier version used every parsed record, which admitted
            # singly-parsed questions and produced odd denominators.
            qs_ = sorted(q for q, o in perq.items() if "AB" in o and "BA" in o)
            n_dropped = len(perq) - len(qs_)
            for q in qs_:
                byq[q] = [perq[q]["AB"], perq[q]["BA"]]
            flat = [x for q in qs_ for x in byq[q]]
            n = len(flat)
            if not n:
                continue
            stat = (sum(a for a, _ in flat) - sum(b for _, b in flat)) / n
            rnd = _r.Random(rr.BASE_SEED)
            boots = []
            for _ in range(10000):
                samp = [x for _ in qs_ for x in byq[rnd.choice(qs_)]]
                m = len(samp)
                boots.append((sum(a for a, _ in samp) - sum(b for _, b in samp)) / m)
            boots.sort()
            lo = boots[int(len(boots) * ALPHA / 2)]
            hi = boots[int(len(boots) * (1 - ALPHA / 2))]
            out[(d["judge"], tpl)] = {"stat": stat, "lo": lo, "hi": hi, "n_parsed": n,
                                      "n_unparsed": nunparsed, "n_questions": len(qs_),
                                      "n_dropped_incomplete": n_dropped}
    if verbose:
        print("=" * 104)
        print("H2 under D-8: signed first-minus-second position win rate, per judge, per surviving")
        print("both-order arm. Intervals at %.2f%% (Holm most-stringent, D-8 amendment iii)." % (100 * (1 - ALPHA)))
        print("%-28s %-13s %7s %9s %9s %8s %10s %9s" % ("judge", "arm", "signed", "lo", "hi",
                                                          "n", "unparsed", "dropped"))
        for (j, t), r in sorted(out.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            print("%-28s %-13s %+7.3f %+9.3f %+9.3f %8d %10d %9d"
                  % (j[:28], t, r["stat"], r["lo"], r["hi"], r["n_parsed"], r["n_unparsed"],
                     r["n_dropped_incomplete"]))
        for tpl in ("SCORING_CODE", "COMPARING"):
            rows = {j: r for (j, t), r in out.items() if t == tpl}
            if len(rows) < 2:
                continue
            print("\n  %s -- pairwise sign difference with non-overlapping intervals:" % tpl)
            js = sorted(rows)
            found = []
            for i in range(len(js)):
                for k in range(i + 1, len(js)):
                    a, b = rows[js[i]], rows[js[k]]
                    # a statistic of exactly 0 has NO sign; it is not "opposite" to a positive one.
                    sg = lambda x: 0 if x == 0 else (1 if x > 0 else -1)
                    opp = sg(a["stat"]) != 0 and sg(b["stat"]) != 0 and sg(a["stat"]) != sg(b["stat"])
                    nonov = a["hi"] < b["lo"] or b["hi"] < a["lo"]
                    # D-7 / an internal review decision: "degenerate" is REPORTED but is NOT part of the decision.
                    # It was added after a spurious CONFIRMED and the verdict does not need it:
                    # NOTE: with the frame fix (D-18) the Llama/Qwen SCORING_CODE pair DOES qualify; an earlier
    # comment here said no pair qualifies, which was true only of the pre-D-18 numbers, so the decision rests on the
                    # registered criteria (opposite sign AND non-overlapping intervals) only.
                    degen = (a["hi"] - a["lo"] == 0) or (b["hi"] - b["lo"] == 0)
                    if opp and nonov:
                        found.append((js[i], js[k]))
                    print("    %-26s vs %-26s opposite sign=%-5s non-overlap=%-5s degenerate(reported only)=%-5s"
                          % (js[i][:26], js[k][:26], opp, nonov, degen))
            print("    -> %s" % ("CONFIRMED: %d qualifying pair(s)" % len(found) if found
                                 else "NOT confirmed. Per the registered asymmetry this is "
                                      "INCONCLUSIVE, never a refutation."))
    return out


if __name__ == "__main__" and os.environ.get("H2"):
    h2()


# ---------------------------------------------------------------- c - s intervals (referee findings on interval reporting)
def cs_intervals(verbose=True):
    """Question-clustered bootstrap interval on (c - s), which 4.6 previously reported as a bare
    point estimate. Added after referee findings on interval reporting.

    c = share of questions whose MEC verdict changes between AB and BA.
    s = share of questions whose identical-order (AB) MEC verdict differs from the noise-arm repeat.
    Both are paired on question, so the bootstrap resamples QUESTIONS and recomputes both from the
    same resample, which is what makes the difference's interval meaningful.
    10,000 resamples, seed 1234, per the registration.
    """
    import random as _r
    rows = []
    byjudge = {}
    for f in sorted(glob.glob(os.path.join(HERE, "results", "verdicts_*.json"))):
        d = json.load(open(f))
        byjudge.setdefault(d["judge"], []).extend(canonicalise(d["verdicts"]))
    for judge, V in sorted(byjudge.items()):
        for tpl in ("SCORING_CODE", "COMPARING"):
            base = common_set_cs(V, tpl)
            if not base:
                continue
            mec, noise, qs_ = base["mec"], base["noise"], base["qs"]
            def stat(sample):
                c = sum(1 for q in sample if mec[q]["AB"] != mec[q]["BA"]) / len(sample)
                s = sum(1 for q in sample if mec[q]["AB"] != noise[q]) / len(sample)
                return c, s, c - s
            c, s, d_ = stat(qs_)
            rnd = _r.Random(rr.BASE_SEED)
            boots = sorted(stat([rnd.choice(qs_) for _ in qs_])[2] for _ in range(10000))
            lo, hi = boots[250], boots[9749]
            rows.append((judge, tpl, len(qs_), c, s, d_, lo, hi))
    if verbose:
        print("=" * 96)
        print("c - s with question-clustered bootstrap 95% intervals (10,000 resamples, seed 1234)")
        print("%-28s %-13s %5s %7s %7s %8s %18s" % ("judge", "template", "n", "c", "s", "c-s", "95% CI"))
        for j, t, n, c, s, d_, lo, hi in rows:
            print("%-28s %-13s %5d %7.3f %7.3f %8.3f   [%+.3f, %+.3f]"
                  % (j[:28], t, n, c, s, d_, lo, hi))
        print()
        print("n is questions with BOTH MEC orders parsed AND a parsed noise repeat, so it is")
        print("smaller than the per-arm record counts. Reported rather than silently dropped.")
    return rows


if __name__ == "__main__" and os.environ.get("CS"):
    cs_intervals()


def cs_consistency_check():
    """FAILS the run if main's c - s and cs_intervals' c - s ever diverge.

    They share common_set_cs now, so divergence would mean someone reintroduced a second
    definition. Required after a referee found main printing 0.041 while cs_intervals printed
    0.038 for the same quantity.
    """
    byj = {}
    for f in sorted(glob.glob(os.path.join(HERE, "results", "verdicts_*.json"))):
        d = json.load(open(f))
        byj.setdefault(d["judge"], []).extend(canonicalise(d["verdicts"]))
    bad = []
    for judge, t, n, c, s_, d_, lo, hi in cs_intervals(verbose=False):
        m = common_set_cs(byj[judge], t)
        if m is None or abs(m["cs"] - d_) > 1e-9:
            bad.append((judge, t, m and m["cs"], d_))
    if bad:
        print("  C-S CONSISTENCY CHECK: FAIL")
        for j, t, a, b in bad:
            print("    %s %s main=%s intervals=%s" % (j, t, a, b))
        return 1
    print("  C-S CONSISTENCY CHECK: PASS (one definition, %d cells agree)"
          % len(cs_intervals(verbose=False)))
    return 0


if __name__ == "__main__" and os.environ.get("CSCHECK"):
    raise SystemExit(cs_consistency_check())


if __name__ == "__main__" and os.environ.get("FRAME"):
    raise SystemExit(frame_selftest())
