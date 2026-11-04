# Results and abstract

The abstract and the Results section of the article. Assembled into the manuscript by
`build_paper.py`; released so the documented build runs from a clone.

Pre-registration: https://osf.io/jw59c/ (DOI 10.17605/OSF.IO/JW59C), registered 2026-10-10 before
any judge run. Deviations are listed in the deviations register and referenced inline by number. The
per-judge control verdicts quoted below are recorded in the run log,
`logs/run-20261010T032331Z.log`, and the per-record counts in `results/verdicts_*.json`.

## 4.1 The headline: none of the three hypotheses is evaluable as registered

None of H1, H2 or H3 is evaluable as registered.

H1 reads from the temperature-0 VANILLA arm, and that arm did not survive for any of the three
judges. H3 reads from it too, and was additionally unevaluable for reasons independent of the
determinism failure, set out in the deviations register, D-9 and D-10: the VANILLA/COMPARING cell was never
generated, and no counterpart to the original's calibrated quantity was ever computed.

H2 is also not evaluable as registered. Under a post-registration deviation its unchanged test
was applied to the surviving MEC arms and reported descriptively; section 4.6 gives the figures
and the limits on reading them.

An earlier draft of this paper reported H2 as evaluated and inconclusive. That classification was
wrong, and it was corrected only after the null result was known; the deviations register, D-12 records the
reclassification, its timing and the referee reading that prompted it. The H2 numbers changed when a later frame error was corrected; the deviations register, D-18 gives the detail.

Two judges failed the pre-registered determinism control, PC-4, which requires that re-running a
prompt at temperature 0 with a fixed seed reproduce byte-identical output. The control checks ten
prompts per judge. Qwen2.5-7B-Instruct failed on 1 of 10 (question 77), Mistral-7B-Instruct on
2 of 10 (questions 33 and 52), and Llama-3.1-8B-Instruct on 0 of 10. In both failing cases the
registered rule, on the per-arm reading we adopted and disclose at D-15, halted the temperature-0
arm and the failure is reported here as a methods finding;
it was not converted into a correction term, which the pre-registration explicitly forbids.

Llama-3.1-8B-Instruct passed PC-4 and ran all three arms. Its temperature-0 data is nonetheless
unusable for the registered tests, for a different reason given in 4.3: under the registered parser
only 1 of 160 question-pair cells has both presentation orders parsed, so there is effectively no
paired data to test.

This is a negative result about the protocol under judge substitution, not a finding about
positional bias. We did not measure positional bias well enough to say anything about it.

## 4.2 What the determinism failure means for the original's assumption

The original states that it sets "the generated temperature to 0 for deterministic generation
results". On this stack that assumption did not hold for two of three judges. The effect is
intermittent: the prompt that failed for Qwen reproduced byte-identical output on four subsequent
isolated repeats. Those four repeats were themselves re-executions of the determinism check outside
any declared protocol, before D-1 existed. They are not a second registered test and we do not
treat them as one.

All three judges were checked on the same ten questions: the harness draws them with a fixed seed
(`random.Random(20261010)`) from a question file pinned by commit and checksum, so the draw is
identical across judges and reproducible from the released code. The three failures therefore fall
on three different questions, with none shared between judges. That observation is weak on its own
terms, 3 mismatches across 30 checks. A load or scheduling explanation would fit it; the D-1 re-test
below tested that explanation and did not support it. So the observation is reported as a
description of where the failures fell and not as evidence for any mechanism. Question 77 did recur
for the same judge in that re-test, which is the one point of continuity across the two runs.

A single controlled re-test was pre-declared in the deviations register, D-1 before the outcome was known,
and it has now run. It was exploratory and reinstated no halted arm. It does not support the load
explanation. Under the declared protocol - serial requests, `OLLAMA_NUM_PARALLEL=1`, the judge model
resident before the first call, nothing else issuing requests, all of which were INTENDED
conditions rather than enforced ones, since `pc4_retest.py` records the environment variable
and verifies none of the four, so whether they held is unverifiable from the artefact -, Qwen2.5-7B-Instruct differed on
3 of 20 prompt pairs, a mismatch rate of 0.15: 1 of the 10 originally checked questions and 2 of 10
newly drawn ones
(`results/pc4_retest_declared.json`, fields `n_prompts`, `n_mismatched`, `mismatch_rate`,
`mismatched`). The differences are substantial rather than marginal, for example 332 against 307
output tokens on question 77.

