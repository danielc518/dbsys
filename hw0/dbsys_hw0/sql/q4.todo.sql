-- For each of the top 5 nations with the greatest value (i.e., sum of l_extendedprice) of orders placed, find ALL the nations that supply these orders.
-- Output schema: (name of nation acting as customer, name of nation acting as supplier, value of orders between supplier and customer)
-- Order by: (name of nation acting as customer, name of nation acting as supplier).
 
-- There are 2 changes to note:
-- 1) We ask you to sum over the l_extendedprice in lineitem, instead of using o_totalprice from orders.
-- 2) We ask for ALL nations in the second part of the description.
  
-- Because there are 25 nations in the database, the final result will now have 125 (5 x 25) rows, instead of 25 (5 x 5).

-- Student SQL code here:
WITH T AS (
  SELECT
    n_nationkey as placer_nationkey, 
    n_name as placer_nationname,
    s_suppkey as suppkey,
    s_nationkey as supp_nation,
    o_orderkey as orderkey,
    l_extendedprice as value
  FROM 
    nation,
    customer,
    orders,
    lineitem,
    supplier
  WHERE
    c_nationkey = n_nationkey
    AND o_custkey = c_custkey
    AND l_orderkey = o_orderkey
    AND s_suppkey = l_suppkey 
)
SELECT 
  placer_nationname, nation.n_name as supplier_nationname, sum(T1.value) as value
FROM 
  T as T1,
  (SELECT placer_nationkey, sum(value) as value 
   FROM T 
   GROUP BY placer_nationkey 
   ORDER BY value desc 
   LIMIT 5
  ) as T2,
  nation
WHERE
  n_nationkey = T1.supp_nation
  AND T1.placer_nationkey = T2.placer_nationkey
GROUP BY placer_nationname, supplier_nationname
ORDER BY placer_nationname, supplier_nationname;
