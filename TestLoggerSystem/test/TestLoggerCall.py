# imports
import unittest
import time
import logging
import sys
# sut
from DIRAC import gLogger
from DIRAC.TestLoggerSystem.test.TestLogger import TestLogger


class TestLoggerCall(TestLogger):

  def test_always(self):
    gLogger.always("gLoggeralways")  
    logging.always("Loggingalways")

  def test_notice(self):
    gLogger.notice("gLoggernotice")
    logging.notice("Loggingnotice")

  def test_info(self):
    gLogger.info("gLoggerinfo")
    logging.info("Logginginfo")

  def test_verbose(self):
    gLogger.verbose("gLoggerverbose")
    logging.verbose("Loggingverbose")

  def test_debug(self):
    gLogger.debug("gLoggerdebug")
    logging.debug("Loggingdebug")

  def test_warn(self):
    gLogger.warn("gLoggerwarn")
    logging.warn("Loggingwarn")

  def test_error(self):
    gLogger.error("gLoggererror")
    logging.error("Loggingerror")

  def test_fatal(self):
    gLogger.fatal("gLoggerfatal")
    logging.fatal("Loggingfatal")

  def test_exception(self):
    try:
      a = 1 / 0
    except Exception:
      gLogger.exception('gLoggerexception')

    try:
      a = 1 / 0
    except Exception:
      # this does not display as expected
      logging.exception("Loggingexception", exc_info=True)


class TestSubLoggerCall(TestLogger):

  def test_always(self):
    log = gLogger.getSubLogger('log')
    log.always("gLoggeralways")

    log = logging.getLogger('log')
    log.always("Loggingalways")

  def test_notice(self):
    log = gLogger.getSubLogger('log')
    log.notice("gLoggernotice")

    log = logging.getLogger('log')
    log.notice("Loggingnotice")

  def test_info(self):
    log = gLogger.getSubLogger('log')
    log.info("gLoggerinfo")

    log = logging.getLogger('log')
    log.info("Logginginfo")

  def test_verbose(self):
    log = gLogger.getSubLogger('log')
    log.verbose("gLoggerverbose")

    log = logging.getLogger('log')
    log.verbose("Loggingverbose")

  def test_debug(self):
    log = gLogger.getSubLogger('log')
    log.debug("gLoggerdebug")

    log = logging.getLogger('log')
    log.debug("Loggingdebug")

  def test_warn(self):
    log = gLogger.getSubLogger('log')
    log.warn("gLoggerwarn")

    log = logging.getLogger('log')
    log.warn("Loggingwarn")

  def test_error(self):
    log = gLogger.getSubLogger('log')
    log.error("gLoggererror")

    log = logging.getLogger('log')
    log.error("Loggingerror")

  def test_fatal(self):
    log = gLogger.getSubLogger('log')
    log.fatal("gLoggerfatal")

    log = logging.getLogger('log')
    log.fatal("Loggingfatal")

  def test_exception(self):
    log = gLogger.getSubLogger('log')
    try:
      a = 1 / 0
    except Exception:
      log.exception('gLoggerexception')

    log = logging.getLogger('log')
    try:
      a = 1 / 0
    except Exception:
      # this does not display as expected
      log.exception("Loggingexception", exc_info=True)


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLogger)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestLoggerCall))
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestSubLoggerCall))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)