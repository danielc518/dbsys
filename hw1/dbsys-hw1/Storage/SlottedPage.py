import functools, math, struct
from struct import Struct
from io     import BytesIO

from Catalog.Identifiers import PageId, FileId, TupleId
from Catalog.Schema import DBSchema
from Storage.Page import PageHeader, Page

###########################################################
# DESIGN QUESTION 1: should this inherit from PageHeader?
# If so, what methods can we reuse from the parent?
#
class SlottedPageHeader(PageHeader):
  """
  A slotted page header implementation. This should store a slot bitmap
  implemented as a memoryview on the byte buffer backing the page
  associated with this header. Additionally this header object stores
  the number of slots in the array, as well as the index of the next
  available slot.

  The binary representation of this header object is: (numSlots, nextSlot, slotBuffer)

  >>> import io
  >>> buffer = io.BytesIO(bytes(4096))
  >>> ph     = SlottedPageHeader(buffer=buffer.getbuffer(), tupleSize=16)
  >>> ph2    = SlottedPageHeader.unpack(buffer.getbuffer())

  ## Dirty bit tests
  >>> ph.isDirty()
  False
  >>> ph.setDirty(True)
  >>> ph.isDirty()
  True
  >>> ph.setDirty(False)
  >>> ph.isDirty()
  False

  ## Tuple count tests
  >>> ph.hasFreeTuple()
  True

  # First tuple allocated should be at the first slot.
  # Notice this is a slot index, not an offset as with contiguous pages.
  >>> ph.nextFreeTuple() == 0
  True

  >>> ph.numTuples()
  1

  >>> tuplesToTest = 10
  >>> [ph.nextFreeTuple() for i in range(0, tuplesToTest)]
  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  
  >>> ph.numTuples() == tuplesToTest+1
  True

  >>> ph.hasFreeTuple()
  True

  # Check space utilization
  >>> ph.usedSpace() == (tuplesToTest+1)*ph.tupleSize
  True

  >>> ph.freeSpace() == 4096 - (ph.headerSize() + ((tuplesToTest+1) * ph.tupleSize))
  True

  >>> remainingTuples = int(ph.freeSpace() / ph.tupleSize)

  # Fill the page.
  >>> [ph.nextFreeTuple() for i in range(0, remainingTuples)] # doctest:+ELLIPSIS
  [11, 12, ...]

  >>> ph.hasFreeTuple()
  False

  # No value is returned when trying to exceed the page capacity.
  >>> ph.nextFreeTuple() == None
  True
  
  >>> ph.freeSpace() < ph.tupleSize
  True
  """

  def __init__(self, **kwargs):
    buffer     = kwargs.get("buffer", None)

    if buffer:
      self.numSlots = kwargs.get("numSlots", None)
      self.slots    = kwargs.get("slots", None)

      # 2 bytes for storing 'numSlots'
      headerSize = PageHeader.size + 2

      if self.numSlots is None:
        tupleSize     = kwargs.get("tupleSize", None)
        pageCapacity  = kwargs.get("pageCapacity", len(buffer))

        # '0.125' bytes (i.e. (1/8) bytes) per tuple for slot storage
        self.numSlots = math.floor((pageCapacity - PageHeader.size - 2) / (tupleSize + 0.125))

      if self.slots is None:
        self.slots = memoryview(buffer[headerSize:headerSize + math.ceil(0.125*self.numSlots)])
      else:
        self.slots = memoryview(self.slots)
      
      self.reprSize = headerSize + self.slots.nbytes
      
      super().__init__(**kwargs)
    else:
      raise ValueError("No backing buffer supplied for SlottedPageHeader")

  def __eq__(self, other):
    return (    super().__eq__(other)
            and self.numSlots == other.numSlots
            and self.slots == other.slots )

  def __hash__(self):
    return hash((self.flags, self.tupleSize, self.pageCapacity, self.numSlots, self.slots))

  def headerSize(self):
    return self.reprSize

  # Flag operations.
  def flag(self, mask):
    return (ord(self.flags) & mask) > 0

  def setFlag(self, mask, set):
    if set:
      self.flags = bytes([ord(self.flags) | mask])
    else:
      self.flags = bytes([ord(self.flags) & ~mask])

  # Dirty bit accessors
  def isDirty(self):
    return self.flag(PageHeader.dirtyMask)

  def setDirty(self, dirty):
    self.setFlag(PageHeader.dirtyMask, dirty)

  def numTuples(self):
    return len(self.usedSlots())

  # Returns the space available in the page associated with this header.
  def freeSpace(self):
    return self.pageCapacity - self.headerSize() - self.usedSpace()

  # Returns the space used in the page associated with this header.
  def usedSpace(self):
    return len(self.usedSlots()) * self.tupleSize


  # Slot operations.
  def slotByteOffset(self, slotIndex):
    return math.floor(slotIndex / 8)

  def offsetOfSlot(self, slotIndex):
    return self.headerSize() + (self.tupleSize * slotIndex)

  def hasSlot(self, slotIndex):
    # byte offset must be smaller than total available bytes
    return self.slotByteOffset(slotIndex) < self.slots.nbytes

  def getSlot(self, slotIndex):
    if self.hasSlot(slotIndex):
      byteChunk = self.slots[self.slotByteOffset(slotIndex)]
      return bool(self.getBit(byteChunk, slotIndex % 8))
    else:
      raise ValueError("There is no slot for the given index.")

  def setSlot(self, slotIndex, slot):
    if self.hasSlot(slotIndex):
      byteOffset = self.slotByteOffset(slotIndex);
      if slot:
        self.slots[byteOffset] = self.setBit(self.slots[byteOffset], slotIndex % 8)
      else:
        self.slots[byteOffset] = self.clearBit(self.slots[byteOffset], slotIndex % 8)
      

  def resetSlot(self, slotIndex):
    self.setSlot(slotIndex, False)

  def freeSlots(self):
    freeSlots = list()
    for slotIndex in range(self.numSlots):
      if not self.getSlot(slotIndex):
        freeSlots.append(slotIndex)
    return freeSlots

  def usedSlots(self):
    usedSlots = list()
    for slotIndex in range(self.numSlots):
      if self.getSlot(slotIndex):
        usedSlots.append(slotIndex)
    return usedSlots

  # Tuple allocation operations.
  
  # Returns whether the page has any free space for a tuple.
  def hasFreeTuple(self):
    return len(self.freeSlots()) > 0 and self.tupleSize <= self.freeSpace()

  # Returns the tupleIndex of the next free tuple.
  # This should also "allocate" the tuple, such that any subsequent call
  # does not yield the same tupleIndex.
  def nextFreeTuple(self):
    if self.hasFreeTuple():
      freeSlots = self.freeSlots()
      self.setSlot(freeSlots[0], True)
      return freeSlots[0]
    else:
      return None

  def nextTupleRange(self):
    slotIndex = self.nextFreeTuple()
    if slotIndex is None:
      return (None, None, None)
    else:
      start = self.offsetOfSlot(slotIndex)
      return (slotIndex, start, start + self.tupleSize)

  def tupleRange(self, tupleId):
    start = self.offsetOfSlot(tupleId.tupleIndex)
    return (start, start + self.tupleSize)

  # Reference: https://wiki.python.org/moin/BitManipulation
  def setBit(self, int_type, offset):
    mask = 1 << offset
    return(int_type | mask)

  # Reference: https://wiki.python.org/moin/BitManipulation
  def clearBit(self, int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)

  def getBit(self, int_type, offset):
    mask = 1 << offset
    return(int_type & mask)

  # Create a binary representation of a slotted page header.
  # The binary representation should include the slot contents.
  def pack(self):
    return super().pack() + Struct("H"+str(self.slots.nbytes)+"s").pack(self.numSlots, self.slots.tobytes())

  # Create a slotted page header instance from a binary representation held in the given buffer.
  @classmethod
  def unpack(cls, buffer):
    pageHeader = PageHeader.unpack(buffer)
    numSlots = Struct("H").unpack_from(buffer, offset=PageHeader.size)[0]
    slots = Struct("H"+str(math.ceil(0.125*numSlots))+"s").unpack_from(buffer, offset=PageHeader.size)[1]
    return cls(flags=pageHeader.flags, tupleSize=pageHeader.tupleSize, buffer=buffer, numSlots=numSlots, slots=slots)



