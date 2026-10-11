# DEVIATIONS from the registered plan

Registration: https://osf.io/jw59c/ — DOI 10.17605/OSF.IO/JW59C, registered 2026-10-10T03:19:58Z.
Cleared text sha256 4ee7bc7467459459b8ad57891eb0d4767c3b49124af574bcbe0db36e47281350.

Every entry here is dated and written BEFORE the work it describes, or immediately on discovery.
Nothing in this file may weaken a registered outcome rule. Entries are append-only.

---

## D-1. Declared PC-4 re-test, to characterise the cause of a determinism failure
**Written 2026-10-10T03:40Z, under ruling D-P10-15 item 3.**

**Written deliberately BEFORE reading the PC-4 outcomes for judges 2 and 3**, and it will be run
whatever those outcomes turn out to be. That ordering is the point of the entry: a diagnostic
chosen after seeing the results it might excuse is not a diagnostic.

WHAT HAPPENED. On the first run, judge 1 (qwen2.5:7b-instruct) failed PC-4: 1 of 10 prompts
(question 77) was not byte-identical on an immediate repeat at temperature 0 with a fixed seed. The
harness halted as the plan requires. Re-running question 77 four times in isolation afterwards gave
byte-identical output every time, which suggests the effect is intermittent rather than a fixed
property of the model or that prompt.

WHAT THIS DEVIATION ADDS. One re-test of PC-4 under controlled conditions, to characterise the
cause. Protocol, fixed here in advance:

- ONE re-test only. If it passes, that does not reinstate judge 1's temperature-0 arms. If it
  fails, nothing further is attempted.
- Serial requests only, `OLLAMA_NUM_PARALLEL=1`, the judge model resident before the first call,
  and nothing else issuing requests to the Ollama server for the duration.
- The same 10 prompts as the failed check, PLUS 10 newly drawn ones. Draw seed disclosed:
  `random.Random(20261010)` selected the original 10; the additional 10 are drawn with
  `random.Random(20261011)` from the remaining questions.
- Judge model, decoding settings and base seed exactly as registered (temperature 0, seed 1234).

STATUS OF ITS RESULT. Exploratory. It characterises a cause; it is not a hypothesis test, it is not
a correction term, and it NEVER replaces the registered halt of judge 1's temperature-0 arms. The
registered halt stands regardless of what this re-test shows.

WHAT WAS REJECTED AND WHY. Re-specifying PC-4 empirically and correcting the conflict rate by a
measured non-determinism rate (a relaxed-parser alternative that was considered) is rejected. It would change an outcome
rule after seeing the outcome, which is the specific failure pre-registration exists to prevent.

---

## D-2. Harness was STRICTER than the registered plan; corrected
**Written 2026-10-10T03:40Z, under ruling D-P10-15 item 2.**

The registered plan ties PC-4 to the temperature-0 arms: the self-inconsistency rate is zero there
"by construction under PC-4", and a PC-4 failure "halts the affected arm". The temperature-1 arms
(MEC, and the MEC component of MEC+BPC) do not rest on PC-4 at all; they rest on the measured
noise control, which is why that control exists.

My harness halted the ENTIRE judge on a PC-4 failure. That is stricter than registered, and
strictness is still a deviation: it would have thrown away MEC and MEC+BPC data the plan entitles
us to collect, and silently narrowed the study.

CORRECTION. PC-4 now gates only the temperature-0 arm (the Table 2 / VANILLA arm). On failure, that
arm is halted and the failure is recorded in the results artefact; the temperature-1 arms proceed.
Judge 1's temperature-1 arms will be run on this basis.

No re-run of PC-4 is performed for judge 1 as part of this correction. Its outcome is already
recorded, and re-executing the check outside the D-1 protocol would be an undeclared second test.

---

## D-3. PC-4 implemented in the harness after registration
**Written 2026-10-10T03:40Z, under ruling D-P10-15 item 4.**

PC-4 was specified in the registered plan but was not implemented in `run_replication.py` at the
time of registration; the harness implemented PC-1, PC-2, PC-3 and PC-5 only. I implemented it
before any arm ran, so no data was collected under a plan whose control was absent.

Per that decision this implements the plan rather than changing it.

[2026-10-11, CORRECTION. The provenance originally recorded here did not support the claim. We
cited commit f271021700b4343c4579ea1721f4b3987cbe278c, dated 2026-10-09 22:30:41 -0500. In UTC that
is 2026-10-10T03:30:41Z, and the first run began at 03:23:31Z. The commit is SEVEN MINUTES AFTER
the run it was cited to precede, so it evidences nothing about the order. We had quoted its local
timestamp without converting it.

What the evidence does support: the first run's own log, logs/run-20261010T032331Z.log line 18,
shows the PC-4 check executing and failing for the first judge, and the harness halting that
judge's temperature-0 arm before any arm produced data. So no arm data in this study is ungated by
PC-4.

What it does NOT support: any claim about how long before the run the check was written. We cannot
evidence that, and we no longer assert it. The file hash of the harness as run is
88fd58bb427da1585921397d666af0c36a570b66f5bb4c2af27ad78b66c10241.]

---

## D-4. Pinned inputs relocated out of /tmp
**Written 2026-10-10T03:40Z, accepted under ruling D-P10-15 item 4.**

The registered plan requires inputs fetched at run time from the original public repository, pinned
by commit and checksum, and not redistributed in our artefact. They were initially cloned under
`/tmp`, which a multi-hour run can lose. Copied to `~/.cache/p10-inputs/FairEval`, outside the
artefact, and re-verified there with the hydration verifier (exit 0, all six files).

Pin and non-redistribution are unchanged. This is a storage-location change only.

---

## D-5. A relaxed parser, added as a SECONDARY analysis only
**Written 2026-10-10T11:35Z, under ruling D-P10-16 item 2, BEFORE computing anything with it.**

TWO THINGS STATED UP FRONT, because the ruling requires them and because they are the only honest
framing of this entry:

1. **This rule was chosen AFTER seeing the model outputs.** It is not a pre-registered rule and it
   is not presented as one.
2. **The recovered count was already known when this rule was written.** 274 of llama3.1's 313
   strict-unparseable vanilla records were known to contain a bare two-score line before a single
   character of the relaxed parser existed.

That ordering is the reason this is a secondary analysis and can never be a confirmatory one.

