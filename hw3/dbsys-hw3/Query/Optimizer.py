import itertools

from Query.Plan import Plan
from Query.Operators.Join import Join
from Query.Operators.Project import Project
from Query.Operators.Select import Select
from Query.Operators.TableScan import TableScan
from Utils.ExpressionInfo import ExpressionInfo

class Optimizer:
  """
  A query optimization class.

  This implements System-R style query optimization, using dynamic programming.
  We only consider left-deep plan trees here.

  We provide doctests for example usage only.
  Implementations and cost heuristics may vary.

  >>> import Database
  >>> db = Database.Database()
  >>> try:
  ...   db.createRelation('department', [('did', 'int'), ('eid', 'int')])
  ...   db.createRelation('employee', [('id', 'int'), ('age', 'int')])
  ... except ValueError:
  ...   pass

  # Join Order Optimization
  >>> query4 = db.query().fromTable('employee').join( \
        db.query().fromTable('department'), \
        method='block-nested-loops', expr='id == eid').finalize()

  >>> db.optimizer.pickJoinOrder(query4)

  # Pushdown Optimization
  >>> query5 = db.query().fromTable('employee').union(db.query().fromTable('employee')).join( \
        db.query().fromTable('department'), \
        method='block-nested-loops', expr='id == eid')\
        .where('eid > 0 and id > 0 and (eid == 5 or id == 6)')\
        .select({'id': ('id', 'int'), 'eid':('eid','int')}).finalize()

  >>> db.optimizer.pushdownOperators(query5)

  """

  def __init__(self, db):
    self.db = db
    self.statsCache = {}
    self.numPlansConsidered = 0

  # Caches the cost of a plan computed during query optimization.
  def addPlanCost(self, plan, cost):
    raise NotImplementedError

  # Checks if we have already computed the cost of this plan.
  def getPlanCost(self, plan):
    raise NotImplementedError

  # Given a plan, return an optimized plan with both selection and
  # projection operations pushed down to their nearest defining relation
  # This does not need to cascade operators, but should determine a
  # suitable ordering for selection predicates based on the cost model below.
  def pushdownOperators(self, plan):
    newRoot = self.pushdownOperator(plan.root)
    return Plan(root=newRoot)

  def pushdownOperator(self, op):
    opType = op.operatorType()

    # PROJECT pushdown
    if opType == "Project":
      op.subPlan = self.pushdownOperator(op.subPlan)

      subPlanType = op.subPlan.operatorType()

      if subPlanType == "Select":
        selections = ExpressionInfo(op.subPlan.selectExpr).getAttributes()

        for selection in selections:
          if selection not in op.projectExprs.keys():
            return op # Cannot push-down

        op.subPlan = op.subPlan.subPlan
        op.subPlan.subPlan = self.pushdownOperator(op)
      elif subPlanType.endswith("Join"):
        lFields = op.subPlan.lhsPlan.schema().fields
        rFields = op.subPlan.rhsPlan.schema().fields

        lProjectExprs = dict()
        rProjectExprs = dict()

        for (attr, (expr, _)) in op.projectExprs.items():
          projections = ExpressionInfo(expr).getAttributes()

          if self.contains(lFields, projections):
            lProjectExprs[attr] = op.projectExprs[attr]
            continue
          if self.contains(rFields, projections):
            rProjectExprs[attr] = op.projectExprs[attr]

        if lProjectExprs:
          op.subPlan.lhsPlan = self.pushdownOperator(Project(op.subPlan.lhsPlan, lProjectExprs))
        if rProjectExprs:
          op.subPlan.rhsPlan = self.pushdownOperator(Project(op.subPlan.rhsPlan, rProjectExprs))

        if len(op.projectExprs) != (len(lProjectExprs) + len(rProjectExprs)):
          return op # Cannot push-down completely
      elif subPlanType == "UnionAll":
        op.subPlan.lhsPlan = self.pushdownOperator(Project(op.subPlan.lhsPlan, op.projectExprs))
        op.subPlan.rhsPlan = self.pushdownOperator(Project(op.subPlan.rhsPlan, op.projectExprs))
      else:
        return op # Cannot push-down

      return op.subPlan # Return pushed-down plan

    # SELECT pushdown
    elif opType == "Select":
      op.subPlan = self.pushdownOperator(op.subPlan)

      subPlanType = op.subPlan.operatorType()

      if subPlanType == "Sort":
        op.subPlan = op.subPlan.subPlan
        op.subPlan.subPlan = self.pushdownOperator(op)
      elif subPlanType.endswith("Join"):
        lFields = op.subPlan.lhsPlan.schema().fields
        rFields = op.subPlan.rhsPlan.schema().fields

        lSelectExprs  = list()
        rSelectExprs  = list()
        unPushedExprs = list()

        # All 'Select' expressions are in Conjunctive Normal Form 
        selectExprs = ExpressionInfo(op.selectExpr).decomposeCNF()

        for selectExpr in selectExprs:
          selections = ExpressionInfo(selectExpr).getAttributes()
          if self.contains(lFields, selections):
            lSelectExprs.append(selectExpr)
          elif self.contains(rFields, selections):
            rSelectExprs.append(selectExpr)
          else:
            unPushedExprs.append(selectExpr)

        if lSelectExprs:
          op.subPlan.lhsPlan = self.pushdownOperator(Select(op.subPlan.lhsPlan, ' and '.join(lSelectExprs)))
        if rSelectExprs:
          op.subPlan.rhsPlan = self.pushdownOperator(Select(op.subPlan.rhsPlan, ' and '.join(rSelectExprs)))
        if unPushedExprs:
          return Select(op.subPlan, ' and '.join(unPushedExprs))
      elif subPlanType == "UnionAll":
        op.subPlan.lhsPlan = self.pushdownOperator(Select(op.subPlan.lhsPlan, op.selectExpr))
        op.subPlan.rhsPlan = self.pushdownOperator(Select(op.subPlan.rhsPlan, op.selectExpr))
      else:
        return op

      return op.subPlan # Return pushed-down plan
    elif opType == "GroupBy" or opType == "Sort":
      op.subPlan = self.pushdownOperator(op.subPlan)
      return op
    elif opType == "UnionAll" or opType.endswith("Join"):
      op.lhsPlan = self.pushdownOperator(op.lhsPlan)
      op.rhsPlan = self.pushdownOperator(op.rhsPlan)
      return op
    else:
      # Push down not supported.
      return op

  # Checks whether 'lhs' contains 'rhs'
  def contains(self, lhs, rhs):
    for r in rhs:
      if r not in lhs:
        return False
    return True

  # Returns an optimized query plan with joins ordered via a System-R style
  # dyanmic programming algorithm. The plan cost should be compared with the
  # use of the cost model below.
  def pickJoinOrder(self, plan):
    # Some restrictions apply:
    # 1. Cannot involve hash-joins or index-joins
    # 2. Only join operations beyond certain point (i.e. cannot have join -> aggregation -> join, etc.)

    tableIds = list()
    joinOps  = list()
    optPlans = dict()
    fields   = dict()

    firstOpWithJoins = self.extractJoinInfo(plan, tableIds, joinOps, optPlans, fields)

    if len(joinOps) == 0:
      return plan
    
    numTables = 2
    while numTables <= len(tableIds):
      possibleJoinOrders = itertools.combinations(tableIds, numTables)
      for possibleJoinOrder in possibleJoinOrders:
        minCost = None
        optPlan = None
        for tableId in possibleJoinOrder:
          # Left-deep-only optimizer (i.e. rhs operand is a base relation)
          lhsIds = list(possibleJoinOrder)
          lhsIds.remove(tableId)

          lhsJoinKey = self.getJoinKey(lhsIds)
          rhsJoinKey = str(tableId)

          lhsOpt = optPlans[lhsJoinKey] if lhsJoinKey in optPlans else None
          rhsOpt = optPlans[rhsJoinKey] if rhsJoinKey in optPlans else None

          if lhsOpt is None or rhsOpt is None:
            continue # Skip irrelevant joins

          # Form a list of available attributes of this join
          allAttrs = list()
          for lhsId in lhsIds:
            allAttrs.extend(fields[lhsId])

          allAttrs.extend(fields[tableId])

          currJoinExpr = None

          # Check whether any join expression can be satisfied with this join
          for join in joinOps:      
            if join.joinExpr:
              joinAttrs = ExpressionInfo(join.joinExpr).getAttributes()
              if self.contains(allAttrs, joinAttrs):
                currJoinExpr = join.joinExpr
                break
            else:
              # Should not involve hash-joins or index-joins (limitation)
              return plan

          if currJoinExpr is None:
            continue # Irrelevant join

          for joinMethod in ["nested-loops", "block-nested-loops"]:
            possiblePlan = Plan(root=Join(lhsPlan=lhsOpt, rhsPlan=rhsOpt, method=joinMethod, expr=currJoinExpr))

            possiblePlan.prepare(self.db)
            # possiblePlan.sample(1.0) # Sampling causes too much overhead!
            cost = possiblePlan.cost(estimated=True)

            if minCost is None or cost < minCost:
              minCost = cost
              optPlan = possiblePlan

        optPlans[self.getJoinKey(possibleJoinOrder)] = None if optPlan is None else optPlan.root 

      numTables = numTables + 1

    firstOpWithJoins.subPlan = optPlans[self.getJoinKey(tableIds)]

    plan.prepare(self.db)

    return plan

  # Extracts relations, join operators, and fields involved in the given plan
  def extractJoinInfo(self, plan, tableIds, joinOps, optPlans, fields):
    firstOpWithJoins = None

    for (_,op) in plan.flatten():
      if firstOpWithJoins is None and not isinstance(op, Join) and not isinstance(op, TableScan) and isinstance(op.subPlan, Join):
        firstOpWithJoins = op

      if isinstance(op, Project):
        if isinstance(op.subPlan, TableScan):
          tableIds.append(op.subPlan.id())
          optPlans[str(op.subPlan.id())] = op
          fields[op.subPlan.id()] = op.subPlan.schema().fields
      elif isinstance(op, Select):
        if isinstance(op.subPlan, TableScan):
          tableIds.append(op.subPlan.id())
          optPlans[str(op.subPlan.id())] = op
          fields[op.subPlan.id()] = op.subPlan.schema().fields
      elif isinstance(op, TableScan):
        if str(op.id()) not in optPlans:
          tableIds.append(op.id())
          optPlans[str(op.id())] = op
          fields[op.id()] = op.schema().fields
      elif isinstance(op, Join):
        joinOps.append(op)
      else:
        continue

    return firstOpWithJoins

  # Return a string key of table ids for use in dictionary 
  def getJoinKey(self, tableIds):
    return ','.join(str(x) for x in tableIds)

  # Optimize the given query plan, returning the resulting improved plan.
  # This should perform operation pushdown, followed by join order selection.
  def optimizeQuery(self, plan):
    pushedDown_plan = self.pushdownOperators(plan)
    joinPicked_plan = self.pickJoinOrder(pushedDown_plan)

    return joinPicked_plan

if __name__ == "__main__":
  import doctest
  doctest.testmod()
