"""Run harness for the replication of Wang et al. (2024), "LLMs are not Fair Evaluators".

Implements the frozen pre-registered design in PREREGISTRATION-OSF.md. Written during the registration window; see the deviations register, D-3, on what the
timestamps do and do not evidence
so that no time is lost after it; it makes NO judge calls unless explicitly told to run an arm, and
the controls that need no inference can be verified now.

DO NOT RUN THE ARMS UNTIL THE PRE-REGISTRATION IS REGISTERED. The gate is a kmvee-only public
action. `--arms` refuses to run unless --osf-doi is supplied, which is the mechanical expression of
that gate rather than a note asking someone to remember it.

Usage
  python run_replication.py --controls-only            # PC-1/2/3 scaffolding, zero judge calls
  python run_replication.py --arms all --judge qwen2.5:7b-instruct --osf-doi 10.17605/OSF.IO/JW59C

Arms, per pre-registration sections 4, 4b, 4c:
  table2  VANILLA, temperature 0, both orders, close pair + far pair      320 calls
  table5  MEC(k=3, T=1) only, no BPC arm exists (see D-10), both orders, both templates      960 calls
  noise   second independent MEC verdict in the IDENTICAL order,          480 calls
          close pair, both templates, disjoint seed block
Total 1,760 calls per judge; 5,280 for three judges.
"""
import argparse
import collections
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.request

ROOT_DEFAULT = os.path.expanduser("~/.cache/p10-inputs/FairEval")  # moved out of /tmp, see D-4
PIN = "453c117a69159fd7b7de2f4e0519bac57bee21f4"
OLLAMA = "http://127.0.0.1:11434/api/generate"

# Pre-registered constants. Section 6 of the pre-registration. Do not edit after registration
# without recording a dated deviation.
BASE_SEED = 1234
NOISE_SEED = 1334           # disjoint block, so the noise verdict is an independent draw
K_MEC = 3
NUM_PREDICT = 400
TEMP_VANILLA = 0.0
TEMP_MEC = 1.0
BOOTSTRAP_RESAMPLES = 10000
GAP_BINS = [0, 1, 2, 3, 4]  # 4 means "4 or more"; collapse rule in section 10

# The paper's Table 1 template, used verbatim.
TPL_SCORING = """[Question]
{Q}

[The Start of Assistant 1's response]
{R1}
[The End of Assistant 1's response]

[The Start of Assistant 2's response]
{R2}
[The End of Assistant 2's response]

[System]
We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above. Please rate the helpfulness, relevance, accuracy, level of details of their responses. Each assistant receives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance. Please first output a single line containing only two values indicating the scores for Assistant 1 and 2, respectively. The two scores are separated by a space. In the subsequent line, please provide a comprehensive explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment.
"""

TPL_COMPARING = """[Question]
{Q}

[The Start of Assistant 1's response]
{R1}
[The End of Assistant 1's response]

[The Start of Assistant 2's response]
{R2}
[The End of Assistant 2's response]

[System]
We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above. Please compare the helpfulness, relevance, accuracy, level of details of their responses. Please first output a single line containing only one value indicating the comparison result, which should be "Assistant 1" if Assistant 1 is better, "Assistant 2" if Assistant 2 is better, or "Same" if they are equally good. In the subsequent line, please provide a comprehensive explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment.
"""

# --- The authors' CODE template, verbatim from FairEval.py lines 35-49 at the pinned commit.
# It DIFFERS from the paper's Table 1: it adds a system prompt, says "Answer" not "response", and
# crucially puts the EXPLANATION FIRST and the scores last, in a two-line labelled format.
# The two templates are not interchangeable and each arm uses a specific one. The VANILLA arm
# uses TPL_SCORING, the plain template printed in the original's Table 1. The MEC and noise arms
# use TPL_SCORING_CODE, a near-verbatim variant of the original's Table 3 evidence-calibration
# template as it appears in the authors' released gen_prompt, which is the prompt their own code
# sends and the only one consistent with MEC's evidence-first mechanism. TPL_COMPARING is our
# reconstruction; the original specifies its labels in prose but prints no template.
SYS_PROMPT_CODE = "You are a helpful and precise assistant for checking the quality of the answer."

TPL_SCORING_CODE = """[Question]
{Q}

[The Start of Assistant 1's Answer]
{R1}
[The End of Assistant 1's Answer]

[The Start of Assistant 2's Answer]
{R2}
[The End of Assistant 2's Answer]

[System]
We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above.
    Please rate the helpfulness, relevance, accuracy, level of details of their responses. 

    Each assistant receives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance.
    Please first provide a comprehensive explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment. 
    Then, output two lines indicating the scores for Assistant 1 and 2, respectively.

    Output with the following format:
    Evaluation evidence: <your evluation explanation here>
    Score of the Assistant 1: <score>
    Score of the Assistant 2: <score>
"""

