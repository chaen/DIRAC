"""
Test SubLogger
"""

__RCSID__ = "$Id$"

import unittest

from DIRAC.FrameworkSystem.private.standardLogging.test.TestLoggingBase import Test_Logging, gLogger


class Test_SubLogger(Test_Logging):
  """
  Test the creation of subloggers and their properties
  """

  def test_00getSubLogger(self):
    """
    Create a sublogger and create a log record
    """
    log = gLogger.getSubLogger('log')
    log.always('message')

    self.assertIn(" Framework/log ", self.buffer.getvalue())
    self.buffer.truncate(0)

  def test_01getSubSubLogger(self):
    """
    Create a subsublogger and create a logrecord
    """
    log = gLogger.getSubLogger('log')
    sublog = log.getSubLogger('sublog')
    sublog.always('message')

    self.assertIn(" Framework/log/sublog ", self.buffer.getvalue())
    self.buffer.truncate(0)

  def test_02getSubSubSubLogger(self):
    """
    Create a subsubsublogger and create a logrecord
    """
    log = gLogger.getSubLogger('log')
    sublog = log.getSubLogger('sublog')
    subsublog = sublog.getSubLogger('subsublog')
    subsublog.always('message')

    self.assertIn(" Framework/log/sublog/subsublog ", self.buffer.getvalue())
    self.buffer.truncate(0)

  def test_03changeSubLoggerLevel(self):
    """
    Create subloggers, and check that the changes of log levels are effective
    """

    # log has level DEBUG, sublog has level INFO
    # ERROR messages should come from both
    # DEBUG message should come from log only

    log = gLogger.getSubLogger('log')

    sublog = log.getSubLogger('sublog')
    sublog.setLevel('INFO')

    log.error("changeLevel")
    self.assertIn(" Framework/log ERROR: changeLevel", self.buffer.getvalue())
    sublog.error("changeLevel")
    self.assertIn(" Framework/log/sublog ERROR: changeLevel", self.buffer.getvalue())

    log.debug("changeLevel")
    self.assertIn(" Framework/log DEBUG: changeLevel", self.buffer.getvalue())
    sublog.debug("changeLevel")
    self.assertNotIn(" Framework/log/sublog DEBUG: changeLevel", self.buffer.getvalue())

    self.buffer.truncate(0)


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test_SubLogger)
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