So temperature-0 non-determinism persisted under the one controlled condition we tested, serial requests to a server we intended to be otherwise idle with the model resident, conditions the re-test script records but does not verify, which is narrower than "contention removed" in general. We do not compare the two
rates: 3 of 20 against 1 of 10 cannot be distinguished at these sample sizes (Fisher exact,
two-sided, p = 1.00), so the re-test establishes persistence and not a change in magnitude. We
therefore do not attribute the non-determinism to load or scheduling. We also
do not offer a replacement explanation: identifying the mechanism would need instrumentation below
the inference server, which this study does not have. What we can say is that on this stack, for
this judge, a fixed seed and temperature 0 did not produce reproducible output under the one
condition the artefact records: the script issued its requests serially. Server-side state was not
observed, so we cannot say the server was handling one request at a time.

The practical reading, stated for the models we ran and not beyond them: on these locally served
7-8B models, temperature 0 did not guarantee identical output, and a conflict rate computed without
a determinism check cannot separate run-to-run variation from positional bias. That is the
ambiguity PC-4 was written to detect, and it detected it.

We make no claim about the original's own numbers. Its judges were different models served
differently, and three locally served models on one stack cannot speak to them.

## 4.3 Parse accounting (PC-5), and one parser artefact

PC-5 requires unparseable outputs to be counted and reported per judge, never dropped. Counts for
the arms that ran:

| judge | arm / template | records | parsed (registered) | unparseable |
|---|---|---|---|---|
| Llama-3.1-8B | VANILLA / SCORING | 320 | 7 | 313 (97.8%) |
| Llama-3.1-8B | MEC / SCORING_CODE | 160 | 159 | 1 (0.6%) |
| Llama-3.1-8B | MEC / COMPARING | 160 | 109 | 51 (31.9%) |
| Llama-3.1-8B | noise / SCORING_CODE | 80 | 80 | 0 |
| Llama-3.1-8B | noise / COMPARING | 80 | 73 | 7 (8.8%) |
| Mistral-7B | MEC / SCORING_CODE | 160 | 160 | 0 |
| Mistral-7B | MEC / COMPARING | 160 | 133 | 27 (16.9%) |
| Mistral-7B | noise / SCORING_CODE | 80 | 80 | 0 |
| Mistral-7B | noise / COMPARING | 80 | 71 | 9 (11.2%) |

A record counts as parsed if ANY of its k = 3 samples parsed, so the record-level rates above
understate how often an individual generation failed. Sample-level accounting, which the record
level hides:

| judge | arm / template | records | unparsed records | samples | unparsed samples |
|---|---|---|---|---|---|
| Llama-3.1-8B | VANILLA / SCORING | 320 | 313 (97.8%) | 320 | 313 (97.8%) |
| Llama-3.1-8B | MEC / SCORING_CODE | 160 | 1 (0.6%) | 480 | 116 (24.2%) |
| Llama-3.1-8B | MEC / COMPARING | 160 | 51 (31.9%) | 480 | 359 (74.8%) |
| Llama-3.1-8B | noise / SCORING_CODE | 80 | 0 | 240 | 69 (28.8%) |
| Llama-3.1-8B | noise / COMPARING | 80 | 7 (8.8%) | 240 | 159 (66.2%) |
| Mistral-7B | MEC / SCORING_CODE | 160 | 0 | 480 | 9 (1.9%) |
| Mistral-7B | MEC / COMPARING | 160 | 27 (16.9%) | 480 | 250 (52.1%) |
| Mistral-7B | noise / SCORING_CODE | 80 | 0 | 240 | 1 (0.4%) |
| Mistral-7B | noise / COMPARING | 80 | 9 (11.2%) | 240 | 116 (48.3%) |
| Qwen2.5-7B | MEC / SCORING_CODE | 160 | 0 | 480 | 9 (1.9%) |
| Qwen2.5-7B | MEC / COMPARING | 160 | 0 | 480 | 0 |
| Qwen2.5-7B | noise / SCORING_CODE | 80 | 0 | 240 | 0 |
| Qwen2.5-7B | noise / COMPARING | 80 | 0 | 240 | 0 |