WHAT WAS OBSERVED. llama3.1:8b-instruct-q4_K_M, on the paper's Table 1 SCORING template, emits a
markdown label and then the two scores one line down:

    **Overall Scores:**
    8.5 9.0

    **Evaluation Explanation:**
    ...

Under the registered parser, which requires the two scores on the FIRST line, 313 of 320 vanilla
records are unparseable. The scores are present; the registered rule does not reach them.

WHAT THIS DEVIATION ADDS. A separate function `parse_verdict_relaxed`. The registered
`parse_verdict` and the registered `SCORE_LINE` regex are NOT modified, so every confirmatory
number remains computable exactly as registered, from the same code, forever.

THE RELAXED RULE, deliberately narrow, and nothing broader:
- Skip leading lines that consist ONLY of a markdown heading or emphasis label, for example
  `**Overall Scores:**` or `## Scores`.
- Then apply the UNCHANGED `SCORE_LINE` regex to the first remaining non-empty line.
- Do NOT skip bullets. Do NOT skip prose. Do NOT skip any other kind of line.
- Applied ONLY where the SCORING template is used, which is the vanilla arm.

STATUS OF ITS RESULTS. Exploratory, always printed beside the registered figure, never substituted
for it, and never stated in an abstract as a hypothesis test. H1, H2 and H3 remain NOT EVALUABLE AS
REGISTERED: two judges' temperature-0 arms are halted under PC-4, and the third yields 1
strict-parsed contributing pair.
[2026-10-10, superseded for H2 by D-8: H2 is evaluated on the arms with both orders and is
INCONCLUSIVE; H1 and H3 remain not evaluable. The sentence above is left as written because this is
a dated register entry.]

WHAT WAS REJECTED. An OSF amendment changing the registered parser. Changing a registered
measurement rule after the data is in is the worse option, and it is not taken.

---

## D-6. An operational loss: Qwen's MEC arm was executed twice
**Written 2026-10-10T15:15Z, under ruling D-P10-20 item 2. No rule changed.**

WHAT HAPPENED. The phase-3b script issued two separate invocations for Qwen2.5-7B-Instruct, one for
the MEC (Table 5) arm and one for the identical-order noise arm. Both wrote to the same output path,
`results/verdicts_qwen2.5_7b-instruct.json`. The MEC arm completed first with 320 verdict records;
the noise arm then wrote 160 records to the same path and destroyed them. This was a fault in our
harness, not in the registered design.

WHAT WAS DONE. The output filename now includes the arm set, so two invocations for one judge can no
longer collide. The MEC arm was then re-executed from an immutable snapshot of the run script, with
the same registered settings and with the PC-4 outcome declared from the existing record rather than
re-tested. The re-execution is the data of record for that arm.

WHAT CANNOT BE DONE, STATED PLAINLY. The lost verdicts are not recoverable. They also cannot be
compared with the re-execution record by record, and the reason is a finding of this same paper:
section 4.2 shows that this stack does not produce identical output at temperature 0 even under
serial requests, so two executions of the same arm are not expected to agree verdict for verdict.
Anyone wanting a record-level comparison of the two executions cannot have one, and no amount of
care on our part would have provided it after the fact.

THE ONLY AVAILABLE CROSS-CHECK is the lost run's logged summary, which is reported beside the
re-execution's so a reader can see both:

    lost execution   (logs/phase3b-rerun-20261010T110714Z.log): PC-3 PASS, PC-5 320
      records,
                     0 unparseable, rate 0.0
    re-execution     (logs/qwen-table5-rerun-20261010T150514Z.log): reported in section
      4.3

NO RULE CHANGED. No hypothesis, threshold, parser, control or arm definition is affected. The arm is
one the registered plan entitles us to collect, per D-2.

---

## D-7. A post-hoc reporting flag for near-constant judge output
**Written 2026-10-11T08:30Z, under ruling D-P10-23 item (b). NO registered analysis changed.**

WHAT THIS IS. A reporting flag, not an analysis rule. Section 4.6 marks any judge-template cell in
which a single verdict category exceeds 90% of parsed verdicts, and reports the conflict rates from
those cells as uninformative because the output is near-constant. [2026-10-11T07:00:52Z, narrowed: this flag covers the candidate-frame CONFLICT RATES only. The slot-frame H2 signed figure for Llama-3.1 COMPARING is +0.884 and IS informative; see section 4.6. Original wording restored verbatim after it was wrongly edited in place]

CHOSEN AFTER SEEING THE DATA, AND SAID SO. The 90% threshold was selected by us after inspecting
the verdict distributions. It is not pre-registered and it is not presented as though it were. The
raw shares are printed in full in 4.6 so a reader can apply any threshold they prefer, or none.

WHY IT EXISTS. Two cells are affected: Llama-3.1-8B returns the first assistant on 95.4% of its
parsed COMPARING verdicts, and Mistral-7B returns a tie on 98.5% of its own. Mistral's COMPARING
conflict rate is 0.000, which follows arithmetically from answering the same way almost every time. [2026-10-11T07:00:52Z, corrected: the CONFLICT RATE c is 0.018. It is the NET order-dependence c - s that is 0.000. Original wording restored verbatim after it was wrongly edited in place]
Without the flag a reader could take that zero as evidence that the judge is unaffected by
presentation order, which it is not.

WHAT WAS NOT DONE. The pre-registration has an interpretation rule for the opposite failure, a judge
whose self-inconsistency rate approaches its conflict rate. It has no rule for a degenerate judge.
We did not invent one, and we did not drop, reweight or re-specify any registered quantity. The
affected conflict rates are still printed; only their interpretation is annotated.

---

## CORRECTION NOTE, appended 2026-10-10T21:15:57Z

D-7 above is stamped 2026-10-11T08:30Z. That time was in the future when D-7 was written. The real
time at this note is 2026-10-10T21:15:57Z, so D-7 should be read as having been written on 2026-10-10,
shortly before this note. The entry is not edited; the correction is appended so the record shows
both the error and the fix.

Cause and remedy are the same as recorded in DECISION-LOG.md: stamps were composed by hand instead
of taken from `date -u`, and from now on they are taken from `date -u` only.

---

## D-8. H2's arm was never registered, so H2 is evaluated on every surviving both-order arm
**Written 2026-10-10T21:16:30Z, under ruling D-P10-28 item (A), BEFORE any H2 quantity was computed.**

