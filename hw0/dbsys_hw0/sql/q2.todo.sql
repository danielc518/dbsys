--  Find the 10 customers who spent the highest average number of days waiting for shipments.
-- A customer is waiting between a shipment's ship date and receipt date
-- Output schema: (customer key, customer name, average wait)
-- Order by: average wait DESC

-- Notes
--  1) Use the sqlite DATE(<text>) function to interpret a text field as a date.
--  2) Use subtraction to compute the duration between two dates (e.g., DATE(column1) - DATE(column2)).
--  3) Assume that a package cannot be received before it is shipped.

-- Student SQL code here:

SELECT c.c_custkey,
       c.c_name,
       AVG(DATE(l.l_receiptdate) - DATE(l.l_shipdate)) AS avwait
FROM customer c,
     orders o,
     lineitem l
WHERE c.c_custkey = o.o_custkey
  AND o.o_orderkey = l.l_orderkey
GROUP BY c.c_custkey
ORDER BY avwait DESC LIMIT 10;




