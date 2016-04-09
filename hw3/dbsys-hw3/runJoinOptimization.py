import Database
import numpy as np
import sys

from Query.Optimizer import Optimizer
from Query.BushyOptimizer import BushyOptimizer
from Query.GreedyOptimizer import GreedyOptimizer
from Catalog.Schema import DBSchema
from time import time

def cleanup(db):
  if db.hasRelation('A'):
    db.removeRelation('A')
  if db.hasRelation('B'):
    db.removeRelation('B')
  if db.hasRelation('C'):
    db.removeRelation('C')
  if db.hasRelation('D'):
    db.removeRelation('D')
  if db.hasRelation('E'):
    db.removeRelation('E')
  if db.hasRelation('F'):
    db.removeRelation('F')
  if db.hasRelation('G'):
    db.removeRelation('G')
  if db.hasRelation('H'):
    db.removeRelation('H')
  if db.hasRelation('I'):
    db.removeRelation('I')
  if db.hasRelation('J'):
    db.removeRelation('J')
  if db.hasRelation('K'):
    db.removeRelation('K')
  if db.hasRelation('L'):
    db.removeRelation('L')

# Create synthetic database schema, consisting of relations with triples of integers

db = Database.Database()

cleanup(db)

db.createRelation('A', [('a_a', 'int'), ('a_b', 'int'), ('a_c', 'int')])
db.createRelation('B', [('b_a', 'int'), ('b_b', 'int'), ('b_c', 'int')])
db.createRelation('C', [('c_a', 'int'), ('c_b', 'int'), ('c_c', 'int')])
db.createRelation('D', [('d_a', 'int'), ('d_b', 'int'), ('d_c', 'int')])
db.createRelation('E', [('e_a', 'int'), ('e_b', 'int'), ('e_c', 'int')])
db.createRelation('F', [('f_a', 'int'), ('f_b', 'int'), ('f_c', 'int')])
db.createRelation('G', [('g_a', 'int'), ('g_b', 'int'), ('g_c', 'int')])
db.createRelation('H', [('h_a', 'int'), ('h_b', 'int'), ('h_c', 'int')])
db.createRelation('I', [('i_a', 'int'), ('i_b', 'int'), ('i_c', 'int')])
db.createRelation('J', [('j_a', 'int'), ('j_b', 'int'), ('j_c', 'int')])
db.createRelation('K', [('k_a', 'int'), ('k_b', 'int'), ('k_c', 'int')])
db.createRelation('L', [('l_a', 'int'), ('l_b', 'int'), ('l_c', 'int')])

aSchema = db.relationSchema('A')
bSchema = db.relationSchema('B')
cSchema = db.relationSchema('C')
dSchema = db.relationSchema('D')
eSchema = db.relationSchema('E')
fSchema = db.relationSchema('F')
gSchema = db.relationSchema('G')
hSchema = db.relationSchema('H')
iSchema = db.relationSchema('I')
jSchema = db.relationSchema('J')
kSchema = db.relationSchema('K')
lSchema = db.relationSchema('L')

# Insert synthetic tuples for each relation

