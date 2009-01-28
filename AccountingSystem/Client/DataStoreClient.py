# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/AccountingSystem/Client/DataStoreClient.py,v 1.8 2009/01/28 10:54:53 acasajus Exp $
__RCSID__ = "$Id: DataStoreClient.py,v 1.8 2009/01/28 10:54:53 acasajus Exp $"

import time
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.Core.Utilities.ThreadSafe import Synchronizer
from DIRAC.RequestManagementSystem.Client.RequestContainer import RequestContainer
from DIRAC.RequestManagementSystem.Client.RequestClient import RequestClient

gAccountingSynchro = Synchronizer()

class DataStoreClient:


  def __init__( self, setup = False, retryGraceTime = 0 ):
    self.__setup = setup
    self.__maxRecordsInABundle = 100
    self.__registersList = []
    self.__maxTimeRetrying = retryGraceTime
    self.__lastSuccessfulCommit = time.time()

  def setRetryGraceTime( self, retryGraceTime ):
    self.__maxTimeRetrying = retryGraceTime

  def __checkBaseType( self, obj ):
    """
    Check to find that the class inherits from the Base Type
    """
    for parent in obj.__bases__:
      if parent.__name__ == "BaseAccountingType":
        return True
      if self.__checkHandler( parent ):
        return True
    return False

  @gAccountingSynchro
  def addRegister( self, register ):
    """
    Add a register to the list to be sent
    """
    if not self.__checkBaseType( register.__class__ ):
      return S_ERROR( "register is not a valid type (has to inherit from BaseAccountingType" )
    retVal = register.checkValues()
    if not retVal[ 'OK' ]:
      return retVal
    self.__registersList.append( register.getValues() )
    return S_OK()

  @gAccountingSynchro
  def commit( self ):
    """
    Send the registers in a bundle mode
    """
    if self.__setup:
      rpcClient = RPCClient( "Accounting/DataStore", setup = self.__setup )
    else:
      rpcClient = RPCClient( "Accounting/DataStore" )
    sent = 0
    while len( self.__registersList ) > 0:
      registersToSend = self.__registersList[ :self.__maxRecordsInABundle ]
      retVal = rpcClient.commitRegisters( registersToSend )
      if not retVal[ 'OK' ]:
        if time.time() - self.__lastSuccessfulCommit > self.__maxTimeRetrying:
          gLogger.verbose( "Sending accounting records to failover" )
          result = self.__sendToFailover( self.__setup )
          if not result[ 'OK' ]:
            return result
        return S_ERROR( "Cannot commit data to DataStore service" )
      sent += len( registersToSend )
      del( self.__registersList[ :self.__maxRecordsInABundle ] )
      self.__lastSuccessfulCommit = time.time()
    return S_OK( sent )

  def __sendToFailover( self, setup = False ):
    if self.__setup:
      rpcClient = RPCClient( "Accounting/DataStore", setup = self.__setup )
    else:
      rpcClient = RPCClient( "Accounting/DataStore" )
    requestClient = RequestClient()
    while len( self.__registersList ) > 0:
      registersToSend = self.__registersList[ :self.__maxRecordsInABundle ]
      retVal = rpcClient.commitRegisters( registersToSend )
      if not retVal[ 'OK' ]:
        request = RequestContainer()
        request.setDISETRequest( retVal[ 'rpcStub' ] )

        requestStub = request.toXML()['Value']
        result = requestClient.setRequest( "Accounting.DataStore.%s" % time.time(),
                                           requestStub )
        if not result[ 'OK' ]:
          return result
        del( self.__registersList[ :self.__maxRecordsInABundle ] )
    return S_OK()

gDataStoreClient = DataStoreClient()
