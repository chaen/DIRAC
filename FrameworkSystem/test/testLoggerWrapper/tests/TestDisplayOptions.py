"""
Test SubLogger
"""
# imports
import unittest

# sut
from DIRAC import gLogger, oldgLogger


class TestDisplayOptions(unittest.TestCase):
  """
  Test the creation of subloggers and their properties
  """

  def setUp(self):
    """
    Initialize at debug level with a sublogger and a special handler
    """
    gLogger.setLevel('debug')

  def test_00setShowHeaders(self):
    """
    Set the headers
    """
    gLogger.showHeaders(False)
    gLogger.verbose('message')
    # display message

    gLogger.showHeaders(True)
    gLogger.verbose('message')
    # display Framework/log ...

  def test_01setShowThreadIDs(self):
    """
    Set the thread ID
    """
    gLogger.showThreadIDs(False)
    gLogger.verbose('message')
    # display Framework/log ...

    gLogger.showThreadIDs(True)
    gLogger.verbose('message')
    # display Framework/log[125486448] ...

  def test_02setShowThreadIDsHeaders(self):
    """
    Create a subsubsublogger and create a logrecord
    """
    gLogger.showHeaders(False)
    gLogger.showThreadIDs(False)
    gLogger.verbose('message')
    # display message

    gLogger.showHeaders(False)
    gLogger.showThreadIDs(True)
    gLogger.verbose('message')
    # display message

    gLogger.showHeaders(True)
    gLogger.showThreadIDs(False)
    gLogger.verbose('message')
    # display Framework/log ...

    gLogger.showHeaders(True)
    gLogger.showThreadIDs(True)
    gLogger.verbose('message')
    # display Framework/log[125486448] ...


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSubLogger)
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
