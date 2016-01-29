-- Find the name of the most heavily ordered (i.e., highest quantity) part per nation.
-- Output schema: (nation key, nation name, part key, part name, quantity ordered)
-- Order by: (nation key, part key) SC

-- Notes
--   1) You may use a SQL 'WITH' clause for common table expressions.
--   2) A single nation may have more than 1 most-heavily-ordered-part.

-- Student SQL code here:

WITH total_quantity AS
  (SELECT SUM(l_quantity) AS t_quantity,
          n_nationkey,
          n_name,
          p_partkey,
          p_name
   FROM lineitem,
        orders,
        customer,
        nation,
        part
   WHERE l_orderkey = o_orderkey
     AND o_custkey = c_custkey
     AND c_nationkey = n_nationkey
     AND l_partkey = p_partkey
   GROUP BY n_nationkey,
            l_partkey
   ORDER BY SUM(l_quantity))
SELECT n_nationkey,
       n_name,
       p_partkey,
       p_name,
       t_quantity
FROM total_quantity,
  (SELECT MAX(t_quantity) AS max_quantity,
          n_nationkey AS t_nationkey
   FROM total_quantity
   GROUP BY n_nationkey)
WHERE t_quantity = max_quantity
  AND n_nationkey = t_nationkey
ORDER BY n_nationkey,
         p_partkey ASC;
		 