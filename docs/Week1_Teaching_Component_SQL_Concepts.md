# Week 1 Teaching Component
## SQL Window Functions, Joins, CTEs, and Subqueries — Explained for a Beginner

---

## Introduction: Objectives and Learning Outcomes

**Objective:** This document consolidates everything covered during Week 1's SQL practice — spanning hands-on queries against the Chinook database, two Coursera guided projects, and a real data-provenance problem encountered while building a custom database — into a single, structured reference. The goal isn't just to record *what was learned*, but to preserve the *reasoning* behind each concept: why a query behaves the way it does, what assumptions are hiding inside a default behavior, and how to diagnose a surprising result rather than just memorizing a fix. This document is also the Week 1 written teaching component — meaning it's written to be usable by someone else (a beginner colleague, or a future NGO training participant) rather than just as a personal cheat sheet.

**By the end of this document, the reader should be able to:**

1. **Explain the difference between `RANK()`, `DENSE_RANK()`, and `ROW_NUMBER()`**, and predict how each will behave differently on data containing ties.
2. **Write window functions correctly**, understanding the required `OVER()` structure, the role of `PARTITION BY` and `ORDER BY`, and where window functions can (and cannot) legally appear in a query.
3. **Use `LEAD()`, `LAG()`, `FIRST_VALUE()`, `LAST_VALUE()`, and `NTH_VALUE()`** to compare a row against other rows in its partition, and recognize when a function's result depends on the window *frame*, not just the ordering.
4. **Correctly diagnose window frame behavior** — explain the difference between `ROWS`, `RANGE`, and `GROUPS` frame modes, know when SQL applies a default frame silently, and know how to widen a frame explicitly with `UNBOUNDED PRECEDING`/`FOLLOWING` when needed.
5. **Choose the appropriate join type** (`INNER`, `LEFT`, `RIGHT`, `FULL OUTER`, `CROSS`, `SELF`) based on how missing matches should be handled, and understand why the default (`INNER JOIN`) can silently drop real data on messier datasets.
6. **Distinguish `WHERE` from `HAVING`**, understand the order in which SQL clauses actually execute, and recognize how that execution order affects window functions too (a filter applied via `WHERE` limits what a partition can ever "see").
7. **Write `CASE WHEN` logic**, including the conditional-aggregation pattern for counting/summing conditionally within a single query.
8. **Use `NTILE()` to bucket data into quantiles** (e.g., income quintiles) — a pattern directly relevant to socioeconomic and health equity analysis.
9. **Replicate `GROUPING SETS`, `ROLLUP`, and `CUBE`** using `UNION ALL` in SQL engines (like SQLite) that don't natively support them, and understand what distinguishes the three from one another.
10. **Recognize a reproducibility gap** in a data pipeline — specifically, understand why a database file alone is not sufficient, and know how to write a build script that regenerates derived data from raw sources in a repeatable way.

**A note on how this document was built:** every concept here was arrived at through actually running queries, hitting a genuinely confusing or "wrong-looking" result, and diagnosing *why* — rather than being explained upfront in the abstract. That approach is intentional and worth preserving if this document is ever adapted for teaching others: a debugged surprise is a far stronger teaching moment than a fact stated in isolation.

---

## 1. RANK() vs. ROW_NUMBER() — How They Handle Ties

Imagine you're ranking tracks by price within each music genre. Some tracks are tied at the exact same price — so what rank do they get?

**`RANK()`** gives tied rows the *same* rank, and then **skips** the next rank number(s) to account for how many rows were tied. If 40 tracks in the "Alternative" genre are all priced at $0.99, all 40 of them get rank `1` — because they're genuinely, mathematically tied. There's no meaningful way to say one $0.99 track outranks another.

**`ROW_NUMBER()`** never ties. It just counts — `1, 2, 3, 4...` — even if every single row has the exact same value. It picks an arbitrary order among the ties (based on whatever the database happens to process first) and numbers them sequentially regardless.

