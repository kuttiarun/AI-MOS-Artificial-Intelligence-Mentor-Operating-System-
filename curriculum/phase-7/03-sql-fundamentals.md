# SQL Fundamentals — DDL, DML, Joins & Indexes

## What You'll Master
- Core SQL categories: DDL, DML, DCL
- Joins — INNER, LEFT, RIGHT, FULL — with visual examples
- Indexes — what they are, when they help, when they hurt
- Aggregation, GROUP BY, HAVING, subqueries

---

## SQL Categories

| Category | Commands | Purpose |
|---|---|---|
| DDL | CREATE, ALTER, DROP, TRUNCATE | Define/modify schema |
| DML | SELECT, INSERT, UPDATE, DELETE | Manipulate data |
| DCL | GRANT, REVOKE | Permissions |
| TCL | COMMIT, ROLLBACK, SAVEPOINT | Transactions |

---

## Essential DDL

```sql
CREATE TABLE employees (
    id          SERIAL PRIMARY KEY,           -- auto-increment
    name        VARCHAR(100) NOT NULL,
    department  VARCHAR(50)  NOT NULL DEFAULT 'General',
    salary      DECIMAL(10,2) CHECK (salary > 0),
    manager_id  INTEGER REFERENCES employees(id), -- self-join FK
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add column
ALTER TABLE employees ADD COLUMN email VARCHAR(200) UNIQUE;

-- Rename column
ALTER TABLE employees RENAME COLUMN department TO dept;

-- DROP (irreversible!)
DROP TABLE employees;

-- TRUNCATE (keeps structure, deletes all rows, faster than DELETE)
TRUNCATE TABLE employees RESTART IDENTITY;
```

---

## Joins — The Interview Core

```
employees:              departments:
id | name  | dept_id    id | name
1  | Arun  | 10         10 | Engineering
2  | Priya | 20         20 | Marketing
3  | Ram   | NULL       30 | HR (no employees)
```

```sql
-- INNER JOIN: only matching rows (both sides must match)
SELECT e.name, d.name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.id;
-- Result: Arun/Engineering, Priya/Marketing

-- LEFT JOIN: all employees, NULL if no dept
SELECT e.name, d.name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.id;
-- Result: Arun/Engineering, Priya/Marketing, Ram/NULL

-- RIGHT JOIN: all departments, NULL if no employee
SELECT e.name, d.name
FROM employees e
RIGHT JOIN departments d ON e.dept_id = d.id;
-- Result: Arun/Engineering, Priya/Marketing, NULL/HR

-- FULL OUTER JOIN: all rows from both sides
SELECT e.name, d.name
FROM employees e
FULL OUTER JOIN departments d ON e.dept_id = d.id;
-- All combinations, NULLs where no match

-- SELF JOIN: employee + their manager
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

---

## Aggregation & GROUP BY

```sql
-- Find average salary per department (only depts with > 2 employees)
SELECT dept_id, AVG(salary) AS avg_salary, COUNT(*) AS headcount
FROM employees
WHERE salary > 30000          -- filters ROWS (before grouping)
GROUP BY dept_id
HAVING COUNT(*) > 2           -- filters GROUPS (after grouping)
ORDER BY avg_salary DESC
LIMIT 5;

-- Window functions (no grouping collapse)
SELECT name, salary,
    RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rank_in_dept,
    AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg
FROM employees;
```

---

## Indexes — Speed vs Storage Trade-off

```sql
-- B-Tree index (default) — good for =, <, >, BETWEEN, LIKE 'prefix%'
CREATE INDEX idx_employees_dept ON employees(dept_id);

-- Composite index — column order matters!
CREATE INDEX idx_emp_dept_salary ON employees(dept_id, salary);
-- Good for: WHERE dept_id = 10 AND salary > 50000
-- Good for: WHERE dept_id = 10
-- Bad for:  WHERE salary > 50000 (dept_id must come first)

-- Unique index
CREATE UNIQUE INDEX idx_emp_email ON employees(email);

-- Partial index — only index rows matching condition
CREATE INDEX idx_active_emp ON employees(name) WHERE status = 'ACTIVE';

-- Check query plan
EXPLAIN ANALYZE SELECT * FROM employees WHERE dept_id = 10;
-- Look for "Index Scan" (good) vs "Seq Scan" (table scan — slow on large tables)
```

**When indexes hurt:**
- Heavy `INSERT`/`UPDATE`/`DELETE` workloads (index must be updated too)
- Small tables (full scan can be faster than index lookup + fetch)
- Low-cardinality columns (boolean, status with 2-3 values)

---

## Subqueries & CTEs

```sql
-- Correlated subquery — employees earning above their dept avg
SELECT name, salary
FROM employees e
WHERE salary > (
    SELECT AVG(salary) FROM employees WHERE dept_id = e.dept_id
);

-- CTE (Common Table Expression) — readable, reusable
WITH dept_averages AS (
    SELECT dept_id, AVG(salary) AS avg_sal
    FROM employees GROUP BY dept_id
)
SELECT e.name, e.salary, da.avg_sal
FROM employees e
JOIN dept_averages da ON e.dept_id = da.dept_id
WHERE e.salary > da.avg_sal;
```

---

## Revision Checkpoint

> Write a query to find the second highest salary in the `employees` table without using `LIMIT`/`TOP`. Then explain when you'd use a CTE vs a subquery.
