"""PC-4 re-test under the controlled protocol declared in DEVIATIONS.md D-1.

Authorised by a documented review decision. ONE re-test only. Its result is EXPLORATORY: it
characterises the cause of the determinism failure and never reinstates judge 1's temperature-0
arms, which stay halted as registered whatever this shows.

Protocol, exactly as declared before the judge 2 and 3 outcomes were read:
  - serial requests only, nothing else issuing requests to the Ollama server
  - OLLAMA_NUM_PARALLEL=1 (the caller restarts the server with this set)
  - only the judge model resident
  - the SAME 10 prompts as the failed check, drawn with random.Random(20261010)
  - PLUS 10 newly drawn ones, drawn with random.Random(20261011) from the remaining questions
  - judge, decoding and base seed exactly as registered: temperature 0, seed 1234

Usage: python3 pc4_retest.py <judge> <inputs-root> <out.json>
"""
import importlib.util
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rr", os.path.join(HERE, "run_replication.py"))
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)


def main(judge, root, outpath):
    qs, answers, _ = rr.load_inputs(root)
    m1, m2 = rr.PAIRS["close"]

    original = random.Random(20261010).sample(qs, 10)          # the same 10 as the failed check
    orig_ids = {q["question_id"] for q in original}
    remaining = [q for q in qs if q["question_id"] not in orig_ids]
    fresh = random.Random(20261011).sample(remaining, 10)      # 10 newly drawn

    rows = []
    for tag, batch in (("original", original), ("fresh", fresh)):
        for q in batch:
            qid = q["question_id"]
            p = rr.TPL_SCORING.format(Q=q["text"], R1=answers[m1][qid], R2=answers[m2][qid])
            a = rr.call_judge(judge, p, rr.TEMP_VANILLA, rr.BASE_SEED)
            time.sleep(0.3)                                     # serial, no overlap
            b = rr.call_judge(judge, p, rr.TEMP_VANILLA, rr.BASE_SEED)
            same = (a["text"] == b["text"])
            rows.append({"set": tag, "qid": qid, "identical": same,
                         "len_a": len(a["text"]), "len_b": len(b["text"]),
                         "tok_a": a.get("output_tokens"), "tok_b": b.get("output_tokens")})
            print("  %-8s q%-3s identical=%s" % (tag, qid, same), flush=True)

    n = len(rows)
    bad = [r for r in rows if not r["identical"]]
    res = {
        "status": "EXPLORATORY - characterises the cause; does NOT reinstate any halted arm",
        "authorised_by": "a documented review decision; protocol declared in DEVIATIONS.md D-1",
        "judge": judge,
        "osf_doi": "10.17605/OSF.IO/JW59C",
        "protocol": {"serial": True, "ollama_num_parallel": os.environ.get("OLLAMA_NUM_PARALLEL"),
                     "temperature": rr.TEMP_VANILLA, "seed": rr.BASE_SEED,
                     "draw_seed_original": 20261010, "draw_seed_fresh": 20261011},
        "n_prompts": n, "n_mismatched": len(bad),
        "mismatch_rate": round(len(bad) / n, 4) if n else None,
        "mismatched": bad, "rows": rows,
    }
    json.dump(res, open(outpath, "w"), indent=1)
    print("\n%d of %d prompt pairs differed (rate %.3f)" % (len(bad), n, res["mismatch_rate"]))
    print("wrote", outpath)
    print("REMINDER: judge 1's temperature-0 arms remain halted as registered regardless of this.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], os.path.expanduser(sys.argv[2]), sys.argv[3])
