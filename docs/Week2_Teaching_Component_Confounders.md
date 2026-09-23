# Week 2 Teaching Component
## Checking a Confounder vs. Controlling for a Confounder — and Why the Difference Matters

*Written as if explaining to a colleague who has run a crosstab before, but has never had to explain why "I checked for confounders" and "I controlled for confounders" are not the same claim.*

---

## The Setup: A Finding That Looked Solid

This week's analysis found a real, statistically significant pattern: patients who never received an A1C test had worse 30-day readmission rates than patients who did (chi-square = 92.20, p < 0.0001, on over 95,000 patients). That's a big, reliable sample — not a fluke.

The natural next step, and the right instinct, was to ask: **could something else explain this, rather than the test itself mattering?** This is where "checking a confounder" comes in.

---

## What "Checking a Confounder" Actually Means

Checking a confounder, in practice, means picking one variable you suspect might be driving the pattern, splitting your data by that variable, and seeing if the original relationship holds up within each split.

This week, two confounders were checked this way:

**Admission type and length of stay:** patients who weren't A1C-tested were more likely to be elective admissions and had shorter hospital stays — both signs of *lower* acuity. If anything, this made the original finding *more* surprising, not less — a group that looked healthier on two independent measures still had worse outcomes. This check **strengthened confidence** in the finding.

**Death/hospice discharges:** these patients were excluded entirely (since "not readmitted because deceased" isn't a meaningful outcome), and the core finding barely moved. This check **ruled out** one specific distortion.

Both of these are legitimate, useful checks. But then a third check hit a wall.

---

## Where Checking One at a Time Breaks Down

`medical_specialty` turned out to matter a lot: orthopedic surgeons almost never order A1C tests (91-94% "Not Tested"), while internal medicine physicians order them far more often (78-85% "Not Tested"). That's a plausible confounder — maybe specialty, not the test itself, explains the pattern.

So the natural next step was to **isolate** specialty by restricting the analysis to orthopedics patients only, and re-running the same test within that single group. The result: no significant relationship (p = 0.77) — but with only 50-80 patients in three of the four A1C categories, far too small a sample to trust either way.

**This is the actual limit of "checking one confounder at a time":** every time you split your data by another variable, your sample size shrinks. Eventually it shrinks so much that you can no longer tell the difference between "the effect genuinely disappeared here" and "there just aren't enough patients left to detect anything." Restricting to one specialty didn't answer the question — it just ran out of data before it could.

The same pattern showed up again, independently, with a completely different variable this week: `race` showed a real, robust readmission disparity (chi-square = 302.26, p < 0.0001). Checking it against `payer_code` and `age` revealed that Caucasian and "Unknown race" patients skew substantially older — and age plausibly explains part of the payer-type pattern and part of the outcome disparity too. But age, race, and payer type are all correlated *with each other simultaneously*. There's no single "restrict to one group" move available here, the way there was with orthopedics — because unlike specialty (a discrete category you can subset to), age interacts with *both* race and outcome continuously and jointly.

---

## The Actual Distinction: Checking vs. Controlling

**Checking a confounder** = splitting your data by one variable at a time, and seeing if a relationship holds up within each split. This is done with tools you already know well — `groupby()`, `crosstab()`, a chi-square test on a subset. It's honest, useful, and a necessary first step. But it has two hard limits:

1. **Sample size erosion.** Every split shrinks your data. Split enough times, and you can no longer detect anything, whether or not something is really there (the orthopedics problem).
2. **It only handles one variable at a time.** If two potential confounders are themselves correlated with each other (age and race, in this case), checking them one by one can't tell you what happens when you account for *both simultaneously* — because holding "just age" constant while race also shifts isn't the same as holding both fixed at once.

**Controlling for a confounder** means holding multiple variables constant *simultaneously*, within a single model, without throwing away data by splitting it into ever-smaller groups. This is what multivariate regression does: instead of asking "what's the readmission rate for orthopedics patients only," a regression model can ask "holding specialty, age, and admission type all fixed at once, does A1C testing status still predict readmission?" — using the *entire* dataset in one model, rather than fragmenting it.

**A useful mental image:** checking a confounder is like looking at a slice of a photograph one variable at a time — informative, but you only ever see one dimension cut out. Controlling for a confounder is like looking at the whole photograph while mathematically holding several dimensions fixed at once, without needing to physically cut the photo into smaller and smaller pieces to do it.

---

## Why This Matters Beyond This Week's Dataset

This isn't a one-off quirk of the diabetes dataset — it's a structural limitation of stratification as a technique, and it will come up in any real-world analysis with more than one plausible confounder (which is nearly all of them). The signal that you've hit this wall is exactly what happened twice this week:

- You have a real, significant finding.
- You check a confounder and the sample size gets uncomfortably small, or
- You have *multiple* plausible confounders that are themselves correlated with each other, so checking them one at a time can't cleanly separate their effects.

When either of those happens, the honest conclusion isn't "the effect isn't real" or "the effect is definitely real" — it's **"stratification has reached its limit here; a method that can hold several variables constant at once is needed to go further."** That's not a failure of the analysis — recognizing it is the actual skill. It's also precisely the motivation for regression (Week 3) and, later, purpose-built causal inference methods like difference-in-differences and propensity score matching (Weeks 5-6), which exist specifically to do simultaneously what one-at-a-time crosstabs structurally cannot.

---

## A Related, Smaller Lesson Worth Keeping: "Not Tested" Doesn't Always Mean the Same Thing

One more thing worth flagging from this week, since it's an easy trap: `A1Cresult` and `max_glu_serum` are both diabetes-related lab tests, both handled with the identical "missing = Not tested" recoding — but they showed *opposite* patterns. For A1C, "Not Tested" was the worst-outcome group. For glucose serum, "Not Tested" looked unremarkable, while the actual abnormal *values* (`>200`, `>300`) drove a clear dose-response pattern instead.

The likely reason: A1C reflects long-term average blood sugar control, so *whether it gets ordered at all* may itself correlate with how proactively a patient's diabetes is being managed. Glucose serum is a single-moment snapshot — its *value* carries the signal, not whether the snapshot was taken.

**The transferable lesson:** never assume a pattern found in one variable automatically transfers to a superficially similar variable, even within the same dataset, cleaned the same way. Each variable's missingness needs to be understood on its own terms — a lesson that echoes back to Section 10 of the Week 1 teaching document, just applied to *interpretation* this time rather than *cleaning*.