**The practical difference, in one sentence:** `RANK()` tells you the *truth* about ties (some things really are equal), while `ROW_NUMBER()` *forces* a strict order even when the underlying data doesn't actually support one.

**Real example encountered this week:** ranking Chinook tracks by `UnitPrice` within each genre returned rank `1` for almost every row. At first this looked like a bug — but checking `COUNT(DISTINCT UnitPrice)` per genre revealed that most genres only have a *single* price point across all their tracks (e.g., every "Alternative" track is $0.99). With zero price variation inside the genre, `RANK()` was working exactly as intended — everyone tied for first, because everyone genuinely *is* tied. `ROW_NUMBER()` on the same data would have quietly handed out 1 through 40, implying a false sense of ordering that doesn't reflect reality.

**Lesson:** when a ranking result looks "too flat" or "too repetitive," check whether the data itself lacks variation before assuming the code is broken. `RANK()` surfaces that flatness; `ROW_NUMBER()` can hide it.

There's also a third option worth knowing: **`DENSE_RANK()`**, which is like `RANK()` in that ties share a rank, but it does *not* skip numbers afterward. So if 5 rows tie for rank 1, `RANK()` jumps straight to rank 6 for the next group, while `DENSE_RANK()` continues at rank 2.

| Function | Ties get same rank? | Skips numbers after a tie? |
|---|---|---|
| `RANK()` | Yes | Yes |
| `DENSE_RANK()` | Yes | No |
| `ROW_NUMBER()` | No — always unique | N/A |

---

## 2. The General Rules of Window Functions

A window function always follows this shape:

```sql
SELECT column,
       WINDOW_FUNCTION() OVER (
           PARTITION BY some_column   -- optional: restart the calculation per group
           ORDER BY another_column    -- optional: defines order within each partition
       ) AS result_alias
FROM table;
```

A few rules worth internalizing:

- A window function must be followed by `OVER(...)` — that clause is what makes it a "window" function rather than a regular one.
- Window functions can appear in the `SELECT` list or in `ORDER BY` — but **not** directly in `WHERE`, `GROUP BY`, or `HAVING`. If you need to filter based on a window function's result, you typically have to wrap the whole query in a subquery or CTE first, then filter in the outer layer.
- `PARTITION BY` is like a `GROUP BY` that doesn't collapse rows — it just tells the window function "restart your calculation for each group," while every original row stays visible in the output.
- `ORDER BY` inside `OVER()` determines the order used for ranking, running totals, or "previous/next row" functions — and it's completely independent of any `ORDER BY` at the very end of the query (which just controls the final display order of results).

---

## 3. LEAD(), LAG(), and FIRST_VALUE()

These are window functions that let you look at *other rows* relative to the current one — something that's normally impossible in plain SQL without a self-join.

**`LAG(column, n)`** — looks *backward* n rows (default n=1) within the partition. Useful for comparing a row to the one before it — e.g., "what was this customer's previous invoice total?"

```sql
SELECT CustomerId, InvoiceDate, Total,
       LAG(Total, 1) OVER (PARTITION BY CustomerId ORDER BY InvoiceDate) AS previous_invoice_total
FROM Invoice;
```

**`LEAD(column, n)`** — the mirror image, looking *forward* n rows. Useful for "what's the next invoice date after this one?" — handy for calculating the gap between a customer's purchases.

```sql
SELECT CustomerId, InvoiceDate,
       LEAD(InvoiceDate, 1) OVER (PARTITION BY CustomerId ORDER BY InvoiceDate) AS next_invoice_date
FROM Invoice;
```

**`FIRST_VALUE(column)`** — returns the *first* value within the partition, based on the specified order, repeated across every row in that partition. Useful for comparing every row to a fixed reference point — e.g., "how does this invoice compare to this customer's very first invoice?"

```sql
SELECT CustomerId, InvoiceDate, Total,
       FIRST_VALUE(Total) OVER (PARTITION BY CustomerId ORDER BY InvoiceDate) AS first_invoice_total
FROM Invoice;
```

