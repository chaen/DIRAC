"""
Test Display Options
"""
# imports
import unittest

# sut
from DIRAC import gLogger, oldgLogger
from DIRAC.FrameworkSystem.test.testLoggerWrapper.tests.TestLoggerWrapper import TestLoggerWrapper, cleaningLog


class TestDisplayOptions(TestLoggerWrapper):
  """
  Test the creation of subloggers and their properties
  """

  def tearDown(self):
    gLogger.showHeaders(True)
    gLogger.showThreadIDs(False)

    oldgLogger.showHeaders(True)
    oldgLogger.showThreadIDs(False)

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
