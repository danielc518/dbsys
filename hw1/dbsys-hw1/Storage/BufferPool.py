import io, math, struct

from collections import OrderedDict
from struct      import Struct

from Catalog.Identifiers import PageId, FileId, TupleId
from Catalog.Schema      import DBSchema

import Storage.FileManager

class BufferPool:
  """
  A buffer pool implementation.

  Since the buffer pool is a cache, we do not provide any serialization methods.

  >>> schema = DBSchema('employee', [('id', 'int'), ('age', 'int')])
  >>> bp = BufferPool()
  >>> fm = Storage.FileManager.FileManager(bufferPool=bp)
  >>> bp.setFileManager(fm)

  # Check initial buffer pool size
  >>> len(bp.pool.getbuffer()) == bp.poolSize
  True

  """

  # Default to a 10 MB buffer pool.
  defaultPoolSize = 10 * (1 << 20)

  # Buffer pool constructor.
  #
  # REIMPLEMENT this as desired.
  #
  # Constructors keyword arguments, with defaults if not present:
  # pageSize       : the page size to be used with this buffer pool
  # poolSize       : the size of the buffer pool
  def __init__(self, **kwargs):
    self.pageSize     = kwargs.get("pageSize", io.DEFAULT_BUFFER_SIZE)
    self.poolSize     = kwargs.get("poolSize", BufferPool.defaultPoolSize)
    self.pool         = io.BytesIO(b'\x00' * self.poolSize)
    self.fileMgr      = None

    ####################################################################################
    # DESIGN QUESTION: what other data structures do we need to keep in the buffer pool?
    self.freeList     = list()
    self.pageDict     = OrderedDict()


  def setFileManager(self, fileMgr):
    self.fileMgr = fileMgr

  # Basic statistics

  def numPages(self):
    return math.floor(self.poolSize / self.pageSize)

  def numFreePages(self):
    raise len(self.freeList)

  def size(self):
    return self.poolSize

  def freeSpace(self):
    return self.numFreePages() * self.pageSize

  def usedSpace(self):
    return self.size() - self.freeSpace()


  # Buffer pool operations

  def hasPage(self, pageId):
    return pageId in self.pageDict
  
  def getPage(self, pageId):
    if not self.hasPage(pageId):
      if len(self.freeList) == 0:
        self.evictPage()

      page = self.readFreePage(pageId)
    
    self.pageDict.move_to_end(pageId)
    (page, _) = self.pageDict[pageId]
    
    return page

  # Removes a page from the page map, returning it to the free 
  # page list without flushing the page to the disk.
  def discardPage(self, pageId):
    if self.hasPage(pageId):
      (page, offset) = self.pageDict[pageId]
      self.pageDict.pop(pageId, None)
      self.freeList.append(offset)
      return page
    else:
      return None

  def flushPage(self, pageId):
    page = self.discardPage(pageId)
    if page is not None:
      self.fileMgr.writePage(page)

  # Evict using LRU policy. 
  # We implement LRU through the use of an OrderedDict, and by moving pages
  # to the end of the ordering every time it is accessed through getPage()
  def evictPage(self):
    (page, offset) = self.pageDict.pop(0)
    self.flushPage(page.pageId)

  def readFreePage(self, pageId):
    offset = self.freeList.pop()
    buffer = self.pool.getbuffer()[offset:offset+self.pageSize]
    page   = self.fileMgr.readPage(pageId, buffer)
    self.pageDict[pageId] = (page, offset)
    return page

if __name__ == "__main__":
    import doctest
    doctest.testmod()
