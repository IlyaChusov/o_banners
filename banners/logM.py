import time 
import os

def logM(message):
   file = open(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/utils/logs', 'a')
   if message == None:
      message = 'none'
   file.write('\n' + time.strftime("%Y-%m-%d_%H:%M:%S") + '\n' + message + '\n')
   file.close()
