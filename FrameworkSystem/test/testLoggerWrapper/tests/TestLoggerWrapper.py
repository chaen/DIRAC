"""
Test Levels
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

class TestLoggerWrapper(unittest.TestCase):
  """
  Test get and set levels.
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

    # modify the output to capture the log into a buffer
    if logging.getLogger().handlers:
      logging.getLogger().handlers[0].stream = self.buffer
    logging.getLogger('root.log').setLevel(logging.NOTSET)


if __name__ == '__main__':
  from DIRAC.FrameworkSystem.test.testLoggerWrapper.tests.TestDisplayOptions import TestDisplayOptions
  from DIRAC.FrameworkSystem.test.testLoggerWrapper.tests.TestLevels import TestLevels
  from DIRAC.FrameworkSystem.test.testLoggerWrapper.tests.TestLogRecordCreation import TestLogRecordCreation
  from DIRAC.FrameworkSystem.test.testLoggerWrapper.tests.TestSubLogger import TestSubLogger

  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLoggerWrapper)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestDisplayOptions))
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestLevels))
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestLogRecordCreation))
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestSubLogger))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
