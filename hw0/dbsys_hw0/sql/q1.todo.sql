-- Find the top 10 parts that with the highest quantity in returned orders. 
-- An order is returned if the returnflag field on any lineitem part is the character R.
-- Output schema: (part key, part name, quantity returned)
-- Order by: by quantity returned, descending.

-- Student SQL code here:

SELECT l_partkey,
       p_name,
       SUM(l_quantity)
FROM lineitem,
     part
WHERE l_partkey = p_partkey
  AND l_returnflag = 'R'
GROUP BY p_partkey
ORDER BY SUM(l_quantity) DESC LIMIT 10;
