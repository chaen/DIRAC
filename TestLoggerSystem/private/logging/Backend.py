import logging

class Backend:

  def __init__(self, name, handler, formatter):
    self.name = name
    self.handler = handler
    self.formatter = formatter