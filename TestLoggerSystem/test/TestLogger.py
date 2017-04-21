# imports
import unittest
import time
import logging
import sys
# sut
from DIRAC import gLogger


from contextlib import contextmanager
from StringIO import StringIO
from DIRAC.TestLoggerSystem.private.logging.LoggingConfiguration import LoggingConfiguration


@contextmanager
def captured_output():
  new_out, new_err = StringIO(), StringIO()
  old_out, old_err = sys.stdout, sys.stderr
  try:
    sys.stdout, sys.stderr = new_out, new_err
    yield sys.stdout, sys.stderr
  finally:
    sys.stdout, sys.stderr = old_out, old_err


class TestLogger(unittest.TestCase):

  def setUp(self):
    LoggingConfiguration.initializeLogging()
    logging.getLogger().setLevel(logging.ALWAYS)
    gLogger.setLevel('fatal')

  def tearDown(self):
    LoggingConfiguration.removeHandlers()


