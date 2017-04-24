# imports
import unittest
import time
import logging
import sys
# sut
from DIRAC import gLogger
from DIRAC.TestLoggerSystem.test.TestLogger import TestLogger
from DIRAC.TestLoggerSystem.Client.ClientB import ClientB
from DIRAC.TestLoggerSystem.Client.ClientA import ClientA

from DIRAC.TestLoggerSystem.private.logging.LoggingConfiguration import LoggingConfiguration


class TestLoggerCallFromClient(TestLogger):

  def setUp(self):
    super(TestLoggerCallFromClient, self).setUp()
 
    self.clientA = ClientA()
    self.clientB = ClientB()

  def tearDown(self):
    super(TestLoggerCallFromClient, self).tearDown()


  def test_clientA(self):
    self.clientA.logSomething()
    self.clientA.logSomethingNew()

  def test_clientB(self):
    self.clientB.logSomething()
    self.clientB.logSomethingNew()

  def test_clientBFromClientA(self):
    self.clientA.logSomethingFromB()
    self.clientA.logSomethingFromBNew()

  def test_atomHandlerFromClientA(self):
    self.clientA.addStuff("test")

  def test_clientAWithShowHeadersFalse(self):
    gLogger.showHeaders(False)
    self.clientA.logSomething()
    
    LoggingConfiguration.showHeaders(False)
    self.clientA.logSomethingNew()

  def test_clientAWithShowHeadersTrue(self):
    gLogger.showHeaders(True)
    self.clientA.logSomething()
    
    LoggingConfiguration.showHeaders(True)
    self.clientA.logSomethingNew()

  def test_clientAWithShowThreadIDFalse(self):
    gLogger.showThreadIDs(False)
    self.clientA.logSomething()
    
    LoggingConfiguration.showThreadIDs(False)
    self.clientA.logSomethingNew()

  def test_clientAWithShowThreadIDTrue(self):
    gLogger.showThreadIDs(True)
    self.clientA.logSomething()
    
    LoggingConfiguration.showThreadIDs(True)
    self.clientA.logSomethingNew()

  def test_clientAWithShowThreadIDFalseShowHeaderTrue(self):
    gLogger.showHeaders(True)
    gLogger.showThreadIDs(False)
    self.clientA.logSomething()
    
    LoggingConfiguration.showHeaders(True)
    LoggingConfiguration.showThreadIDs(False)
    self.clientA.logSomethingNew()

  def test_clientAWithShowThreadIDFalseShowHeaderFalse(self):
    gLogger.showHeaders(False)
    gLogger.showThreadIDs(False)
    self.clientA.logSomething()
    
    LoggingConfiguration.showHeaders(False)
    LoggingConfiguration.showThreadIDs(False)
    self.clientA.logSomethingNew()

  def test_clientAWithShowThreadIDTrueShowHeaderTrue(self):
    gLogger.showHeaders(True)
    gLogger.showThreadIDs(True)
    self.clientA.logSomething()
    
    LoggingConfiguration.showHeaders(True)
    LoggingConfiguration.showThreadIDs(True)
    self.clientA.logSomethingNew()

  def test_clientAWithShowThreadIDTrueShowHeaderFalse(self):
    gLogger.showHeaders(False)
    gLogger.showThreadIDs(True)
    self.clientA.logSomething()
    
    LoggingConfiguration.showHeaders(False)
    LoggingConfiguration.showThreadIDs(True)
    self.clientA.logSomethingNew()





if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLogger)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestLoggerCallFromClient))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)