# imports
import unittest
import time
import logging
import sys
# sut
from DIRAC import gLogger


class TestLogger(unittest.TestCase):

  def setUp(self):
    # basic configuration of root logger
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s UTC %(name)s  %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # to do : path of the subLogger
    logging.getLogger().name = 'Framework'
    logger = logging.getLogger()

    # addlevel
    levelDict = {10: "ALWAYS",
                 20: "NOTICE",
                 30: "INFO",
                 40: "VERBOSE",
                 50: "DEBUG",
                 60: "WARN",
                 70: "ERROR",
                 80: "EXCEPTION",
                 90: "FATAL"}

    for level in levelDict:
      logging.addLevelName(level, levelDict[level])
      setattr(logging, levelDict[level], level)
      setattr(logging.Logger, levelDict[level].lower(),
              (lambda level: lambda inst, msg, *args, **kwargs: inst.log(level, msg, *args, **kwargs))(level))
      setattr(logging, levelDict[level].lower(), (lambda level: lambda msg,
                                                  *args, **kwargs: logging.log(level, msg, *args, **kwargs))(level))

  def tearDown(self):
    pass


class TestLoggerCall(TestLogger):

  def test_always(self):
    gLogger.always("always")
    logging.always("always")

  def test_notice(self):
    gLogger.notice("notice")
    logging.notice("notice")

  def test_info(self):
    gLogger.info("info")
    logging.info("info")

  def test_verbose(self):
    gLogger.verbose("verbose")
    logging.verbose("verbose")

  def test_debug(self):
    gLogger.debug("debug")
    logging.debug("debug")

  def test_warn(self):
    gLogger.warn("warn")
    logging.warn("warn")

  def test_error(self):
    gLogger.error("error")
    logging.error("error")

  def test_fatal(self):
    gLogger.fatal("fatal")
    logging.fatal("fatal")

  def test_exception(self):
    try:
      a = 1 / 0
    except Exception:
      gLogger.exception('exception')

    try:
      a = 1 / 0
    except Exception:
      # this does not display as expected
      logging.exception("exception", exc_info=True)


class TestSubLoggerCall(TestLogger):

  def test_always(self):
    log = gLogger.getSubLogger('log')
    log.always("always")

    log = logging.getLogger('log')
    log.always("always")

  def test_notice(self):
    log = gLogger.getSubLogger('log')
    log.notice("notice")

    log = logging.getLogger('log')
    log.notice("notice")

  def test_info(self):
    log = gLogger.getSubLogger('log')
    log.info("info")

    log = logging.getLogger('log')
    log.info("info")

  def test_verbose(self):
    log = gLogger.getSubLogger('log')
    log.verbose("verbose")

    log = logging.getLogger('log')
    log.verbose("verbose")

  def test_debug(self):
    log = gLogger.getSubLogger('log')
    log.debug("debug")

    log = logging.getLogger('log')
    log.debug("debug")

  def test_warn(self):
    log = gLogger.getSubLogger('log')
    log.warn("warn")

    log = logging.getLogger('log')
    log.warn("warn")

  def test_error(self):
    log = gLogger.getSubLogger('log')
    log.error("error")

    log = logging.getLogger('log')
    log.error("error")

  def test_fatal(self):
    log = gLogger.getSubLogger('log')
    log.fatal("fatal")

    log = logging.getLogger('log')
    log.fatal("fatal")

  def test_exception(self):
    log = gLogger.getSubLogger('log')
    try:
      a = 1 / 0
    except Exception:
      log.exception('exception')

    log = logging.getLogger('log')
    try:
      a = 1 / 0
    except Exception:
      # this does not display as expected
      log.exception("exception", exc_info=True)


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLogger)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestLoggerCall))
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestSubLoggerCall))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
