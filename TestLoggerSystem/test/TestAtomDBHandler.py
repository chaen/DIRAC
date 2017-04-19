# imports
import unittest
# sut
from DIRAC.Core.DISET.RPCClient import RPCClient


class TestAtomDBHandler(unittest.TestCase):

  def setUp(self):
    self.atomService = RPCClient('TestLogger/Atom')

  def tearDown(self):
    pass


class TestAtomDBHandlerSuccess(TestAtomDBHandler):

  def test_success(self):
    result = self.atomService.addStuff('test')
    self.assert_(result['OK'])


class TestAtomDBHandlerFailure(TestAtomDBHandler):

  def test_failure(self):
    result = self.atomService.addStuff(2)
    self.assertFalse(result['OK'])

if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAtomDBHandler)
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestAtomDBHandlerSuccess))
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
      TestAtomDBHandlerFailure))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
  
