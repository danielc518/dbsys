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
    # TODO
    return plan

