"""
System Logging Handler
"""

__RCSID__ = "$Id$"

import logging
import Queue
import threading

from DIRAC.Core.Utilities import Network



class RemoteHandler(logging.Handler, threading.Thread):
  """
  Equivalent class to the old remote backend:
  - emit() sends to a LoggingSystemClient
  """

  def __init__(self, sleepTime, interactive, site):
    logging.Handler.__init__(self)
    threading.Thread.__init__(self)
    self.__logQueue = Queue.Queue()

    self.__sleepTime = sleepTime
    self.__interactive = interactive
    self.__site = site
    self.__transactions = []
    self.__hostname = Network.getFQDN()
    self.__alive = True
    self.__maxBundledLogs = 20

    self.setDaemon(True)
    self.start()

  def emit(self, record):
    """
    Add the record to the queue.
    :params record: log record object
    """
    self.__logQueue.put(record)

  def run(self):
    import time
    while self.__alive:
      self.__bundleLogs()
      time.sleep(float(self.__sleepTime))

  def __bundleLogs(self):
    """
    Prepare the log to the sending
    """
    while not self.__logQueue.empty():
      bundle = []
      while (len(bundle) < self.__maxBundledLogs) and (not self.__logQueue.empty()):
        record = self.__logQueue.get()
        self.format(record)
        logTuple = (record.componentname, record.levelname, record.created, record.getMessage(), '',
                    record.pathname + ":" + str(record.lineno), record.name)
        bundle.append(logTuple)

      if bundle:
        self.__sendLogToServer(bundle)

    if self.__transactions:
      self.__sendLogToServer()

  def __sendLogToServer(self, logBundle=None):
    """
    Send log to the SystemLogging service.
    :params logBundle: list of logs ready to be send to the service
    """
    from DIRAC.Core.DISET.RPCClient import RPCClient
    if logBundle:
      self.__transactions.append(logBundle)
    transactionsLength = len(self.__transactions)
    if transactionsLength > 100:
      del self.__transactions[:transactionsLength - 100]
      transactionsLength = 100

    try:
      oSock = RPCClient("Framework/SystemLogging")
    except Exception:
      return False

    while transactionsLength:
      result = oSock.addMessages(self.__transactions[0], self.__site, self.__hostname)
      if result['OK']:
        transactionsLength = transactionsLength - 1
        self.__transactions.pop(0)
      else:
        return False
    return True
