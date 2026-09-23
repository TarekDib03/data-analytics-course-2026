# Week 2 Mini-Project: A1C Testing, Race, and 30-Day Hospital Readmission
## Diabetes 130-US Hospitals Dataset (1999-2008)

---

## Research Question

Is there a relationship between whether a patient received an A1C (HbA1c) test
during their hospital stay and their likelihood of readmission — and, separately,
is there a relationship between race and readmission — and if so, are either of
these relationships robust to plausible alternative explanations?

Both questions emerged from open-ended exploration of the dataset rather than
being decided in advance. `A1Cresult` (which includes a large "Not Tested"
category alongside actual test results) stood out first, particularly since it
is the central variable the original dataset was constructed to study (Strack
et al., 2014). `race` emerged as a second thread worth investigating while
checking `A1Cresult`'s own missingness patterns earlier in the cleaning process.

**A note on scope and method:** `A1Cresult` and `race` are the two primary
variables of interest — the actual relationships this analysis set out to
explain. Five additional variables — `admission_type_desc`, `time_in_hospital`,
`medical_specialty`, `payer_code`, and `age` — are investigated throughout,
but not as separate research questions in their own right. Each was examined
specifically as a **candidate confounder**: a variable that might explain away
the primary relationship, rather than the test/race variables genuinely
mattering. This distinction matters methodologically — a confounder is
investigated *in service of* answering the primary question rigorously, not
as an independent question being asked for its own sake. Findings 3 and 4
(Part 1) and the confounder analysis in Finding 5 (Part 2) walk through each
of these five variables in turn.

---

## Data Preparation Summary

Before analysis, the following data quality issues were identified and
addressed, each with a rationale tied to what the missingness or irregularity
actually represented, rather than a single blanket rule:

| Issue | Finding | Treatment | Rationale |
|---|---|---|---|
| `weight` | 96.9% missing | Dropped | Not routinely collected; no analyzable signal remains |
| `max_glu_serum`, `A1Cresult` | 83-95% missing | Recoded to "Not tested" | Missingness reflects a clinical decision (test not ordered), not lost data |
| `payer_code`, `medical_specialty` | 40-49% missing | Recoded to "Unknown" | Administrative fields; missingness may itself be informative |
| `race` | 2.2% missing | Kept, recoded to "Unknown" | Checked missingness rate across admission types (1.2%-4.8%, no concentration) — consistent with close to random missingness, not a systematic exclusion pattern |
| `diag_1` | 21 missing (0.02%) | Rows dropped | Primary diagnosis; too small a loss to justify imputation risk |
| `diag_2`, `diag_3` | 0.35%-1.4% missing | Recoded to "None recorded" | Secondary/tertiary diagnoses; preserving the primary-diagnosis row was prioritized over dropping for incomplete secondary fields |
| Admission/discharge/source ID lookups | Merge initially failed for thousands of rows | Fixed a dtype mismatch (`int64` vs. `Int64`) between the lookup tables and main dataset before merging | "Looks identical when printed" does not mean "is the same type" — dtype must match for a merge key to work |
| Lookup table descriptions | Literal `NULL` values in the raw CSV were being silently converted to missing by `pandas.read_csv()`'s default NA handling | Re-read the CSV with `keep_default_na=False` to preserve `NULL` as a real category label | A dataset's own text can use the word "NULL" as a meaningful category, not as an indicator of missingness — this must be verified against the raw file, not assumed |

---

## Part 1: A1C Testing and Readmission

### Finding 1: A Significant Aggregate Association

A chi-square test of independence was run between `A1Cresult` and `readmitted`:

**Chi-square statistic: 92.20, p-value < 0.0001** (after excluding death/hospice discharges — see Finding 2)

| A1Cresult | <30 days | >30 days | Not readmitted |
|---|---|---|---|
| Norm | 10% | 32% | 58% |
| >7 | 10% | 34% | 55% |
| >8 | 10% | 36% | 54% |
| **Not tested** | **12%** | **36%** | **52%** |

Patients with a normal A1C result have the best outcomes; patients who were
never tested have the worst — both the lowest non-readmission rate and the
highest rate of rapid (<30 day) readmission.

