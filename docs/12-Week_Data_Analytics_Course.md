# 12-Week Applied Data Analytics Course
### From Theoretical Knowledge → Applied Practice → Teaching Others
**Focus fields:** Epidemiology, Healthcare, Education, Socioeconomic Research
**Designed for:** Transition into analytics + capacity-building consulting for NGOs/nonprofits

---

## 1. Baseline (Where You're Starting From)

- **Theory-strong, application-weak.** You know linear/logistic regression, clustering, and even advanced methods (survival analysis, causal inference, mixed models, Bayesian methods) *conceptually*, but have never applied them under real project constraints.
- **Guided-learning history.** Past practice with Python/R was structured (courses, notebooks with answer keys) — the "figure it out from ambiguity" muscle is underdeveloped.
- **Strong narrative communicator, weak technical defender.** You're skilled at donor reports for program managers/donors (non-technical audiences), but untested at defending methodological choices to a technical peer.
- **Basic engineering practices.** Git, SQL beyond simple queries, and reproducible workflows (notebooks, project structure, documentation) are all at a "basic" level — functional, not robust.
- **Good self-rescue instincts.** You use Stack Overflow/AI tools effectively when stuck — meaning we can push you into unguided territory without you getting stranded, as long as you're also asked to explain *why* a fix worked.

**Implication:** This course is less about new concepts, more about *applied, unguided, real-dataset re-practice*, with a technical-rigor and teaching layer built in from day one.

---

## 2. Destination (What Success Looks Like at Week 12)

By the end of Week 12, you will have:

1. **A flagship capstone project** — an end-to-end, technically defensible epidemiology/healthcare analysis, built on a real public dataset, using applied ML, survival analysis, and/or causal inference methods. Hosted on GitHub as a portfolio piece.
2. **A separate teaching project** — a simpler, NGO-staff-friendly case study designed explicitly for training beginners.
3. **A recorded video series** walking through the teaching project as if training NGO/nonprofit staff.
4. **A live dry-run presentation** of the teaching project (to a colleague, friend, or peer) — the real test of "trainer-ready," not just "content-created."
5. Working fluency in **Python + SQL** (primary stack), **Tableau + Streamlit** (dashboarding), with translation-level fluency in **R and Power BI**.
6. Applied, practical exposure to **deep learning** (one concrete health-relevant task), **causal inference**, **survival analysis**, and **automation** (scripted pipelines + AI-assisted workflows).

**Long-term positioning:** capacity-building consultant/trainer for NGO and nonprofit staff in data analytics.

---

## 3. What to Ignore For Now

Explicitly out of scope for these 12 weeks — revisit later if a specific job or project demands it:

- Measure-theoretic/proof-heavy statistics, derivations of gradient descent/backpropagation (intuition only, not proofs)
- Big data / distributed computing (Spark, BigQuery, Hadoop, cloud data warehouses)
- Full web app development (Flask, Django, React) — lightweight dashboards (Streamlit, Tableau, Power BI) only
- R and Power BI as full parallel tracks — treated as periodic "translation" exercises, not deep independent practice
- Chasing every ML/AI trend — depth over breadth on the methods most relevant to your target fields

---

## 4. The 12-Week Sequence

### Phase 1: Foundations & Re-Anchoring (Weeks 1–3)
Rebuild engineering habits and start the ambiguity-tolerance muscle immediately.

**Week 1 — Engineering Foundations**
- Git/GitHub: branching, commits, pull requests, resolving conflicts
- SQL deep-dive: multi-table joins, subqueries, window functions, writing queries from scratch (not modifying given ones)
- Reproducible project structure (folders, environments, README conventions)
- *Milestone:* Push a small, self-contained analysis (any dataset) to GitHub with a clean README, proper commit history, and a runnable environment file. Full rubric provided upfront.
- *Teaching component (written):* A README section explaining your project structure "for a beginner" — as if handing this repo to a new NGO colleague.

