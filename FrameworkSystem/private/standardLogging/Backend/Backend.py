from abc import ABCMeta, abstractmethod

class Backend:
  __metaclass__=ABCMeta

  def __init__(self, handler, formatter):
    self.handler = handler
    self.formatter = formatter

  @abstractmethod
  def setParameters(self, parameters):
    pass