SCORE_LINE = re.compile(r"^\s*(\d{1,2}(?:\.\d+)?)\s+(\d{1,2}(?:\.\d+)?)\s*$")
# Parser for the CODE format: labelled scores, anywhere in the output, explanation first.
SCORE_LABELLED = re.compile(
    r"Score\s+of\s+the\s+Assistant\s+1\s*:\s*(\d{1,2}(?:\.\d+)?).*?"
    r"Score\s+of\s+the\s+Assistant\s+2\s*:\s*(\d{1,2}(?:\.\d+)?)", re.I | re.S)
COMPARE_LINE = re.compile(r"^\s*(Assistant 1|Assistant 2|Same)\s*\.?\s*$", re.I)

PAIRS = {
    "close": ("gpt35", "vicuna-13b"),      # the paper's "Vicuna-13B v.s. ChatGPT"
    "far": ("alpaca-13b", "vicuna-13b"),   # the paper's "Vicuna-13B v.s. Alpaca-13B"
}


def load_inputs(root):
    def jl(p):
        return [json.loads(l) for l in open(p) if l.strip()]
    qs = jl(os.path.join(root, "question.jsonl"))
    answers = {}
    for m in ("gpt35", "vicuna-13b", "alpaca-13b", "gpt-4"):
        answers[m] = {d["question_id"]: d["text"]
                      for d in jl(os.path.join(root, "answer", "answer_%s.jsonl" % m))}
    labels = [l.strip() for l in
              open(os.path.join(root, "review", "review_gpt35_vicuna-13b_human.txt")) if l.strip()]
    return qs, answers, labels


# ---------------------------------------------------------------- positive controls, section 8

def pc1_input_integrity(root):
    """Delegates to the hydration verifier, which is the single source of truth for the pin."""
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run([sys.executable, os.path.join(here, "hydrate_faireval.py"), root],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1] if r.stdout or r.stderr else ""


def pc2_ground_truth_recovery(labels):
    """Must reproduce exactly ChatGPT 41 / TIE 14 / VICUNA13B 25, n = 80."""
    c = collections.Counter(labels)
    expected = {"CHATGPT": 41, "TIE": 14, "VICUNA13B": 25}
    ok = (len(labels) == 80 and all(c.get(k) == v for k, v in expected.items()))
    return ok, dict(c), expected


def pc3_order_bookkeeping(verdicts):
    """Exactly one AB and one BA verdict per (question, pair, arm, template).

    NOT a hash comparison. r1_sha/r2_sha are stored on every record but this check never reads
    them, so a silently swapped candidate text would NOT be detected here. The registration
    described a hash-based check; see the deviations register.
    """
    seen = collections.defaultdict(set)
    for v in verdicts:
        key = (v["qid"], v["pair"], v["arm"], v["template"])
        if v["order"] in seen[key]:
            return False, "duplicate %s for %s" % (v["order"], key)
        seen[key].add(v["order"])
    bad = [k for k, o in seen.items() if o != {"AB", "BA"}]
    return (not bad), ("incomplete order pairs: %d" % len(bad) if bad else "all (q,pair,arm,template) have both orders")


def pc4_determinism(judge, qs, answers, n=10, seed_base=BASE_SEED):
    """At temperature 0 with a fixed seed, re-running prompts must reproduce byte-identical output.

    Registered consequence: a failure here HALTS the affected arm and is reported as a methods
    finding. It is never converted into a correction term (see the noise-control section).
    """
    rnd = random.Random(20261010)
    picks = rnd.sample(qs, min(n, len(qs)))
    m1, m2 = PAIRS["close"]
    mismatches = []
    for q in picks:
        qid = q["question_id"]
        p = TPL_SCORING.format(Q=q["text"], R1=answers[m1][qid], R2=answers[m2][qid])
        a = call_judge(judge, p, TEMP_VANILLA, seed_base)
        b = call_judge(judge, p, TEMP_VANILLA, seed_base)
        if a["text"] != b["text"]:
            mismatches.append(qid)
    return (not mismatches), {"checked": len(picks), "mismatched_qids": mismatches}


def pc5_parse_accounting(verdicts):
    """Unparseable verdicts are counted and reported, never dropped."""
    n = len(verdicts)
    bad = sum(1 for v in verdicts if v["parsed"] is False)
    rate = (bad / n) if n else 0.0
    return {"total": n, "unparseable": bad, "rate": round(rate, 4), "over_10pct": rate > 0.10}


# ---------------------------------------------------------------- inference