**Week 2 — Reproducible Workflows + First Ambiguous Mini-Project**
- Notebook hygiene (Jupyter/R Markdown structured for others to rerun)
- Mini-project: given a messy, real dataset (I'll shortlist 2-3 options) with **no instructions**, produce a basic exploratory analysis
- *Milestone:* Notebook runs top-to-bottom with no errors on a fresh environment; you self-verify against a checklist (rubric still provided upfront).
- *Teaching component (recorded):* 2-3 min video explaining one finding from your EDA as if to a program manager.

**Week 3 — Re-Applying Core Stats/ML on Real Data**
- Linear/logistic regression, clustering — but on messy real-world data with genuine ambiguity (missing data, outliers, unclear variable definitions)
- Emphasis on *justifying* choices (why this model, why this transformation) — first taste of technical defense
- *Milestone:* A short methods writeup defending 3 analytical decisions you made. Rubric still provided upfront.
- *Teaching component (written):* Explain one modeling decision in plain language.

---

### Phase 2: Applied Depth — Epidemiology-Relevant Methods (Weeks 4–6)
Rubric shifts to co-created checklists starting Week 5 — you draft your own "definition of done," then compare against mine.

**Week 4 — Survival Analysis**
- Kaplan-Meier curves, Cox proportional hazards, applied to a real health/epi dataset
- *Milestone:* A working survival analysis notebook + written interpretation for a non-technical audience.
- *Teaching component (recorded):* Explain "what survival analysis tells us" in under 3 minutes, no jargon.

**Week 5 — Causal Inference I (Difference-in-Differences)**
- DiD design, parallel trends assumption, applied to a policy/program evaluation dataset (very relevant to M&E background)
- *Milestone:* You draft your own checklist for "what a defensible DiD analysis needs" before starting; compare against mine at week's end.
- *Teaching component (written):* A short explainer of DiD using a real-world program example.

**Week 6 — Causal Inference II (Propensity Score Matching) + Buffer/Flex Week**
- PSM applied to a health or socioeconomic dataset
- **This week doubles as a buffer** — if any prior week ran long or hours dropped, catch up here instead of falling behind.
- *Milestone:* PSM analysis + a short comparison of DiD vs. PSM (when to use which).
- *Teaching component (recorded):* 3-minute video comparing the two methods for a non-technical audience.

---

### Phase 3: Modern Tools — ML, AI, Automation, Deep Learning (Weeks 7–9)

**Week 7 — Applied ML + AI in Health/Epi Contexts**
- A predictive modeling task (e.g., disease outcome prediction) using classical ML
- Light exploration of AI/LLM-assisted analysis (e.g., using AI tools for literature summarization, code generation, data documentation)
- *Milestone:* A working predictive model + a written reflection on where AI tools sped up vs. risked your workflow.
- *Teaching component (written):* "3 ways AI tools can help (and 2 ways they can hurt) an NGO analyst."

**Week 8 — Automation: Scripted Pipelines + AI-Assisted Workflows**
- Build a script that automates a repeatable task end-to-end (pull → clean → analyze → report) — directly modeled on donor-reporting cycles
- Layer in AI-assisted drafting for narrative sections
- *Milestone:* A working automated pipeline script, documented, that could plausibly replace a piece of your old M&E reporting routine.
- *Teaching component (recorded):* Demo video of the pipeline running, explained simply.

**Week 9 — Applied Deep Learning (Concrete, Field-Relevant Task)**
- One hands-on neural network project — e.g., basic image classification (skin lesion/x-ray) or simple NLP text classification (symptom/survey text)
- Emphasis on intuition and application, not theory/derivation
- *Milestone:* A working (even if simple) deep learning notebook + a plain-language explanation of what the model is doing and its limitations.
- *Teaching component (written):* "When would I actually reach for deep learning vs. simpler methods?" — a decision-guide paragraph.

---

### Phase 4: Capstone, Teaching Project, and Delivery (Weeks 10–12)
Minimal upfront rubric from here — you define "good" and defend it, closer to real consulting conditions.

**Week 10 — Capstone Build**
- Full end-to-end epidemiology/healthcare analysis combining methods from Weeks 4-9 as appropriate (survival analysis and/or causal inference, possibly ML)
- Includes a technical writeup: methods, assumptions, limitations — written for a technical reviewer, not a donor
- *Milestone (hard gate):* Capstone repo complete, documented, and ready for review — bring it back for real critique.
- *Teaching component (recorded):* A 5-minute "defend your capstone" video, as if presenting to a skeptical technical peer.

**Week 11 — Teaching Project + Video Series Build**
- Design and build the separate, beginner-friendly teaching case study
- Script and record the training video series for NGO/nonprofit staff
- Light R/Power BI translation exercise: recreate one piece of the teaching project in R and/or Power BI for job-market fluency
- *Milestone (hard gate):* Video series drafted/recorded, teaching materials complete.

**Week 12 — Live Dry-Run + Buffer/Wrap-Up**
- Deliver the live dry-run presentation of the teaching project to a real audience (colleague, friend, peer group)
- Incorporate feedback, finalize GitHub portfolio, finalize video series
- **This week also serves as final buffer** if earlier weeks slipped
- *Milestone (hard gate):* All three destination deliverables complete — capstone repo, video series, live presentation delivered.

---

## 5. Milestone & Gating Summary

| Weeks | Rubric Style | Gate Type | Teaching Component |
|---|---|---|---|
| 1–4 | Full rubric provided upfront | Weekly self-verified checklist | Alternating written/recorded |
| 5–8 | You draft checklist, compare to mine | Weekly self-verified + phase review | Alternating written/recorded |
| 9–12 | Minimal upfront rubric, self-defined "done" | Hard review gates (capstone, teaching project, live presentation) | Alternating written/recorded, culminating in full video series + live talk |

Buffer weeks: **Week 6** and **Week 12** both carry flex capacity in case your available hours drop from 30-40/week to 15-20/week.

---

## 6. Next Steps

1. I'll shortlist 2-3 candidate public epidemiology/healthcare datasets for your capstone (separate message) — feel free to bring your own candidates in parallel.
2. Confirm this structure works, or flag any week you want rebalanced.
3. We start Week 1 whenever you're ready.