Every arm that ran is listed, including Qwen2.5's four cells and the two noise cells an earlier
draft omitted. Qwen2.5 has no VANILLA row because its temperature-0 arm was halted by PC-4 before
producing any record, and Mistral-7B has none for the same reason.

This changes how the MEC arms should be read. At record level Llama-3.1's MEC/SCORING_CODE arm looks
almost clean at 0.6% unparseable; at generation level 24.2% of its samples failed to parse, and the
majority vote over k = 3 concealed that. Llama-3.1's and Mistral-7B's COMPARING arms fail on half to
three quarters of individual generations. Only Qwen2.5 is clean at both levels. Any statement that
"the MEC arms are clean" holds at record level only, and we do not make it without that
qualification.

The 97.8% figure needs explaining, because on its own it would imply that Llama-3.1 cannot score a
pair of answers. It can. It emits a markdown label and then the two scores on the next line:

    **Overall Scores:**
    8.5 9.0

    **Evaluation Explanation:**

The registered parser requires the two scores on the first line, so it does not reach them. This is
a limitation of our measurement rule meeting a formatting habit of the model, and both halves of
that sentence matter.

We did not change the registered parser. A secondary parser is declared in the deviations register, D-5, which
records that its rule was chosen after the outputs were seen and that the recovered count was known
before the rule was written. It skips leading lines that are only a markdown heading or emphasis
label, then applies the unchanged regex to the first remaining non-empty line. Its skip rule is broader than a markdown label: the pattern matches any line of letters and spaces, so a
short punctuation-free prose line is skipped too. Reviewer 1 on #142 gave the example `Both were
helpful overall` followed by `9 8`, which the released parser accepts; we reproduced it. In the 274
records actually recovered the skipped labels were all `**Overall Scores:**` or `**Scores:**`, so
the broader rule did not change the recovery count, and the guard is left as implemented rather
than tightened after the fact.

Under that secondary parser, 281 of 320 VANILLA records parse, recovering 274. The 313 strict
failures therefore split into two groups rather than one: 274 follow the markdown-label pattern and
are recovered, and the remaining 39 use other formats that the secondary rule does not reach and
which we did not characterise further. Paired cells with
both orders parsed go from 1 of 160 under the registered parser to 132 of 160 under the secondary
one. Every figure from the secondary parser is exploratory in the sense of D-5 and is reported here
beside its registered counterpart, never in place of it. And the recovery does not make this judge
a clean one: Llama-3.1 remains above the registered 10% PC-5 flag under both parsers, at 97.8%
unparseable under the registered rule and 12.2% under the secondary rule, so it is reported as a
high-unparseable judge either way.

## 4.4 The COMPARING template carries its declared confound

COMPARING shows elevated unparseable rates on two of the three judges that ran it. Qwen2.5 parsed all 160 of its COMPARING records with none unparseable. The elevated rates belong to
the other two judges: 31.9% and 8.8% for
Llama-3.1, 16.9% and 11.2% for Mistral-7B. The same judges on the authors' own released SCORING
prompt sit at 0.6% and 0.0%.

The pre-registration already declares our COMPARING prompt as a reconstruction, because the
original prints it nowhere: not in the paper, which has no appendix, and not in the released code,
which implements only the scoring prompt. The contrast above is consistent with the reconstruction
being implicated in the parse failures, though Qwen2.5 parsed the same reconstruction perfectly, which
points to an interaction between judge and template rather than to the template alone. We therefore report the COMPARING
arm with that confound attached and draw no conclusion from it about judge behaviour.

## 4.5 What the surviving data supports

The MEC arms on the authors' own released prompt are clean AT RECORD LEVEL: 0.6% unparseable for
Llama-3.1 and 0.0% for Mistral-7B. At sample level they are not, as 4.3 sets out: 24.2% of
Llama-3.1's individual generations on that arm failed to parse and the majority vote hid it. Quantities internal to the MEC arms are therefore computable, including the
self-inconsistency rate from the identical-order noise control. Those results are reported in 4.6.

What cannot be done is the comparison the study was built around. Every registered hypothesis
contrasts something against VANILLA, and VANILLA is gone for two judges by the determinism control
and effectively gone for the third by the parse rule.

## 4.6 Results from the surviving arms

Everything in this section is DESCRIPTIVE, including the H2 figures: they come from the registered
test applied under a post-registration deviation to arms that are not the registered setting. Nothing here is a test of H1 or H3: both read from the temperature-0 VANILLA arm,
which is halted for two judges and yields one contributing pair for the third. Computed by `analyze_mec.py` from
`results/verdicts_*.json`.

Accuracy and Cohen's kappa are against the 80 released human labels, whose marginals are ChatGPT 41,
tie 14, Vicuna-13B 25. Kappa is reported with PABAK, and the matched-marginal chance agreement pe is printed by
`analyze_mec.py` for every cell though it is not carried in the table below, as
the analysis plan requires.

| judge | template | order | n | accuracy | kappa | PABAK |
|---|---|---|---|---|---|---|
| Llama-3.1-8B | SCORING_CODE | AB | 80 | 0.588 | 0.315 | 0.175 |
| Llama-3.1-8B | SCORING_CODE | BA | 79 | 0.557 | 0.249 | 0.114 |
| Mistral-7B | SCORING_CODE | AB | 80 | 0.537 | 0.181 | 0.075 |
| Mistral-7B | SCORING_CODE | BA | 80 | 0.525 | 0.221 | 0.050 |
| Qwen2.5-7B | SCORING_CODE | AB | 80 | 0.600 | 0.259 | 0.200 |
| Qwen2.5-7B | SCORING_CODE | BA | 80 | 0.512 | 0.226 | 0.025 |

Random-order MEC accuracy, computed by resampling the stored both-order verdicts as the
pre-registration specifies in place of 100 fresh random-order runs. This is NOT the original's
Balanced Position Calibration: BPC averages the numeric scores across both orders before deciding,
and no BPC quantity was computed in this study (the deviations register, D-10). On SCORING_CODE the figures are, each with a 95% bracket from 1,000 draws over presentation
orders, Llama-3.1 0.576
[0.519, 0.633], Mistral-7B 0.532 [0.463, 0.600] and Qwen2.5 0.556 [0.487, 0.625]. The original reports 53.2% for MEC on its SCORING template with ChatGPT as evaluator, and all
three of our open-weight judges land around or slightly above that figure. THIS IS A DESCRIPTIVE
BENCHMARK, NOT A LIKE-FOR-LIKE REPLICATION, and not a confirmation that calibration recovers
accuracy: our aggregation is a majority vote over three samples where the original averages
numeric scores, our judges are open-weight and quantised where theirs was ChatGPT, and the arm
these figures come from is not the one the registration named. An earlier version of this paper reported
0.429, 0.419 and 0.456 and concluded that all three sat below the original; that comparison was an
artefact of the frame error recorded in the deviations register, D-16, and it reverses.

Conflict rate on the MEC arm, with the identical-order self-inconsistency rate from the noise
control subtracted as section 4.2 of the pre-registration requires:

| judge | template | n | c | s | c - s | 95% CI |
|---|---|---|---|---|---|---|
| Llama-3.1-8B | SCORING_CODE | 79 | 0.316 | 0.278 | 0.038 | [-0.089, +0.165] |
| Mistral-7B | SCORING_CODE | 80 | 0.375 | 0.237 | 0.138 | [+0.000, +0.275] |
| Qwen2.5-7B | SCORING_CODE | 80 | 0.475 | 0.225 | 0.250 | [+0.100, +0.400] |
| Llama-3.1-8B | COMPARING | 42 | 0.881 | 0.071 | 0.810 | [+0.667, +0.929] |
| Mistral-7B | COMPARING | 55 | 0.018 | 0.018 | 0.000 | [-0.055, +0.055] |
| Qwen2.5-7B | COMPARING | 80 | 0.287 | 0.075 | 0.212 | [+0.100, +0.325] |

Intervals are question-clustered bootstrap, 10,000 resamples, seed 1234, computed by
`analyze_mec.py` function `cs_intervals`. n counts questions with both MEC orders parsed AND a
parsed noise repeat, so it is smaller than the per-arm record counts; it is reported rather than
left implicit. One of the three SCORING_CODE intervals, Qwen2.5's [+0.100, +0.400], strictly excludes zero.
Mistral-7B's lower bound is exactly zero, so its interval does not exclude zero, and Llama-3.1's
[-0.089, +0.165] includes it. Of the three COMPARING intervals, only Mistral-7B's [-0.055, +0.055] includes zero,
while Llama-3.1's [+0.667, +0.929] and Qwen2.5's [+0.100, +0.325] exclude it. An earlier version of
this paper said all three SCORING_CODE intervals excluded zero and that both COMPARING intervals
included it; both statements were wrong, and the second miscounted the rows as well.

What c - s supports, and what it does not. The quantity c - s is the pre-registered operational
measure of order dependence, so on the SCORING_CODE template we can say that these judges' verdicts
change with presentation order beyond their own same-order noise by 0.038, 0.138 and 0.250 on the
scoring template, with Llama-3.1's interval including zero. That is a
descriptive statement about the MEC arm. It is not a test of H1, which is registered on the halted
temperature-0 arm.

The accuracy gap between presentation orders is small on the scoring template once the frame error
is corrected: 0.588 against 0.557 for Llama-3.1, 0.537 against 0.525 for Mistral-7B, 0.600 against
0.512 for Qwen2.5. An earlier version of this paper reported gaps of around 0.3 and built an
argument about an unexplained order-dependent asymmetry on them. Those gaps were an artefact of our
own analysis error and that argument is withdrawn; the deviations register, D-16 gives the detail.

An earlier version of this paper said the H2 figures were unaffected by that correction because
they were slot-frame quantities. THAT WAS FALSE and is withdrawn: two analysis functions each
carried their own order-conditional remap, so the H2 table and the content-blind shares were wrong
in every row. The deviations register records it at D-18, and the figures below are the corrected ones.

### Content-blind benchmark (exploratory, added after the results were seen; not registered)

A judge that ignored the answers entirely and chose by slot alone would still show an accuracy gap
between the two orders, purely because the human labels are not symmetric across slots. This table
asks how much of each cell's observed gap such a content-blind judge would reproduce, using that
judge's own slot and tie shares.

| judge | template | order | p(slot 1) | p(slot 2) | p(tie) | observed gap | content-blind gap |
|---|---|---|---|---|---|---|---|
| Llama-3.1-8B | SCORING_CODE | AB | 0.425 | 0.575 | 0.000 | +0.031 | -0.013 |
| Llama-3.1-8B | SCORING_CODE | BA | 0.506 | 0.494 | 0.000 | | |
| Llama-3.1-8B | COMPARING | AB | 0.982 | 0.018 | 0.000 | +0.121 | +0.165 |
| Llama-3.1-8B | COMPARING | BA | 0.925 | 0.075 | 0.000 | | |
| Mistral-7B | SCORING_CODE | AB | 0.613 | 0.388 | 0.000 | +0.012 | +0.045 |
| Mistral-7B | SCORING_CODE | BA | 0.613 | 0.388 | 0.000 | | |
| Mistral-7B | COMPARING | AB | 0.015 | 0.000 | 0.985 | +0.040 | +0.026 |
| Mistral-7B | COMPARING | BA | 0.015 | 0.000 | 0.985 | | |
| Qwen2.5-7B | SCORING_CODE | AB | 0.738 | 0.263 | 0.000 | +0.088 | +0.090 |
| Qwen2.5-7B | SCORING_CODE | BA | 0.713 | 0.287 | 0.000 | | |
| Qwen2.5-7B | COMPARING | AB | 0.237 | 0.037 | 0.725 | -0.025 | -0.013 |
| Qwen2.5-7B | COMPARING | BA | 0.163 | 0.225 | 0.613 | | |

The content-blind prediction is computed on the SAME parsed questions as the observed figure
beside it. An earlier version drew the human label marginals from all 80 registered questions
while observing on parsed records only, so the two sides of each comparison rested on different
question sets wherever a cell had unparsed records; three of the six cells changed when that was
corrected. The deviations register records it.

Gaps are per template, not per order, so they appear once on each pair of rows. There is
deliberately NO "fraction of the gap reproduced" column: after the frame correction several observed
gaps are close to zero, Mistral-7B's on SCORING_CODE is 0.012, and a ratio of two near-zero numbers
is numerically unstable and tells a reader nothing. Both gaps are printed in the same units, so a
reader who wants the ratio can form it and will see how little it rests on.

The figure that matters most here is Mistral-7B on SCORING_CODE: p(slot 1) is 0.613 in BOTH orders.
That is a stable preference for the first slot, invariant to which candidate occupies it, and it was
invisible before the frame correction in the deviations register, D-18, because the earlier analysis re-flipped
the BA records and made the two orders look like mirror images. Qwen2.5's content-blind gap on
SCORING_CODE, +0.090 against an observed +0.088, is the one cell where slot shares alone account for
essentially the whole observed gap.

This table is exploratory. It was not registered, it was added after the results were seen, and no
mechanism is claimed from it.

These judges almost never emit a tie on the SCORING_CODE template, while the human labels tie on 14 of
80 questions. That caps achievable accuracy at roughly 0.825 before order enters, and it accounts
for part of the distance between our numbers and the original's.

Verdict distribution per judge and template, over parsed verdicts, so a reader can see when a
conflict rate is carrying information and when it is not:

| judge | template | n | slot 1 ("A") | slot 2 ("B") | tie | |
|---|---|---|---|---|---|---|
| Llama-3.1-8B | SCORING_CODE | 159 | 46.5% | 53.5% | 0.0% | |
| Llama-3.1-8B | COMPARING | 109 | 95.4% | 4.6% | 0.0% | near-constant |
| Mistral-7B | SCORING_CODE | 160 | 61.3% | 38.8% | 0.0% | |
| Mistral-7B | COMPARING | 133 | 1.5% | 0.0% | 98.5% | near-constant |
| Qwen2.5-7B | SCORING_CODE | 160 | 72.5% | 27.5% | 0.0% | |
| Qwen2.5-7B | COMPARING | 160 | 20.0% | 13.1% | 66.9% | |

Two cells are flagged near-constant. The flag marks any cell where one verdict category exceeds 90%
of parsed verdicts, and that 90% threshold was chosen by us after seeing these data; it is a
reporting flag and not a pre-registered rule, which is why the raw shares are printed above so a
reader can apply any threshold they prefer. See the deviations register, D-7.

For the two flagged cells we still print the conflict rates. Only ONE of them should be read as
uninformative, and the distinction is worth stating because it is not obvious: near-constant output
drives the conflict rate in opposite directions depending on WHICH verdict is constant. Mistral-7B
returns a tie on 98.5% of its parsed COMPARING items, and a constant tie cannot flip when the
candidates swap, so its conflict rate c = 0.018 is near zero for an arithmetic reason and carries no
information about order sensitivity. Llama-3.1 returns the FIRST SLOT on 95.4% of its parsed items,
and a constant slot choice flips the candidate every time the order swaps, so its conflict rate
c = 0.881 is near its maximum for the same arithmetic reason - and that is an informative position
effect, not an artefact. The figures are those in the c - s table above,
on the single common-set definition used throughout: Llama-3.1 COMPARING c = 0.881, s = 0.071,
c - s = 0.810 on n = 42; Mistral-7B COMPARING c = 0.018, s = 0.018, c - s = 0.000 on n = 55.
Earlier drafts carried a second pair of values for these cells computed over each quantity's own
available set; the common-set definition is now used everywhere and its denominator is stated. Mistral-7B's net order-dependence c - s of 0.000, with a conflict rate c of 0.018, follows from
returning a tie on 98.5% of parsed items. It is not evidence that the judge is
unaffected by presentation order, and it must not be read that way.

The pre-registration has an interpretation rule for the opposite failure, a judge whose
self-inconsistency approaches its conflict rate. It has no rule for a judge that answers almost
identically on every item, and we have not invented one.

### H2, as computed under the D-8 deviation (descriptive)

Signed first-position minus second-position win rate, per judge, on every surviving both-order arm.
Intervals are at the Holm most-stringent level, 1 - 0.05/3 = 98.33%, for the reason given in the
D-8 amendment. Computed by `analyze_mec.py` function `h2`, reproduced from the results files.

| judge | arm | signed difference | 98.33% interval | n records | excluded unparsed | questions dropped |
|---|---|---|---|---|---|---|
| Llama-3.1-8B | SCORING_CODE | -0.063 | [-0.215, +0.089] | 158 | 1 | 1 |
| Mistral-7B | SCORING_CODE | +0.225 | [+0.075, +0.375] | 160 | 0 | 0 |
| Qwen2.5-7B | SCORING_CODE | +0.450 | [+0.312, +0.588] | 160 | 0 | 0 |
| Llama-3.1-8B | COMPARING | +0.884 | [+0.767, +0.977] | 86 | 51 | 23 |
| Mistral-7B | COMPARING | +0.017 | [+0.000, +0.069] | 116 | 27 | 17 |
| Qwen2.5-7B | COMPARING | +0.069 | [-0.013, +0.156] | 160 | 0 | 0 |

The registered decision rule asks whether any two judges differ in SIGN with NON-OVERLAPPING
intervals. Every pair, on both arms:

| arm | pair | opposite sign | non-overlapping | qualifies |
|---|---|---|---|---|
| SCORING_CODE | Llama-3.1 vs Mistral-7B | yes | no | no |
| SCORING_CODE | Llama-3.1 vs Qwen2.5 | yes | **yes** | **yes** |
| SCORING_CODE | Mistral-7B vs Qwen2.5 | no | no | no |
| COMPARING | Llama-3.1 vs Mistral-7B | no | yes | no |
| COMPARING | Llama-3.1 vs Qwen2.5 | no | yes | no |
| COMPARING | Mistral-7B vs Qwen2.5 | no | no | no |

Each complete pair contributes two records, so n records is twice the number of contributing
questions: 158 records is 79 questions for Llama-3.1 on SCORING_CODE, 86 is 43 questions for its
COMPARING cell. Questions dropped are those where only one presentation order parsed, which the
registration excludes from a paired test.

On SCORING_CODE one pair qualifies: Llama-3.1 leans toward the second slot (-0.063) and Qwen2.5
toward the first (+0.450), and their intervals do not overlap. That is the criterion H2's registered
test names. On COMPARING no pair qualifies, because all three judges lean the same way.

WHAT THIS IS AND IS NOT. It is NOT a confirmation of H2. H2 is not evaluable as registered: the
registered claim is scoped to the Table 1 temperature-0 arm, which produced no analysable data, and
that is unchanged. What the table shows is a descriptive result on arms the registration did not
name, computed under a post-registration deviation, on judges whose temperature-0 determinism we
could not establish.

Two further reasons for caution, both of which weigh against us. First, an earlier version of this
paper reported the opposite outcome on this arm, because the analysis was wrong; this result exists
only because referees found that error, and it arrived in our favour, which is a reason for more
scrutiny rather than less. Second, the surviving arms use Multiple Evidence Calibration, the
original's own remedy for positional bias, so they are a weak setting in which to learn anything
about a claim made on the uncalibrated template.

One reading in an earlier version also falls. Llama-3.1's COMPARING cell was described as
"uninformative because the output is near-constant". Its corrected signed slot share is +0.884 with
an interval of [+0.767, +0.977]. A judge that selects the first slot on almost every item is not
uninformative about slot position; it carries the strongest slot-position signal in this study. The
D-7's near-constant flag applies to the OUTPUT of both cells, but its uninformativeness
conclusion holds only for Mistral-7B, whose constant verdict is a tie and whose conflict rate is
therefore near zero by arithmetic. Llama-3.1's constant verdict is a SLOT, so a swap flips the
candidate every time and its conflict rate of 0.881 sits near its maximum for the same arithmetic
reason. Both its conflict rate and its slot share of +0.884 measure one real position effect, and
nothing about Llama-3.1's COMPARING cell is uninformative.


The pre-specified score-gap analysis (C-3) is not reported here. It needs the scoring template's
numeric scores, and the registered binning was specified for the VANILLA arm.

## 4.7 One operational loss, disclosed

Qwen2.5-7B-Instruct's MEC arm was executed twice. The first execution completed and its output was
then destroyed by an output-path collision in our own harness; the arm was re-executed and the
re-execution is the data of record. The loss, what can and cannot be cross-checked, and the fix are
recorded in the deviations register, D-6.

---

# Abstract (draft, conservative)

CLEARED FOR BUILD by ruling an internal review decision, with its two required edits applied and its optional
descriptive sentence included. No figure from the secondary parser appears here, and nothing here
is stated as a test of a hypothesis.

@wang2024 report that large language models used as pairwise evaluators reverse their
verdicts when the two candidate answers are swapped, and propose three calibration strategies, one of which, Multiple Evidence Calibration, this study replicates; they report that these
strategies recover alignment with human labels. Their judges were closed OpenAI endpoints, and the snapshot
pinned in their repository is not in the provider's current model list, so their numbers can no longer be reproduced with the original judges.
We pre-registered a replication that repeats their published protocol while substituting three
open-weight instruction-tuned judges, and report it here.

None of the three pre-registered hypotheses is evaluable as registered. All three read from a
temperature-0 arm that did not survive: a determinism control we registered
before running found that two of the three judges failed to reproduce byte-identical output at
temperature 0 with a fixed seed, which halted their temperature-0 arms by the rule we had committed
to, and the third judge's output did not satisfy the registered output-format parser for 313 of its
320 records. H3 was additionally unevaluable for a reason independent of that: one of its two
required cells was never generated, and no counterpart to the original's calibrated quantity was
ever computed. H2 was not evaluable as registered, because the registered Table 1 temperature-0 VANILLA arm
produced no analysable data. Under a post-registration deviation (the deviations register, D-8), fixed before any
H2 statistic was computed, the unchanged test was applied to every surviving both-order MEC arm and
the descriptive criterion was met on SCORING_CODE - one pair, Llama-3.1 against Qwen2.5, with
opposite signs and non-overlapping intervals - and was not met on COMPARING. H2 remains NOT
evaluable as registered; these results are descriptive only.
Under the asymmetry declared in advance, a null is never written as a refutation. A single pre-declared re-test
under serial requests, run on the one judge that had failed first (Qwen2.5-7B-Instruct), found the
non-determinism persisted for that judge under the one controlled condition we tested, serial requests to a server we intended to be otherwise idle with the model resident, conditions the re-test script records but does not verify, which is narrower than "contention removed" in general, so we do not attribute it to
load.

The temperature-1 arms survived and are reported descriptively. On those arms, and as a description
rather than a test, verdicts changed with presentation order beyond each judge's own same-order
noise - by 0.038, 0.138 and 0.250 on the scoring template, and most strongly by 0.810 on the
reconstructed COMPARING prompt. We also report what the failures
cost, the parse accounting per judge and arm, one operational data loss of our own, and every
deviation from the registered plan, each dated. The replication's contribution is therefore not a
verdict on positional bias. It is a demonstration that a protocol resting on temperature-0
determinism and on a strict output format can fail to execute on open-weight judges, and a record
of exactly where and how it failed.

Pre-registration: https://osf.io/jw59c/ (DOI 10.17605/OSF.IO/JW59C).
