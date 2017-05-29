"""
Test Display Options
"""
# imports
import unittest
import logging
import sys
from StringIO import StringIO

# sut
from DIRAC import gLogger, oldgLogger


def cleaningLog(log):
  """
  Remove date and space from the log string
  """
  log = log[20:]
  log = log.replace(" ", "")
  return log


class TestDisplayOptions(unittest.TestCase):
  """
  Test the creation of subloggers and their properties
  """

  def setUp(self):
    """
    Initialize at debug level with a sublogger and a special handler
    """
    gLogger.setLevel('debug')
    self.log = gLogger.getSubLogger('log')
    self.buffer = StringIO()

    oldgLogger.setLevel('debug')
    self.oldlog = oldgLogger.getSubLogger('log')
    self.oldbuffer = StringIO()
    sys.stdout = self.oldbuffer

    gLogger.showHeaders(True)
    gLogger.showThreadIDs(False)

    oldgLogger.showHeaders(True)
    oldgLogger.showThreadIDs(False)

    # modify the output to capture the log into a buffer
    if logging.getLogger().handlers:
      logging.getLogger().handlers[0].stream = self.buffer

  def test_00setShowHeaders(self):
    """
    Set the headers
    """
    gLogger.showHeaders(False)
    gLogger.notice('message')

    oldgLogger.showHeaders(False)
    oldgLogger.notice('message')

    self.assertEqual(self.buffer.getvalue().replace(" ", ""), self.oldbuffer.getvalue().replace(" ", ""))
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    gLogger.showHeaders(True)
    gLogger.notice('message')

    oldgLogger.showHeaders(True)
    oldgLogger.notice('message')

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_01setShowThreadIDs(self):
    """
    Set the thread ID
    Differences between the two systems :
    - gLogger: threadID [1254868214]
    - old gLogger: threadID [GEko]
    """
    gLogger.showThreadIDs(False)
    gLogger.notice('message')

    oldgLogger.showThreadIDs(False)
    oldgLogger.notice('message')

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    gLogger.showThreadIDs(True)
    gLogger.notice('message')

    oldgLogger.showThreadIDs(True)
    oldgLogger.notice('message')

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertNotEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_02setShowThreadIDsHeaders(self):
    """
    Create a subsubsublogger and create a logrecord
    """
    gLogger.showHeaders(False)
    gLogger.showThreadIDs(False)
    gLogger.notice('message')

    oldgLogger.showHeaders(False)
    oldgLogger.showThreadIDs(False)
    oldgLogger.notice('message')

    self.assertEqual(self.buffer.getvalue().replace(" ", ""), self.oldbuffer.getvalue().replace(" ", ""))
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    gLogger.showHeaders(False)
    gLogger.showThreadIDs(True)
    gLogger.notice('message')

    oldgLogger.showHeaders(False)
    oldgLogger.showThreadIDs(True)
    oldgLogger.notice('message')

    self.assertEqual(self.buffer.getvalue().replace(" ", ""), self.oldbuffer.getvalue().replace(" ", ""))
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    gLogger.showHeaders(True)
    gLogger.showThreadIDs(False)
    gLogger.notice('message')

    oldgLogger.showHeaders(True)
    oldgLogger.showThreadIDs(False)
    oldgLogger.notice('message')

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    gLogger.showHeaders(True)
    gLogger.showThreadIDs(True)
    gLogger.notice('message')

    oldgLogger.showHeaders(True)
    oldgLogger.showThreadIDs(True)
    oldgLogger.notice('message')

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertNotEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestDisplayOptions)
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
