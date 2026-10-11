# Code and data availability

Drafted while the fresh review runs, under the instruction that it stay OUT of the build until the
reviews land. Nothing here is rendered into `build/p10.pdf`.

Two public actions are reserved to the project owner and are not taken here: creating the public
repository, and minting the Zenodo DOI after acceptance.

---

## 1. What we release

Our own code, all of it in the project root:

    run_replication.py    the harness: arms, prompts, seeds, the five positive controls,
                          the registered parser, the per-arm halt rule
    hydrate_faireval.py   fetches and verifies the third-party inputs at a pinned commit
    analyze_mec.py        MEC-arm quantities, the content-blind benchmark, H2, c-s intervals
    relaxed_parse.py      the secondary exploratory parser, with its guard tests
    pc4_retest.py         the single pre-declared determinism re-test
    sweep.py              the stale-claim and scaffolding sweep, with --selftest
    build_paper.py        assembles and builds the PDF
    bench_judge_latency.py  the compute measurement used for planning

Our own results, in `results/`:

    verdicts_llama3.1_8b-instruct-q4_K_M.json    800 records
    verdicts_mistral_7b-instruct.json            480 records
    verdicts_qwen2.5_7b-instruct.json            160 records (noise arm)
    verdicts_qwen2.5_7b-instruct_table5.json     320 records (MEC arm, re-executed)
    pc4_retest_declared.json                     the D-1 re-test

Each verdict record carries the arm, template, candidate pair, question id, presentation order, the
aggregated verdict, a parsed flag, k, temperature, the seed block, every individual sample with its
raw text, and SHA-256 hashes of both candidate answers.

The documentation set: the registered pre-registration, the dated deviations register, and the
decision log.

## 2. What we do NOT release, and why

THE THIRD-PARTY INPUTS. The question set, candidate answers and human labels come from
`https://github.com/i-Eval/FairEval`. That repository carries no licence file, so we redistribute
none of its contents. `hydrate_faireval.py` fetches them at commit
`453c117a69159fd7b7de2f4e0519bac57bee21f4` and verifies SHA-256 and byte length for all six files
it pins before any run proceeds.

A CONSEQUENCE A READER SHOULD KNOW: if that upstream repository is deleted or rewritten, our
artefact cannot be rehydrated from it, and the verifier will refuse to proceed rather than run on
different bytes. We judged refusing to redistribute unlicensed material the right call and accept
this fragility as its cost. The pinned hashes are recorded in `hydrate_faireval.py`, so a reader who
obtains the files from any source can confirm they are the same bytes we used.

THE MODEL WEIGHTS. Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct-q4_K_M and Mistral-7B-Instruct are
third-party open-weight models. We release their local digests, not the weights.

## 3. A reproducibility limitation we must state

The registration committed to recording each arm's model digest in the results artefact before its
run. That did not happen. The artefacts carry the model name and tag but no digest field; the only
hashes in them cover candidate answers.

The digests are recorded in the deviations register and in the Methods section, but they were read
from the local model store AFTER the runs. So a reader cannot confirm from an artefact alone which
weights produced it, and must take our word that the store was unchanged between the run and the
reading. We did not retrofit digests into the completed files, because that would produce artefacts
that look like they satisfied a commitment they did not.

## 4. How to reproduce

    python3 hydrate_faireval.py <path>          # fetch and verify inputs; must exit 0
    python3 run_replication.py --root <path> --arms all --judge <model> --osf-doi <doi>
    python3 analyze_mec.py                      # with CB=1, H2=1 or CS=1 for the other tables
    python3 sweep.py --selftest && python3 sweep.py

The harness refuses to run any arm until a registration DOI is supplied, which is deliberate: it
makes running before registering impossible rather than merely discouraged.

Expect to reproduce the pipeline and the controls. Do NOT expect to reproduce our verdicts
byte-for-byte. Section 4.2 of the paper reports that two of our three judges failed a temperature-0
determinism check, and a pre-declared re-test found the failure persisting under serial requests.
Any attempt to reproduce this work should treat verdict-level agreement as the thing being measured,
not as a precondition.

## 5. Pre-registration

Registered before any judge run: https://osf.io/jw59c/, DOI 10.17605/OSF.IO/JW59C. The registered
text is public and immutable. Every departure from it is listed, dated, in the deviations register,
including those that are unfavourable to us.