WHY THIS ENTRY EXISTS. The registered text binds H1 to a comparison that exists only on the
temperature-0 Table 2 arm, but it names NO arm for H2. H2 reads in full: "Positional preference
direction is judge-specific. Test: per judge, the signed difference between first-position and
second-position win rates with a question-clustered bootstrap interval; then whether any two judges
differ in sign with non-overlapping intervals." Nothing in that sentence restricts it to VANILLA.

We had previously reported H1, H2 and H3 together as not evaluable as registered. That was wrong for
H2, and the error was ours: we inherited H1's arm restriction and applied it to a hypothesis that
carries none.

WHAT IS DONE INSTEAD. H2's registered test is applied, unchanged, to EVERY surviving arm that has
both presentation orders. On the data that exists those arms are MEC/SCORING and MEC/COMPARING. The
test is run per judge and Holm-corrected across judges exactly as registered.

THE RULE THAT MAKES THIS HONEST. Every arm is reported. No arm is selected, dropped, or promoted
after inspection, and no arm's result is given precedence over another's. If the arms disagree, the
disagreement is the result.

STATED PLAINLY: THE ARM CHOICE WAS MADE AFTER SEEING THE RESULTS. It had to be, because the
registration named no arm and only some arms survived. That is why the choice is fixed here, in
writing, before any H2 number is computed, and why it is "all surviving both-order arms" rather
than any criterion that could have been tuned to an outcome.

THE DEGENERATE-JUDGE FLAG STILL APPLIES. Two COMPARING cells are near-constant under D-7
(Llama-3.1 95.4% one verdict, Mistral-7B 98.5% tie). Their H2 statistics are reported and flagged
uninformative on the same basis as their conflict rates, and they are not quietly excluded. [2026-10-11T07:00:52Z, superseded in part: the CONFLICT RATES of these two cells are uninformative under D-7 [2026-10-11T08:16:23Z, narrowed further: true for MISTRAL-7B only. Llama-3.1's conflict rate of 0.881 is near its maximum because its constant verdict is a slot, and it is informative; see section 4.6], but the SLOT-FRAME H2 signed figure is NOT. Llama-3.1's is +0.884, the strongest slot-position signal in the study. Section 4.6 carries the governing reading. Original wording restored verbatim after it was wrongly edited in place] Section 4.6 carries that reading and it governs.

WHAT THIS DOES NOT CHANGE. H1 remains not evaluable as registered: its close-pair against far-pair
comparison exists only on the halted temperature-0 arm. H3's position is addressed separately.

[2026-10-11T00:52:14Z, THE ALTERNATIVE READING, ACKNOWLEDGED. A referee has pointed out that the
claim H2 tests is not unscoped. C-2 is quoted in the registration as "on the same evaluation
template T in Table 1, GPT-4 tends to favor the response in the first position, while ChatGPT shows
a preference for the response in the second position", and section 10 lists "positional preference
direction per judge (C-2, H2)" inside a Primary bullet that opens with the temperature-0 VANILLA
arm. On that reading H2 belongs to the Table 1 template, which is the VANILLA arm, and H2 would
therefore be NOT EVALUABLE for the same reasons as H1 rather than inconclusive.

Our reading was that H2's own TEST sentence names no arm, so it applies wherever both orders exist.
We still think that is defensible, and it was fixed before any H2 statistic
was computed. But it is a reading, not the only one, and the difference is not cosmetic: under the
restrictive reading the paper reports one fewer evaluable hypothesis.

We therefore do not present our reading as settled. The restrictive reading is recorded here, the
arm choice remains disclosed as made after the results because the registration named no arm in the
test sentence, and a reader who prefers the restrictive reading should treat H2 as not evaluable and
the figures in 4.6 as descriptive only.]


### D-8 AMENDMENT, appended 2026-10-10T21:31:12Z under ruling D-P10-29. Supersedes the paraphrase above.

**(i) H2 verbatim.** The block above described H2 as quoted "in full" and then paraphrased it. That
was wrong. We were asked for the internal draft's wording, but the binding text is
PREREGISTRATION-OSF.md, which is what is registered at osf.io/jw59c and is hash-bound at
4ee7bc7467459459. The two differ in wording while agreeing in substance, so quoting the internal
draft would leave a reader comparing against the public registration with a mismatch. The verbatim
registered text is therefore:

    **H2 (primary, with a declared asymmetry).** Positional preference direction is
      judge-specific.
    Test: per judge, the signed difference between first-position and second-position
      win rates with a
    question-clustered bootstrap interval; then whether any two judges differ in sign
      with
    non-overlapping intervals. Confirmed if at least two judges differ in sign with
      non-overlapping
    intervals.
    Declared asymmetry: finding a sign difference supports the conclusion that direction
      does not
    generalise. NOT finding one is reported as inconclusive and never as refutation of
      the original
    claim, because three judges cannot support a confident negative. This asymmetry is
      fixed in advance
    so that a null result cannot later be presented as evidence.

A reader who wants the internal draft's wording will find it at PREREGISTRATION-DRAFT.md l.103-111;
it says the same thing in different words, and the discrepancy is recorded here rather than
resolved silently.

**(ii) Definitions the registration leaves open, fixed here before computation.**
- First-position win rate, per arm. SCORING: the share of parsed verdicts in which the answer in
  slot 1 received the higher score. COMPARING: the share of parsed verdicts answering
  "Assistant 1".
- Ties remain in the denominator and count as neither a win nor a loss, so a judge that ties often
  has both rates depressed rather than excluded.
- Unparsed records are excluded from both numerator and denominator, and the excluded count is
  printed beside every figure.
- Bootstrap: 10,000 resamples of questions, seed 1234, as section 10 of the registration specifies.

**(iii) How Holm is applied to an interval-based decision.** The registration's multiplicity rule
is "Holm-Bonferroni within each hypothesis family across the three judges", but H2's own decision
rule is a non-overlap of intervals and names no p-values, so Holm cannot be applied to it in its
usual step-down form. We apply it to the interval level instead, and conservatively: every per-judge
interval is computed at the most stringent Holm level, 1 - 0.05/3 = 98.33%, rather than at a
rank-dependent level. This is stricter than a step-down procedure would be, which is the safe
direction, and it avoids inventing a p-value ordering the registration does not define. The choice
is recorded here before any H2 number exists.

### D-8 AMENDMENT 2, appended 2026-10-10T21:46:08Z under ruling D-P10-30 item 3.

**The first H2 run was buggy and reported a CONFIRMED result. Its output is reproduced verbatim
here so the error is on the record rather than only its correction.**

Verbatim output of the first run, COMPARING block:

      COMPARING -- pairwise sign difference with non-overlapping intervals:
        llama3.1:8b-instruct-q4_K_ vs mistral:7b-instruct        opposite sign=True
          non-overlap=False
        llama3.1:8b-instruct-q4_K_ vs qwen2.5:7b-instruct        opposite sign=False
          non-overlap=False
        mistral:7b-instruct        vs qwen2.5:7b-instruct        opposite sign=True
          non-overlap=True
        -> CONFIRMED: 1 qualifying pair(s)

TWO DEFECTS, both of which pushed toward a positive finding.

1. Sign test. The code tested `(a["stat"] > 0) != (b["stat"] > 0)`. That classifies a statistic of
   exactly 0 as not-positive, and therefore as opposite in sign to a positive one. A statistic of
   zero has no sign. Mistral's COMPARING statistic is exactly 0.000 (1 slot-1 win, 1 slot-2 win,
   131 ties, of 133 parsed), so it was wrongly counted as differing in sign from Qwen2.5's +0.131.

