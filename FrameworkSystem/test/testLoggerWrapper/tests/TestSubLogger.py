"""
Test SubLogger
"""

__RCSID__ = "$Id$"

# imports
import unittest

# sut
from DIRAC import gLogger
from DIRAC.FrameworkSystem.test.testLoggerWrapper.tests.TestLoggerWrapper import TestLoggerWrapper


class TestSubLogger(TestLoggerWrapper):
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
    self.oldbuffer.truncate(0)

  def test_01getSubSubLogger(self):
    """
    Create a subsublogger and create a logrecord
    """
    log = gLogger.getSubLogger('log')
    sublog = log.getSubLogger('sublog')
    sublog.always('message')

    self.assertIn(" Framework/log/sublog ", self.buffer.getvalue())
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

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
    self.oldbuffer.truncate(0)

  #def test_03subsubLoggerRegisterBackends(self):
  #  """
  #  Register a backend for a subsublogger
  #  """
  #  log = gLogger.getSubLogger('log')
  #  sublog = log.getSubLogger('sublog')
  #  subsublog = sublog.getSubLogger('subsublog')
  #  subsublog.registerBackends(['stdout'])
  #  subsublog.always('message')
#
  #  self.assertEqual(" Framework/log/sublog/subsublog ", self.buffer.getvalue())
  #  self.buffer.truncate(0)
  #  self.oldbuffer.truncate(0)


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSubLogger)
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
