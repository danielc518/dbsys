import itertools

from Query.Plan import Plan
from Query.Operators.Join import Join
from Query.Operators.Project import Project
from Query.Operators.Select import Select
from Query.Operators.TableScan import TableScan
from Query.Optimizer import Optimizer
from Utils.ExpressionInfo import ExpressionInfo

class BushyOptimizer(Optimizer):
  
  def pickJoinOrder(self, plan):
    self.numPlansConsidered = 0

    tableIds = list()
    joinOps  = list()
    optPlans = dict()
    fields   = dict()

    self.extractJoinInfo(plan, tableIds, joinOps, optPlans, fields)
    
    numTables = 2
    while numTables <= len(tableIds):
      # Get all possible combinations of table IDs of size 2, 3, 4, ... etc.
      joinOrdersOuter = itertools.combinations(tableIds, numTables)
      for joinOrderOuter in joinOrdersOuter:
        # Find optimal plan for a particular combination joins
        minCost = None
        optPlan = None

        # Distribute the combinations in half (i.e. bushy)
        for num in range(1, int(numTables / 2) + 1):
          # Break down into further possible combinations
          joinOrdersInner = itertools.combinations(joinOrderOuter, num)

          for joinOrderInner in joinOrdersInner:
            # Start examining each possible plan
            lhsIds = list(joinOrderInner)
            rhsIds = list(set(joinOrderOuter) - set(joinOrderInner))

            lhsJoinKey = self.getJoinKey(lhsIds)
            rhsJoinKey = self.getJoinKey(rhsIds)

            lhsOpt = optPlans[lhsJoinKey] if lhsJoinKey in optPlans else None
            rhsOpt = optPlans[rhsJoinKey] if rhsJoinKey in optPlans else None

            if lhsOpt is None or rhsOpt is None:
              continue # Skip irrelevant joins

            # Form a list of available attributes of this join
            allAttrs = list()
            for lhsId in lhsIds:
              allAttrs.extend(fields[lhsId])

            for rhsId in rhsIds:
              allAttrs.extend(fields[rhsId])

            currJoinExpr = None

            # Check whether any join expression can be satisfied with this join
            for join in joinOps:   
              if join.joinExpr:
                joinAttrs = ExpressionInfo(join.joinExpr).getAttributes()
                if self.contains(allAttrs, joinAttrs):
                  currJoinExpr = join.joinExpr
                  break

            if currJoinExpr is None:
              continue # Skip irrelevant joins

            self.numPlansConsidered += 1
            
            # Compare costs of different type of joins 
            for joinMethod in ["nested-loops", "block-nested-loops"]:
              possiblePlan = Plan(root=Join(lhsPlan=lhsOpt, rhsPlan=rhsOpt, method=joinMethod, expr=currJoinExpr))

              possiblePlan.prepare(self.db)
              # possiblePlan.sample(1.0) # Sampling causes too much overhead!
              cost = possiblePlan.cost(estimated=True)

              if minCost is None or cost < minCost:
                minCost = cost
                optPlan = possiblePlan

        optPlans[self.getJoinKey(joinOrderOuter)] = None if optPlan is None else optPlan.root 

      numTables = numTables + 1

    return optPlans[self.getJoinKey(tableIds)]
