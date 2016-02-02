-- For each of the top 5 nations with the greatest value (i.e., sum of l_extendedprice) of orders placed
-- find ALL the nations that supply these orders.
-- Output schema: (name of nation acting as customer, name of nation acting as supplier, value of orders between supplier and customer)
-- Order by: (name of nation acting as customer, name of nation acting as supplier).

-- Student SQL code here:

SELECT placer_name,
       n_name AS supplier_name,
       SUM(l_extendedprice) AS val_orders
FROM lineitem, orders, customer, supplier, nation,
  (SELECT c_nationkey AS placer_key,
          n_name AS placer_name,
          SUM(l_extendedprice) AS totalprice
   FROM lineitem,
        orders,
        customer,
        nation
   WHERE l_orderkey = o_orderkey
     AND o_custkey = c_custkey
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
         supplier_name
ORDER BY placer_name,
         supplier_name;
