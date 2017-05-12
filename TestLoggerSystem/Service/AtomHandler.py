""" Atom Service is an example of how to build services in the DIRAC framework
"""

__RCSID__ = "$Id: $"

import logging

import types
from DIRAC.Core.DISET.RequestHandler import RequestHandler
from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.Utilities import Time
from DIRAC.TestLoggerSystem.DB.AtomDB import AtomDB


class AtomHandler(RequestHandler):

  @classmethod
  def initializeHandler(cls, serviceInfo):
    """ Handler initialization
    """
    return S_OK()

  def initialize(self):
    """ Response initialization
    """
    #gLogger
    self.logger = gLogger.getSubLogger('AtomHandlerLogger')
    try:
      #gLogger
      self.logger.always("AtomHandler.initialize.selflogger")
      
      gLogger.always("AtomHandler.initialize.gLogger")

      log = self.logger.getSubLogger('AtomHandlerLog')
      log.always("AtomHandler.initialize.log")

      self.atomdb = AtomDB()
    except Exception:
      gLogger.error("Oops. Something went wrong...")
      raise

  auth_addStuff = ['all']
  types_addStuff = [types.StringTypes]

  def export_addStuff(self, stuff):
    """ Add a row in AtomDB : atomDB_table : stuff
    """
    self.logger.always("AtomHandler.addStuff.selflogger")
      
    gLogger.always("AtomHandler.addStuff.gLogger")

    log = self.logger.getSubLogger('AtomHandlerLog')
    log.always("AtomHandler.addStuff.log")
    
    result = self.atomdb.addStuff(stuff)
    return result
