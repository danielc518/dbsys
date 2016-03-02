-- Usage: sqlite3 [path-to-database] < [path-to-script]

-- Output to a text file (to only see time results)
.output sqlite_results.txt

.timer on

-- Query 1

select p.p_name, s.s_name
from part p, supplier s, partsupp ps
where p.p_partkey = ps.ps_partkey
  and ps.ps_suppkey = s.s_suppkey
  and ps.ps_availqty = 1
union all
select p.p_name, s.s_name
from part p, supplier s, partsupp ps
where p.p_partkey = ps.ps_partkey
      and ps.ps_suppkey = s.s_suppkey
      and ps.ps_supplycost < 5;

-- Query 2

select part.p_name, count(*) as count
from part, lineitem
where part.p_partkey = lineitem.l_partkey and lineitem.l_returnflag = 'R'
group by part.p_name;

-- Query 3

with temp as (
   select n.n_name as nation, p.p_name as part, sum(l.l_quantity) as num
   from customer c, nation n, orders o, lineitem l, part p
   where c.c_nationkey = n.n_nationkey
     and c.c_custkey = o.o_custkey
     and o.o_orderkey = l.l_orderkey
     and l.l_partkey = p.p_partkey
   group by n.n_name, p.p_name
)
select nation, max(num)
from temp
group by nation; 