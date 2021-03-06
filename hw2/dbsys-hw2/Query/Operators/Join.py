import itertools

from Catalog.Schema import DBSchema
from Query.Operator import Operator

class Join(Operator):
  def __init__(self, lhsPlan, rhsPlan, **kwargs):
    super().__init__(**kwargs)

    if self.pipelined:
      raise ValueError("Pipelined join operator not supported")

    self.lhsPlan    = lhsPlan
    self.rhsPlan    = rhsPlan
    self.joinExpr   = kwargs.get("expr", None)
    self.joinMethod = kwargs.get("method", None)
    self.lhsSchema  = kwargs.get("lhsSchema", None if lhsPlan is None else lhsPlan.schema())
    self.rhsSchema  = kwargs.get("rhsSchema", None if rhsPlan is None else rhsPlan.schema())

    self.lhsKeySchema   = kwargs.get("lhsKeySchema", None)
    self.rhsKeySchema   = kwargs.get("rhsKeySchema", None)
    self.lhsHashFn      = kwargs.get("lhsHashFn", None)
    self.rhsHashFn      = kwargs.get("rhsHashFn", None)

    self.validateJoin()
    self.initializeSchema()
    self.initializeMethod(**kwargs)

  # Checks the join parameters.
  def validateJoin(self):
    # Valid join methods: "nested-loops", "block-nested-loops", "indexed", "hash"
    if self.joinMethod not in ["nested-loops", "block-nested-loops", "indexed", "hash"]:
      raise ValueError("Invalid join method in join operator")

    # Check all fields are valid.
    if self.joinMethod == "nested-loops" or self.joinMethod == "block-nested-loops":
      methodParams = [self.joinExpr]

    elif self.joinMethod == "indexed":
      methodParams = [self.lhsKeySchema]

    elif self.joinMethod == "hash":
      methodParams = [self.lhsHashFn, self.lhsKeySchema, \
                      self.rhsHashFn, self.rhsKeySchema]

    requireAllValid = [self.lhsPlan, self.rhsPlan, \
                       self.joinMethod, \
                       self.lhsSchema, self.rhsSchema ] \
                       + methodParams

    if any(map(lambda x: x is None, requireAllValid)):
      raise ValueError("Incomplete join specification, missing join operator parameter")

    # For now, we assume that the LHS and RHS schema have
    # disjoint attribute names, enforcing this here.
    for lhsAttr in self.lhsSchema.fields:
      if lhsAttr in self.rhsSchema.fields:
        raise ValueError("Invalid join inputs, overlapping schema detected")


  # Initializes the output schema for this join.
  # This is a concatenation of all fields in the lhs and rhs schema.
  def initializeSchema(self):
    schema = self.operatorType() + str(self.id())
    fields = self.lhsSchema.schema() + self.rhsSchema.schema()
    self.joinSchema = DBSchema(schema, fields)

  # Initializes any additional operator parameters based on the join method.
  def initializeMethod(self, **kwargs):
    if self.joinMethod == "indexed":
      self.indexId = kwargs.get("indexId", None)
      if self.indexId is None or self.lhsKeySchema is None:
        raise ValueError("Invalid index for use in join operator")

  # Returns the output schema of this operator
  def schema(self):
    return self.joinSchema

  # Returns any input schemas for the operator if present
  def inputSchemas(self):
    return [self.lhsSchema, self.rhsSchema]

  # Returns a string describing the operator type
  def operatorType(self):
    readableJoinTypes = { 'nested-loops'       : 'NL'
                        , 'block-nested-loops' : 'BNL'
                        , 'indexed'            : 'Index'
                        , 'hash'               : 'Hash' }
    return readableJoinTypes[self.joinMethod] + "Join"

  # Returns child operators if present
  def inputs(self):
    return [self.lhsPlan, self.rhsPlan]

  # Iterator abstraction for join operator.
  def __iter__(self):
    self.initializeOutput()
    # Pipelined join operator is not supported according to constructor
    self.outputIterator = self.processAllPages()
    return self

  def __next__(self):
    return next(self.outputIterator)

  # Page-at-a-time operator processing
  def processInputPage(self, pageId, page):
    raise ValueError("Page-at-a-time processing not supported for joins")

  # Set-at-a-time operator processing
  def processAllPages(self):
    if self.joinMethod == "nested-loops":
      return self.nestedLoops()

    elif self.joinMethod == "block-nested-loops":
      return self.blockNestedLoops()

    elif self.joinMethod == "indexed":
      return self.indexedNestedLoops()

    elif self.joinMethod == "hash":
      return self.hashJoin()

    else:
      raise ValueError("Invalid join method in join operator")

  # Return an iterator to the output relation
  def outputRelationIterator(self):
    return self.storage.pages(self.relationId())


  ##################################
  #
  # Nested loops implementation
  #
  def nestedLoops(self):
    self.runNestedLoops(iter(self.lhsPlan), iter(self.rhsPlan), False, False, False)
    # Return an iterator to the output relation
    return self.outputRelationIterator()

  # Common function used by all types of joins
  def runNestedLoops(self, lhsPageIter, rhsPageIter, isBlock, isIndex, isHash):
    for (lPageId, lhsPage) in lhsPageIter:
      for lTuple in lhsPage:
        # Load the lhs once per inner loop.
        joinExprEnv = self.loadSchema(self.lhsSchema, lTuple)

        if isIndex:
          keyData = self.lhsSchema.projectBinary(lTuple, self.lhsKeySchema)
          idxManager = self.storage.fileMgr.indexManager
          rhsPageIter = idxManager.lookupByIndex(self.indexId, keyData)

        for rhsItem in rhsPageIter:
          rhsTupleIter = None

          if isIndex:
            # Retrieve index-matched tuple from corresponding page
            page = self.storage.bufferPool.getPage(rhsItem.pageId) # rhsItem = rhsTupId
            rhsTupleIter = [page.getTuple(rhsItem)]
          else:
            # Need to scan all tuples
            rhsTupleIter = rhsItem[1] # rhsItem = (rPageId, rhsPage)

          for rTuple in rhsTupleIter:
            # Load the RHS tuple fields.
            joinExprEnv.update(self.loadSchema(self.rhsSchema, rTuple))

            # Evaluate the join predicate, and output if we have a match.
            validJoin = False

            if isIndex:
              validJoin = True
            else:
              if isHash:
                lhsKeyData = self.lhsSchema.projectBinary(lTuple, self.lhsKeySchema)
                rhsKeyData = self.rhsSchema.projectBinary(rTuple, self.rhsKeySchema)
                validJoin = lhsKeyData == rhsKeyData
              else:
                validJoin = True

            if self.joinExpr:
              validJoin = validJoin and eval(self.joinExpr, globals(), joinExprEnv)

            if validJoin:
              outputTuple = self.joinSchema.instantiate(*[joinExprEnv[f] for f in self.joinSchema.fields])
              self.emitOutputTuple(self.joinSchema.pack(outputTuple))

        # No need to track anything but the last output page when in batch mode.
        if self.outputPages:
          self.outputPages = [self.outputPages[-1]]
      
      if isBlock:
        self.storage.bufferPool.unpinPage(lPageId)

  ##################################
  #
  # Block nested loops implementation
  #
  # This attempts to use all the free pages in the buffer pool
  # for its block of the outer relation.

  # Accesses a block of pages from an iterator.
  # This method pins pages in the buffer pool during its access.
  # We track the page ids in the block to unpin them after processing the block.
  def accessPageBlock(self, bufPool, pageIterator):
    pinnedPages = list()
    try:
      while bufPool.numFreePages() > 0:
        (lPageId, lhsPage) = next(pageIterator)
        bufPool.pinPage(lPageId)
        pinnedPages.append((lPageId, lhsPage))
    except StopIteration:
      pass
    return pinnedPages

  def pinPages(self, pageIterator):
    return self.accessPageBlock(self.storage.bufferPool, pageIterator)

  def blockNestedLoops(self):
    self.runBlockNestedLoops(iter(self.lhsPlan), self.rhsPlan, False)
    return self.outputRelationIterator()

  def runBlockNestedLoops(self, lhsPageIter, rhsPageIter, isHashJoin):
    pinnedPages = self.pinPages(lhsPageIter)
    # Keep running untill ALL pages have been loaded
    # Note: 'rhsPageIter' should be 'list' type NOT 'iter'
    while len(pinnedPages) > 0:
      self.runNestedLoops(iter(pinnedPages), rhsPageIter, True, False, isHashJoin)
      pinnedPages = self.pinPages(lhsPageIter)

  ##################################
  #
  # Indexed nested loops implementation
  #
  def indexedNestedLoops(self):
    self.runNestedLoops(iter(self.lhsPlan), None, False, True, False)
    return self.outputRelationIterator()

  ##################################
  #
  # Hash join implementation.
  #
  def hashJoin(self):
    lhsRelIdMap = {}
    rhsRelIdMap = {}

    # Partition each relation using hash function
    self.partition(self.lhsPlan, self.lhsHashFn, self.lhsSchema, lhsRelIdMap, "lhs")
    self.partition(self.rhsPlan, self.rhsHashFn, self.rhsSchema, rhsRelIdMap, "rhs")

    # Perform block nested loop join for each bucket
    for hashValue, relId in lhsRelIdMap.items():
      lhsPageIter = self.storage.pages(relId)
      rhsPageIter = self.storage.pages(rhsRelIdMap[hashValue])

      self.runBlockNestedLoops(lhsPageIter, list(rhsPageIter), True)

    # Remove partitions
    partitionIter = itertools.chain(lhsRelIdMap.items(), rhsRelIdMap.items())
    for _, relId in partitionIter:
      self.storage.removeRelation(relId)

    return self.outputRelationIterator()
        
  # Partitions a given relation based on some hash function 
  def partition(self, plan, hashFn, schema, relIdMap, relPrefix):
    for (pageId, page) in iter(plan):
      for tuple in page:
        # Compute hash value for every tuple
        fieldBindings = self.loadSchema(schema, tuple)
        hashValue = eval(hashFn, globals(), fieldBindings)

        # Store in temporary buckets (files)
        if not hashValue in relIdMap:
          relId = str(self.id()) + "_" + relPrefix + "_" + str(hashValue)
          self.storage.createRelation(relId, schema)
          relIdMap[hashValue] = relId

        self.storage.insertTuple(relIdMap[hashValue], tuple)          

  # Plan and statistics information

  # Returns a single line description of the operator.
  def explain(self):
    if self.joinMethod == "nested-loops" or self.joinMethod == "block-nested-loops":
      exprs = "(expr='" + str(self.joinExpr) + "')"

    elif self.joinMethod == "indexed":
      exprs =  "(" + ','.join(filter(lambda x: x is not None, (
          [ "expr='" + str(self.joinExpr) + "'" if self.joinExpr else None ]
        + [ "indexKeySchema=" + self.lhsKeySchema.toString() ]
        ))) + ")"

    elif self.joinMethod == "hash":
      exprs = "(" + ','.join(filter(lambda x: x is not None, (
          [ "expr='" + str(self.joinExpr) + "'" if self.joinExpr else None ]
        + [ "lhsKeySchema=" + self.lhsKeySchema.toString() ,
            "rhsKeySchema=" + self.rhsKeySchema.toString() ,
            "lhsHashFn='" + self.lhsHashFn + "'" ,
            "rhsHashFn='" + self.rhsHashFn + "'" ]
        ))) + ")"

    return super().explain() + exprs
