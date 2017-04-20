# imports
import unittest
import time
import logging
import sys
# sut
from DIRAC import gLogger


from contextlib import contextmanager
from StringIO import StringIO


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
    # basic configuration of root logger
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(level=logging.DEBUG,
                        #stream=sys.stdout,
                        format='%(asctime)s UTC %(name)s  %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # to do : path of the subLogger
    logging.getLogger().name = 'Framework'
    logger = logging.getLogger()

    # addlevel
    levelDict = {10: "ALWAYS",
                 20: "NOTICE",
                 30: "INFO",
                 40: "VERBOSE",
                 50: "DEBUG",
                 60: "WARN",
                 70: "ERROR",
                 80: "EXCEPTION",
                 90: "FATAL"}

    for level in levelDict:
      logging.addLevelName(level, levelDict[level])
      setattr(logging, levelDict[level], level)
      setattr(logging.Logger, levelDict[level].lower(),
              (lambda level: lambda inst, msg, *args, **kwargs: inst.log(level, msg, *args, **kwargs))(level))
      setattr(logging, levelDict[level].lower(), (lambda level: lambda msg,
                                                  *args, **kwargs: logging.log(level, msg, *args, **kwargs))(level))

  def tearDown(self):
    pass


