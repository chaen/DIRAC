# imports
import unittest
import time
import logging
import sys
# sut
from DIRAC import gLogger
from DIRAC.TestLoggerSystem.test.TestLogger import TestLogger

class TestLevel(TestLogger):

  def test_loggerSetLevel0(self):
    gLogger.setLevel('debug')
    logging.getLogger().setLevel(logging.DEBUG)

    gLogger.debug("gLoggerdebug")  
    logging.debug("Loggingdebug")

  def test_loggerSetLevel1(self):
    gLogger.setLevel('debug')
    logging.getLogger().setLevel(logging.DEBUG)

    gLog = gLogger.getSubLogger('log')
    log = logging.getLogger('log')

    gLog.setLevel('always')
    log.setLevel(logging.ALWAYS)

    gLogger.debug("gLoggerdebug")  
    logging.debug("Loggingaldebug")

    gLog.always("always")
    log.always("always")
    gLog.notice('notice')
    log.notice('notice')

  def test_loggerSetLevel2(self):
    gLogger.setLevel('always')
    logging.getLogger().setLevel(logging.ALWAYS)

    gLog = gLogger.getSubLogger('log')
    log = logging.getLogger('log')

    gLog.setLevel('debug')
    log.setLevel(logging.DEBUG)

    print gLog.getLevel()
    print log.getEffectiveLevel()

    gLogger.always("gLoggeralways")  
    logging.always("Loggingalways")

    gLog.debug("debug")
    log.debug("debug")
    gLog.notice('notice')
    log.notice('notice')

  def test_loggerSetLevel3(self):
    gLogger.setLevel('debug')
    logging.getLogger().setLevel(logging.DEBUG)

    gLog = gLogger.getSubLogger('log', False)
    log = logging.getLogger('log')

    gLog.setLevel('always')
    log.setLevel(logging.ALWAYS)

    gLogger.debug("gLoggerdebug")  
    logging.debug("Loggingaldebug")

    gLog.always("always")
    log.always("always")
    gLog.notice('notice')
    log.notice('notice')

  def test_loggerSetLevel4(self):
    gLogger.setLevel('always')
    logging.getLogger().setLevel(logging.ALWAYS)

    gLog = gLogger.getSubLogger('log', False)
    log = logging.getLogger('log')

    gLog.setLevel('debug')
    log.setLevel(logging.DEBUG)

    gLogger.always("gLoggeralways")  
    logging.always("Loggingalways")

    gLog.debug("debug")
    log.debug("debug")
    gLog.notice('notice')
    log.notice('notice')

  def test_loggerSetLevel5(self):
    gLogger.setLevel('always')
    logging.getLogger().setLevel(logging.ALWAYS)

    gLog = gLogger.getSubLogger('log')
    log = logging.getLogger('log')

    gLog.setLevel('debug')
    log.setLevel(logging.DEBUG)

    gLogLog = gLog.getSubLogger('loglog')
    gLogLog.setLevel('notice')

    gLogger.always("gLoggeralways")  
    logging.always("Loggingalways")

    gLog.debug("debug")
    log.debug("debug")
    gLog.notice('notice')
    log.notice('notice')

    gLogLog.notice("notice")

  def test_loggerSetLevel6(self):
    gLogger.setLevel('debug')
    logging.getLogger().setLevel(logging.DEBUG)

    gLog = gLogger.getSubLogger('log', False)
    log = logging.getLogger('log')

    gLog.setLevel('always')
    log.setLevel(logging.ALWAYS)

    gLogLog = gLog.getSubLogger('loglog')
    gLogLog.setLevel('notice')

    gLogger.debug("gLoggerdebug")  
    logging.debug("Loggingaldebug")

    gLog.always("always")
    log.always("always")
    gLog.notice('notice')
    log.notice('notice')

    gLogLog.notice('notice')




if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLogger)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestLevel))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)