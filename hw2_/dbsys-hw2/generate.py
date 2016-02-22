import subprocess
import shutil

from Database                import Database
from Utils.WorkloadGenerator import WorkloadGenerator
from Storage.File            import StorageFile
from Storage.Page            import Page
from Storage.SlottedPage     import SlottedPage
from Storage.FileManager     import FileManager

if __name__ == "__main__":
  csvDir = '/home/cs416/datasets/tpch-sf0.1/'
  wg = WorkloadGenerator()
  db = Database()
  wg.createRelations(db)
  wg.loadDataset(db, csvDir, 1.0)
