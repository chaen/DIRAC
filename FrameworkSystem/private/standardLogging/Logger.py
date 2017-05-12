import logging

"""
Logger class.
Second new logging solution :
Advantages  :  Minimise modification
Drawbacks   :  Maximize maintenability
"""

class Logger(logging.getLoggerClass()):

  def __init__(self, name):
    Logger.__init__(name)

  

