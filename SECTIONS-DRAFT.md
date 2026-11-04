# Front matter, Introduction, Related Work, Methods, Discussion, References

The narrative sections of the article (Introduction, Related work, Methods, Discussion). Assembled
into the manuscript by `build_paper.py`; released so the documented build runs from a clone.

Every citation below was verified before it was written: Wang et al. by its DOI and the fetched PDF,
Zheng et al. independently through OpenAlex (two records, arXiv and NeurIPS), the FairEval
repository by cloning it at the pinned commit, the model identities by local digest, the venue
policy by fetching the ReScience C author guidelines, and our own registration by its DOI. Nothing
is cited from memory.

---

# 1 Introduction

Large language models are now routinely used to score other models' outputs. The appeal is obvious:
a judge model is cheaper than a human annotator and available on demand. The risk is equally
obvious, and @wang2024 demonstrated one form of it. They showed that an LLM asked to pick
the better of two answers can reverse its verdict when the two answers are swapped in the prompt,
reported conflict rates as high as 82.5% under such a swap, and proposed three calibration strategies. This study replicates
ONE of them, Multiple Evidence Calibration. Balanced Position Calibration was not run: no BPC
quantity was computed at any point, which is one of two independent reasons H3 is not evaluable
(see the deviations register).

That result matters to anyone who uses a judge model, and it invites a direct question. The original
used two closed OpenAI endpoints as judges. The snapshot pinned in its repository,
`gpt-3.5-turbo-0301`, is not in the provider's current model list, so the original's numbers can no longer be reproduced
with the original judges by anyone, including its authors. Does the finding survive when the judge
is an open-weight model that anyone can download and pin by digest?

