#!/usr/bin/python

import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

throughput = []
diskUsage = []

for line in sys.stdin:
  strlist = line.rstrip().split(":")
  if strlist[0] == "Throughput":
    throughput.append(float(strlist[1]))
  if strlist[0] == "Disk usage":
    diskUsage.append(float(strlist[1]));

def plotLines(data):
  x_range = np.arange(0.2, 1.2, 0.2)
  lines = plt.plot(x_range, data[0:5], 'r^-', x_range, data[5:10], 'b^-',
         x_range, data[10:15], 'g^-', x_range, data[15:20], 'k^-',
         x_range, data[20:25], 'ro-', x_range, data[25:30], 'bo-',
         x_range, data[30:35], 'go-', x_range, data[35:40], 'ko-',
         x_range, data[40:45], 'r^:', x_range, data[45:50], 'b^:',
         x_range, data[50:55], 'g^:', x_range, data[55:60], 'k^:',
         x_range, data[60:65], 'ro:', x_range, data[65:70], 'bo:',
         x_range, data[70:75], 'go:', x_range, data[75:80], 'ko:')
  return lines

def labelLines(lines):
  index = 0
  for pageType in [ 'Page' ]:
    for pageSize in [4, 32]:
      for mode in [1, 2, 3, 4]: 
        plt.setp(lines[index], label = "{}, {}KB, Mode {}".format(pageType, pageSize, mode))
        index += 1

def createPlot(data, label, fileName):
  plt.figure(1)
  plt.xlabel('Scale Factor')
  plt.ylabel(label)

  labelLines(plotLines(data))

  plt.legend(loc='upper left', fontsize = 'x-small', ncol=2, borderaxespad=0.)

  plt.savefig(fileName)

createPlot(throughput, 'Throughput', 'throughput.png')
createPlot(diskUsage, 'Disk Usage (KB)', 'disk_usage.png')
