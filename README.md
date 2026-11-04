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
| `hydrate_faireval.py` | verifies the upstream inputs at a pinned commit |
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

## Reproducing from a clean checkout

Reviewer 1 on ReScience #142 (2026-11-04) found the previous instruction unusable: `python3
hydrate_faireval.py` exits with usage text because it is a **verifier**, not a fetcher, and
`analyze_mec.py` assumed a hard-coded input root. Both are fixed. This is the complete path.

**1. Obtain the pinned upstream inputs.** They are third-party and unlicensed, so this repository
cannot contain them (see `DATA-AVAILABILITY.md`). Clone at the pinned commit:

```
git clone https://github.com/i-Eval/FairEval /tmp/FairEval
git -C /tmp/FairEval checkout 453c117a69159fd7b7de2f4e0519bac57bee21f4
```

**2. Verify them.** `hydrate_faireval.py` takes the checkout path and checks SHA-256 and byte length
of all six input files. It exits non-zero on any mismatch.

```
python3 hydrate_faireval.py /tmp/FairEval
```

**3. Recompute the reported tables.** Pass the same path with `--inputs`, or set `P10_INPUTS`:

```
python3 analyze_mec.py --inputs /tmp/FairEval              # all reported tables
P10_INPUTS=/tmp/FairEval python3 analyze_mec.py            # equivalent
```

Individual tables and the self-checks:

```
CB=1      python3 analyze_mec.py --inputs /tmp/FairEval     # content-blind gaps
H2=1      python3 analyze_mec.py --inputs /tmp/FairEval     # H2 descriptive table
CS=1      python3 analyze_mec.py --inputs /tmp/FairEval     # c - s estimates and intervals
FRAME=1   python3 analyze_mec.py --inputs /tmp/FairEval     # verdict-frame self-check
CSCHECK=1 python3 analyze_mec.py --inputs /tmp/FairEval     # one-definition check for c - s
```

Other checks that need no inputs:

```
python3 verify_parser_pins.py --check    # the four parser pins, under the stated convention
python3 redact_public.py --selftest      # redaction behavioural tests
python3 redact_public.py --scan results logs   # no verbatim upstream text in released files
python3 sweep.py --selftest              # stale-claim checker
```

### What this does and does not reproduce

These commands **recompute statistics from the released verdict files**. They do **not** re-run model
generation: that requires Ollama, the three judge models, and roughly seven hours on comparable
hardware, and this paper's own finding is that two of the three judges were not reproducible at
temperature 0, so re-running would not return byte-identical verdicts. Reproducing the numbers and
reproducing the generation are different claims, and only the first is available from this artefact.

The released verdict files are **redacted** of verbatim upstream spans. The assertion that redaction
moves no statistic is checked against the unredacted originals, which are not released — so that
particular equality is not independently checkable from this repository, as Reviewer 1 noted. What
is independently checkable is that every released sample reparses to its stored verdict and that
record aggregation reproduces the stored majority votes, both of which the reviewer confirmed.

### The hardware and models this ran on

Inference ran locally through Ollama 0.30.8 on an Apple M4 Pro with 48 GB unified memory. All three
judges are Q4_K_M quantised builds, which the registration did not anticipate; see `DEVIATIONS.md`,
D-19.

**Expect to reproduce the pipeline and the controls. Do not expect byte-identical verdicts:** this
paper's own finding is that two of the three judges were not reproducible at temperature 0.

### Building the article

`build_paper.py` needs `SECTIONS-DRAFT.md` and `RESULTS-DRAFT.md`, which are now released:

```
python3 build_paper.py          # writes build/p10.pdf
```

The submitted artefact is the ReScience C template build in `article/article.pdf`; `build/p10.pdf`
is a pandoc build retained for diffing and is **not** the submitted paper.


## Licence

Code and results: MIT (see `LICENSE`). The FairEval inputs and the model weights are **not** covered
— see the NOTICE section of `LICENSE`.
