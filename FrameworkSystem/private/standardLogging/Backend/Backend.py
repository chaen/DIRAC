from abc import ABCMeta, abstractmethod
import logging


class Backend(object):
  __metaclass__ = ABCMeta
  """
  Backend wrapper
  To gather handler and formatter

  - make stdout/stderr distinction
  - each backend can get its options and 
    format them to give them to the handler
  """

  def __init__(self, handler, formatter):
    self._handler = handler
    self._formatter = formatter

  @abstractmethod
  def setParameters(self, parameters):
    pass

  @abstractmethod
  def configureHandler(self):
    pass

  def getHandler(self):
    return self._handler

  def setFormat(self, fmt, datefmt, component, options):
    self._formatter.setFormat(fmt, datefmt, component, options)
    self._handler.setFormatter(self._formatter)
