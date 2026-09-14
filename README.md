## Setup

This repo does not include raw data files directly — they're either publicly
downloadable or sourced from a Coursera guided project not intended for
redistribution. Follow the steps below to regenerate everything locally.

### Chinook Database (Week 1, SQL fundamentals)

1. Download the Chinook `.sqlite` file from the official releases page:
   https://github.com/lerocha/chinook-database/releases
2. Place it in `data/raw/`.

### project-db.db (SQL Window Functions for Analytics)

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

**Note:** `data/raw/` is git-ignored — none of the files above will appear
in this repository. Only the *code* that builds/uses them is tracked.