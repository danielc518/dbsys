List of performance optimizations:

* Kepts the views created from exercise 2 (see dbsys-hw4/views.txt)

* alter table lineitem parallel 4;

* alter table lineitem_shipdate parallel 4;
* alter table lineitem_cust_order parallel 4;
* alter table l_c_o_s_n_r parallel 4;
* alter table lineitem_ship_disc_quant parallel 4;
* alter table lineitem_orderkey parallel 4;
* alter table customer_order parallel 4;
* alter table subquery parallel 4;

* alter table lineitem inmemory; 
* alter table orders inmemory;
* alter table customer inmemory;
* alter table supplier inmemory;
* alter table nation inmemory;
* alter table region inmemory;

* alter table lineitem_shipdate inmemory; 
* alter table lineitem_cust_order inmemory;
* alter table l_c_o_s_n_r inmemory;
* alter table lineitem_ship_disc_quant inmemory;
* alter table lineitem_orderkey inmemory;
* alter table customer_order inmemory;
* alter table subquery inmemory;

* analyze table lineitem compute statistics;
* analyze table orders compute statistics;
* analyze table customer compute statistics;
* analyze table supplier compute statistics;
* analyze table nation compute statistics;
* analyze table region compute statistics;

* analyze table lineitem_shipdate compute statistics;
* analyze table lineitem_cust_order compute statistics;
* analyze table l_c_o_s_n_r compute statistics;
* analyze table lineitem_ship_disc_quant compute statistics;
* analyze table lineitem_orderkey compute statistics;
* analyze table customer_order compute statistics;
* analyze table subquery compute statistics;