from abc import ABCMeta, abstractmethod


class Backend:
  __metaclass__ = ABCMeta
  """
  Backend wrapper
  To gather handler and formatter

  - make stdout/stderr distinction
  - each backend can get its options and 
    format them to give them to the handler
  """

  def __init__(self, handler, formatter):
    self.handler = handler
    self.formatter = formatter

  @abstractmethod
  def setParameters(self, parameters):
    pass
