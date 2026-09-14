## Setup
1. Place `project-db.txt`, `Sales.csv`, and `Customers.csv` into `data/raw/`.
2. Run `python src/build_project_db.py` to generate `project-db.db`.
3. Notebooks in `notebooks/` can then connect to `data/raw/project-db.db`.