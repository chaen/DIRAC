# imports
import unittest
# sut
from DIRAC.Core.DISET.RPCClient import RPCClient


class TestHelloHandler(unittest.TestCase):

  def setUp(self):
    self.helloService = RPCClient('TestLogger/Hello')

  def tearDown(self):
    pass


class TestHelloHandlerSuccess(TestHelloHandler):

  def test_success(self):
    result = self.helloService.sayHello('you')
    self.assert_(result['OK'])


class TestHelloHandlerFailure(TestHelloHandler):

  def test_failure(self):
    result = self.helloService.sayHello(2)
    self.assertFalse(result['OK'])

if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestHelloHandler)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestHelloHandlerSuccess))
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestHelloHandlerFailure))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