######################################################
# DESIGN QUESTION 2: should this inherit from Page?
# If so, what methods can we reuse from the parent?
#
class SlottedPage(Page):
  """
  A slotted page implementation.

  Slotted pages use the SlottedPageHeader class for its headers, which
  maintains a set of slots to indicate valid tuples in the page.

  A slotted page interprets the tupleIndex field in a TupleId object as
  a slot index.

  >>> from Catalog.Identifiers import FileId, PageId, TupleId
  >>> from Catalog.Schema      import DBSchema

  # Test harness setup.
  >>> schema = DBSchema('employee', [('id', 'int'), ('age', 'int')])
  >>> pId    = PageId(FileId(1), 100)
  >>> p      = SlottedPage(pageId=pId, buffer=bytes(4096), schema=schema)

  # Validate header initialization
  >>> p.header.numTuples() == 0 and p.header.usedSpace() == 0
  True

  # Create and insert a tuple
  >>> e1 = schema.instantiate(1,25)
  >>> tId = p.insertTuple(schema.pack(e1))

  >>> tId.tupleIndex
  0

  # Retrieve the previous tuple
  >>> e2 = schema.unpack(p.getTuple(tId))
  >>> e2
  employee(id=1, age=25)

  # Update the tuple.
  >>> e1 = schema.instantiate(1,28)
  >>> p.putTuple(tId, schema.pack(e1))

  # Retrieve the update
  >>> e3 = schema.unpack(p.getTuple(tId))
  >>> e3
  employee(id=1, age=28)

  # Compare tuples
  >>> e1 == e3
  True

  >>> e2 == e3
  False

  # Check number of tuples in page
  >>> p.header.numTuples() == 1
  True

  # Add some more tuples
  >>> for tup in [schema.pack(schema.instantiate(i, 2*i+20)) for i in range(10)]:
  ...    _ = p.insertTuple(tup)
  ...

  # Check number of tuples in page
  >>> p.header.numTuples()
  11

  # Test iterator
  >>> [schema.unpack(tup).age for tup in p]
  [28, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38]

  # Test clearing of first tuple
  >>> tId = TupleId(p.pageId, 0)
  >>> sizeBeforeClear = p.header.usedSpace()  
  >>> p.clearTuple(tId)
  
  >>> schema.unpack(p.getTuple(tId))
  employee(id=0, age=0)

  >>> p.header.usedSpace() == sizeBeforeClear
  True

  # Check that clearTuple only affects a tuple's contents, not its presence.
  >>> [schema.unpack(tup).age for tup in p]
  [0, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38]

  # Test removal of first tuple
  >>> sizeBeforeRemove = p.header.usedSpace()
  >>> p.deleteTuple(tId)

  >>> [schema.unpack(tup).age for tup in p]
  [20, 22, 24, 26, 28, 30, 32, 34, 36, 38]
  
  # Check that the page's slots have tracked the deletion.
  >>> p.header.usedSpace() == (sizeBeforeRemove - p.header.tupleSize)
  True

  """

  headerClass = SlottedPageHeader

  # Slotted page constructor.
  #
  # REIMPLEMENT this as desired.
  #
  # Constructors keyword arguments:
  # buffer       : a byte string of initial page contents.
  # pageId       : a PageId instance identifying this page.
  # header       : a SlottedPageHeader instance.
  # schema       : the schema for tuples to be stored in the page.
  # Also, any keyword arguments needed to construct a SlottedPageHeader.
  def __init__(self, **kwargs):
    buffer = kwargs.get("buffer", None)
    if buffer:
      super().__init__(**kwargs)  
    else:
      raise ValueError("No backing buffer provided to page constructor.")


  # Header constructor override for directory pages.
  def initializeHeader(self, **kwargs):
    schema = kwargs.get("schema", None)
    if schema:
      return SlottedPageHeader(buffer=self.getbuffer(), tupleSize=schema.size)
    else:
      raise ValueError("No schema provided when constructing a slotted page.")

  # Tuple iterator.
  def __iter__(self):
    self.counter = 0
    return self

  def __next__(self):
    usedSlots = self.header.usedSlots()
    
    if self.counter >= len(usedSlots):
      raise StopIteration

    slotIndex = usedSlots[self.counter]
    self.counter += 1

    return self.getTuple(TupleId(self.pageId, slotIndex))

  # Removes the tuple at the given tuple id, shifting subsequent tuples.
  def deleteTuple(self, tupleId):
    self.clearTuple(tupleId)
    self.header.resetSlot(tupleId.tupleIndex)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
