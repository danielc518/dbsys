import sys
import os

from Utils.WorkloadGenerator import WorkloadGenerator
from Storage.File import StorageFile
from Storage.SlottedPage import SlottedPage
from Storage.Page import Page

datadir = './data/'

def diskUsage():
  diskUsage = 0
  for file in os.listdir(datadir):
    if file.endswith('.rel'):
      diskUsage += os.path.getsize(os.path.join(datadir, file))
  return diskUsage / 1024

def runWorkload():
  for pageSize in [4096, 32768]:
    for mode in [1, 2, 3, 4]:
      for scale in [0.2, 0.4, 0.6, 0.8, 1.0]:
        WorkloadGenerator().runWorkload(datadir, scale, pageSize, mode)
        print("Disk usage: {}".format(diskUsage()))

datadir = '/home/cs416/datasets/tpch-sf0.1'

StorageFile.defaultPageClass = Page
runWorkload()
