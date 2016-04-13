EXPERIMENT RESULTS

Exercise #4:

As evident from the results below, greedy optimization yields much better performance than bushy optimization.

RESULTS WITH NO SAMPLING (sampling consumed too much time): 

***** Bushy Optimizer *****

Number of plans considered: 4
Time to join 2 plans: 0.0042095184326171875

Number of plans considered: 16
Time to join 4 plans: 0.017929553985595703

Number of plans considered: 28
Time to join 6 plans: 0.03610968589782715

Number of plans considered: 138
Time to join 8 plans: 0.2331066131591797

Number of plans considered: 154
Time to join 10 plans: 0.37946152687072754

Number of plans considered: 1006
Time to join 12 plans: 3.1011226177215576

***** Greedy Optimizer *****

Number of plans considered: 2
Time to join 2 plans: 0.0021636486053466797

Number of plans considered: 12
Time to join 4 plans: 0.01446223258972168

Number of plans considered: 30
Time to join 6 plans: 0.0416865348815918

Number of plans considered: 56
Time to join 8 plans: 0.08860135078430176

Number of plans considered: 90
Time to join 10 plans: 0.18964147567749023

Number of plans considered: 132
Time to join 12 plans: 0.2771165370941162


RESULTS WITH SAMPLING (only limited set of results due to long running time):

***** Bushy Optimizer *****

Number of plans considered: 4
Time to join 2 plans: 0.7834987640380859

Number of plans considered: 16
Time to join 4 plans: 58.114935636520386

Number of plans considered: 28
Time to join 6 plans: 72.34911513328552

***** Greedy Optimizer *****

Number of plans considered: 2
Time to join 2 plans: 0.47540950775146484

Number of plans considered: 12
Time to join 4 plans: 8.497896432876587


Exercise #5:

Except for TPC-H Query 3, the optimizer helped reduce the running time of each query.
For query 3, it may be the case that turning off the sampling feature (since it took too much time) affected the join order in a bad way.
However, it is quite impressive that the running time of query 5 is almost reduced by half.
