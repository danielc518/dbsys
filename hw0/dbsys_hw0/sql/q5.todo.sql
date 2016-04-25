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
WITH quantity_per_segment_year AS (
  SELECT
    c_mktsegment, CAST(strftime('%Y', o_orderdate) as INTEGER) as year, COUNT(o_orderkey) as num_orders
  FROM
    orders,
    customer
  WHERE
    o_custkey = c_custkey
  GROUP BY
    c_mktsegment, year
)
SELECT
  T1.c_mktsegment, T1.last_year, T2.num_orders - T3.num_orders as difference
FROM
  (SELECT
    c_mktsegment, MAX(CAST(strftime('%Y', o_orderdate) as INTEGER)) as last_year
  FROM
    orders,
    customer
  WHERE
    o_custkey = c_custkey
  GROUP BY
    c_mktsegment
  ) as T1,
  quantity_per_segment_year as T2,
  quantity_per_segment_year as T3
WHERE
  T1.c_mktsegment = T2.c_mktsegment
  and T1.last_year = T2.year
  and T2.c_mktsegment = T3.c_mktsegment
  and T2.year = T3.year + 1
  and difference < 0
ORDER BY
  T1.c_mktsegment asc;
