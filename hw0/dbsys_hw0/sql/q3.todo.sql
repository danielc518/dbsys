-- Find the name of the most heavily ordered (i.e., highest quantity) part per nation.
-- Output schema: (nation key, nation name, part key, part name, quantity ordered)
-- Order by: (nation key, part key) SC

-- Notes
--   1) You may use a SQL 'WITH' clause for common table expressions.
--   2) A single nation may have more than 1 most-heavily-ordered-part.

-- Student SQL code here:
WITH quantity_per_np AS (
  SELECT
    c_nationkey, l_partkey, SUM(l_quantity) as quantity
  FROM
    lineitem,
    orders,
    customer
  WHERE
    l_orderkey = o_orderkey
    and o_custkey = c_custkey
  GROUP BY
    c_nationkey, l_partkey
)
SELECT
  n_nationkey, n_name, p_partkey, p_name, T1.max as quantity
FROM
  (SELECT
    c_nationkey, MAX(quantity) as max
  FROM
    quantity_per_np
  GROUP BY
    c_nationkey
  ) as T1,
  quantity_per_np as T2,
  nation,
  part
WHERE
  T1.c_nationkey = T2.c_nationkey
  and T1.max = T2.quantity
  and T1.c_nationkey = n_nationkey
  and T2.l_partkey = p_partkey
ORDER BY
  n_nationkey, p_partkey asc;
