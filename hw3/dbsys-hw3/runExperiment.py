from Database import Database
from Catalog.Schema import DBSchema
from time import time

db = Database(dataDir='./data');

# TPCH Query 6

query1 = db.query().fromTable('lineitem').where( \
            "(L_SHIPDATE >= 19940101) and (L_SHIPDATE < 19950101) and \
            (0.06 - 0.01 <= L_DISCOUNT <= 0.06 + 0.01) and (L_QUANTITY < 24)").groupBy( \
            groupSchema=DBSchema('groupKey', [('ONE', 'int')]), \
            aggSchema=DBSchema('groupBy', [('revenue','float')]), \
            groupExpr=(lambda e: 1), \
            aggExprs=[(0, lambda acc, e: acc + (e.L_EXTENDEDPRICE * e.L_DISCOUNT), lambda x: x)], \
            groupHashFn=(lambda gbVal: hash(gbVal) % 1)).select( \
            {'revenue' : ('revenue', 'float')}).finalize()

# TPCH Query 14

query2 = db.query().fromTable('lineitem').join( \
            db.query().fromTable('part'),
            method = 'hash', \
            lhsHashFn = 'hash(L_PARTKEY) % 5', lhsKeySchema = DBSchema('partkey2',[('L_PARTKEY', 'int')]), \
            rhsHashFn = 'hash(P_PARTKEY) % 5', rhsKeySchema = DBSchema('partkey1',[('P_PARTKEY', 'int')])).where( \
            "L_SHIPDATE >= 19950901 and L_SHIPDATE < 19951001").groupBy( \
            groupSchema=DBSchema('groupKey', [('ONE', 'int')]), \
            aggSchema=DBSchema('groupBy', [('promo_revenue','float')]), \
            groupExpr=(lambda e: 1), \
            aggExprs=[(0, lambda acc, e: acc + (e.L_EXTENDEDPRICE * (1 - e.L_DISCOUNT)), lambda x: x)], \
            groupHashFn=(lambda gbVal: hash(gbVal) % 1)).select( \
            {'promo_revenue' : ('promo_revenue','float')}).finalize()

# TPCH Query 3

query3 = db.query().fromTable('customer').join( \
            db.query().fromTable('orders'),
            method = 'hash', \
            lhsHashFn = 'hash(C_CUSTKEY) % 5', lhsKeySchema = DBSchema('customerKey1', [('C_CUSTKEY', 'int')]), \
            rhsHashFn = 'hash(O_CUSTKEY) % 5', rhsKeySchema = DBSchema('customerKey2', [('O_CUSTKEY', 'int')])).join( \
            db.query().fromTable('lineitem'),
            method = 'hash', \
            lhsHashFn = 'hash(O_ORDERKEY) % 5', lhsKeySchema = DBSchema('orderKey1', [('O_ORDERKEY', 'int')]), \
            rhsHashFn = 'hash(L_ORDERKEY) % 5', rhsKeySchema = DBSchema('orderkey2', [('L_ORDERKEY', 'int')])).where( \
            "C_MKTSEGMENT == 'BUILDING' and O_ORDERDATE < 19950315 and L_SHIPDATE > 19950315").groupBy( \
            groupSchema=DBSchema('groupKey', [('L_ORDERKEY', 'int'), ('O_ORDERDATE', 'int'), ('O_SHIPPRIORITY', 'int')]), \
            aggSchema=DBSchema('groupAgg', [('revenue','float')]), \
            groupExpr=(lambda e: (e.L_ORDERKEY, e.O_ORDERDATE, e.O_SHIPPRIORITY)), \
            aggExprs=[(0, lambda acc, e: acc + (e.L_EXTENDEDPRICE * (1 - e.L_DISCOUNT)), lambda x: x)], \
            groupHashFn=(lambda gbVal: hash(gbVal) % 10)).select( \
            {'l_orderkey' : ('L_ORDERKEY', 'int'), \
             'revenue' : ('revenue', 'float'), \
             'o_orderdate' : ('O_ORDERDATE', 'int'), \
             'o_shippriority' : ('O_SHIPPRIORITY', 'int')}).finalize()
             
# TPCH Query 10

query4 = db.query().fromTable('customer').join( \
            db.query().fromTable('orders'),
            method = 'hash', \
            lhsHashFn = 'hash(C_CUSTKEY) % 5', lhsKeySchema = DBSchema('customerKey1', [('C_CUSTKEY', 'int')]), \
            rhsHashFn = 'hash(O_CUSTKEY) % 5', rhsKeySchema = DBSchema('customerKey2', [('O_CUSTKEY', 'int')])).join( \
            db.query().fromTable('lineitem'),
            method = 'hash', \
            lhsHashFn = 'hash(O_ORDERKEY) % 5', lhsKeySchema = DBSchema('orderKey1', [('O_ORDERKEY', 'int')]), \
            rhsHashFn = 'hash(L_ORDERKEY) % 5', rhsKeySchema = DBSchema('orderkey2', [('L_ORDERKEY', 'int')])).join( \
            db.query().fromTable('nation'),
            method = 'hash', \
            lhsHashFn = 'hash(C_NATIONKEY) % 5', lhsKeySchema = DBSchema('nationKey1', [('C_NATIONKEY', 'int')]), \
            rhsHashFn = 'hash(N_NATIONKEY) % 5', rhsKeySchema = DBSchema('nationKey2', [('N_NATIONKEY', 'int')])).where( \
            "L_RETURNFLAG == 'R' and O_ORDERDATE < 19940101 and O_ORDERDATE >= 19931001").groupBy( \
            groupSchema=DBSchema('groupKey', [('C_CUSTKEY', 'int'), ('C_NAME', 'char(25)'), ('C_ACCTBAL', 'float'), ('C_PHONE', 'char(15)'), ('N_NAME', 'char(25)'), ('C_ADDRESS', 'char(40)'), ('C_COMMENT', 'char(117)')]), \
            aggSchema=DBSchema('groupAgg', [('revenue','float')]), \
            groupExpr=(lambda e: (e.C_CUSTKEY, e.C_NAME, e.C_ACCTBAL, e.C_PHONE, e.N_NAME, e.C_ADDRESS, e.C_COMMENT)), \
            aggExprs=[(0, lambda acc, e: acc + (e.L_EXTENDEDPRICE * (1 - e.L_DISCOUNT)), lambda x: x)], \
            groupHashFn=(lambda gbVal: hash(gbVal) % 10)).select( \
            {'c_custkey' : ('C_CUSTKEY', 'int'), \
             'c_name' : ('C_NAME', 'char(25)'), \
             'revenue' : ('revenue', 'float'), \
             'c_acctbal' : ('C_ACCTBAL', 'float'), \
             'n_name' : ('N_NAME', 'char(25)'), \
             'c_address' : ('C_ADDRESS', 'char(40)'), \
             'c_phone' : ('C_PHONE', 'char(15)'), \
             'c_comment' : ('C_COMMENT', 'char(117)')}).finalize()

