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
    
    gLogger.debug("gLoggerdebug")  

  def test_loggerSetLevel1(self):
    gLogger.setLevel('debug')

    gLog = gLogger.getSubLogger('log')

    gLog.setLevel('always')

    gLogger.debug("gLoggerdebug")  

    gLog.always("appears")
    gLog.notice('appears')

  def test_loggerSetLevel2(self):
    gLogger.setLevel('always')

    gLog = gLogger.getSubLogger('log')

    gLog.setLevel('debug')

    print gLog.getLevel()
    
    gLogger.always("appears")  

    gLog.debug("not appears")
    gLog.notice('not appears')

  def test_loggerSetLevel3(self):
    gLogger.setLevel('debug')

    gLog = gLogger.getSubLogger('log', False)

    gLog.setLevel('always')

    gLogger.debug("appears")  

    gLog.always("appears")
    gLog.notice('appears')

  def test_loggerSetLevel4(self):
    gLogger.setLevel('always')

    gLog = gLogger.getSubLogger('log', False)

    gLog.setLevel('debug')

    gLogger.always("gLoggeralways")  

    gLog.debug("not appears")
    gLog.notice('not appears')

  def test_loggerSetLevel5(self):
    gLogger.setLevel('always')
  
    gLog = gLogger.getSubLogger('log')

    gLog.setLevel('debug')

    gLogLog = gLog.getSubLogger('loglog')
    gLogLog.setLevel('notice')

    gLogger.always("appears")  

    gLog.debug("not appears")
    gLog.notice('not appears')

    gLogLog.notice("not appears")

  def test_loggerSetLevel6(self):
    gLogger.setLevel('debug')

    gLog = gLogger.getSubLogger('log', False)

    gLog.setLevel('always')

    gLogLog = gLog.getSubLogger('loglog')
    gLogLog.setLevel('notice')

    gLogger.debug("appears")  

    gLog.always("appears")
    gLog.notice('appears')

    gLogLog.notice('appears')

    




if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLogger)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestLevel))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)