def call_judge(model, prompt, temperature, seed, system=None):
    payload = {"model": model, "prompt": prompt, "stream": False,
               "options": {"temperature": temperature, "seed": seed,
                           "num_predict": NUM_PREDICT}}
    if system:
        payload["system"] = system
    body = json.dumps(payload).encode()
    req = urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"})
    t0 = time.time()
    r = json.load(urllib.request.urlopen(req, timeout=600))
    return {"text": r.get("response", ""), "wall": time.time() - t0,
            "prompt_tokens": r.get("prompt_eval_count"), "output_tokens": r.get("eval_count")}


def parse_verdict(text, template):
    """Returns (verdict, parsed_flag). Verdict is 'A', 'B' or 'TIE' from A's perspective.

    SCORING_CODE uses the authors' labelled two-line format and tolerates the explanation coming
    first, which is what their code actually asks for. SCORING uses the paper's Table 1 format.
    """
    if not text.strip():
        return None, False
    if template == "SCORING_CODE":
        m = SCORE_LABELLED.search(text)
        if not m:
            return None, False
        a, b = float(m.group(1)), float(m.group(2))
        return ("A" if a > b else "B" if b > a else "TIE"), True
    first = text.strip().splitlines()[0]
    if template == "SCORING":
        m = SCORE_LINE.match(first)
        if not m:
            return None, False
        a, b = float(m.group(1)), float(m.group(2))
        return ("A" if a > b else "B" if b > a else "TIE"), True
    m = COMPARE_LINE.match(first)
    if not m:
        return None, False
    g = m.group(1).lower()
    return ("A" if g == "assistant 1" else "B" if g == "assistant 2" else "TIE"), True