2. Zero-width interval. The same near-constant cell produces a bootstrap interval of
   [+0.000, +0.000]. A zero-width interval fails to overlap any other interval trivially, so the
   non-overlap condition was met for a reason that carries no information.

THE FIX THAT MATTERS is the sign test, because it corrects the code to the registered words "differ
in sign". It is a correction, not a new rule.

[2026-10-11T05:49:10Z: the run quoted above was ALSO affected by the frame error in D-18, so
its numbers are wrong for a second, independent reason. It is retained because it documents the
sign-test defect it was written to record, not because any figure in it stands. The corrected H2
figures are in section 4.6.]

[2026-10-11T06:31:23Z, superseded by D-18: the paragraph below is FALSE after the frame correction. On SCORING_CODE the Llama-3.1/Qwen2.5 pair DOES qualify, with opposite signs and non-overlapping intervals. Left as written because this is a dated entry.]

THE FINAL VERDICT DOES NOT DEPEND ON THE DEGENERATE RULE. With the sign fix alone, no pair
qualifies on either arm: on COMPARING every pair shares a sign or involves the signless cell, and on
SCORING_CODE the one opposite-sign pair (Llama-3.1 negative, Qwen2.5 positive) has overlapping
intervals. The decision therefore rests on the registered criteria only, and the near-constant flag
has been removed from the decision logic in `h2()` and is now reported for information alone.

Recorded because a rule added to decision logic after seeing an unwelcome result is the exact move
pre-registration exists to prevent, even when the rule is defensible and even when it changes
nothing.

---

## D-9. H3 was not evaluable regardless of the determinism failure
**Written 2026-10-10T22:43:16Z, under ruling D-P10-28 item (B).**

We had attributed H3's loss to the PC-4 determinism failure. That was incomplete, and the fuller
account is worse for us.

H3 compares MEC+BPC accuracy against VANILLA accuracy on both templates. Two things make it
unevaluable independently of PC-4:

1. THE VANILLA/COMPARING CELL WAS NEVER GENERATED. In `run_replication.py` the Table 2 arm runs
   only the SCORING template, over the close and far candidate pairs. No VANILLA run on the
   COMPARING template exists in any results file, for any judge, and none was ever launched. So the
   COMPARING half of H3 had no baseline to compare against before a single determinism check ran.

2. NO WANG-STYLE BPC QUANTITY WAS EVER COMPUTED. See D-10.

So H3 is not evaluable for two reasons, one of which is a gap in our own harness rather than a
property of the judges. Reporting only the determinism failure would have let a reader infer that
H3 would have been answerable had the judges been deterministic. It would not.

## D-10. What we called "MEC + BPC" is a random-order MEC estimate, not BPC
**Written 2026-10-10T22:43:16Z, under ruling D-P10-28 item (C).**

The original's Balanced Position Calibration averages the two numeric SCORES a judge gives across
the two presentation orders, and decides from the averaged scores.

What `analyze_mec.py` computes is different: it resamples the stored per-order VERDICTS, which is
what the pre-registration specifies in place of 100 fresh random-order runs. That is a random-order
MEC estimate. It never averages scores and it never forms a calibrated score, so it is not BPC and
must not be labelled as such.

Corrected everywhere it appeared: the code comment and printed label in `analyze_mec.py`, and the
prose in RESULTS-DRAFT.md section 4.6, which now states explicitly that no BPC quantity was computed
in this study.

CONSEQUENCE, stated rather than buried: the original's headline MEC+BPC figures (58.8% on SCORING,
60.0% on COMPARING) have no counterpart in our results. We did not compute the quantity they
report. Any comparison a reader might be tempted to draw between our random-order MEC numbers and
the original's BPC numbers is not a like-for-like comparison.

---

## D-11. A registered reproducibility commitment we did not meet: model digests absent from the artefacts
**Written 2026-10-10T23:02:33Z, under ruling D-P10-28 following review finding gpt-B15.**

The registration states that every arm's model digest is recorded in the results artefact before its
run, and that a model which cannot be pinned by digest is not used.

THE DIGESTS ARE NOT IN THE ARTEFACTS. Each `results/verdicts_*.json` carries `judge` (the model
name and tag) but no digest field, at either the file or the record level. The per-record hashes
present are `r1_sha` and `r2_sha`, which hash the candidate answers, not the model.

WHAT WE CAN AND CANNOT SAY. The digests were read from the local store and are recorded in this
register and in the Methods section: Qwen2.5-7B-Instruct 845dbda0ea48,
Llama-3.1-8B-Instruct-q4_K_M 46e0c10c039e, Mistral-7B-Instruct 6577803aa9a0. But they were captured
AFTER the runs, not written into the artefacts before them, which is weaker than the registration
promised. A reader cannot confirm from an artefact alone which weights produced it; they have to
take our word that the store was unchanged between the run and the reading.

