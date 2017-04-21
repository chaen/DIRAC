# imports
import unittest
import time
import logging
import sys
# sut
from DIRAC import gLogger
from DIRAC.TestLoggerSystem.private.logging.LoggingConfiguration import LoggingConfiguration


class TestLogger(unittest.TestCase):

  def setUp(self):
    LoggingConfiguration.initializeLogging()
    logging.getLogger().setLevel(logging.ALWAYS)

  def tearDown(self):
    LoggingConfiguration.removeHandlers()