We pre-registered a replication to answer that [@prereg]. Registration preceded every confirmatory arm. It
did not precede all contact with the data: the registration itself discloses a 6-call pilot and a
9-call output-format check on 3 of the 80 questions, run before registering
(https://osf.io/jw59c/, DOI 10.17605/OSF.IO/JW59C). The design repeats the published protocol and
varies one technical detail deliberately, the judge, which is the kind of variation a replication involves. Three open-weight instruction-tuned models from three
different families stand in for those endpoints.

The answer is that we could not run the registered test, and the reason is itself the finding.

The pre-registration included a determinism control, written before any run, requiring that
re-running a prompt at temperature 0 with a fixed seed reproduce byte-identical output. The original
states that it sets "the generated temperature to 0 for deterministic generation results", and
H1 and H3 both read from that temperature-0 arm, and H2's scope is discussed in the deviations register. Two of our three judges
failed the control. On the reading we adopted, the registered rule halted their temperature-0 arms (D-15), and we did not convert the
failure into a correction term, because the pre-registration explicitly forbids that. The third
judge passed the control but produced output that did not satisfy the registered output-format
parser on 313 of 320 records, leaving one usable paired observation.

So H1 and H3 are not evaluable as registered, and H2 is not evaluable as registered either. On the
reading we adopt, H2's registered claim C-2 is scoped to the Table 1 temperature-0 VANILLA
template, which produced no analysable data; that scope was established after the null was known and
is recorded, with the earlier alternative reading that the registration bound H2 to no particular
arm, in the deviations register at D-12. What the surviving arms show about H2 is therefore
reported descriptively rather than as a test, and D-18 records the correction that changed
what those arms appear to show. This paper reports that outcome, what survived,
and what it cost, with every deviation from the registered plan dated and listed. We are explicit
about what this is not: it is not evidence that the original result is false. It is evidence that a
protocol resting on temperature-0 determinism and on a strict output format does not transfer
unchanged to open-weight judges served locally.

# 2 Related work

Judge models and their failure modes. @zheng2023 introduced the MT-Bench and Chatbot Arena
evaluations. @wang2024, the study replicated here, isolates the swap-induced verdict
reversal, quantifies it as a conflict rate, and proposes three calibration strategies, of which this study replicates one, Multiple Evidence Calibration. The 80-question
item set we use is the one distributed in the original's own repository; we make no claim here about
who first assembled it, because we did not verify that attribution.

Replication of machine-learning results. The target venue, ReScience C, publishes replications and accepts
negative results; its author guidelines are the source for the venue requirements we follow [@rescience_guidelines]. We do
not quote a definition of replication versus reproduction to a specific page, because we did not
locate that wording on the guidelines page we fetched. 

A concurrent pre-registration by the author [@prereg2], registered on 2026-10-09, re-analyses five previously released judge-verdict datasets, none of them FairEval, for the gap between raw and chance-corrected agreement; it runs no judges, uses none of this study's verdicts, had run no analysis at registration, and the kappa-with-PABAK reporting used here was fixed in this study's own registration (sections 10 and 13), not imported from it.

# 3 Methods

The design was fixed in the pre-registration before data collection and is summarised here. Where
this paper departs from it, the departure is numbered and dated in the deviations register.

## 3.1 Items and inputs

The items are the original authors' released question set, candidate answers and human labels, from
https://github.com/i-Eval/FairEval [@faireval]. That repository carries no licence file, so we redistribute none
of its contents. Instead the inputs are obtained by the reader, who clones the original repository pinned to
commit `453c117a69159fd7b7de2f4e0519bac57bee21f4` and verified by SHA-256 before use. The verifier
checks hash and byte length for all six files it pins and exits non-zero on any mismatch. Five are
consumed by the arms that ran; the GPT-4 answer file is loaded and verified but never judged,
because no arm uses it; it was
tested green on a clean clone and tested to halt on a deliberately altered file.

The human labels are the original's own 80 annotations, with marginals ChatGPT 41, tie 14,
Vicuna-13B 25. We considered re-annotating and rejected it: substituting new labels would replace
the comparison standard and make our accuracy and kappa incomparable with the original's Table 5,
which is the comparison the study exists to make.

## 3.2 Judges

Three open-weight instruction-tuned models from three families. The harness sends model TAGS to
the local server, not digests; the digests below were read from the local model store after the runs
and are recorded for identification, with the limitation set out in the deviations register, D-11:
Qwen2.5-7B-Instruct (`845dbda0ea48`), Llama-3.1-8B-Instruct-q4_K_M (`46e0c10c039e`) and
Mistral-7B-Instruct (`6577803aa9a0`). Those digests were read from the local model store, not
written into the run artefacts as the registration required; see the deviations register, D-11. All inference
ran locally on an Apple M4 Pro with 48 GB of
unified memory. No paid API was used. A model that could not be pinned by digest would not have been
used.

## 3.3 Prompts

Prompt provenance. The original prints two templates. Table 1 is the plain evaluation template,
which asks for two scores on a single first line; we use it for the VANILLA arm. Table 3 is "the
evidence calibration evaluation template that prompts LLMs to generate the evaluation evidence
first, and then evaluate two responses", which is the MEC template. The `gen_prompt` in the released
`FairEval.py`, lines 35-49 at the pinned commit, is a near-verbatim variant of Table 3: it carries a
system message, labels the sections slightly differently, and asks for the explanation before the
scores. We use that released variant for the MEC arms, and record it as a variant rather than as
Table 3 itself.

The evidence that the released code is the MEC path is in the code. `query_gpt` hardcodes
`temperature=1` and `n=args.k`, which is the paper's MEC setting of temperature 1 with k = 3; the
`args.bpc == 1` branch performs the order swap; and the repository README invokes the script as
"evaluation with MEC and BPC strategies". The released code cannot perform a temperature-0 vanilla
run at all, because the temperature is fixed in the source.

The COMPARING prompt is a reconstruction and is declared as a deviation. The original does not print
the template, in any figure or appendix or in the released code. It does specify the labels in prose,
naming results "'Assistant 1', 'Assistant 2', or 'Same'", so the output space is given and only the
prompt wording is ours.

## 3.4 Arms, seeds and controls

Every question in the VANILLA and MEC arms is judged in both presentation orders. Arms per judge: a
Table 2 arm (VANILLA, temperature 0, both orders, two candidate pairs, SCORING template only, 320
calls); a Table 5 arm (MEC, temperature 1, k = 3, both orders, both templates, 960 calls); and an
identical-order noise-control arm measuring each judge's self-inconsistency rate. That arm is
narrower than the others: it runs in the AB order only and on the close candidate pair only
(ChatGPT against Vicuna-13B), over both templates, 480 calls.

Departures from the original beyond the judge substitution, listed rather than left to inference:

- Seeds are fixed, which the original does not state: base 1234, MEC's k = 3 samples at 1234 + i, the
  noise arm at a disjoint block 1334 + i.
- All three judges are Q4_K_M quantised local builds, not full-precision weights. This applies to
  Qwen2.5 and Mistral as well as to Llama-3.1, whose tag names the quantisation explicitly.
- The COMPARING prompt is our reconstruction; the original prints it nowhere.
- The original's 100-run random-order average is computed by resampling our stored both-order
  verdicts rather than by 100 fresh inference passes.
- Verdict extraction uses a strict regex on the template's requested format, and outputs that do not
  match it are recorded as unparseable rather than coerced.
- MEC aggregation is a MAJORITY VOTE over the k = 3 parsed samples, with ties broken by first-seen
  order, and a record counts as parsed if ANY of its samples parsed. The original averages the
  numeric scores instead. This is a substantive difference in aggregation, not a detail.

Because a record counts as parsed if any one sample parsed, the record-level unparseable rate
understates how often an individual generation failed. Section 4.3 therefore reports parse
accounting at BOTH levels, per judge and per template.

Seeds, which the original does not state, were fixed in advance: base seed 1234, with MEC's k = 3
samples drawn at 1234 + i, because a single fixed seed at temperature 1 returns identical text and
would silently collapse MEC to one sample. The noise-control arm uses a disjoint block, 1334 + i, so
its verdict is an independent draw rather than a replay.

Five positive controls are implemented as `pc1_input_integrity`, `pc2_ground_truth_recovery`,
`pc3_order_bookkeeping`, `pc4_determinism` and `pc5_parse_accounting`. PC-3 checks that each
(question, pair, arm, template) cell holds exactly one AB and one BA verdict. It does NOT compare
the stored candidate-answer hashes: those hashes (`r1_sha`, `r2_sha`) are recorded on every record
but never read by the check, so PC-3 detects a missing or duplicated order, not a swapped candidate
text. An earlier version of this paper described it as hash-based, which it is not. The first, second and
fourth run before any arm; the third and fifth require verdicts and so run after the arms but
before any hypothesis is examined. The point of all five is that a pipeline
check could fire before any result existed: input integrity, exact recovery of the human-label
marginals, order bookkeeping, temperature-0 determinism, and parse
accounting in which unparseable verdicts are counted and reported rather than dropped.

## 3.5 Verdict extraction, and the determinism control as implemented

Two parsers exist. One is registered and produces every confirmatory number; the other is a
secondary, exploratory parser declared after the data was seen. They are never mixed.

THE REGISTERED PARSER. `parse_verdict` in `run_replication.py` has THREE extraction rules, one per
template, and they are not the same rule. Stating them precisely matters, because the arm carrying
every MEC result uses the most permissive of the three.

- SCORING, the paper's Table 1 template, used for the VANILLA arm. Requires the two numeric scores
  on the FIRST non-empty line, matched by the regex `SCORE_LINE` applied with `.match` to that line
  only. The pattern requires the whole line to be two numbers separated by whitespace, optionally
  with one decimal place each, and nothing else.
- SCORING_CODE, the authors' released variant, used for every MEC and noise arm. Applies
  `SCORE_LABELLED.search` to the WHOLE output, so the labelled score pair is accepted wherever it
  appears. This is deliberately more permissive than the Table 1 rule, because the authors' own
  prompt asks for the explanation before the scores.
- COMPARING, our reconstruction. Applies `COMPARE_LINE.match` to the first non-empty line and maps
  "Assistant 1", "Assistant 2" and "Same" to the three outcomes.

In all three cases the higher score, or the named assistant, becomes a win for that slot, equal
scores or "Same" become a tie, and an output that does not match is recorded as unparseable with
its raw text retained. Nothing is ever coerced into a verdict.

An earlier version of this section described only the first-line rule and attributed it to "the
scoring templates". That was wrong for SCORING_CODE, and wrong about the arm that produces the MEC
figures.

Because the surrounding harness has changed since registration for reasons unrelated to parsing, a
whole-file hash is the wrong thing to pin. The four objects that must not change are pinned
individually, and can be re-checked from the released code:

    SCORE_LINE 3731d07991798867, SCORE_LABELLED 4889ac20478acbd0, COMPARE_LINE 225bfde4c0c754e0 and
parse_verdict e6e373cf6113f98b. The hashed bytes are stated exactly in `verify_parser_pins.py`,
which recomputes all four from the released source: for each regex, the UTF-8 bytes of the
compiled `.pattern` string with no trailing newline; for the function, the UTF-8 bytes of
`inspect.getsource` exactly as returned. Run `python3 verify_parser_pins.py --check`.

THESE PINS REPLACE FOUR EARLIER ONES. Reviewer 1 on #142 could not reproduce the earlier
prefixes, and neither could we: twenty-six candidate conventions over the released source
reproduced none of them, so the original hashing convention is not recoverable from what we
recorded. That is a fact about the convention, not about the parser - it is NOT evidence that
the parser changed after registration, and we do not claim it did. The superseded values are
kept in the deviations register at D-22.

THE SECONDARY PARSER is `parse_verdict_relaxed` in `relaxed_parse.py`. It imports the unchanged
`SCORE_LINE` from the harness rather than redefining it, so it cannot drift from the registered
rule. It skips leading lines that consist only of a markdown heading or emphasis label, then applies
the unchanged regex to the first remaining non-empty line, once. Its skip rule is broader than a markdown label: the pattern matches
any line consisting only of letters and spaces, with an optional heading marker, emphasis marks or
trailing colon. A short prose line such as "Both responses are adequate" matches it and would be
skipped. It does not skip bullets, numbered lines, or any line containing punctuation or digits. Its rule was chosen after the outputs were seen and the recovered count was known before
it was written; both facts are recorded in the deviations register, D-5. Every figure it produces is labelled
exploratory and is printed beside the registered figure, never instead of it.

THE DETERMINISM CONTROL, PC-4, AS IMPLEMENTED. Ten questions are drawn once with a fixed seed,
`random.Random(20261010).sample(questions, 10)`, from the checksum-pinned question file, so the draw
is identical for every judge and reproducible from the released code. The ten are 6, 23, 30, 33, 42,
43, 45, 46, 52 and 77. For each, the close pair is rendered through the paper's Table 1 template and
submitted twice at temperature 0 with the same fixed seed 1234. The comparison is byte equality of
the two returned strings; nothing is normalised first. A judge fails the control if any of the ten
pairs differs.

THE HALT RULE, AND WHICH READING OF IT WE ADOPTED. Our registration states this twice and the two
statements differ. The H1 section says "A PC-4 failure halts the study; it does not produce a
correction term". The controls section says the assumption failing "is reported as a methods
finding and halts the affected arm". The registration does not rank them. We adopted the second,
per-arm reading, under which a PC-4 failure halts that judge's temperature-0 arm and is reported as
a methods finding; a reader who prefers the first reading would conclude that no arm should have
continued. D-15 records the choice and leaves both wordings visible. It is not converted into a correction term, and it does not halt the judge's temperature-1
arms, which rest on the measured noise control rather than on PC-4. The failure is recorded in the
results artefact as `pc4_ok` and `t0_arm`. One re-test under controlled conditions was pre-declared
in the deviations register, D-1 before its outcome was known. It has run. Under that protocol
Qwen2.5-7B-Instruct differed on 3 of 20 prompt pairs, a mismatch rate of 0.15
(`results/pc4_retest_declared.json`). It is exploratory and reinstates nothing.

## 3.6 Analysis

All statistical inference is paired on question and clustered on question, since the same 80 items recur in
every condition. H1 and H3 were registered as exact McNemar per judge with Holm-Bonferroni
correction across judges within family. H2 was registered differently, and we state it in the
registration's own terms: "per judge, the signed difference between first-position and
second-position win rates with a question-clustered bootstrap interval; then whether any two judges
differ in sign with non-overlapping intervals". Interval types differ and are labelled wherever they appear. The H2 intervals and the c - s
intervals use 10,000 question resamples. The random-order MEC accuracy brackets use 1,000 draws
over presentation orders with the question set held fixed, which is a different resampling
procedure answering a different question; the draw count is set in `analyze_mec.py`'s main
analysis loop. Kappa is reported alongside PABAK in the results table, and the matched-marginal
chance agreement pe and both full marginal distributions are printed for every cell by
`analyze_mec.py`; they are not carried in the table itself. Kappa is never given as a bare
number, because with ties at 17.5% of labels a kappa difference can be an artefact of the marginal
distribution. The registration also asks for prevalence and bias indices [@byrt1993]; those are defined for a
two-category table and our verdict space has three categories, so they are not computed, and
the deviations register, D-13 records that as an unmet registered requirement rather than substituting a
look-alike number.

Because the temperature-0 arm did not survive, no registered test of H1 or H3 was performed. H2 is also not evaluable as registered; what the surviving arms show about it is a post-registration descriptive deviation, set out in the deviations register, D-12 and D-18. Section
4 reports descriptive quantities from the arms that did survive, labelled as such.

# 5 Discussion

What we can conclude. On two of these three locally served judges, Qwen2.5-7B and Mistral-7B, a
temperature-0 setting did not guarantee identical output. Llama-3.1-8B PASSED the determinism
control on all ten checked prompts, so the failure is not a property of every open-weight judge we
tried. That PASS is a statement about those ten prompts on an immediate repeat, not about the 320
prompts in the arm: nothing here establishes determinism beyond the sampled checks, and the
exploratory twenty-prompt re-test on a different judge found 15% mismatches. The rest of this
sentence continues:
tried, and we do not present it as one. Where it does occur, a conflict rate computed without a
determinism check cannot separate run-to-run variation from order dependence. A pre-declared re-test under serial requests, run on the
one judge that failed first, found the non-determinism persisted under the one controlled condition we tested, serial requests to a server we intended to be otherwise idle with the model resident, conditions the re-test script records but does not verify, which is narrower than "contention removed" in general, so we do
not attribute it to load. We do not offer a replacement mechanism: identifying one would need
instrumentation below the inference server, which this study does not have.

One limit on what the surviving arms could ever have shown about H2. They use Multiple Evidence
Calibration, which is the original's own remedy for positional bias. A result on a calibrated arm is weak evidence about a claim the original made on the uncalibrated
Table 1 template, whatever the interval around it, and that holds whichever way the result points. That is a reason to treat the H2 figures in 4.6 as descriptive, independent of
their width.

What we cannot conclude. We make no claim about the original's numbers. Its judges were different
models served differently, and three local models on one machine cannot speak to them. We also make
no claim about positional bias as such. On the temperature-1 arms verdicts did change with presentation order beyond each judge's own
same-order noise, though by less than an earlier version of this paper claimed: by 0.038, 0.138
and 0.250 on the scoring template, with one interval including zero, and most strongly by 0.810
on the reconstructed COMPARING prompt. We report those descriptively; but the registered test of position dependence was
specified on an arm that did not survive, and we attach no mechanism to the accuracy asymmetry we
observed, for reasons given in 4.6.

What a practitioner should take from it. If you intend to use an open-weight judge and rely on
temperature 0 for reproducibility, verify that assumption on your own stack before you build on it,
because it did not hold for two of our three judges. If you intend to parse a judge's output with a
strict format rule, measure the compliance rate first: the registered parser could not reach the
scores for 313 of one judge's 320 VANILLA records. Those 313 split into 274 that place the scores one
line down behind a markdown label, and 39 in other formats we did not characterise. We did not
assess whether any of those scores were substantively correct, only whether the registered rule
could read them.

Limitations. Three judges on one machine. The COMPARING arm rests on a reconstructed prompt.
Two COMPARING cells show near-constant output, and that cuts two ways: Mistral-7B's constant
verdict is a tie, so its conflict rate is near zero by arithmetic and uninformative, while
Llama-3.1's constant verdict is a slot, so its conflict rate is near its maximum for the same
reason and measures a real position effect. One judge's
MEC arm was executed twice after we destroyed the first execution's output through a filename
collision in our own harness, and the two executions cannot be compared record by record. The MEC
arm runs at temperature 1 with k = 3 samples per record, so two executions of it are not expected to
agree verdict for verdict even on a perfectly deterministic stack. All of these are
in the deviations register.

On contacting the original authors. We did not contact them. This replication therefore rests
entirely on the published article and the released repository, and a reader should weigh it on
that basis. We make no claim here about what the venue requires on this point.

# 6 Code and data availability

Our code and results are released in the project repository at https://github.com/dosvk/faireval-openweight-replication, archived at a Zenodo DOI obtained on acceptance, under the MIT licence required by section 9
of the registration. Released: the harness, the input verifier, the analysis scripts,
the secondary parser, the determinism re-test, the stale-claim sweep and the build script; the
per-judge verdict files with every individual sample and its raw text, with verbatim spans of
the original benchmark's questions and answers redacted (see the data section of the
registration, and the deviations register); the determinism re-test
output; and the dated deviations register itself, as `DEVIATIONS.md` in the repository: it is released
rather than reproduced in this article, so that every deviation stays recorded in full while
the article keeps to the length of a ReScience C replication.

NOT released: the question set, candidate answers and human labels. Those come from the original
authors' repository, which carries no licence file, so we redistribute none of them. The input verifier checks them at a pinned commit and checks SHA-256 and byte length for all six files it
pins before any run proceeds; five are consumed by the arms that ran. A consequence worth stating:
if that upstream repository is deleted or rewritten, our artefact cannot be rehydrated from it, and
the verifier will refuse to run rather than proceed on different bytes.

Also not released: the model weights, which are third-party. Inference ran locally through Ollama
0.30.8 on an Apple M4 Pro with 48 GB of unified memory. No paid API was used.

One reproducibility limitation, stated rather than left to be discovered. The registration
committed to recording each arm's model digest in the results artefact before its run. That did not
happen: the artefacts carry the model name and tag but no digest field. The digests appear in
the deviations register and in section 3.2, but they were read from the local model store after the runs, so a
reader cannot confirm from an artefact alone which weights produced it.

Expect to reproduce the pipeline and the controls. Do not expect byte-identical verdicts: section
4.2 reports that two of three judges failed a temperature-0 determinism check, so verdict-level
agreement is a thing this paper measures rather than a precondition it relies on.

