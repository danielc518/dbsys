List of performance optimizations:

* Create materialized views as in exercise 2 (see dbsys-hw4/views.txt)

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