### Finding 2: Robustness Check — Death and Hospice Discharges

Before trusting the readmission rates above, encounters ending in death or
hospice transfer were identified and excluded, since these patients cannot
be meaningfully described as "not readmitted" for reasons related to
diabetes management:

- `Expired`
- `Hospice / home`
- `Hospice / medical facility`
- `Expired at home. Medicaid only, hospice.`
- `Expired in a medical facility. Medicaid only, hospice.`

This affected roughly 2.4% of the dataset. **The core finding was essentially
unchanged after exclusion** (if anything, the gap between "Norm" and "Not
tested" widened slightly) — ruling out the possibility that the original
result was an artifact of critically ill, non-recoverable patients being
concentrated in the "Not Tested" group.

### Finding 3: A Plausible Confounder — Admission Type

Comparing the composition of each `A1Cresult` group by admission type
revealed that "Not Tested" patients were admitted electively at roughly
**twice the rate** of tested patients (~20% vs. ~10-13%), and via emergency
admission less often.

This raised the hypothesis that "Not Tested" patients might simply be a
lower-acuity population — but this was **not confirmed** by a follow-up
check: "Not Tested" patients also had the *shortest* average length of stay
(4.31 days vs. 4.7-4.9 days for tested groups), which is consistent with
lower acuity, not higher. If "Not Tested" patients look less severe on two
independent measures (admission type and length of stay) yet still show the
*worst* readmission outcomes, this actually strengthens rather than
undermines the original finding — it becomes harder to explain the pattern
away as "sicker patients just don't get tested."

### Finding 4: A More Serious Confounder — Medical Specialty, and Its Limits

Checking `A1Cresult` composition by admitting medical specialty revealed a
much starker pattern: surgical/procedural specialties (Orthopedics,
Orthopedics-Reconstructive, Radiology) had dramatically higher "Not Tested"
rates (91-94%) than internal-medicine-type specialties (Cardiology, Internal
Medicine, Family/General Practice, 78-85%). This makes clinical sense — an
orthopedic surgeon has little reason to routinely order an A1C test — and
suggests that whether a patient gets tested may be driven substantially by
**which specialty is treating them**, largely independent of the patient's
actual diabetes severity.

To test whether the original A1C-readmission relationship held up *within*
a single specialty (controlling for the specialty-level confound), the
analysis was repeated restricted to orthopedics patients alone. The result:
**no statistically significant relationship was detected (chi-square =
3.32, p = 0.77)**. However, this null result should not be over-interpreted:
three of the four `A1Cresult` groups within orthopedics had fewer than 80
patients each (compared to tens of thousands in the full dataset), making
this subgroup far too small to reliably detect an effect even if one exists.

### Part 1 Conclusion

There is a statistically significant, robust association at the population
level between A1C testing status and 30-day hospital readmission: patients
who are not tested have measurably worse outcomes, and this finding survives
two of the three robustness checks applied (death/hospice exclusion did not
change it; admission-type and length-of-stay composition, if anything,
strengthen the case that "Not Tested" is not simply a proxy for "healthier").

However, the specialty-stratified check reveals a genuine limitation of this
analysis: because testing rates vary so dramatically by specialty, and
because specialty likely also correlates with baseline readmission risk for
reasons unrelated to A1C testing, **it is not possible to confirm from
simple stratified crosstabs alone whether A1C testing has an independent
effect on readmission, or whether the aggregate association is substantially
explained by which specialty happens to treat a given patient.** Attempting
to isolate the effect by restricting to a single specialty ran into a sample
size wall, illustrating precisely why multivariate methods exist — a
technique that can hold multiple confounders constant *simultaneously*,
without fragmenting the sample into subgroups too small to analyze, would be
needed to resolve this question properly. This is a direct motivation for
the regression and causal inference methods covered later in this course
(Weeks 3-6).

### Part 1 Recommendation

Given the strength and robustness of the aggregate finding, but the
genuine uncertainty about whether it reflects a causal effect of testing
itself: **hospitals should consider a routine A1C check before discharge for
diabetic patients regardless of admitting specialty**, since current testing
practice appears to be driven substantially by specialty convention rather
than individual clinical need. This recommendation is offered as a
reasonable, low-cost precaution supported by a real association — not as a
proven causal fix — pending further analysis with methods capable of
properly controlling for specialty and other confounders simultaneously.

---

## Part 2: Race and Readmission

### Finding 5: A Robust Association Requiring Careful Interpretation

A second pattern emerged during exploration: `race` shows a statistically
significant relationship with readmission (chi-square = 302.26, p < 0.0001,
n = 99,323 across six categories with adequate sample sizes in every group).

| race | <30 days | >30 days | Not readmitted |
|---|---|---|---|
| Caucasian | 12% | 37% | 52% |
| AfricanAmerican | 11% | 35% | 53% |
| Hispanic | 10% | 32% | 58% |
| Other | 10% | 30% | 60% |
| Asian | 10% | 26% | 64% |
| **Unknown** | **8%** | **24%** | **68%** |

Unlike the A1C finding, **this pattern does not have a natural clinical-decision
explanation to test** — race is not something a hospital chooses to "do" to a
patient the way ordering a test is. This reframes the analytical goal:
rather than asking whether a hospital process should change, the goal here
is to determine what, if anything, race is actually standing in for.

**Two plausible confounding pathways were identified and checked:**

1. **Insurance/payer type.** Medicare (`MC`) share varies substantially by
   race: 37-42% for Caucasian and Unknown-race patients, versus 18-27% for
   AfricanAmerican, Hispanic, and Asian patients. Since Medicare is
   overwhelmingly age-eligibility-based, this strongly suggested age as an
   underlying driver rather than payer type itself.

2. **Age distribution.** This hypothesis was confirmed directly: Caucasian
   (46%) and Unknown-race (43%) patients are aged 70+ at roughly double the
   rate of AfricanAmerican (29%) and Hispanic (26%) patients. Older patients
   generally carry higher baseline readmission risk independent of race,
   making age a serious, concrete confounding candidate.

**A specific note on the "Unknown" race category:** this group has both the
best outcomes and the *lowest* rate of missing payer code (27%, versus 41-56%
for named race categories) — meaning "Unknown race" does **not** appear to be
a general marker of poor record-keeping at certain facilities. Whatever
causes race to go unrecorded appears distinct from what causes other fields
to go unrecorded, and remains an open question this analysis cannot resolve.

**Why this cannot be taken further with the tools used so far:** age and
payer type are themselves correlated with each other and with race
simultaneously. One-at-a-time stratification cannot determine whether race
has any association with readmission *after* accounting for age — doing so
would require a multivariate model holding multiple variables constant at
once, which is precisely the motivation for Week 3's regression methods.

### Part 2 Conclusion — Interpretive Caution

This finding must not be read as "race causes differences in readmission."
Race in administrative healthcare data is best understood as a proxy that
may reflect underlying differences in age, insurance access, socioeconomic
factors, or documented disparities in care delivery — none of which have
been isolated here. Presenting a raw racial disparity without this caveat
would risk misattributing a likely structural or demographic pattern to the
demographic category itself. The responsible conclusion is: **a real,
robust outcome disparity by race exists in this data, at least two plausible
non-racial explanatory pathways (age, insurance type) have been identified,
and disentangling them requires methods beyond simple stratification.** No
policy recommendation is offered for this finding, unlike Part 1 — a
demographic disparity of unknown origin does not translate into an
actionable intervention the way a testing-protocol gap does; the responsible
next step is further investigation with proper multivariate methods, not
a premature recommendation.

---

## Overall Methodological Note for Future Reference

Both parts of this analysis independently arrived at the same structural
limitation: checking one confounder at a time via stratified crosstabs is a
useful and honest way to stress-test a finding, but it has two real limits
worth remembering — (1) each additional stratification shrinks the sample
size, eventually making results too noisy to trust (the orthopedics subgroup
in Part 1), and (2) confounders are rarely independent of each other, so
controlling for one at a time cannot fully replicate the effect of
controlling for several simultaneously (age, race, and payer type in Part 2,
all correlated with one another). Both limitations point toward the same
solution: multivariate regression or purpose-built causal inference methods,
rather than an ever-finer sequence of manual crosstabs. This is the direct
motivation for Week 3 onward.
