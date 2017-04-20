# imports
import unittest
import time
import logging
import sys
# sut
from DIRAC import gLogger
from DIRAC.TestLoggerSystem.test.TestLogger import TestLogger, captured_output
from DIRAC.TestLoggerSystem.Client.ClientB import ClientB
from DIRAC.TestLoggerSystem.Client.ClientA import ClientA


class TestLoggerCallFromClient(TestLogger):

  def setUp(self):
    super(TestLogger, self).setUp()
    self.clientA = ClientA()
    self.clientB = ClientB()

  def tearDown(self):
    pass

  def test_clientA(self):
    self.clientA.logSomething()

  def test_clientB(self):
    self.clientB.logSomething()

  def test_clientBFromClientA(self):
    self.clientA.logSomethingFromB()

  def test_atomHandlerFromClientA(self):
    self.clientA.addStuff("test")



if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLogger)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestLoggerCallFromClient))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
