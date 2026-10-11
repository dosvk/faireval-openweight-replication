# Does positional bias in LLM-as-judge evaluation, and its calibration fix, hold for open-weight judges?

Code and results for a pre-registered replication of Wang et al. (2024), *Large Language Models are
not Fair Evaluators* (ACL 2024), substituting three open-weight instruction-tuned judges for the
closed judges of the original.

**Pre-registration:** https://osf.io/jw59c/ — DOI 10.17605/OSF.IO/JW59C

## The headline result

**None of the three pre-registered hypotheses is evaluable as registered.** Two of the three judges
failed a pre-registered temperature-0 determinism control, which halted their temperature-0 arms as
the registration required; the third judge's output defeated the registered parser on 313 of 320
records.

This is **not** a claim that the original finding is false. It reports that a pre-registered
protocol proved non-executable on these systems. The surviving temperature-1 arms are reported
descriptively in the article.

## Read `DEVIATIONS.md` first

Every departure from the registered plan is recorded there, dated, with the original wording left
intact beside every later correction. That includes corrections to the register's own earlier
entries — notably **D-16** and **D-18**, where an analysis error of ours was found by referees and
two descriptive claims reversed as a result.

The register is the honest record of how this study actually went. It is longer than the article.

## What is here

| path | what it is |
|---|---|
| `run_replication.py` | the harness: arms, prompts, controls PC-1 to PC-5 |
| `analyze_mec.py` | all reported statistics, with `FRAME=1` and `CSCHECK=1` selftests |
| `relaxed_parse.py` | the secondary parser, exploratory use only |
| `pc4_retest.py` | the determinism re-test |
| `redact_public.py` | produces the redacted public results; `--assert-stats` proves no statistic moves |
| `sweep.py` | the stale-claim checker used on the manuscript |
| `hydrate_faireval.py` | fetches and verifies the upstream inputs at a pinned commit |
| `results/` | per-judge verdict files, **redacted** (see below) |
| `DEVIATIONS.md` | the dated deviations register |
| `DATA-AVAILABILITY.md` | what is and is not released, and why |
| `metadata.yaml` | ReScience C submission metadata |

## The results files are redacted, and why

A judge's raw output routinely quotes the question and both candidate answers back verbatim. Those
are upstream FairEval text, and that repository carries no licence, so the registration commits this
study to redistributing none of it.

Every maximal run of **eight or more** consecutive words occurring verbatim in the upstream
questions or candidate answers is therefore replaced by:

    [upstream span redacted, sha256:<first 16 hex of the removed span>]

1,509 of 4,640 samples were affected; 2,130 spans removed. The hash lets anyone holding the upstream
corpus confirm exactly what was taken out without us republishing it.

**Redaction does not move any number.** Every statistic in the article is computed from the
unredacted files, and `python3 redact_public.py --assert-stats` recomputes the H2 figures, the
content-blind gaps and the c−s values from both the originals and the redacted copies and requires
exact equality. See `DEVIATIONS.md`, D-21.

## Reproducing

```
python3 hydrate_faireval.py          # fetch + verify inputs at the pinned commit
python3 run_replication.py --help    # arms and controls
python3 analyze_mec.py               # the reported statistics
FRAME=1   python3 analyze_mec.py     # frame selftest
CSCHECK=1 python3 analyze_mec.py     # one-definition check for c - s
python3 redact_public.py --selftest  # redaction behavioural tests
```

Inference ran locally through Ollama 0.30.8 on an Apple M4 Pro with 48 GB unified memory. All three
judges are Q4_K_M quantised builds, which the registration did not anticipate — see `DEVIATIONS.md`,
D-19.

**Expect to reproduce the pipeline and the controls. Do not expect byte-identical verdicts:** this
paper's own finding is that two of three judges were not reproducible at temperature 0.

## Licence

Code and results: MIT (see `LICENSE`). The FairEval inputs and the model weights are **not** covered
— see the NOTICE section of `LICENSE`.
