"""
Test SubLogger
"""
# imports
import unittest

# sut
from DIRAC import gLogger, oldgLogger


class TestSubLogger(unittest.TestCase):
  """
  Test the creation of subloggers and their properties
  """

  def setUp(self):
    """
    Initialize at debug level with a sublogger and a special handler
    """
    gLogger.setLevel('debug')

  def test_00getSubLogger(self):
    """
    Create a sublogger and create a log record
    """
    log = gLogger.getSubLogger('log')
    log.always('message')

    # display Framework/log

  def test_01getSubSubLogger(self):
    """
    Create a subsublogger and create a logrecord
    """
    log = gLogger.getSubLogger('log')
    sublog = log.getSubLogger('sublog')
    sublog.always('message')

    # display Framework/log/sublog

  def test_02getSubSubSubLogger(self):
    """
    Create a subsubsublogger and create a logrecord
    """
    log = gLogger.getSubLogger('log')
    sublog = log.getSubLogger('sublog')
    subsublog = sublog.getSubLogger('subsublog')
    subsublog.always('message')
    # display Framework/log/sublog/subsublog

  def test_03tryToGetSubSubSubLoggerRoot(self):
    """
    Try to get the root logger in a subsubsublogger and create a logrecord
    """
    log = gLogger.getSubLogger('log')
    sublog = log.getSubLogger('sublog')
    subsublog = sublog.getSubLogger('')
    subsubsublog = subsublog.getSubLogger('log')
    subsubsublog.always('message')
    # display Framework/log/sublog//log

  def test_04tryToGetSubLoggerRoot(self):
    """
    Try to get the root logger in a sublogger and create a logrecord
    """
    log = gLogger.getSubLogger('')
    sublog = log.getSubLogger('sublog')
    sublog.always('message')
    # display Framework//sublog


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSubLogger)
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
