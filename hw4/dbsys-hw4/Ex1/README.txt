* The query plans are recored in q1.txt, ..., q22.txt.

Q1.

The filter "l_shipdate <= DATE '1998-09-02'" is pushed down appropriately (occurs in TABLE ACCESS) to reduce the number of records that need aggregation.
However, the reduction is not so significant with the filter since 5789K records are produced which is close to the full number of records (about 6001K).
So the subsequent group by aggregation takes quite a while to process this enormous number of records.

Q3.

All filters have been pushed down to the table access level. This time, unline Q1, the filter for lineitem is quite selective. 
Table access produces 3225K records, which is about half the number of full records (about 6001K).
The plan first performs hash join between customer and orders and then, with this relatively smaller temporary result (compared to lineitem), performs hash join with lineitem.
This last join and the subsequent aggregation incurs the most cost.

Q5.

All filters have been pushed down to the table access level. However, there is no filter for lineitem so all 6001K records are produced by table access on lineitem.
Since the query involves joins between many tables, the plan has many kinds of operations such as buffer sort, merge join cartesian, view creation, and hash joins.
The last two hash joins and the subsequent aggregation incurs the most cost.

Q6.

It is interesting to note that all four filters have been merged into a single filter with 'and' operators and has been pushed down to table access level.
As a result, the table access produces only 155K results, which is just 2.6% of full table. The entire plan just involves an aggregation after such table access.

Q18.

Unfortunately the only filter in this query is in the subquery and this necessiates the view creation evident in the plan.
Since there are no filters except for the subquery, the plan simply involves full table scans and pipelined joins on these massive results. 

Q22.

This query is relatively fast because it only involves small sized tables (compared to lineitem).
For example, orders has 1500K records and customer has 150K records.
Similar to Q6, the numerous filters have been merged into just two filters that occur in relevant table access operations.
Applying these filters on customer, we only get 9K records for one scan and 500 records for another scan.
It is interesting to note that the 'AND NOT EXISTS' is dealt by performing 'HASH JOIN ANTI' operation, which seems to produce the complements of all matches.

