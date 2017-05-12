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

class TestLoggerCallFromClient(TestLogger):

  def setUp(self):
    super(TestLoggerCallFromClient, self).setUp()
 
    self.clientA = ClientA()
    self.clientB = ClientB()

  def tearDown(self):
    super(TestLoggerCallFromClient, self).tearDown()


  def test_clientA(self):
    self.clientA.logSomething()

  def test_clientB(self):
    self.clientB.logSomething()

  def test_clientBFromClientA(self):
    self.clientA.logSomethingFromB()

  def test_atomHandlerFromClientA(self):
    self.clientA.addStuff("test")

  def test_clientAWithShowHeadersFalse(self):
    gLogger.showHeaders(False)
    self.clientA.logSomething()

  def test_clientAWithShowHeadersTrue(self):
    gLogger.showHeaders(True)
    self.clientA.logSomething()
    

  def test_clientAWithShowThreadIDFalse(self):
    gLogger.showThreadIDs(False)
    self.clientA.logSomething()
    

  def test_clientAWithShowThreadIDTrue(self):
    gLogger.showThreadIDs(True)
    self.clientA.logSomething()

  def test_clientAWithShowThreadIDFalseShowHeaderTrue(self):
    gLogger.showHeaders(True)
    gLogger.showThreadIDs(False)
    self.clientA.logSomething()

  def test_clientAWithShowThreadIDFalseShowHeaderFalse(self):
    gLogger.showHeaders(False)
    gLogger.showThreadIDs(False)
    self.clientA.logSomething()
    
  def test_clientAWithShowThreadIDTrueShowHeaderTrue(self):
    gLogger.showHeaders(True)
    gLogger.showThreadIDs(True)
    self.clientA.logSomething()

  def test_clientAWithShowThreadIDTrueShowHeaderFalse(self):
    gLogger.showHeaders(False)
    gLogger.showThreadIDs(True)
    self.clientA.logSomething()
    

if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLogger)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestLoggerCallFromClient))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)