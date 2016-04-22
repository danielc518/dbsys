List of performance optimizations:

* Create materialized views as in exercise 2 (see dbsys-hw4/Ex2/views.txt)

-- Materialized Views --

* alter table lineitem_shipdate parallel 4;
* alter table lineitem_cust_order parallel 4;
* alter table full_join parallel 4;
* alter table lineitem_ship_disc_quant parallel 4;
* alter table lineitem_orderkey parallel 4;
* alter table customer_order parallel 4;
* alter table subquery parallel 4;

* alter table lineitem_shipdate inmemory; 
* alter table lineitem_cust_order inmemory;
* alter table full_join inmemory;
* alter table lineitem_ship_disc_quant inmemory;
* alter table lineitem_orderkey inmemory;
* alter table customer_order inmemory;
* alter table subquery inmemory;

* analyze table lineitem_shipdate compute statistics;
* analyze table lineitem_cust_order compute statistics;
* analyze table full_join compute statistics;
* analyze table lineitem_ship_disc_quant compute statistics;
* analyze table lineitem_orderkey compute statistics;
* analyze table customer_order compute statistics;
* analyze table subquery compute statistics;

-- Original Tables --

* alter table lineitem parallel 4;
* alter table orders parallel 4;
* alter table customer parallel 4;
* alter table supplier parallel 4;
* alter table nation parallel 4;
* alter table region parallel 4;

* alter table lineitem inmemory; 
* alter table orders inmemory;
* alter table customer inmemory;
* alter table supplier inmemory;
* alter table nation inmemory;
* alter table region inmemory;

* analyze table lineitem compute statistics;
* analyze table orders compute statistics;
* analyze table customer compute statistics;
* analyze table supplier compute statistics;
* analyze table nation compute statistics;
* analyze table region compute statistics;

--------------------------------------------------------------------------------------------------------------------

We left out indexes since exercise 2 showed that these were not helpful for our particular queries.
Otherwise, we kept everything we did in exercise 2 and, in addition, computed statistics for the views
and turned the views into in-memory access.

In exercise 2, we saw that every query benefited from at least one tuning option. Hence, by combining
all these tuning options, we were able to drop the running time significantly.

Main beneficial factors for each query:
Query 1: Parallel access of lineitem.
Query 3: Pre-joined view involving lineitem, orders, and customer.
Query 5: Pre-joined view involving customer, orders, lineitem, supplier, nation, region.
Query 6: Pre-filtered view of lineitem.
Query 18: Subquery view involving orders and lineitem.
Query 22: Subquery view involving orders and customer.

Apart from these factors, the in-memory + parallel access to these pre-computed views were greatly helpful as well.

