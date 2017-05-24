"""
Test Levels
"""
# imports
import unittest

# sut
from DIRAC import gLogger


class TestLevels(unittest.TestCase):
  """
  Test get and set levels.
  """

  def setUp(self):
    """
    Initialize at debug level with a sublogger and a special handler
    """
    gLogger.setLevel('debug')
    self.log = gLogger.getSubLogger('log')

  def test_00setLevelGetLevel(self):
    """
    Set gLogger level to error and get it
    """
    gLogger.setLevel('error')
    self.assertEqual(gLogger.getLevel(), 'ERROR')

  def test_01setLevelCreateLog(self):
    """
    Set gLogger level to error and try to create debug and error logs
    """
    gLogger.setLevel('error')

    gLogger.debug("message")
    # does not appear
    gLogger.verbose('message')
    # does not appear
    gLogger.info('message')
    # does not appear
    gLogger.warn('message')
    # does not appear
    gLogger.notice('message')
    # does not appear
    gLogger.error('message')
    # appear
    gLogger.always('message')
    # appear
    gLogger.fatal('message')
    # appear

  def test_02setLevelGetSubLogLevel(self):
    """
    Set gLogger level to error and get its sublogger level
    """
    gLogger.setLevel('error')
    self.assertEqual(self.log.getLevel(), 'ERROR')

  def test_03setLevelCreateLogSubLog(self):
    """
    Set gLogger level to error and try to create debug and error logs and sublogs
    """
    gLogger.setLevel('error')

    gLogger.debug("message")
    self.log.debug("message")
    # does not appear
    gLogger.verbose('message')
    self.log.verbose('message')
    # does not appear
    gLogger.info('message')
    self.log.info('message')
    # does not appear
    gLogger.warn('message')
    self.log.warn('message')
    # does not appear
    gLogger.notice('message')
    self.log.notice('message')
    # does not appear
    gLogger.error('message')
    self.log.error('message')
    # appear
    gLogger.always('message')
    self.log.always('message')
    # appear
    gLogger.fatal('message')
    self.log.fatal('message')
    # appear

  def test_04setLevelSubLevelCreateLogSubLog(self):
    """
    Set gLogger level to error and log level to debug, and try to create debug and error logs and sublogs
    """
    gLogger.setLevel('error')
    self.log.setLevel('debug')
    gLogger.debug("message")
    # does not appear
    self.log.debug("message")
    # appear
    gLogger.verbose('message')
    # does not appear
    self.log.verbose('message')
    # appear
    gLogger.info('message')
    # does not appear
    self.log.info('message')
    # appear
    gLogger.warn('message')
    # does not appear
    self.log.warn('message')
    # appear
    gLogger.notice('message')
    # does not appear
    self.log.notice('message')
    # appear
    gLogger.error('message')
    # appear
    self.log.error('message')
    # appear
    gLogger.always('message')
    # appear
    self.log.always('message')
    # appear
    gLogger.fatal('message')
    # appear
    self.log.fatal('message')
    # appear

  def test_05setLevelSubLevelCreateLogSubLog2(self):
    """
    Set gLogger level to debug and log level to error, and try to create debug and error logs and sublogs
    """
    gLogger.setLevel('debug')
    self.log.setLevel('error')
    gLogger.debug("message")
    # appear
    self.log.debug("message")
    # does not appear
    gLogger.verbose('message')
    # appear
    self.log.verbose('message')
    # does not appear
    gLogger.info('message')
    # appear
    self.log.info('message')
    # does not appear
    gLogger.warn('message')
    # appear
    self.log.warn('message')
    # does not appear
    gLogger.notice('message')
    # appear
    self.log.notice('message')
    # does not appear
    gLogger.error('message')
    # appear
    self.log.error('message')
    # appear
    gLogger.always('message')
    # appear
    self.log.always('message')
    # appear
    gLogger.fatal('message')
    # appear
    self.log.fatal('message')
    # appear

  def test_06getAllLevels(self):
    self.assertEqual(gLogger.getAllPossibleLevels(), ['INFO', 'CRITICAL',
                                                      'NOTICE', 'WARNING', 'VERBOSE', 'ERROR', 'DEBUG', 'ALWAYS'])

    self.assertEqual(self.log.getAllPossibleLevels(), ['INFO', 'CRITICAL',
                                                       'NOTICE', 'WARNING', 'VERBOSE', 'ERROR', 'DEBUG', 'ALWAYS'])


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLevels)
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
