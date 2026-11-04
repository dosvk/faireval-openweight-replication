# Code and data availability

What this repository releases, what it does not, and why. This file is documentation for readers of
the artefact; it is not rendered into the article.

Two public actions are reserved to the project owner and are not taken here: creating the public
repository, and minting the Zenodo DOI after acceptance.

---

## 1. What we release

Our own code, all of it in the project root:

    run_replication.py    the harness: arms, prompts, seeds, the five positive controls,
                          the registered parser, the per-arm halt rule
    hydrate_faireval.py   VERIFIES a third-party checkout against pinned SHA-256 and byte
                          lengths. It does not fetch; you clone at the pinned commit and pass
                          the path. See the README for the clone step.
    analyze_mec.py        MEC-arm quantities, the content-blind benchmark, H2, c-s intervals
    relaxed_parse.py      the secondary exploratory parser, with its guard tests
    pc4_retest.py         the single pre-declared determinism re-test
    sweep.py              the stale-claim and scaffolding sweep, with --selftest
    verify_parser_pins.py recomputes the four parser pins under the convention stated in its
                          docstring; --check exits non-zero on mismatch
    check_claims.py       stated-once gate: fails if any released text carries a superseded
                          wording of a canonical claim, listed in claims.json
    check_release.py      orphan-line gate on the built markdown, and a check that this
                          inventory names every script in the release
    build_article.sh      reproducible build of the article; --check fails if the sha moves

The article source, under `rescience-build/`, so the submitted PDF can be rebuilt from a clone:

    article.tex, content.tex, header.tex, metadata.tex, metadata.yaml, rescience.cls,
    Makefile, article.py, yaml-to-latex.py, bibliography.bib, README.md   the ReScience C
                          article template (GPL v3, COPYING included) with our content
    TEMPLATE-CHANGES.md   every change we made to the template, as GPL v3 requires, with the
                          reason for each; each change is also commented where it occurs
    roboto/, source-code-pro/, source-sans-pro/, source-serif-pro/   the template's bundled
                          fonts, Apache 2.0 and SIL OFL, each licence in its own directory

LaTeX build residue (`.aux`, `.bbl`, `.bcf`, `.blg`, `.log`, `.fls`, `.fdb_latexmk`, `.out`,
`.run.xml`, `.toc`) is NOT released; `.gitignore` excludes it and `build_article.sh`
regenerates it.

The build inputs, released so the documented build runs from a clone:

    SECTIONS-DRAFT.md     the narrative sections of the article
    RESULTS-DRAFT.md      the abstract and the Results section
    rescience-build/bibliography.bib   the biblatex bibliography the ReScience build reads
    logs/run-20261010T032331Z.log      the first-run log; see the PC-4 section below for what
                          each of its cited lines supports and the one redaction made to it
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

The documentation set: the registered pre-registration and the dated deviations register.

NOT the decision log. Earlier versions of this file listed it; it is an internal working log of
coordination and self-criticism, not a scientific record, and it does not ship. The scientific record
of every departure from the plan is `DEVIATIONS.md`, which does. Reviewer 1 on #142 correctly noted
the inventory advertised files the release did not contain; this is one of them, narrowed rather than
released.

## 2. What we do NOT release, and why

THE THIRD-PARTY INPUTS. The question set, candidate answers and human labels come from
`https://github.com/i-Eval/FairEval`. That repository carries no licence file, so we redistribute
none of its contents. `hydrate_faireval.py` verifies a checkout of them at commit
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

    python3 hydrate_faireval.py <path>          # VERIFY an existing checkout; must exit 0
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

---

## PC-4 determinism: which record supports each reported outcome

Reviewer 1 on ReScience #142 (2026-11-04) observed that the manuscript refers to
`results/pc4_retest_declared.json` and to the first-run log cited in D-3, that neither was in the
released repository, and that the three judges' PC-4 evidence in the released verdict files is
uneven: Mistral carries a detail field, Qwen's points back at an earlier run, and Llama's verdict
file has no PC-4 field at all. The reviewer asked us to identify the record behind each reported
outcome and to say plainly where no contemporaneous record exists.

Both files are now released. ONE REDACTION WAS MADE TO THE LOG, and it is the only one: line 5
recorded the local input root as an absolute path under a home directory, and the home prefix
is replaced by `<HOME>`. Nothing else in the log is altered, the line count is unchanged, and
the line numbers cited below were re-verified after the edit. The attribution below is read off
the first-run log, which carries an
explicit `########## JUDGE <name>` banner before each judge's block, so each PC-4 line is
attributable by name rather than by inference.

| judge | reported PC-4 outcome | record that supports it | status |
|---|---|---|---|
| `qwen2.5:7b-instruct` | FAIL, 1 of 10, q77 | `logs/run-20261010T032331Z.log` line 18, under the judge banner at line 15; the HARD STOP is line 19 | **contemporaneous, inspectable** |
| `llama3.1:8b-instruct-q4_K_M` | PASS, 0 of 10 | `logs/run-20261010T032331Z.log` line 1532, under the judge banner at line 22 | **contemporaneous, inspectable.** Note its verdict file has no PC-4 field; the log is the only record, which is why the log is now released |
| `mistral:7b-instruct` | FAIL, 2 of 10, q33 and q52 | `logs/run-20261010T032331Z.log` line 2862, under the judge banner at line 1538, **and** independently `pc4_detail` inside `results/verdicts_mistral_7b-instruct.json` | **contemporaneous, inspectable, doubly recorded** |
| `qwen2.5:7b-instruct` (table 5 arm) | FAIL, inherited | the same judge's earlier failure above. The verdict file says `"recorded on a previous run; not re-tested"`; that previous run is the released log | **contemporaneous for the original failure; the table-5 arm was not re-tested** |

### What `results/pc4_retest_declared.json` is, and is not

It is the **later, exploratory** re-test declared in register row D-1: 20
prompts on `qwen2.5:7b-instruct`, 3 mismatched, rate 0.15. That is the 3/20 figure the manuscript
cites. It is **not** the original PC-4 gate record and does not reinstate any halted arm; its own
`status` field says so. The original gate result for that judge is the 1-of-10 failure in the log.
The two must not be conflated: different sample sizes, different purposes, different dates.

Its rows carry `qid`, `set`, `identical`, `len_a`, `len_b`, `tok_a`, `tok_b` — lengths and token
counts, not response text, so the original response pairs were never retained. Anyone wanting to
re-examine the mechanism would have to generate new samples; we are not presenting these rows as a
substitute for that.

### Ten checks is a statement about ten checks

PC-4 sampled ten prompts per judge. Llama's PASS means those ten repeated byte-identically on an
immediate retry. **It is not evidence that the judge is deterministic over all 320 prompts**, and
the exploratory 20-prompt re-test on a different judge found 15% mismatches, which is a reason to
expect sampling to matter. Nothing in this artefact establishes determinism beyond the sampled
checks.

### Redaction

Both newly released files were passed through `redact_public.py` with the same token rules as the
verdict files. Both contain **zero** upstream spans at the 8-word and 12-word thresholds: the log
records control outcomes, counts and timings rather than judge prose, and the re-test rows carry
only lengths and token counts. So they ship unmodified, and that is a measured result rather than an
assumption — re-run `python3 redact_public.py --scan logs results/pc4_retest_declared.json` to
confirm.
