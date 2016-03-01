from Catalog.Schema import DBSchema
from Query.Operator import Operator

import itertools
import types

class GroupBy(Operator):
  def __init__(self, subPlan, **kwargs):
    super().__init__(**kwargs)

    if self.pipelined:
      raise ValueError("Pipelined group-by-aggregate operator not supported")

    self.subPlan     = subPlan
    self.subSchema   = subPlan.schema()
    self.groupSchema = kwargs.get("groupSchema", None)
    self.aggSchema   = kwargs.get("aggSchema", None)
    self.groupExpr   = kwargs.get("groupExpr", None)
    self.aggExprs    = kwargs.get("aggExprs", None)
    self.groupHashFn = kwargs.get("groupHashFn", None)

    self.validateGroupBy()
    self.initializeSchema()

  # Perform some basic checking on the group-by operator's parameters.
  def validateGroupBy(self):
    requireAllValid = [self.subPlan, \
                       self.groupSchema, self.aggSchema, \
                       self.groupExpr, self.aggExprs, self.groupHashFn ]

    if any(map(lambda x: x is None, requireAllValid)):
      raise ValueError("Incomplete group-by specification, missing a required parameter")

    if not self.aggExprs:
      raise ValueError("Group-by needs at least one aggregate expression")

    if len(self.aggExprs) != len(self.aggSchema.fields):
      raise ValueError("Invalid aggregate fields: schema mismatch")

  # Initializes the group-by's schema as a concatenation of the group-by
  # fields and all aggregate fields.
  def initializeSchema(self):
    schema = self.operatorType() + str(self.id())
    fields = self.groupSchema.schema() + self.aggSchema.schema()
    self.outputSchema = DBSchema(schema, fields)

  # Returns the output schema of this operator
  def schema(self):
    return self.outputSchema

  # Returns any input schemas for the operator if present
  def inputSchemas(self):
    return [self.subPlan.schema()]

  # Returns a string describing the operator type
  def operatorType(self):
    return "GroupBy"

  # Returns child operators if present
  def inputs(self):
    return [self.subPlan]

  # Iterator abstraction for selection operator.
  def __iter__(self):
    self.initializeOutput()
    self.outputIterator = self.processAllPages()
    return self

  def __next__(self):
    return next(self.outputIterator)

  # Page-at-a-time operator processing
  def processInputPage(self, pageId, page):
    raise ValueError("Page-at-a-time processing not supported for joins")

  # Set-at-a-time operator processing
  def processAllPages(self):
    relIdMap = {}

    # Perform partition using hash function
    self.partition(relIdMap)

    # Perform group-by operation
    for hashValue, relId in relIdMap.items():
      pageIter = self.storage.pages(relId)

      aggregationResults = {} # Stores intermediate aggregation results

      for _, page in pageIter:
        for tupleP in page:
          tupleU = self.subSchema.unpack(tupleP)
          gbVal = self.getGroupByValue(tupleU)

          # Get intermediate results for this group-by value
          intermediateResults = aggregationResults.get(gbVal, None)

          if intermediateResults is None:
            intermediateResults = list()
            aggregationResults[gbVal] = intermediateResults
            for aggExpr in self.aggExprs:
              # Form a list of initial values
              intermediateResults.append(aggExpr[0])
          
          idx = 0
          for aggExpr in self.aggExprs:
            # Perform aggregation by applying the lambda function (aggExpr[1])
            intermediateResult = intermediateResults[idx]
            intermediateResults[idx] = aggExpr[1](intermediateResult, tupleU)
            idx = idx + 1

      for gbVal, intermediateResults in aggregationResults.items():
        idx = 0
        for aggExpr in self.aggExprs:
          # Perform final step by applying the lambda function (aggExpr[2])
          intermediateResult = intermediateResults[idx]
          intermediateResults[idx] = aggExpr[2](intermediateResult)
          idx = idx + 1

        outputList = itertools.chain([gbVal[0]], intermediateResults)
        outputTuple = self.outputSchema.instantiate(*outputList)
        self.emitOutputTuple(self.outputSchema.pack(outputTuple))

      # No need to track anything but the last output page when in batch mode.
      if self.outputPages:
        self.outputPages = [self.outputPages[-1]]

    # Remove partitions
    for _, relId in relIdMap.items():
      self.storage.removeRelation(relId)

    return self.storage.pages(self.relationId())

  # Partitions a given relation based on some hash function 
  def partition(self, relIdMap):
    for (pageId, page) in iter(self.subPlan):
      for tupleP in page:
        # Compute hash value for every tuple
        tupleU = self.subSchema.unpack(tupleP)
        hashVal = self.groupHashFn(self.getGroupByValue(tupleU))

        # Store in temporary buckets (files)
        if not hashVal in relIdMap:
          relId = str(self.id()) + "_grp_" + str(hashVal)
          self.storage.createRelation(relId, self.subSchema)
          relIdMap[hashVal] = relId

        self.storage.insertTuple(relIdMap[hashVal], tupleP)

  def getGroupByValue(self, unpackedTuple):
    gbVal = self.groupExpr(unpackedTuple)
    return gbVal if type(gbVal) is tuple else gbVal,

  # Plan and statistics information

  # Returns a single line description of the operator.
  def explain(self):
    return super().explain() + "(groupSchema=" + self.groupSchema.toString() \
                             + ", aggSchema=" + self.aggSchema.toString() + ")"
