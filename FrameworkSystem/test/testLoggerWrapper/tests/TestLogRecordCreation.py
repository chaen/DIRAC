"""
Test LogRecord Creation
"""
# imports
import unittest

# sut
from DIRAC import gLogger, oldgLogger
from DIRAC.FrameworkSystem.test.testLoggerWrapper.tests.TestLoggerWrapper import TestLoggerWrapper


def cleaningLog(log):
  """
  Remove date and space from the log string
  """
  log = log[20:]
  log = log.replace(" ", "")
  return log


class TestLogRecordCreation(TestLoggerWrapper):
  """
  Test the creation of the different log records 
  via the always, notice, ..., fatal methods.
  """

  def test_00always(self):
    """
    Create Always log and test it
    """
    gLogger.always("message")
    oldgLogger.always("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    self.log.always("message")
    self.oldlog.always("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_01notice(self):
    """
    Create Notice log and test it
    """
    gLogger.notice("message")
    oldgLogger.notice("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    self.log.notice("message")
    self.oldlog.notice("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_02info(self):
    """
    Create Info log and test it
    """
    gLogger.info("message")
    oldgLogger.info("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    self.log.info("message")
    self.oldlog.info("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_03verbose(self):
    """
    Create Verbose log and test it
    Differences between the two systems :
    - gLogger: VERBOSE
    - old gLogger: VERB
    """
    gLogger.verbose("message")

    logstring1 = cleaningLog(self.buffer.getvalue())

    self.assertEqual("UTCFrameworkVERBOSE:message\n", logstring1)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    self.log.verbose("message")

    logstring1 = cleaningLog(self.buffer.getvalue())

    self.assertEqual("UTCFramework/logVERBOSE:message\n", logstring1)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_04debug(self):
    """
    Create Debug log and test it
    """
    gLogger.debug("message")
    oldgLogger.debug("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    self.log.debug("message")
    self.oldlog.debug("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_05warn(self):
    """
    Create Warn log and test it
    """
    gLogger.warn("message")
    oldgLogger.warn("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    self.log.warn("message")
    self.oldlog.warn("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_06error(self):
    """
    Create Error log and test it
    """
    gLogger.error("message")
    oldgLogger.error("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    self.log.error("message")
    self.oldlog.error("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_07fatal(self):
    """
    Create Fatal log and test it
    """
    gLogger.fatal("message")
    oldgLogger.fatal("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    self.log.fatal("message")
    self.oldlog.fatal("message")

    logstring1 = cleaningLog(self.buffer.getvalue())
    logstring2 = cleaningLog(self.oldbuffer.getvalue())

    self.assertEqual(logstring1, logstring2)
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_08exception(self):
    """
    Create Exception log and test it
    Differences between the two systems :
    - gLogger: Traceback ...
    - old gLogger: === Exception === ...
    """
    try:
      badIdea = 1 / 0
      print badIdea
    except ZeroDivisionError:
      gLogger.exception("message")
      oldgLogger.exception("message")

      logstring1 = cleaningLog(self.buffer.getvalue())
      logstring2 = cleaningLog(self.oldbuffer.getvalue())

      self.assertNotEqual(logstring1, logstring2)
      self.buffer.truncate(0)
      self.oldbuffer.truncate(0)

      self.log.exception("message")
      self.oldlog.exception("message")

      logstring1 = cleaningLog(self.buffer.getvalue())
      logstring2 = cleaningLog(self.oldbuffer.getvalue())

      self.assertNotEqual(logstring1, logstring2)
      self.buffer.truncate(0)
      self.oldbuffer.truncate(0)

  def test_09WithExtrasArgs(self):
    """
    Create Always log with extra arguments and test it
    """
    self.log.always('%s.' % "message")
    logstring1 = cleaningLog(self.buffer.getvalue())

    self.assertEqual(logstring1, "UTCFramework/logALWAYS:message.\n")
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

    # display Framework/log ALWAYS: message

  def test_10onMultipleLines(self):
    """
    Create Always log on multiple lines and test it
    Differences between the two systems :
    - gLogger: ALWAYS: this
               ALWAYS: is
    - old gLogger: ALWAYS: this
                   is
    """
    self.log.always('this\nis\na\nmessage\non\nmultiple\nlines.')
    logstring1 = cleaningLog(self.buffer.getvalue())

    self.assertEqual(logstring1, "UTCFramework/logALWAYS:this\nis\na\nmessage\non\nmultiple\nlines.\n")
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_11WithVarMsg(self):
    """
    Create Always log with variable message and test it
    """
    self.log.always("mess", "age")
    logstring1 = cleaningLog(self.buffer.getvalue())

    self.assertEqual(logstring1, "UTCFramework/logALWAYS:message\n")
    self.buffer.truncate(0)
    self.oldbuffer.truncate(0)

  def test_12getName(self):
    """
    Get the system name of the log record
    """
    self.assertEqual(gLogger.getName(), oldgLogger.getName())

    log = gLogger.getSubLogger('log')
    oldLog = oldgLogger.getSubLogger('log')

    self.assertEqual(log.getName(), oldLog.getName())

  def test_13getSubName(self):
    """
    Get the log name of the log record
    """
    self.assertEqual(gLogger.getSubName(), "")

    log = gLogger.getSubLogger('log')
    oldLog = oldgLogger.getSubLogger('log')

    self.assertEqual(log.getSubName(), oldLog.getSubName())

    sublog = log.getSubLogger('sublog')
    suboldLog = oldLog.getSubLogger('sublog')

    self.assertEqual(sublog.getSubName(), 'log.sublog')
    self.assertEqual(suboldLog.getSubName(), 'sublog')


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLogRecordCreation)
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
