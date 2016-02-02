-- For each of the top 5 nations with the greatest value (i.e., total price) of orders placed,
-- find the top 5 nations which supply these orders.
-- Output schema: (Order placer name, Order supplier name, value of orders placed)
-- Order by: (Order placer, Order supplier)

-- Notes
--  1) We are expecting exactly 25 results 

-- Student SQL code here:

WITH top_supplier AS
-- table of suppliers for each (top 5) order placer
  (SELECT placer_name,
          n_name AS supplier_name,
          SUM(o_totalprice) AS val_orders
   FROM lineitem, orders, customer, supplier, nation,
     (SELECT c_nationkey AS placer_key,
             n_name AS placer_name,
             SUM(o_totalprice) AS totalprice
      FROM orders,
           customer,
           nation
      WHERE o_custkey = c_custkey
        AND c_nationkey = n_nationkey
      GROUP BY c_nationkey,
               placer_name
      ORDER BY totalprice DESC LIMIT 5)
   WHERE l_suppkey = s_suppkey
     AND l_orderkey = o_orderkey
     AND o_custkey = c_custkey
     AND placer_key = c_nationkey
     AND s_nationkey = n_nationkey
   GROUP BY placer_name,
            supplier_name)
-- choose top 5 suppliers for each order placer
SELECT placer_name,
       supplier_name,
       val_orders
FROM top_supplier t1
WHERE
    (SELECT COUNT(*)
     FROM top_supplier t2
     WHERE t2.placer_name = t1.placer_name
       AND t2.val_orders <= t1.val_orders) <= 5
ORDER BY placer_name,
         supplier_name;