for tuple in [aSchema.pack(aSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('A', tuple)
for tuple in [bSchema.pack(bSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('B', tuple)
for tuple in [cSchema.pack(cSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('C', tuple)
for tuple in [dSchema.pack(dSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('D', tuple)
for tuple in [eSchema.pack(eSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('E', tuple)
for tuple in [fSchema.pack(fSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('F', tuple)
for tuple in [gSchema.pack(gSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('G', tuple)
for tuple in [hSchema.pack(hSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('H', tuple)
for tuple in [iSchema.pack(iSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('I', tuple)
for tuple in [jSchema.pack(jSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('J', tuple)
for tuple in [kSchema.pack(kSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('K', tuple)
for tuple in [lSchema.pack(lSchema.instantiate(np.random.randint(100), np.random.randint(100), np.random.randint(100))) for i in range(100)]:
  db.insertTuple('L', tuple)

# Create queries involving different size of joins (2, 4, 6, 8, 10, 12)

query2 = db.query().fromTable('A').join( \
           db.query().fromTable('B'), \
           method='block-nested-loops', expr='a_a == b_a').finalize()

query4 = db.query().fromTable('A').join( \
           db.query().fromTable('B'), \
           method='block-nested-loops', expr='a_a == b_a').join( \
           db.query().fromTable('C'), \
           method='block-nested-loops', expr='a_a == c_a').join( \
           db.query().fromTable('D'), \
           method='block-nested-loops', expr='a_a == d_a').finalize()

query6 = db.query().fromTable('A').join( \
           db.query().fromTable('B'), \
           method='block-nested-loops', expr='a_a == b_a').join( \
           db.query().fromTable('C'), \
           method='block-nested-loops', expr='a_a == c_a').join( \
           db.query().fromTable('D'), \
           method='block-nested-loops', expr='a_a == d_a').join( \
           db.query().fromTable('E'), \
           method='block-nested-loops', expr='a_a == e_a').join( \
           db.query().fromTable('F'), \
           method='block-nested-loops', expr='a_a == f_a').finalize()

query8 = db.query().fromTable('A').join( \
           db.query().fromTable('B'), \
           method='block-nested-loops', expr='a_a == b_a').join( \
           db.query().fromTable('C'), \
           method='block-nested-loops', expr='a_a == c_a').join( \
           db.query().fromTable('D'), \
           method='block-nested-loops', expr='a_a == d_a').join( \
           db.query().fromTable('E'), \
           method='block-nested-loops', expr='a_a == e_a').join( \
           db.query().fromTable('F'), \
           method='block-nested-loops', expr='a_a == f_a').join( \
           db.query().fromTable('G'), \
           method='block-nested-loops', expr='a_a == g_a').join( \
           db.query().fromTable('H'), \
           method='block-nested-loops', expr='a_a == h_a').finalize()

query10 = db.query().fromTable('A').join( \
           db.query().fromTable('B'), \
           method='block-nested-loops', expr='a_a == b_a').join( \
           db.query().fromTable('C'), \
           method='block-nested-loops', expr='a_a == c_a').join( \
           db.query().fromTable('D'), \
           method='block-nested-loops', expr='a_a == d_a').join( \
           db.query().fromTable('E'), \
           method='block-nested-loops', expr='a_a == e_a').join( \
           db.query().fromTable('F'), \
           method='block-nested-loops', expr='a_a == f_a').join( \
           db.query().fromTable('G'), \
           method='block-nested-loops', expr='a_a == g_a').join( \
           db.query().fromTable('H'), \
           method='block-nested-loops', expr='a_a == h_a').join( \
           db.query().fromTable('I'), \
           method='block-nested-loops', expr='a_a == i_a').join( \
           db.query().fromTable('J'), \
           method='block-nested-loops', expr='a_a == j_a').finalize()

query12 = db.query().fromTable('A').join( \
           db.query().fromTable('B'), \
           method='block-nested-loops', expr='a_a == b_a').join( \
           db.query().fromTable('C'), \
           method='block-nested-loops', expr='a_a == c_a').join( \
           db.query().fromTable('D'), \
           method='block-nested-loops', expr='a_a == d_a').join( \
           db.query().fromTable('E'), \
           method='block-nested-loops', expr='a_a == e_a').join( \
           db.query().fromTable('F'), \
           method='block-nested-loops', expr='a_a == f_a').join( \
           db.query().fromTable('G'), \
           method='block-nested-loops', expr='a_a == g_a').join( \
           db.query().fromTable('H'), \
           method='block-nested-loops', expr='a_a == h_a').join( \
           db.query().fromTable('I'), \
           method='block-nested-loops', expr='a_a == i_a').join( \
           db.query().fromTable('J'), \
           method='block-nested-loops', expr='a_a == j_a').join( \
           db.query().fromTable('K'), \
           method='block-nested-loops', expr='a_a == k_a').join( \
           db.query().fromTable('L'), \
           method='block-nested-loops', expr='a_a == l_a').finalize()

# Perform experiments on BushyOptimizer
optimizerName = "Default" if len(sys.argv) < 2 else sys.argv[1]

if optimizerName == "Bushy":
  db.optimizer = BushyOptimizer(db)
elif optimizerName == "Greedy":
  db.optimizer = GreedyOptimizer(db)
else:
  pass

print("Testing " + optimizerName + " Optimizer...\n")

start = time()
db.optimizer.pickJoinOrder(query2)
end = time()
print("Number of plans considered: " + str(db.optimizer.numPlansConsidered))
print("Time to join 2 plans: " + str(end - start) + "\n")

start = time()
db.optimizer.pickJoinOrder(query4)
end = time()
print("Number of plans considered: " + str(db.optimizer.numPlansConsidered))
print("Time to join 4 plans: " + str(end - start) + "\n")

start = time()
db.optimizer.pickJoinOrder(query6)
end = time()
print("Number of plans considered: " + str(db.optimizer.numPlansConsidered))
print("Time to join 6 plans: " + str(end - start) + "\n")

start = time()
db.optimizer.pickJoinOrder(query8)
end = time()
print("Number of plans considered: " + str(db.optimizer.numPlansConsidered))
print("Time to join 8 plans: " + str(end - start) + "\n")

start = time()
db.optimizer.pickJoinOrder(query10)
end = time()
print("Number of plans considered: " + str(db.optimizer.numPlansConsidered))
print("Time to join 10 plans: " + str(end - start) + "\n")

start = time()
db.optimizer.pickJoinOrder(query12)
end = time()
print("Number of plans considered: " + str(db.optimizer.numPlansConsidered))
print("Time to join 12 plans: " + str(end - start) + "\n")

# Clean-up relations

cleanup(db)

db.close()