NOT RETROFITTED. We did not insert digests into the completed artefacts after the fact. Doing so
would produce files that look like they satisfied the commitment when they did not.

The harness has been left as-is rather than patched, because changing it now would not repair the
artefacts that already exist and would obscure which runs were affected: all of them.

---

## D-12. H2 reclassified as NOT EVALUABLE as registered
**Written 2026-10-11T01:16:07Z. D-8's original text above is unchanged.**

WHAT CHANGED. H2 was previously reported as evaluated-and-inconclusive under D-8. It is now
reported as NOT EVALUABLE as registered, for the same reason as H1 and H3: the registered
temperature-0 Table 1 VANILLA arm produced no analysable data.

WHY. A referee read the registration more carefully than we had. The claim H2 tests, C-2, is scoped
in the registration to "the same evaluation template T in Table 1", and section 10 places
"(C-2, H2)" inside the Primary bullet anchored to the temperature-0 VANILLA arm. H2's test sentence
is silent on the arm, and a test sentence silent on the arm inherits its claim's scope. Where the
registration is ambiguous, it resolves against us.

WHEN, STATED PLAINLY BECAUSE IT MATTERS. This reclassification came AFTER the null result was
known. We computed H2 on the surviving MEC arms, found it not confirmed, and only then accepted that
those arms were not the registered setting. Anyone assessing this paper should weigh the
reclassification in that light. What it does not do is change any number: the H2 statistics,
intervals, denominators and pairwise decisions in section 4.6 are identical before and after, and [2026-10-11T06:31:23Z, superseded by D-18: this is FALSE. The frame error corrected in D-18 changed every H2 figure, interval and pairwise decision; the sentence is left as written because this is a dated entry.]
they remain in the body rather than being moved to this appendix.

WHAT D-8 NOW IS. D-8 remains a post-registration deviation, fixed before any H2 statistic was
computed, under which the unchanged registered test was applied to every surviving both-order MEC
arm. It was not specified before the results existed: it was written after we knew which arms had
survived, and that is the honest description of it. Its results are reported as DESCRIPTIVE.

ONE LIMIT ON WHAT THOSE DESCRIPTIVE RESULTS COULD EVER SHOW. The surviving arms use Multiple
Evidence Calibration, which is the original's own remedy for positional bias. A null on a calibrated
arm is weak evidence about a claim made on the uncalibrated template, whatever its interval. That
point is made once in the Discussion.

SUPERSEDES. An earlier decision set D-8 up as the H2 test, and this supersedes it on classification only; the test itself, and its output, are untouched. [2026-10-11T06:30:54Z, superseded by D-18: the OUTPUT was not untouched. D-18 corrected a frame error that changed every H2 row. The test procedure was unchanged; its output was not.]

---

## D-13. The registered prevalence and bias indices are not computed, and why
**Written 2026-10-11T02:46:31Z.**

The registration requires kappa to be reported "with prevalence and bias indices and PABAK". PABAK
is reported. The prevalence and bias indices are NOT, and this entry says why rather than leaving a
registered requirement quietly unmet.

THOSE INDICES ARE DEFINED FOR A 2x2 TABLE. Byrt, Bishop and Carlin define the prevalence index as
the absolute difference between the two diagonal cells divided by n, and the bias index as the
absolute difference between the two off-diagonal cells divided by n. Both presuppose two categories.

OUR TABLE IS 3x3. Verdicts and human labels both take three values: prefers the first candidate,
prefers the second, or tie. There is no single accepted generalisation of either index to three
categories, and the registration did not specify one.

WE TRIED AN AD-HOC GENERALISATION AND DISCARDED IT. Summing the signed marginal differences across
categories returns exactly zero for every judge and arm, because both marginals sum to n and the
differences cancel. That is an arithmetic identity, not a measurement. Reporting it as a prevalence
index of 0.000 for twelve cells would have looked like a finding and meant nothing.

WHAT IS REPORTED INSTEAD, all well defined on a 3x3 table: Cohen's kappa and PABAK in the results
table, and observed agreement, matched-marginal chance agreement pe and both full marginal
distributions in the script output, so a reader with the released code can compute any index they
consider appropriate. [2026-10-11T08:01:53Z: the results table carries kappa and PABAK only; pe and the marginals
are in the script output, not the table. An earlier version of this sentence implied all of them
appeared in the table.]

This is a registered requirement we do not meet. It is recorded as unmet rather than satisfied by a
number that would not survive being asked what it measures.

---

## D-14. The registered stopping rule was not satisfied
**Written 2026-10-11T04:01:14Z, after a referee raised it.**

The registration's stopping rule reads: "the study is complete when the five positive controls have
been evaluated, all three judges have completed the Table 2, Table 5 and temperature-1
noise-control arms with a per-judge unparseable rate recorded, and H1, H2 and H3 have been
evaluated by the tests above."

THAT CONDITION IS NOT MET, on two counts. Two judges never completed a Table 2 arm, because PC-4
halted it. And none of H1, H2 or H3 has been evaluated by the registered tests. So the study is
being written up short of its own completion criterion.

WE ARE NOT CLAIMING OTHERWISE. The paper reports what the controls caught and what the surviving
arms show, and it is explicit that no registered hypothesis was evaluated. But a reader comparing
the write-up against the stopping rule would find the rule unsatisfied, and we would rather say so
here than have it discovered.

WHY WE STOPPED ANYWAY. The halt was itself a registered instruction: PC-4's failure halts the
temperature-0 arm and is reported as a methods finding. Continuing would have meant either
overriding that rule or re-running until the control passed, and the second is the behaviour
pre-registration exists to prevent. Stopping short was the only option consistent with the plan.

## D-15. Two further descriptions corrected after referee findings
**Written 2026-10-11T04:01:14Z.**

THE COMPARING ARM IS NOT A TRUE MEC ARM. We have called it "MEC/COMPARING" throughout. Two things
are missing. The system prompt is applied only to the scoring template, so COMPARING runs with none
(`system = SYS_PROMPT_CODE if template == "SCORING_CODE" else None`). And the COMPARING template
does not ask for the explanation before the verdict, which is the mechanism Multiple Evidence
Calibration consists of. So COMPARING is a temperature-1, k=3, both-orders arm on a reconstructed
prompt: it is not evidence-first, and calling it MEC overstates what it implements. The label is
retained for continuity with the arm names in the released code and artefacts, and this entry is
what the label means.