# TPCH Query 5

query5 = db.query().fromTable('customer').join( \
            db.query().fromTable('orders'),
            method = 'hash', \
            lhsHashFn = 'hash(C_CUSTKEY) % 5', lhsKeySchema = DBSchema('customerKey1', [('C_CUSTKEY', 'int')]), \
            rhsHashFn = 'hash(O_CUSTKEY) % 5', rhsKeySchema = DBSchema('customerKey2', [('O_CUSTKEY', 'int')])).join( \
            db.query().fromTable('lineitem'),
            method = 'hash', \
            lhsHashFn = 'hash(O_ORDERKEY) % 5', lhsKeySchema = DBSchema('orderKey1', [('O_ORDERKEY', 'int')]), \
            rhsHashFn = 'hash(L_ORDERKEY) % 5', rhsKeySchema = DBSchema('orderkey2', [('L_ORDERKEY', 'int')])).join( \
            db.query().fromTable('supplier'),
            method = 'hash', \
            lhsHashFn = 'hash(L_SUPPKEY) % 5', lhsKeySchema = DBSchema('suppKey1', [('L_SUPPKEY', 'int')]), \
            rhsHashFn = 'hash(S_SUPPKEY) % 5', rhsKeySchema = DBSchema('suppkey2', [('S_SUPPKEY', 'int')])). join( \
            db.query().fromTable('nation'),
            method = 'hash', \
            lhsHashFn = 'hash(S_NATIONKEY) % 5', lhsKeySchema = DBSchema('nationKey1', [('S_NATIONKEY', 'int')]), \
            rhsHashFn = 'hash(N_NATIONKEY) % 5', rhsKeySchema = DBSchema('nationKey2', [('N_NATIONKEY', 'int')])).join( \
            db.query().fromTable('region'),
            method = 'hash', \
            lhsHashFn = 'hash(N_REGIONKEY) % 5', lhsKeySchema = DBSchema('regionKey1', [('N_REGIONKEY', 'int')]), \
            rhsHashFn = 'hash(R_REGIONKEY) % 5', rhsKeySchema = DBSchema('regionKey2', [('R_REGIONKEY', 'int')])).where( \
            "R_NAME == 'ASIA' and O_ORDERDATE >= 19940101 and O_ORDERDATE < 19950101").groupBy( \
            groupSchema=DBSchema('groupKey', [('N_NAME', 'char(25)')]), \
            aggSchema=DBSchema('groupAgg', [('revenue','float')]), \
            groupExpr=(lambda e: e.N_NAME), \
            aggExprs=[(0, lambda acc, e: acc + (e.L_EXTENDEDPRICE * (1 - e.L_DISCOUNT)), lambda x: x)], \
            groupHashFn=(lambda gbVal: hash(gbVal) % 10)).select( \
            {'n_name' : ('N_NAME', 'char(25)'), \
             'revenue' : ('revenue', 'float')}).finalize()

# Run experiments

def getResults(query, db):
  return [query.schema().unpack(tup) for page in db.processQuery(query) for tup in page[1] ]
             
print("Query 1")
start = time()
results = getResults(query1, db)
end = time()
print("Not Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")
query1 = db.optimizer.optimizeQuery(query1)
start = time()
results = getResults(query1, db)
end = time()
print("Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")

print("\nQuery 2")
start = time()
results = getResults(query2, db)
end = time()
print("Not Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")
query2 = db.optimizer.optimizeQuery(query2)
start = time()
results = getResults(query2, db)
end = time()
print("Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")

print("\nQuery 3")
start = time()
results = getResults(query3, db)
end = time()
print("Not Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")
query3 = db.optimizer.optimizeQuery(query3)
start = time()
results = getResults(query3, db)
end = time()
print("Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")

print("\nQuery 4")
start = time()
results = getResults(query4, db)
end = time()
print("Not Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")
query4 = db.optimizer.optimizeQuery(query4)
start = time()
results = getResults(query4, db)
end = time()
print("Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")

print("\nQuery 5")
start = time()
results = getResults(query5, db)
end = time()
print("Not Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")
query5 = db.optimizer.optimizeQuery(query5)
start = time()
results = getResults(query5, db)
end = time()
print("Optimized: " + str(end - start) + " (Results: " + str(len(results)) + ")")
            
db.close();