def hash_text(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def run_arm(arm, judge, qs, answers, template, pair_name, out):
    """Appends verdict records. One record per (question, order)."""
    m1, m2 = PAIRS[pair_name]
    # an internal review decision: VANILLA and non-MEC arms use the paper's Table 1; every MEC arm (with or without
    # BPC) uses the authors' released gen_prompt verbatim, system prompt included.
    if arm in ("mec", "noise") and template == "SCORING":
        template = "SCORING_CODE"
    tpl = {"SCORING": TPL_SCORING, "SCORING_CODE": TPL_SCORING_CODE,
           "COMPARING": TPL_COMPARING}[template]
    system = SYS_PROMPT_CODE if template == "SCORING_CODE" else None
    temp = TEMP_MEC if arm in ("mec", "noise") else TEMP_VANILLA
    k = K_MEC if arm in ("mec", "noise") else 1
    seed0 = NOISE_SEED if arm == "noise" else BASE_SEED
    orders = [("AB",)] if arm == "noise" else [("AB",), ("BA",)]
    for q in qs:
        qid = q["question_id"]
        a1, a2 = answers[m1][qid], answers[m2][qid]
        for (order,) in orders:
            r1, r2 = (a1, a2) if order == "AB" else (a2, a1)
            samples = []
            for i in range(k):
                res = call_judge(judge, tpl.format(Q=q["text"], R1=r1, R2=r2), temp, seed0 + i,
                                 system=system)
                v, parsed = parse_verdict(res["text"], template)
                samples.append({"verdict": v, "parsed": parsed, "raw": res["text"],
                                "seed": seed0 + i, "wall": res["wall"]})
            votes = [s["verdict"] for s in samples if s["parsed"]]
            agg = collections.Counter(votes).most_common(1)[0][0] if votes else None
            out.append({"judge": judge, "arm": arm, "template": template, "pair": pair_name,
                        "qid": qid, "order": order, "verdict": agg,
                        "parsed": bool(votes), "k": k, "temperature": temp,
                        "seed_block": seed0, "samples": samples,
                        "r1_sha": hash_text(r1), "r2_sha": hash_text(r2)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--controls-only", action="store_true",
                    help="run the inference-free controls and exit; makes ZERO judge calls")
    ap.add_argument("--arms", choices=["table2", "table5", "noise", "all"])
    ap.add_argument("--judge")
    ap.add_argument("--osf-doi", help="registration DOI; required before any arm may run")
    ap.add_argument("--out", default="results")
    ap.add_argument("--pc4", choices=["run", "recorded-fail", "recorded-pass"], default="run",
                    help="'recorded-fail' skips re-testing determinism and treats the temperature-0 "
                         "arm as halted, for a judge whose PC-4 outcome is already on record. "
                         "Re-executing PC-4 outside the declared re-test protocol would be an "
                         "undeclared second test (see DEVIATIONS.md D-1, D-2).")
    a = ap.parse_args()

    qs, answers, labels = load_inputs(a.root)

    print("PC-1 input integrity ... ", end="")
    ok1, msg1 = pc1_input_integrity(a.root)
    print("PASS" if ok1 else "FAIL", "-", msg1)

    print("PC-2 ground truth recovery ... ", end="")
    ok2, got, exp = pc2_ground_truth_recovery(labels)
    print("PASS" if ok2 else "FAIL", "- got", got, "expected", exp)

    if not (ok1 and ok2):
        raise SystemExit("HARD STOP: a positive control failed. No analysis proceeds (section 8).")

    if a.controls_only:
        print("\ncontrols-only: PC-3 and PC-5 are evaluated against verdicts and will run with the "
              "arms; PC-4 (determinism) needs 10 judge calls and is therefore part of the run, "
              "not of this check. ZERO judge calls were made.")
        return

    if not a.arms:
        raise SystemExit("nothing to do: pass --controls-only or --arms")
    if not a.osf_doi:
        raise SystemExit(
            "REFUSED: --osf-doi is required before any arm runs.\n"
            "The pre-registration must be registered first, and that registration is the project "
            "owner's action, not this script's. Supply the DOI once it exists.")
    if not a.judge:
        raise SystemExit("--judge is required")

    # PC-4 gates the TEMPERATURE-0 arm only. The temperature-1 arms do not rest on PC-4; they rest
    # on the measured noise control. Halting a whole judge would be stricter than registered.
    if a.pc4 == "run":
        print("PC-4 determinism (10 prompts, temperature 0, fixed seed) ... ", end="", flush=True)
        ok4, det = pc4_determinism(a.judge, qs, answers)
        print("PASS" if ok4 else "FAIL", "-", det)
    else:
        ok4 = (a.pc4 == "recorded-pass")
        det = {"source": "recorded on a previous run; not re-tested (DEVIATIONS.md D-1/D-2)"}
        print("PC-4 determinism ... %s (declared from record, not re-run)" % ("PASS" if ok4 else "FAIL"))

    verdicts = []
    want = ["table2", "table5", "noise"] if a.arms == "all" else [a.arms]
    if not ok4 and "table2" in want:
        want = [w for w in want if w != "table2"]
        print("  -> TEMPERATURE-0 ARM HALTED for this judge, as registered. Reported as a methods "
              "finding, not corrected. Temperature-1 arms proceed: %s" % (want or "none"))
    if not want:
        print("nothing left to run for this judge after the PC-4 halt.")
        os.makedirs(a.out, exist_ok=True)
        path = os.path.join(a.out, "pc4_halt_%s.json" % a.judge.replace(":", "_").replace("/", "_"))
        json.dump({"judge": a.judge, "osf_doi": a.osf_doi, "pc4_ok": ok4, "pc4_detail": det,
                   "t0_arm": "HALTED as registered"}, open(path, "w"), indent=1)
        print("wrote", path)
        return
    if "table2" in want:
        for pair in ("close", "far"):
            run_arm("vanilla", a.judge, qs, answers, "SCORING", pair, verdicts)
    if "table5" in want:
        for tpl in ("SCORING", "COMPARING"):
            run_arm("mec", a.judge, qs, answers, tpl, "close", verdicts)
    if "noise" in want:
        for tpl in ("SCORING", "COMPARING"):
            run_arm("noise", a.judge, qs, answers, tpl, "close", verdicts)

    ok3, msg3 = pc3_order_bookkeeping([v for v in verdicts if v["arm"] != "noise"])
    print("PC-3 order bookkeeping ...", "PASS" if ok3 else "FAIL", "-", msg3)
    print("PC-5 parse accounting ...", pc5_parse_accounting(verdicts))

    os.makedirs(a.out, exist_ok=True)
    # Filename includes the ARM SET. Without this, two invocations for the same judge wrote the
    # same path and the second silently overwrote the first, which is exactly what happened to
    # qwen's table5 arm on 2026-10-10 and cost 320 verdict records.
    armtag = a.arms if a.arms != "all" else "all"
    path = os.path.join(a.out, "verdicts_%s_%s.json" % (
        a.judge.replace(":", "_").replace("/", "_"), armtag))
    json.dump({"pin": PIN, "osf_doi": a.osf_doi, "judge": a.judge,
               "pc4_ok": ok4, "pc4_detail": det,
               "t0_arm": ("ran" if ok4 else "HALTED as registered (PC-4 failed)"),
               "constants": {"base_seed": BASE_SEED, "noise_seed": NOISE_SEED, "k": K_MEC,
                             "num_predict": NUM_PREDICT, "temp_vanilla": TEMP_VANILLA,
                             "temp_mec": TEMP_MEC},
               "verdicts": verdicts}, open(path, "w"), indent=1)
    print("wrote", path, "-", len(verdicts), "verdict records")


if __name__ == "__main__":
    main()
