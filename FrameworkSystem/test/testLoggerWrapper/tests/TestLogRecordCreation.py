"""
Test LogRecord Creation
"""
# imports
import unittest

# sut
from DIRAC import gLogger, oldgLogger


class TestLogRecordCreation(unittest.TestCase):
  """
  Test the creation of the different log records 
  via the always, notice, ..., fatal methods.
  """

  def setUp(self):
    """
    Initialize at debug level with a sublogger and a special handler
    """
    gLogger.setLevel('debug')
    self.log = gLogger.getSubLogger('log')

  def test_00always(self):
    """
    Create Always log and test it
    """
    gLogger.always("message")
    # display Framework ALWAYS: message
    self.log.always("message")
    # display Framework/log ALWAYS: message

  def test_01notice(self):
    """
    Create Notice log and test it
    """
    gLogger.notice("message")
    # display Framework NOTICE: message
    self.log.notice("message")
    # display Framework/log NOTICE: message

  def test_02info(self):
    """
    Create Info log and test it
    """
    gLogger.info("message")
    # display Framework INFO: message
    self.log.info("message")
    # display Framework/log INFO: message

  def test_03verbose(self):
    """
    Create Verbose log and test it
    """
    gLogger.verbose("message")
    # display Framework VERBOSE: message
    self.log.verbose("message")
    # display Framework/log VERBOSE: message

  def test_04debug(self):
    """
    Create Debug log and test it
    """
    gLogger.debug("message")
    # display Framework DEBUG: message
    self.log.debug("message")
    # display Framework/log: message

  def test_05warn(self):
    """
    Create Warn log and test it
    """
    gLogger.warn("message")
    # display Framework WARN: message
    self.log.warn("message")
    # display Framework/log WARN: message

  def test_06error(self):
    """
    Create Error log and test it
    """
    gLogger.error("message")
    # display Framework ERROR: message
    self.log.error("message")
    # display Framework/log ERROR: message

  def test_07fatal(self):
    """
    Create Fatal log and test it
    """
    gLogger.fatal("message")
    # display Framework CRITICAL: message
    self.log.fatal("message")
    # display Framework/log CRITICAL: message

  def test_08exception(self):
    """
    Create Exception log and test it
    """
    try:
      badIdea = 1 / 0
      print badIdea
    except ZeroDivisionError:
      gLogger.exception('message')
      # display Framework ERROR: message
      # Traceback...
      self.log.exception('message')
      # display Framework/log ERROR: message
      # Traceback...

  def test_09WithExtrasArgs(self):
    """
    Create Always log with extra arguments and test it
    """
    self.log.always('%s.' % "message")
    # display Framework/log ALWAYS: message

  def test_10onMultipleLines(self):
    """
    Create Always log on multiple lines and test it
    """
    self.log.always('this\nis\na\nmessage\non\nmultiple\nlines.')
    # display Framework/log ALWAYS: this
    # is...

  def test_12WithVarMsg(self):
    """
    Create Always log with variable message and test it
    """
    self.log.always("mess", "age")
    # display Framework/log ALWAYS: mess age

  def test_13getName(self):
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