**Why these matter in practice:** `LAG`/`LEAD` are the backbone of time-series-style comparisons (month-over-month change, day-over-day change) without needing a self-join. `FIRST_VALUE` (and its counterpart `LAST_VALUE`) are useful for baseline comparisons — very relevant later on for things like "how has a patient's health metric changed since their first recorded visit."

---

## 4. Types of Joins

Joins determine what happens to rows that *don't* have a perfect match in the other table — this is where a lot of real-world data bugs quietly hide.

- **`INNER JOIN`** (the default when you just write `JOIN`): only keeps rows that have a match in *both* tables. If a track has no matching album, it disappears from the results entirely.
- **`LEFT JOIN`** (a.k.a. `LEFT OUTER JOIN`): keeps *every* row from the left table, filling in `NULL` for any columns from the right table that don't have a match. Critical when you need to know about missing relationships — e.g., "which customers have never placed an invoice?" would require a `LEFT JOIN` from Customer to Invoice, then filtering for `NULL` invoice values.
- **`RIGHT JOIN`** (a.k.a. `RIGHT OUTER JOIN`): the mirror image of `LEFT JOIN` — keeps every row from the right table instead. (Not supported in SQLite, though common in PostgreSQL/SQL Server — usually you can just flip the table order and use `LEFT JOIN` instead.)
- **`FULL OUTER JOIN`**: keeps everything from both tables, matched where possible, `NULL`-filled where not. (Also not supported natively in SQLite — usually simulated with a `UNION` of a `LEFT JOIN` and a `RIGHT JOIN`.)
- **`CROSS JOIN`**: pairs *every* row in one table with *every* row in the other — no matching condition at all. Rarely what you want by accident (it multiplies row counts fast), but occasionally useful for generating all possible combinations of two sets.
- **`SELF JOIN`**: not a different keyword — just a regular join where a table is joined to itself, usually to compare rows within the same table (e.g., finding employees who share the same manager).