THE REGISTRATION CONTRADICTS ITSELF ON WHAT A PC-4 FAILURE HALTS, and we quoted only one side.
Section on H1 says "A PC-4 failure halts the study; it does not produce a correction term". The
controls section says the assumption failing "is reported as a methods finding and halts the
affected arm". We followed the second, per-arm reading, which let the temperature-1 arms continue.
A reader following the first reading would conclude the whole study should have stopped at the first
PC-4 failure. Both sentences are now quoted so the choice is visible rather than implied.

---

## D-16. An analysis error: verdicts were read in the wrong frame for every BA record
**Written 2026-10-11T04:32:22Z, after referee review. No earlier entry is rewritten.**

WHAT THE ERROR WAS. The harness swaps the two responses for the BA order
(`r1, r2 = (a1, a2) if order == "AB" else (a2, a1)`) and stores the parser's output unchanged. So
the stored verdict is in the SLOT frame: "A" means the answer in slot 1 won, and in BA slot 1 holds
the second candidate. Our analysis read every stored verdict as if it named the CANDIDATE, with no
flip for BA. Accuracy, kappa, PABAK, the conflict rate c, the self-inconsistency difference c - s
and the random-order estimate were therefore wrong for every BA record.

HOW IT WAS FOUND. A referee reading the code against the analysis noticed the missing flip. We had
run the pipeline many times without catching it, and the symptom was visible in our own output: on
the scoring template Mistral-7B's stored verdicts were A50/B31 in AB and A50/B31 in BA [2026-10-11T07:00:52Z, corrected: the live counts are A49/B31 in both orders. A50/B31 sums to 81 and n is 80, so the original figure was arithmetically impossible. Original wording restored verbatim after it was wrongly edited in place], identical
slot counts, which the candidate-frame reading turned into a judge that reversed its preference
exactly as the slots reversed. That should have prompted the question and did not.

WHAT CHANGED. Candidate-frame numbers, old then new:

    judge / arm                     BA accuracy        c              c - s
    Llama-3.1 SCORING_CODE          0.266 -> 0.557     0.684 -> 0.316  0.405 -> 0.038
    Mistral-7B SCORING_CODE         0.300 -> 0.525     0.625 -> 0.375  0.388 -> 0.138
    Qwen2.5 SCORING_CODE            0.312 -> 0.512     0.525 -> 0.475  0.300 -> 0.250
    Llama-3.1 COMPARING             0.377 -> 0.415     0.119 -> 0.881  0.048 -> 0.810
    Mistral-7B COMPARING            0.206 -> 0.191     0.000 -> 0.018 -0.018 -> 0.000
    Qwen2.5 COMPARING               0.275 -> 0.425     0.400 -> 0.287  0.325 -> 0.212

    random-order MEC accuracy       Llama 0.429 -> 0.576, Mistral 0.419 -> 0.532,
                                    Qwen 0.456 -> 0.556

WHAT THAT DOES TO THE PAPER'S DESCRIPTIVE CLAIMS. Two reverse.

The order-dependent accuracy asymmetry largely disappears on the scoring template: Llama-3.1 was
0.588 against 0.266 and is 0.588 against 0.557. The earlier text built an argument on a gap that
was an artefact of our own frame error.

The c - s figures no longer support "verdicts change with presentation order beyond same-order
noise by 0.30 to 0.41". On the scoring template they are 0.038, 0.138 and 0.250, and Llama-3.1's
interval now includes zero. The largest c - s in the corrected data is on COMPARING, not SCORING,
and it is Llama-3.1's 0.810.

The comparison with the original also reverses: our random-order MEC accuracies are 0.532 to 0.576,
against the original's 53.2% on its scoring template. They were below it and are now around or
above it.

WHAT DOES NOT CHANGE. H1, H2 and H3 remain not evaluable as registered. The slot-frame quantities
are untouched, because they never used the candidate frame: the H2 signed slot difference, the
slot-1 and slot-2 shares, and the content-blind benchmark are identical before and after. [2026-10-11T06:30:54Z, superseded by D-18: FALSE. h2() and content_blind() each carried an order-conditional remap, so the H2 signed difference, the slot shares and the content-blind figures all changed.] The PC-4
determinism findings, the parse accounting and every count of records and samples are unaffected.

THE FIX. The frame is now canonicalised once at load: every record gains `verdict_cand`, BA flips
A and B, ties are unchanged, and candidate-frame quantities use only that field while slot-frame
quantities use the stored verdict directly. A selftest asserts that a synthetic judge which always
picks slot 1 yields a conflict rate of exactly 1, different AB and BA candidate-frame accuracy, and
a slot-1 share of exactly 1 - the pattern that the conflated frames made invisible. Three analysis
functions loaded records independently and had to be routed through the canonicalisation separately;
fixing only the first would have left two of them wrong.

TIMING, STATED PLAINLY. This error was found after the null results were known and after two rounds
of referee review. It was ours, it survived our own checks, and the corrected numbers are reported
here with the old values beside them rather than quietly replaced.

---

