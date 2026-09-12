# Week 1 Teaching Component
## SQL Window Functions, Joins, CTEs, and Subqueries — Explained for a Beginner

*Written as if explaining to a colleague who has never touched window functions before.*

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
