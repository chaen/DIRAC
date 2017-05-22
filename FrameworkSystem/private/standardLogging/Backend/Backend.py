from abc import ABCMeta, abstractmethod
import logging


class Backend(object):
  __metaclass__ = ABCMeta
  """
  Backend wrapper:
  - to gather handler and formatter
  - make stdout/stderr distinction
  - each backend can get its options and 
    format them to give them to the handler
  """

  def __init__(self, handler, formatter):
    self._handler = handler
    self._formatter = formatter

  @abstractmethod
  def setParameters(self, parameters):
    """
    Each backend can initialize its parameters for their handlers.
    :params parameters: dictionary of parameters. ex: {'FileName': file.log}
    """
    pass

  @abstractmethod
  def configureHandler(self):
    """
    Initialize the handler with the parameters.
    """
    pass

  def getHandler(self):
    """
    :return: the handler
    """
    return self._handler

  def setFormat(self, fmt, datefmt, component, options):
    """
    Each backend give a format to their formatters and attach them to their handlers.
    :params fmt: string representing the log format
    :params datefmt: string representing the date format
    :params component: string represented as "system/component"
    :params options: dictionary of logging options. ex: {'Color': True} 
    """
    self._formatter.setFormat(fmt, datefmt, component, options)
    self._handler.setFormatter(self._formatter)