## D-17. The registered "average results of 100 runs" was not performed
**[2026-10-11T07:01:16Z: this title is the original. The entry's body was corrected - the departure is 1,000 resamples against the registered 100, not resampling instead of fresh inference.]**
**Written 2026-10-11T04:58:28Z, after a referee finding.**

The registration already prescribes resampling our stored both-order verdicts in place of 100 fresh
random-order inference passes, so resampling is not itself the departure. THE DEPARTURE IS THE
COUNT: the registration specifies 100 resamples and we ran 1,000. An earlier version of this entry
described the departure as resampling instead of fresh inference, which misread our own
registration.

WHY THE REGISTRATION ITSELF AVOIDS FRESH PASSES. 100 fresh random-order passes per question per
judge per template would be 100 resamples x 80 questions x 3 judges x 2 templates x 3 samples = 144,000 additional call_judge
invocations on the surviving arms, because the harness issues one call per sample rather than one
per verdict. An earlier version of this entry said 48,000, which is the number of VERDICTS, not
calls; the unit and the number disagreed. At the measured throughput for these local
models that is on the order of days of continuous inference, against a measured 8.4 hours for the
whole registered design. The resample was adopted for that reason.

WHAT IT COSTS. The resample cannot show anything the two stored orders do not already contain. A
fresh 100-run average would sample the model's own stochasticity 100 times per question; ours
samples our two recorded verdicts repeatedly. So our interval reflects uncertainty from which order
is drawn, and NOT the run-to-run variation that 100 fresh passes would capture. Given this paper's
own finding that these judges are not reproducible at temperature 0, that omitted component is
likely to matter, and we do not claim our interval is a substitute for it.

The figures are labelled "random-order MEC" rather than matching the original's procedure, and the
resample count is stated wherever an interval is reported.

---

## D-18. The frame fix was HALF-APPLIED, and correcting it changes the descriptive H2 outcome
**Written 2026-10-11T05:46:48Z, after a second confirmation review. This corrects D-16. [2026-10-11T07:01:16Z: an earlier version of this line said "D-16 is not rewritten". One figure in D-16 WAS edited in place, the A50/B31 count; it has since been restored verbatim with a dated bracket, so the claim now holds for the entry as it stands.]**

WHAT D-16 GOT WRONG ABOUT ITSELF. D-16 states that "the slot-frame quantities are untouched,
because they never used the candidate frame", and the paper repeated that. THAT CLAIM IS FALSE AND
IS WITHDRAWN. Two functions, `h2()` and `content_blind()`, each carried their own
order-conditional remap (`slot1 = "A" if order == "AB" else "B"`), which re-flipped every BA
record and cancelled the slot-position signal. The file's own header comment said slot-frame
quantities must use the stored verdict directly; the two functions contradicted it.

WHY OUR SELFTEST DID NOT CATCH IT. `frame_selftest()` exercised the canonicalisation helper and
nothing else. It called neither `h2()` nor `content_blind()`. So "FRAME SELFTEST: PASS" certified
the helper while both consumers were wrong. A test that does not call the function under test
certifies nothing, and ours printed PASS for a build whose H2 table was wrong in every row.

IT WAS VISIBLE IN OUR OWN PRINTED TABLES. Section 4.6 reported Qwen2.5's SCORING_CODE verdicts as
72.5% slot 1 against 27.5% slot 2 over 160 records. That is a signed share of +0.450. The H2 table
in the same section printed +0.025. Those two numbers cannot both be right, they sat four pages
apart, and we did not notice.

A SECOND, SEPARATE DEPARTURE FOUND AT THE SAME TIME. The registration says "In a paired test a
question contributes only if both members of its pair parsed." `h2()` used every parsed record,
which admitted singly-parsed questions; the printed n of 159 for Llama-3.1 on SCORING_CODE is odd,
which is only possible if one question contributed a single order. Complete pairs are now enforced
and the number of questions dropped for incompleteness is printed per cell.

WHAT THE CORRECTED NUMBERS ARE. Signed first-minus-second slot share, 98.33% intervals:

    judge / arm                    signed    interval            n    dropped
    Llama-3.1 SCORING_CODE         -0.063    [-0.215, +0.089]   158    1
    Mistral-7B SCORING_CODE        +0.225    [+0.075, +0.375]   160    0
    Qwen2.5 SCORING_CODE           +0.450    [+0.312, +0.588]   160    0
    Llama-3.1 COMPARING            +0.884    [+0.767, +0.977]    86   23
    Mistral-7B COMPARING           +0.017    [+0.000, +0.069]   116   17
    Qwen2.5 COMPARING              +0.069    [-0.013, +0.156]   160    0

THE DESCRIPTIVE OUTCOME CHANGES, AND IT CHANGES IN OUR FAVOUR. On SCORING_CODE, Llama-3.1 and
Qwen2.5 differ in sign with non-overlapping intervals, which is exactly the criterion H2's
registered test names. Under the earlier, wrong numbers no pair qualified and we reported "not
confirmed". We now have to report the opposite of what we had published on that arm.

THAT DIRECTION OF CHANGE DEMANDS MORE CAUTION, NOT LESS, so the limits are stated here rather than
left to a reader. H2 REMAINS NOT EVALUABLE AS REGISTERED: D-12 stands, the registered claim is
scoped to the Table 1 temperature-0 arm, and that arm produced no analysable data. What we have is a
descriptive result on arms the registration did not name, obtained under a post-registration
deviation, on judges whose temperature-0 determinism we could not establish, computed after an
analysis error of ours was corrected by referees rather than by us. It is not a confirmation of H2.

ONE EARLIER READING ALSO FALLS. Section 4.6 called Llama-3.1's COMPARING cell "uninformative
because the output is near-constant". Its corrected signed share is +0.884 with an interval well
clear of zero: a judge that picks slot 1 almost always is not uninformative about slot position, it
is the strongest slot-position signal in the study. The near-constant flag from D-7 still matters
for candidate-frame quantities on that cell, and it does not license calling the slot-frame figure
uninformative [2026-10-11T08:16:37Z, narrowed: it applies to MISTRAL-7B's conflict rate only. Llama-3.1's constant verdict is a SLOT, so its conflict rate of 0.881 is near its maximum by arithmetic and measures a real position effect; section 4.6 states that nothing about that cell is uninformative.].

FIX. The remap is deleted from both functions, complete pairs are enforced, and
`frame_selftest()` now runs `h2()` and `content_blind()` over a synthetic always-slot-1 judge,
which must yield a signed share of exactly +1.000 and p(slot 1) of 1.000 in both orders. Verified
that re-introducing either remap makes the selftest FAIL.

---

## D-19. Four departures that had no register entry until now
**Written 2026-10-11T05:49:36Z, after a referee listed them as missing.**

Each of these was visible in the code or the paper and none had a dated entry. That is itself the
failure: a deviations register is worth only as much as its completeness.

PC-3's HASH CHECK WAS NEVER IMPLEMENTED. The registration says candidate texts are hashed "so a
silently swapped assignment is detectable". The hashes exist on every record as `r1_sha` and
`r2_sha`, and `pc3_order_bookkeeping` never reads them. The check as registered does not exist;
what runs is a bookkeeping check that each cell holds exactly one AB and one BA verdict. The
function's own docstring still said "candidate texts hashed" and was wrong.

QUANTISATION. All three judges are Q4_K_M builds, not full-precision weights. The registration does
not mention quantisation at all, so running quantised models is an undeclared departure, and it is
one that could plausibly affect determinism and verdict stability - the two things this paper is
about. Named in Methods and recorded here.

C-3 WAS DROPPED. The registration lists a score-gap analysis, C-3, binning conflict rate by the
size of the score difference. It is not reported. The reason is that the registered binning was
specified for the VANILLA arm, which did not survive; the reason is good but the omission was
reported in the body without a register entry.

THE LICENCE FOR OUR OWN CODE IS NOT NAMED, AND REGISTRATION SECTION 9 REQUIRES ONE. No licence is
stated for the replication's own released code. This is a registered requirement we do not yet meet.
Choosing the licence is the owner's decision, so the availability section carries an explicit
[KMVEE-CODE-LICENCE] placeholder beside the repository placeholder, and the gate fails until both are
filled. Noting separately that the third-party FairEval inputs carry no licence is a different
matter and does not discharge section 9. [2026-10-11T23:10:56Z, RESOLVED: the owner chose MIT. The licence now sits in LICENSE in the released repository, with a NOTICE section stating that it covers only this study's code and results and explicitly NOT the unlicensed FairEval inputs or the third-party model weights. Registration section 9 is therefore met. The original wording above is left intact because it records that the requirement was unmet at the time, which is the fact a reader needs.]

---

## D-20. Two process failures in maintaining this register, and one more analysis fix
**Written 2026-10-11T07:03:05Z, after a fourth confirmation review.**

I EDITED DATED ENTRIES IN PLACE WHEN THE RULE WAS TO APPEND. D-7's and D-8's original wording, and
one figure in D-16, were replaced rather than left intact with a dated note beside them. TWO FURTHER
ENTRIES WERE EDITED THE SAME WAY and are named here rather than reconstructed, because their
pre-correction wording is recoverable from the repository history and summarising it twice would add
nothing. D-17's body originally described the departure as resampling stored verdicts instead of 100
fresh inference passes, and gave the compute cost as "about 48,000 additional judge calls"; both were
wrong and both were corrected in place before this entry existed. D-18's opening line originally
read "D-16 is not rewritten; this corrects it", which was false while D-16's A50/B31 figure was still
edited rather than bracketed. The whole
value of this register is that a reader can see what we said before we knew better; silently
improving it destroys exactly that. The originals have been restored verbatim to the wording the entry carried at 2026-10-11 01:10 CT and the corrections now sit in dated brackets after them. Anyone checking can
compare this file against the version timestamped 2026-10-11 01:10 CT in the released repository.

A FORMULA THAT DID NOT EVALUATE TO ITS OWN ANSWER. D-17 read "100 x 80 x 2 templates x 3 samples =
144,000". That product is 48,000; the judge factor was missing. The 144,000 figure was right and the
arithmetic shown beside it was not, which is worse than a wrong number because it invites a reader
to check and then misleads them. Corrected to name all five factors.

THE CONTENT-BLIND PREDICTION USED THE WRONG QUESTION SET. It drew human label marginals from all 80
registered questions while the observed figure beside it came from that cell's parsed records only.
Wherever a cell had unparsed records the two sides of the comparison rested on different questions.
Corrected to use the parsed questions of each cell. Three of six cells moved: Llama-3.1 COMPARING
+0.181 to +0.165, Mistral-7B COMPARING +0.003 to +0.026, Llama-3.1 SCORING_CODE -0.014 to -0.013.
The three cells with no unparsed records are unchanged, which is the expected signature of this fix.
A selftest now runs the function over a deliberately half-parsed cell and fails if the old
whole-set formula returns.

---

## D-21. The promised artefact would have redistributed unlicensed text; it is now redacted
**Written 2026-10-11T15:03:44Z, after a referee measured it.**

TWO OF OUR OWN COMMITMENTS WERE IN CONFLICT AND WE HAD NOT NOTICED. The registration states that
the original repository "carries no licence file, so this study redistributes none of its contents".
The availability section separately promised the per-judge verdict files "with every individual
sample and its raw text". A judge's raw output routinely quotes the question and both candidate
answers back verbatim, so honouring the second commitment would have broken the first. Releasing
the artefact as described would have redistributed unlicensed upstream text.

HOW MUCH. Measured against the pinned upstream corpus of 400 texts, over all 4,640 raw samples:

    samples containing a verbatim upstream span of   >=8 words    >=12 words
    Llama-3.1                                           758          246
    Mistral-7B                                          458          126
    Qwen2.5 (table 2)                                    99           14
    Qwen2.5 (table 5)                                   194           24
    TOTAL                                              1509          410

WHAT IS RELEASED NOW. `redact_public.py` writes `results-public/`, in which every maximal run of
eight or more consecutive words occurring verbatim in the upstream questions or candidate answers is
replaced by `[upstream span redacted, sha256:<first 16 hex of the span>]`. 2,130 spans across 1,509
samples were removed. The hash lets a reader who already holds the upstream corpus confirm what was
taken out without us publishing it. The unredacted files stay local and are not released.

THE EIGHT-WORD THRESHOLD IS DELIBERATELY STRICTER THAN THE MEASUREMENT. A referee measured the
problem at twelve words; we redact at eight. For a licence control the safe direction is to remove
more than the minimum, so the published threshold is the stricter one and the twelve-word figures
are reported only for comparison.

ONE DISCREPANCY WE CANNOT FULLY RECONCILE, STATED RATHER THAN SMOOTHED. Our twelve-word count is
410; the referee's independent measurement was 405. We traced part of the gap to corpus scope - all
four upstream answer files give 410, the two the study actually used give 397 - but neither choice
reproduces 405 exactly, so the residual is tokenisation. It does not affect the control: redaction
runs at eight words, which removes a strict superset of anything either measurement would find, and
the published copies contain no surviving span at either threshold.

REDACTION DOES NOT MOVE ANY NUMBER, AND THIS IS ASSERTED RATHER THAN ASSUMED. Every statistic in
this paper is computed from the UNREDACTED files. `redact_public.py --assert-stats` recomputes the
H2 signed differences, the content-blind gaps and the c - s values from the originals and from the
redacted copies and requires exact equality; it passes. Redaction touches only
`verdicts[].samples[].raw` and no analysed field.

VERIFIED AFTERWARDS, NOT JUST INTENDED. Re-scanning the released copies finds zero samples
containing a verbatim upstream span of eight words or more, and zero at twelve.
