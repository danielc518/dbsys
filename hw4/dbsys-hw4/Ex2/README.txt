1. Statistics

The use of statistics did not help the performance of any query.
This is evident from the fact that none of the plans have changed compared to the benchmark.
It may just be the case that knowing about the distribution of each table was not a big decisive factor with these particular queries.

2. In-Memory Tables

Using in-memory tables switched the normal 'TABLE ACCESS FULL' operators into 'TABLE ACCESS INMEMORY FULL' operators.
This switch did not help query 1 or query 3 but the rest of the queries benefited from this replacement.
For query 1, it may be the case that the cost of aggregation simply overwhelms the benefit of faster table access.
For query 3, it seems that the joins are the source of major cost rather than table access.

3. Parallelism

The plans now involved complex 'PX' operators that seemed to send data back and forth via a coordinator.
Using parallelism was one of the best tuning option since it helped all of the queries run faster. 
This is indeed expected since sequential access of table records is definitely slower than parallel access of records.

4. Indexes

The indexes we created are summarized in 'indexes.txt'.
Although we expected that indexes would help queries run faster, none of the queries benefited from using indexes.
Almost all of the queries now involved 'INDEX RANGE SCAN' operators and it seemed to be the case that using these
operators turned the execution plan into a suboptimal one. For example, query 5 now introduced 'NESTED LOOPS' which is generally slow.

5. Materialized Views

The views we created are summarized in 'views.txt'.
The plans now involved 'MAT_VIEW REWRITE ACCESS FULL' operators instead of the usual table access operators.
Along with parallelism, this was one of the best tuning option since it helped most of the quries run faster.
Query 1 did not benefit from the view that had pre-filtered on 'l_shipdate' and so this is one more evidence that
aggregation is the most cost incurring operator in this particular query.
Apart from query 1, other queries enjoyed the pre-joined views and subquery views which reduced the running time significantly.