**Why this matters:** the choice of join type is a *decision*, not a default. Chinook is clean enough that `INNER JOIN` rarely causes surprises — but on real, messier datasets (which we'll hit starting Week 2), silently using `INNER JOIN` when you needed `LEFT JOIN` is one of the most common ways to accidentally throw away real data without noticing.

---

## 5. CTEs vs. Subqueries

Both let you break a complex query into smaller, more manageable pieces — they're two different ways of expressing the same underlying logic.

**A subquery** is a query nested inside another query, often inside `FROM`, `WHERE`, or `SELECT`:

```sql
SELECT CustomerId, Total_Spent
FROM (
    SELECT CustomerId, SUM(Total) AS Total_Spent
    FROM Invoice
    GROUP BY CustomerId
)
WHERE Total_Spent > 50;
```

**A CTE (Common Table Expression)**, written with `WITH`, does the same thing but names the intermediate result up front, so the final query reads top-to-bottom like a sequence of steps rather than being nested inside itself:

```sql
WITH customer_totals AS (
    SELECT CustomerId, SUM(Total) AS Total_Spent
    FROM Invoice
    GROUP BY CustomerId
)
SELECT CustomerId, Total_Spent
FROM customer_totals
WHERE Total_Spent > 50;
```

**When to prefer which:**
- CTEs tend to be more **readable** once you have multiple layers of logic, since you can stack several `WITH` blocks in sequence and refer back to earlier ones — nested subqueries get hard to read fast once you go more than one level deep.
- CTEs can be **referenced more than once** in the same query without repeating the logic, whereas a subquery would need to be duplicated if used in two places.
- Subqueries are often quicker to write for a single, one-off filtering step, and are perfectly fine for simple cases.
- Performance is usually equivalent in modern databases (including SQLite) — the choice is mostly about readability and maintainability, not speed.

**Personal example from this week:** the "customers who spent more than average" query was solved two different ways — once as a nested subquery inside `HAVING`, and once as a CTE. Both were logically identical, but the CTE version reads more like a sentence ("first compute each customer's total, then compare it to the average of those totals") — which becomes a real advantage once queries grow more complex.

---

## 6. Aggregate Functions

Aggregate functions take *many* rows and collapse them down into a *single* summary value. They're the foundation everything else this week builds on top of.

The core ones:

- **`COUNT()`** — how many rows (or non-null values in a column).
- **`SUM()`** — total of a numeric column.
- **`AVG()`** — average of a numeric column.
- **`MIN()` / `MAX()`** — smallest/largest value in a column.

Used alone, an aggregate function collapses the *entire* table into one row:

```sql
SELECT AVG(Total) FROM Invoice;
```

Used with `GROUP BY`, it collapses the table into one row *per group* instead of one row overall:

```sql
SELECT CustomerId, SUM(Total) AS Total_Spent
FROM Invoice
GROUP BY CustomerId;
```

**How this connects to window functions:** this is actually the core distinction that makes window functions special. A plain aggregate with `GROUP BY` *collapses* rows — you lose the individual invoice rows and only see one row per customer. A window function (`SUM(Total) OVER (PARTITION BY CustomerId)`) computes the same total, but *keeps every original row visible* alongside it. Same math, very different shape of result.

---

## 7. Filtering: WHERE vs. HAVING

Both filter rows out of your results, but they operate at **different stages** of query execution — and mixing them up is one of the most common beginner errors.

**`WHERE`** filters rows *before* any grouping or aggregation happens. It works on the raw, row-level data:

```sql
SELECT * FROM Invoice WHERE Total > 5;
```

**`HAVING`** filters *after* grouping/aggregation has already happened. It works on the aggregated result, not the raw rows — which means it can filter on things like `SUM()` or `AVG()` that don't exist until the grouping is done:

```sql
SELECT CustomerId, SUM(Total) AS Total_Spent
FROM Invoice
GROUP BY CustomerId
HAVING SUM(Total) > 50;
```

**Why you can't just use `WHERE` for both:** at the point `WHERE` runs, the database hasn't computed `SUM(Total)` yet — grouping hasn't happened. So `WHERE SUM(Total) > 50` would fail; the aggregate simply doesn't exist yet at that stage. `HAVING` exists specifically to filter *after* that aggregation step.

**One-line mental model:** `WHERE` decides which raw rows get let into the group; `HAVING` decides which finished groups get let into the final answer.

**Real example from this week:** in the "customers who spent more than average" query, `HAVING SUM(I.Total) > (...)` was required — not `WHERE` — precisely because the filter depended on an aggregated value (`SUM`) that only exists after grouping by customer.

---

## 8. CASE WHEN Statements

`CASE WHEN` is SQL's version of if/else logic — it lets you create a new column whose value depends on a condition, evaluated row by row.

```sql
SELECT Name, UnitPrice,
       CASE 
           WHEN UnitPrice < 1.00 THEN 'Budget'
           WHEN UnitPrice BETWEEN 1.00 AND 1.98 THEN 'Standard'
           ELSE 'Premium'
       END AS price_tier
FROM Track;
```

A few things worth knowing:

- Conditions are checked **top to bottom**, and the first one that matches "wins" — so order matters if your conditions could overlap.
- `ELSE` is optional — if you omit it and no condition matches, the result is `NULL` for that row.
- `CASE WHEN` can be used almost anywhere a normal column can: in `SELECT`, `WHERE`, `ORDER BY`, and even inside aggregate functions.

**A genuinely useful pattern — conditional aggregation:** combining `CASE WHEN` with an aggregate function lets you count or sum *only* rows meeting a condition, without needing a separate query:

```sql
SELECT CustomerId,
       SUM(CASE WHEN Total > 10 THEN 1 ELSE 0 END) AS large_invoice_count,
       SUM(CASE WHEN Total <= 10 THEN 1 ELSE 0 END) AS small_invoice_count
FROM Invoice
GROUP BY CustomerId;
```

This is a very common real-world pattern — e.g., in a health dataset, counting how many patient visits fell into "high-risk" vs. "low-risk" categories, all in a single pass over the data instead of running multiple separate queries.

---

## 9. NTH_VALUE() and a Window Function Gotcha: Frames

`NTH_VALUE(column, n)` returns the value from the *n-th* row within the partition, based on the specified order — a generalization of `FIRST_VALUE()` (which is really just `NTH_VALUE(column, 1)`).

```sql
SELECT first_name, department, salary,
       NTH_VALUE(salary, 5) OVER (PARTITION BY department ORDER BY first_name) AS fifth_salary
FROM employees;
```

**The gotcha:** running this, the first four employees (alphabetically) in each department show `NULL` for `fifth_salary`, not the actual 5th value repeated across every row the way `FIRST_VALUE()` seems to. This looks like a bug, but it isn't — it's a direct result of how SQL defines the **window frame**.

Every window function operates over a *frame* — the specific slice of rows, within the partition, that it's allowed to "see" for the current row. When you write `ORDER BY` inside `OVER()` without explicitly specifying a frame, SQL silently applies a default:

```
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```

In plain language: "from the start of the partition, up through the current row — nothing beyond it." This default is why `FIRST_VALUE()` never seems to have this problem: the first row of the partition is *always* inside that frame, no matter which row you're currently looking at. But `NTH_VALUE(salary, 5)` needs at least 5 rows to already be inside the frame — so for the first four rows, the 5th value simply doesn't exist yet within the visible window, and the function correctly returns `NULL`. Once the frame grows to include the 5th row, the value appears and stays fixed for every row after that.

**The fix**, if you want the 5th value repeated across every row in the partition (matching how `FIRST_VALUE()` behaves by default), is to explicitly widen the frame to include the *entire* partition, not just "up to the current row":

```sql
SELECT first_name, department, salary,
       NTH_VALUE(salary, 5) OVER (
           PARTITION BY department 
           ORDER BY first_name
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS fifth_salary
FROM employees;
```

**Why this matters beyond just `NTH_VALUE()`:** the same default-frame behavior quietly applies to `SUM()`, `AVG()`, `COUNT()`, `MIN()`, and `MAX()` whenever they're used as window functions with an `ORDER BY`. This is actually what makes **running totals** possible — `SUM(Total) OVER (ORDER BY InvoiceDate)` naturally produces a cumulative sum, precisely *because* the default frame only looks backward to the current row. It's the same mechanism causing the `NTH_VALUE()` gotcha and the thing that makes running totals work — one default behavior, two very different-looking outcomes depending on which function you pair it with.

**One-line mental model:** `PARTITION BY` decides *which* rows a function can see at all; the **frame** decides *how much of that partition* is visible at each individual row. Most beginners only ever think about the first one.

---

## 10. Data Provenance: Why a `.db` File Isn't Enough

This week's SQL practice used two different databases: Chinook (a public, downloadable `.sqlite` file) and a custom `project-db.db` built from a raw SQL script plus two CSVs. The second case surfaced an important reproducibility lesson that's easy to miss.

**The problem:** the database file itself (`project-db.db`) was built once, by hand — running a `.txt` SQL script to create tables, then manually loading two CSVs into it, renaming columns along the way. The `.db` file worked fine locally, but it was never *saved as a repeatable process* — only the end result existed. Combine that with the `.gitignore` rule keeping raw data out of Git (`data/raw/*`), and the result is a project that only works on the exact machine where that manual process happened once. Clone the repo fresh, and there's nothing to regenerate the database from — the knowledge of *how* it was built lived only in memory, not in code.

**The fix:** write the "build" step as an actual script, not a one-time manual action. A build script belongs in `src/` (it's reusable infrastructure code, not analysis), and it should be able to reconstruct the database from the raw source files at any time:

```python
def build_database():
    conn = sqlite3.connect(DB_PATH)

    # Run the raw SQL script to create tables
    with open(SQL_SCRIPT_PATH, "r") as f:
        conn.executescript(f.read())

    # Load CSVs into tables, standardizing column names as you go
    sales_df = pd.read_csv(SALES_CSV_PATH)
    sales_df = standardize_columns(sales_df)
    sales_df.to_sql("sales", conn, if_exists="replace", index=False)

    conn.close()
```

**A related habit worth adopting: standardize column names programmatically, not by hand.** Raw CSVs are often messy — `"Customer ID"`, `"Sub-Category"`, `"Ship Mode"` — with spaces, inconsistent casing, and hyphens that make writing SQL awkward. Renaming these one-by-one by hand is exactly the kind of manual step that silently breaks reproducibility (as happened here). A small, general-purpose function fixes this permanently:

```python
import re

def standardize_column_name(col: str) -> str:
    col = col.strip().lower()
    col = re.sub(r"[\s\-]+", "_", col)
    return col
```

This converts any column name into a consistent `snake_case` format — `"Customer ID"` → `customer_id`, `"Sub-Category"` → `sub_category` — using a *rule*, not a hardcoded list. The advantage over a manual rename mapping: it keeps working correctly even when new raw files are added later with their own messy headers, without needing to remember or re-document every individual rename.

**The broader principle, worth carrying into every future project:** if a data file exists but the *process that created it* doesn't exist anywhere as code, the project isn't actually reproducible — it just happens to still work, for now, on one machine. The test to apply: could someone (including future-you, on a new laptop) regenerate every derived file from nothing but the raw sources and the code in the repo? If the honest answer is "only if they ask me how I did it," that's the signal a build script is missing.

---

## 11. NTILE() — Splitting Rows into Buckets

`NTILE(n)` divides the rows in a partition into `n` roughly equal-sized groups, numbered `1` through `n`, based on the specified order. It's the SQL tool behind the everyday idea of "quartiles," "quintiles," or "deciles."

```sql
SELECT first_name, department, salary,
       NTILE(5) OVER (ORDER BY salary DESC) AS salary_quintile
FROM employees;
```

This splits all employees into 5 groups by salary — the top 20% land in quintile `1`, the next 20% in quintile `2`, and so on. Combine it with `PARTITION BY` to compute quintiles *within* each group separately:

```sql
SELECT first_name, department, salary,
       NTILE(5) OVER (PARTITION BY department ORDER BY salary DESC) AS dept_salary_quintile
FROM employees;
```

**A subtlety worth checking, not assuming:** `NTILE()` divides rows *as evenly as possible*, but if the total row count isn't perfectly divisible by `n`, some buckets get one extra row. Don't assume every group has exactly the same size — verify it:

```sql
SELECT salary_quintile, COUNT(*) 
FROM (SELECT NTILE(5) OVER (ORDER BY salary DESC) AS salary_quintile FROM employees)
GROUP BY salary_quintile;
```

**Why this matters for your target fields:** income/wealth quintiles are a genuinely standard tool in socioeconomic and poverty research — "what share of total income does the bottom quintile hold" is a real, common analysis. `NTILE()` combined with `AVG()` per group (e.g., average salary per quintile) is directly the same pattern you'd use for that kind of analysis later in the course.

---

## 12. Aggregate Functions as Window Functions — and a WHERE Gotcha

Every aggregate function you already know (`SUM`, `COUNT`, `AVG`, `MIN`, `MAX`) can also be used as a *window* function, simply by adding `OVER(...)`. The difference from Section 6 is crucial: a plain aggregate with `GROUP BY` collapses rows down to one per group, while the same aggregate used as a window function keeps every row visible.

```sql
-- Collapses to one row per department
SELECT department, COUNT(*) AS emp_count
FROM employees
GROUP BY department;

-- Keeps every employee row, but adds the department count alongside each one
SELECT first_name, department,
       COUNT(*) OVER (PARTITION BY department) AS dept_count
FROM employees;
```

**Running totals** are a natural extension of this — an aggregate window function with an `ORDER BY` but no `PARTITION BY` (or combined with one) accumulates as it goes, thanks to the default frame behavior from Section 9:

```sql
SELECT first_name, department, hire_date, salary,
       SUM(salary) OVER (PARTITION BY department ORDER BY hire_date) AS running_total
FROM employees;
```

**The gotcha worth internalizing: `WHERE` runs *before* window functions, so a partition only ever sees post-filter rows.**

```sql
SELECT first_name, department,
       COUNT(*) OVER (PARTITION BY department) AS dept_count
FROM employees
WHERE region_id = 2;
```

It's tempting to assume `dept_count` reflects the *entire* department, company-wide. It doesn't — `WHERE region_id = 2` has already thrown away every other region's rows before the window function ever runs, so `dept_count` only reflects how many employees are in that department **within region 2**, not the department as a whole. This is the exact same "what stage does this run at" logic from the `WHERE` vs `HAVING` discussion in Section 7, just applied to window functions instead of `GROUP BY`.

---

## 13. Window Frame Modes: ROWS, RANGE, and GROUPS

Section 9 introduced the idea of a window *frame* through the `NTH_VALUE()` gotcha. There's a further layer worth knowing: the keyword that defines *how the frame counts its boundaries* — called the **frame mode**. There are three:

- **`ROWS`** — counts by physical row position. "2 rows before this one" means exactly 2 rows, full stop, regardless of what values are in them.
- **`RANGE`** — counts by the *value* in the `ORDER BY` column, not row position. Rows that are tied on that value are treated as being at the same logical position — meaning a `RANGE`-based frame can include a *different number* of physical rows depending on how many ties exist. This is the **default** mode whenever `ORDER BY` is used without an explicit frame.
- **`GROUPS`** — counts by groups of tied rows (peer groups) as a single unit, rather than individual rows or raw values. Less commonly used, but exists for cases where ties should move together as one block.

**Why the distinction bites people:** with two tied rows on `hire_date`, `ROWS BETWEEN 1 PRECEDING AND CURRENT ROW` always returns exactly 2 physical rows. `RANGE BETWEEN 1 PRECEDING AND CURRENT ROW` could include *more* than 2, since ties count as occupying the "same" position. Concretely: a running total built with `SUM(salary) OVER (ORDER BY hire_date)` (default `RANGE` mode) will show the **same** cumulative total for two employees hired on the identical date — they're treated as one tied peer group — whereas the same query with explicit `ROWS` would give each of them a distinct, separately-incrementing total.

**The boundary keywords, precisely:**
- `UNBOUNDED PRECEDING` — the *first* row of the partition (go backward as far as possible). Used as the **lower** bound.
- `UNBOUNDED FOLLOWING` — the *last* row of the partition (go forward as far as possible). Used as the **upper** bound.
- `CURRENT ROW` — exactly where you are right now.

Putting it together, `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` reads as: "start from the very first row of the partition, extend all the way to the very last row" — i.e., make the frame equal to the entire partition. That's the fix from Section 9 for `NTH_VALUE()`, and it's also exactly why `LAST_VALUE()` needs the same explicit widening:

```sql
SELECT department,
       FIRST_VALUE(department) OVER (ORDER BY department ASC) AS first_department,
       LAST_VALUE(department) OVER (
           ORDER BY department
           RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS last_department
FROM departments;
```

`FIRST_VALUE()` never needs the frame widened, because under the *default* frame ("start of partition to current row"), the first row is always already included — no matter which row you're currently on. `LAST_VALUE()` has the opposite problem: under the default frame, "the last value visible so far" is just the *current row itself* (since the frame stops there), so without widening, `LAST_VALUE()` would just return each row's own value — never the true last row of the whole partition.

**Frames aren't only backward-looking, either.** A forward-looking frame is just as valid:

```sql
SELECT customer_id,
       MAX(sales) OVER (ORDER BY customer_id ASC ROWS BETWEEN CURRENT ROW AND 1 FOLLOWING) AS next_max_sales
FROM sales;
```

This looks at the current row plus the *next* one, rather than the current row plus prior ones — useful for "what's coming up" comparisons, not just "what's happened so far" ones like moving averages.

**Moving averages** are a direct, practical application of a backward-looking `ROWS` frame — very relevant to smoothing out noisy time-series data (something that will come back directly in the causal inference and epidemiology weeks):

```sql
SELECT first_name, hire_date, salary,
       ROUND(AVG(salary) OVER (ORDER BY hire_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3
FROM employees;
```

This computes a 3-row moving average (the current row plus the 2 preceding it) — the same underlying mechanic used for smoothing stock prices, disease case counts, or any noisy metric tracked over time.

---

## 14. GROUPING SETS, ROLLUP, and CUBE — and Why SQLite Doesn't Have Them

These three keywords extend `GROUP BY` to compute *multiple levels of aggregation in a single query* — instead of running several separate `GROUP BY` queries and combining the results yourself. **None of the three are supported in SQLite** (they exist in PostgreSQL, SQL Server, Oracle, and MySQL 8+), so on SQLite the only option is to manually replicate them with `UNION ALL`.

**`GROUPING SETS`** — produces exactly the specific combinations of columns *you* list, with no implied hierarchy or relationship between them:

```sql
-- What GROUPING SETS(ship_mode, category, sub_category) would do natively elsewhere:
SELECT ship_mode, NULL AS category, NULL AS sub_category, SUM(quantity) AS total_quantity
FROM sales GROUP BY ship_mode
UNION ALL
SELECT NULL, category, NULL, SUM(quantity) FROM sales GROUP BY category
UNION ALL
SELECT NULL, NULL, sub_category, SUM(quantity) FROM sales GROUP BY sub_category;
```

**`ROLLUP`** — produces a specific *hierarchy* of subtotals, always collapsing from the right-hand side inward, assuming a natural nesting order (e.g., category → sub-category → ship mode):

```sql
-- What ROLLUP(category, sub_category, ship_mode) would do natively elsewhere:
SELECT category, sub_category, ship_mode, SUM(quantity) AS total_quantity
FROM sales GROUP BY category, sub_category, ship_mode
UNION ALL
SELECT category, sub_category, NULL, SUM(quantity) FROM sales GROUP BY category, sub_category
UNION ALL
SELECT category, NULL, NULL, SUM(quantity) FROM sales GROUP BY category
UNION ALL
SELECT NULL, NULL, NULL, SUM(quantity) FROM sales;  -- grand total
```

**`CUBE`** — produces *every possible combination* of the given columns (the full power set) — for 3 columns, that's 2³ = 8 groupings, versus `ROLLUP`'s hierarchical n+1 = 4:

```sql
-- CUBE(category, sub_category, ship_mode) needs all 8 combinations, including each
-- column alone, each pair, all three together, and the grand total — see each
-- UNION ALL block covering one distinct combination.
```

**The pattern to remember:**

| Function | Produces | # of groupings for 3 columns |
|---|---|---|
| `GROUPING SETS` | Exactly whatever combinations you list | However many you specify |
| `ROLLUP` | Hierarchical subtotals, right-to-left | n + 1 (here: 4) |
| `CUBE` | Every possible combination | 2ⁿ (here: 8) |

**The deeper lesson:** this is a clean example of why knowing *which* database engine you're actually working with matters. A query that's perfectly idiomatic, standard SQL in Postgres or SQL Server may simply not exist as a keyword in SQLite — meaning the underlying *concept* transfers, but the *syntax* doesn't. When working with a more full-featured engine professionally, reach for the native keyword; on SQLite, the `UNION ALL` replication is the honest workaround.
