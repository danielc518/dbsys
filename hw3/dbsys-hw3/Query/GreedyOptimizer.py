import itertools

from Query.Plan import Plan
from Query.Operators.Join import Join
from Query.Operators.Project import Project
from Query.Operators.Select import Select
from Query.Operators.TableScan import TableScan
from Query.Optimizer import Optimizer
from Utils.ExpressionInfo import ExpressionInfo

class GreedyOptimizer(Optimizer):
  
  def pickJoinOrder(self, plan):
    self.numPlansConsidered = 0

    tableIds = list()
    joinOps  = list()
    optPlans = dict()
    fields   = dict()

    self.extractJoinInfo(plan, tableIds, joinOps, optPlans, fields)

    # Create worklist consisting of table IDs
    worklist = [str(tableId) for tableId in tableIds]

    # Now work our way down the 'worklist' greedily
    numTables = len(worklist)
    while numTables >= 2:
      # Choose the cheapest join that can be made over the remaining sub-plans
      minCost  = None
      optPlan  = None
      optLhsId = None
      optRhsId = None

      possibleJoinOrders = itertools.combinations(worklist, 2)
      for possibleJoinOrder in possibleJoinOrders:
        # Start examining each possible plan
        lhsId = possibleJoinOrder[0]
        rhsId = possibleJoinOrder[1]

        lhsOpt = optPlans[lhsId] if lhsId in optPlans else None
        rhsOpt = optPlans[rhsId] if rhsId in optPlans else None

        if lhsOpt is None or rhsOpt is None:
          continue # Skip irrelevant joins

        # This is to take care of multi-way joins added to worklist
        lhsIds = lhsId.split(",")
        rhsIds = rhsId.split(",")

        # Form a list of available attributes of this join
        allAttrs = list()
        for lId in lhsIds:
          allAttrs.extend(fields[int(lId)])

        for rId in rhsIds:
          allAttrs.extend(fields[int(rId)])

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

        self.numPlansConsidered += 2
            
        # Compare costs of different type of joins 
        for joinMethod in ["nested-loops", "block-nested-loops"]:
          possiblePlan = Plan(root=Join(lhsPlan=lhsOpt, rhsPlan=rhsOpt, method=joinMethod, expr=currJoinExpr))

          possiblePlan.prepare(self.db)
          # possiblePlan.sample(1.0) # Sampling causes too much overhead!
          cost = possiblePlan.cost(estimated=True)

          if minCost is None or cost < minCost:
            minCost  = cost
            optPlan  = possiblePlan
            optLhsId = lhsId
            optRhsId = rhsId

        # Switch left and right and compare again
        for joinMethod in ["nested-loops", "block-nested-loops"]:
          possiblePlan = Plan(root=Join(lhsPlan=rhsOpt, rhsPlan=lhsOpt, method=joinMethod, expr=currJoinExpr))

          possiblePlan.prepare(self.db)
          # possiblePlan.sample(1.0) # Sampling causes too much overhead!
          cost = possiblePlan.cost(estimated=True)

          if minCost is None or cost < minCost:
            minCost  = cost
            optPlan  = possiblePlan
            optLhsId = rhsId
            optRhsId = lhsId

      if optPlan is not None:
        # Update optimal plan
        joinKey = optLhsId + "," + optRhsId
        optPlans[joinKey] = optPlan.root

        # Update worklist
        worklist.remove(optLhsId)
        worklist.remove(optRhsId)
        worklist.append(joinKey)

      numTables = numTables - 1

    # Return single plan left in worklist
    return optPlans[worklist[0]]
