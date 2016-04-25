-- Find the top 10 parts that with the highest quantity in returned orders. 
-- An order is returned if the returnflag field on any lineitem part is the character R.
-- Output schema: (part key, part name, quantity returned)
-- Order by: by quantity returned, descending.

-- Student SQL code here:
SELECT
  l_partkey, p_name, SUM(l_quantity) as quantity
FROM
  lineitem,
  part
WHERE
  l_returnflag = 'R'
  and l_partkey = p_partkey
GROUP BY
  l_partkey
ORDER BY
  quantity desc
LIMIT 10;
