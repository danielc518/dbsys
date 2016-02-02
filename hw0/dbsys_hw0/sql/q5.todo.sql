-- Find the customer market segments where the yearly total number of orders declines 
-- in the last 2 years in the dataset. Note the database will have different date 
-- ranges per market segment, for example segment A records between 1990-1995, and 
-- segment B between 1992-1998. That is for segment A, we want the difference between 
-- 1995 and 1994.
-- Output schema: (market segment, last year for segment, difference in # orders)
-- Order by: market segment ASC 

-- Notes
--  1) Use the sqlite function strftime('%Y', <text>) to extract the year from a text field representing a date.
--  2) Use CAST(<text> as INTEGER) to convert text (e.g., a year) into an INTEGER.
--  3) You may use a SQL 'WITH' clause.

-- Student SQL code here:

WITH yearly_orders AS -- table of total number of orders per year grouped by customer market segments
  (SELECT COUNT(o_orderkey) AS total_orders,
          CAST(strftime('%Y', o_orderdate) AS INTEGER) AS o_year,
          c_mktsegment
   FROM orders,
        customer
   WHERE o_custkey = c_custkey
   GROUP BY c_mktsegment,
            o_year)
-- Finds difference between two years by joining 'yearly_orders' with 'yearly_orders' shifted by 1 year
-- e.g. 123|1995|MACHINERY|456|1994|MACHINERY
SELECT t1.c_mktsegment, max_year, (t2.total_orders - t1.total_orders)
FROM (yearly_orders t1
      INNER JOIN yearly_orders t2 ON t1.o_year = t2.o_year + 1
      AND t1.c_mktsegment = t2.c_mktsegment) t3,

  (SELECT MAX(o_year) AS max_year,
                         c_mktsegment
   FROM yearly_orders
   GROUP BY c_mktsegment) t4
WHERE t1.o_year = t4.max_year
  AND t1.c_mktsegment = t4.c_mktsegment
  AND t2.total_orders - t1.total_orders > 0
ORDER BY t1.c_mktsegment ASC;
