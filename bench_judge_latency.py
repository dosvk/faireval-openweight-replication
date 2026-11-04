import json, time, urllib.request, re, statistics, sys

# m4 (reviewer round 2): ROOT and the output path were hard-coded under /tmp, and the output
# directory was never created, so a fresh run died on the final write. Both are now arguments
# with the old values as defaults. This is a PLANNING script: it measured judge latency to size
# the run, and is released for completeness rather than as part of the analysis path.
import os as _os, sys as _sys
ROOT = _os.environ.get("P10_BENCH_INPUTS", "/tmp/paper10-smoke/FairEval")
OUTDIR = _os.environ.get("P10_BENCH_OUT", "/tmp/paper10-bench")
TEMPLATE = """[Question]
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

def load(p):
    return [json.loads(l) for l in open(p) if l.strip()]

qs = load(f"{ROOT}/question.jsonl")
a1 = {d["question_id"]: d["text"] for d in load(f"{ROOT}/answer/answer_gpt35.jsonl")}
a2 = {d["question_id"]: d["text"] for d in load(f"{ROOT}/answer/answer_vicuna-13b.jsonl")}

MODEL = "qwen2.5:7b-instruct"
def call(prompt, seed):
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0, "seed": seed, "num_predict": 400}}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", body,
                                 {"Content-Type": "application/json"})
    t0 = time.time()
    r = json.load(urllib.request.urlopen(req, timeout=600))
    return time.time() - t0, r

FIRST_LINE = re.compile(r"^\s*(\d{1,2}(?:\.\d+)?)\s+(\d{1,2}(?:\.\d+)?)\s*$")
rows, parse_ok = [], 0
N = 3
for q in qs[:N]:
    qid = q["question_id"]
    for order, (r1, r2) in (("AB", (a1[qid], a2[qid])), ("BA", (a2[qid], a1[qid]))):
        p = TEMPLATE.format(Q=q["text"], R1=r1, R2=r2)
        wall, r = call(p, 1234)
        out = r.get("response", "")
        m = FIRST_LINE.match(out.strip().splitlines()[0]) if out.strip() else None
        parse_ok += 1 if m else 0
        rows.append(dict(qid=qid, order=order, wall=wall,
                         ptok=r.get("prompt_eval_count"), otok=r.get("eval_count"),
                         evald=r.get("eval_duration", 0) / 1e9,
                         parsed=bool(m), scores=(m.groups() if m else None),
                         head=out.strip().splitlines()[0][:70] if out.strip() else ""))
        print(f"  q{qid:<3} {order}  {wall:6.2f}s  prompt_tok={r.get('prompt_eval_count'):<5} "
              f"out_tok={r.get('eval_count'):<4} gen_tok/s={r.get('eval_count',0)/max(r.get('eval_duration',1)/1e9,1e-9):6.1f} "
              f"parsed={bool(m)} first_line={rows[-1]['head']!r}")

walls = [r["wall"] for r in rows]
tps = [r["otok"] / r["evald"] for r in rows if r["evald"]]
print()
print("model:              %s (4.7 GB, Apple M4 Pro, 48 GB)" % MODEL)
print("calls:              %d  (%d questions x 2 orders)" % (len(rows), N))
print("wall per call:      mean %.2fs  median %.2fs  min %.2fs  max %.2fs"
      % (statistics.mean(walls), statistics.median(walls), min(walls), max(walls)))
print("generation speed:   mean %.1f tok/s" % statistics.mean(tps))
print("prompt tokens:      mean %.0f   output tokens: mean %.0f"
      % (statistics.mean([r["ptok"] for r in rows]), statistics.mean([r["otok"] for r in rows])))
print("format compliance:  %d/%d first lines parsed as 'score score'" % (parse_ok, len(rows)))
m = statistics.mean(walls)
print()
print("EXTRAPOLATION to the pre-registered design, at %.2fs per judgement:" % m)
t2 = 80 * 2 * 2
t5 = 80 * 2 * 3 * 2
print("  Table 2 (80 q x 2 orders x 2 pairs)              = %4d calls = %5.1f min" % (t2, t2 * m / 60))
print("  Table 5 (80 q x 2 orders x k=3 x 2 templates)    = %4d calls = %5.1f min" % (t5, t5 * m / 60))
print("  per judge model                                   = %4d calls = %5.1f min" % (t2 + t5, (t2 + t5) * m / 60))
print("  THREE judge models                                = %4d calls = %5.1f min (%.1f h)"
      % (3 * (t2 + t5), 3 * (t2 + t5) * m / 60, 3 * (t2 + t5) * m / 3600))
_os.makedirs(OUTDIR, exist_ok=True)
json.dump(rows, open(_os.path.join(OUTDIR, "bench_rows.json"), "w"), indent=1)
