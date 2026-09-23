# Data Analytics Course 2026

A 12-week applied data analytics course repo — SQL, statistics, causal inference,
applied ML, and automation, built around real (often messy) public datasets in
epidemiology, healthcare, education, and socioeconomic research.

---

## Setup

This repo does not include raw data files directly — they're either publicly
downloadable, sourced from a Coursera guided project not intended for
redistribution, or licensed for reuse with attribution. Follow the steps below
to regenerate everything locally.

### Chinook Database (Week 1, SQL fundamentals)

1. Download the Chinook `.sqlite` file from the official releases page:
   https://github.com/lerocha/chinook-database/releases
2. Place it in `data/raw/`.

### project-db.db (Week 1, SQL Window Functions for Analytics)

This dataset comes from the Coursera Guided Project "SQL Window Functions
for Analytics." Its source files are not redistributed in this repo.

1. Complete (or re-access) the guided project on Coursera to obtain:
   - `project-db.txt`
   - `Sales.csv`
   - `Customers.csv`
2. Place all three files into `data/raw/`.
3. From the repo root, run:
```bash
python src/build_project_db.py
```
   This creates `data/raw/project-db.db`, standardizing all column names
   to snake_case in the process (see `src/build_project_db.py` for details).

### Diabetes 130-US Hospitals Dataset (Week 2, ambiguous mini-project)

Source: UCI Machine Learning Repository, CC BY 4.0 (freely usable with
attribution).
https://archive.ics.uci.edu/dataset/296/diabetes-130-us-hospitals-for-years-1999-2008

1. Download and unzip:
   https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip
2. Place `diabetic_data.csv` and `IDS_mapping.csv` into `data/raw/`.
3. Open `notebooks/week2_diabetes_readmission_exploration.ipynb` and run top
   to bottom. See `docs/Week2_A1C_Readmission_Analysis.md` for the full
   write-up, methodology, and findings.

**Note:** `data/raw/` is git-ignored — none of the files above will appear
in this repository. Only the *code* that builds/uses/cleans them is tracked.

---

## Migrating SQLite Databases into PostgreSQL

Some SQL features (`GROUPING SETS`, `ROLLUP`, `CUBE`, `RIGHT JOIN`, `FULL OUTER JOIN`)
aren't supported in SQLite. To practice these natively, both `Chinook_Sqlite.sqlite`
and `project-db.db` are mirrored into a local PostgreSQL database, each in its own schema.

### 1. Create the target database and schemas

In pgAdmin 4's Query Tool (or `psql`), run:
```sql
CREATE DATABASE analytics_course;
```
Then, connected to `analytics_course`:
```sql
CREATE SCHEMA IF NOT EXISTS chinook;
CREATE SCHEMA IF NOT EXISTS project_db;
```

### 2. Install the required Python packages
```bash
pip install psycopg2-binary sqlalchemy python-dotenv
pip freeze > requirements.txt
```

### 3. Set up your database password securely (see "Secrets Management" below)

Create a `.env` file in the repo root (this file is git-ignored and never
committed):
```
POSTGRES_PASSWORD=your_actual_password
```

### 4. Run the migration script
```bash
python src/migrate_sqlite_to_postgres.py
```
This reads every table out of both SQLite files, standardizes column names to
lowercase snake_case (avoiding Postgres case-sensitivity issues — see
`src/migrate_sqlite_to_postgres.py` for details), and writes them into the
`chinook` and `project_db` schemas respectively.

### 5. Verify in pgAdmin 4

Refresh the `analytics_course` database in the sidebar. You should see both
schemas populated with their respective tables, fully queryable — e.g.,
`SELECT * FROM chinook.track LIMIT 5;` or `SELECT * FROM project_db.sales LIMIT 5;`.

---

## Secrets Management: Never Hardcode Passwords

Any script or notebook that connects to a database needs a password — but that
password must **never** be typed directly into a file that gets committed to
Git. Once a secret is pushed, even briefly, it persists permanently in Git's
history and is recoverable by anyone with access to the repo, even after being
"removed" in a later commit.

**The pattern used throughout this repo:**

1. Real values live in a `.env` file at the repo root (git-ignored, never pushed):
   ```
   POSTGRES_PASSWORD=your_actual_password
   ```
2. A `.env.example` file (safe to commit) documents which variables are needed,
   without real values:
   ```
   POSTGRES_PASSWORD=your_password_here
   ```
3. Scripts and notebooks load secrets at runtime via `python-dotenv`, never
   hardcoding them:
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()
   POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
   ```

**Before every commit, it's worth checking that nothing slipped through:**
```bash
git grep -i "password"
```
Review every match — it should only ever show variable names or placeholders,
never an actual value.

**If a real secret is ever accidentally committed:** editing the file
afterward is not sufficient, since the old commit still contains it in
history. For a local development database like this one, the simplest fix is
to change the actual password — far less effort than rewriting Git history,
and it fully closes the exposure.

---

## Repository Structure

```
data-analytics-course-2026/
├── .env                  <- secrets, git-ignored, never pushed
├── .env.example          <- documents required variable names (safe to commit)
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── raw/               <- git-ignored; see Setup above for how to populate
├── docs/                  <- write-ups and reference material (see Documentation below)
├── notebooks/             <- exploratory and per-week analysis notebooks
└── src/                   <- reusable code, imported by notebooks (see Utilities below)
```

### Utilities in `src/`

- **`build_project_db.py`** — builds `project-db.db` from a raw SQL script and
  two CSVs, standardizing column names to snake_case automatically along the way.
- **`migrate_sqlite_to_postgres.py`** — migrates any SQLite database's tables
  into a PostgreSQL schema, with the same column-name standardization and
  secure `.env`-based password handling.
- **`data_cleaning.py`** — general-purpose missing-value-filling utilities
  (`fill_missing_values`, `fill_vars`) for recoding NaNs to meaningful category
  labels (e.g., "Not tested", "Unknown") rather than dropping or imputing them.

### Documentation in `docs/`

- **`Week1_Teaching_Component_SQL_Concepts.md`** — comprehensive SQL reference:
  window functions, joins, CTEs/subqueries, aggregate functions, `GROUPING SETS`/
  `ROLLUP`/`CUBE`, and data provenance/reproducibility, built from real queries
  developed during Week 1 (Chinook + two Coursera guided projects).
- **`Week2_A1C_Readmission_Analysis.md`** — full write-up of the Week 2
  ambiguous mini-project: data cleaning rationale, statistical findings, and
  multiple confounder robustness checks on the diabetes readmission dataset.
- **`Week2_Teaching_Component_Confounders.md`** — the distinction between
  *checking* a confounder (stratification) and *controlling* for one
  (multivariate methods), illustrated with this course's own findings.
- **`Week1_Day1_Git_Reference_Notes.md`** — Git/GitHub workflow reference from
  the very first setup session (branching, `.gitignore` gotchas, debugging workflow).
- **`12-Week_Data_Analytics_Course.md`** — the full course curriculum, week by
  week, with topics, sources, and milestones.
