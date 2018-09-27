__RCSID__ = "$Id$"

import os
import socket
import time
# import GSI

from M2Crypto import m2, SSL

#https://github.com/eventbrite/m2crypto/blob/master/demo/medusa/asyncore.py

from DIRAC.Core.Utilities.LockRing import LockRing
from DIRAC.Core.Utilities.ReturnValues import S_ERROR, S_OK
from DIRAC.Core.DISET.private.Transports.BaseTransport import BaseTransport
from DIRAC.FrameworkSystem.Client.Logger import gLogger
from DIRAC.Core.DISET.private.Transports.SSL.m2crypto.SocketInfoFactory import gSocketInfoFactory
from DIRAC.Core.Utilities.Devloader import Devloader
from DIRAC.Core.Security import Locations
from DIRAC.Core.Security.m2crypto.X509Chain import X509Chain
from DIRAC.Core.Security.m2crypto.X509Certificate import X509Certificate

# GSI.SSL.set_thread_safe()


class SSLTransport(BaseTransport):

  __readWriteLock = LockRing().getLock()

  def __init__(self, *args, **kwargs):
    self.__writesDone = 0
    self.__locked = False
    BaseTransport.__init__(self, *args, **kwargs)

  def __lock(self, timeout=1000):
    while self.__locked and timeout:
      time.sleep(0.005)
      timeout -= 0.005
    if not timeout:
      return False
    SSLTransport.__readWriteLock.acquire()
    if self.__locked:
      SSLTransport.__readWriteLock.release()
      return self.__lock(timeout)
    self.__locked = True
    SSLTransport.__readWriteLock.release()
    return True

  def __unlock(self):
    self.__locked = False

  def setSocketTimeout(self, timeout):
    """
    This method is used to chenge the default timeout of the socket
    """
    gSocketInfoFactory.setSocketTimeout(timeout)

  def initAsClient(self):
    retVal = gSocketInfoFactory.getSocket(self.stServerAddress, **self.extraArgsDict)
    if not retVal['OK']:
      return retVal
    self.oSocketInfo = retVal['Value']
    self.oSocket = self.oSocketInfo.getSSLSocket()
    # CHRIS TODO: session reuse
    # if not self.oSocket.session_reused():
    #   gLogger.debug( "New session connecting to server at %s" % str( self.stServerAddress ) )
    self.remoteAddress = self.oSocket.getpeername()
    return S_OK()

  def initAsServer(self):
    if not self.serverMode():
      raise RuntimeError("Must be initialized as server mode")
    retVal = gSocketInfoFactory.getListeningSocket(self.stServerAddress,
                                                   self.iListenQueueSize,
                                                   self.bAllowReuseAddress,
                                                   **self.extraArgsDict)
    if not retVal['OK']:
      return retVal
    self.oSocketInfo = retVal['Value']
    self.oSocket = self.oSocketInfo.getSSLSocket()
    # CHRIS GET THIS FUCKER OUT OF THE WAY
    Devloader().addStuffToClose(self.oSocket)
    return S_OK()

  def close(self):
    gLogger.debug("Closing socket")
    try:

      # Chris 11.09.18
      # I think this will never work,
      # From the fsync man page
      # EROFS, EINVAL: fd is bound to a special file (e.g., a pipe, FIFO, or socket) which does not support synchronization.""
      # For the records, it was added in 67ca305a02621cf36a558cb42896dbb599df9dc9
      # I guess it should be just removed alltogther, but well...
      # os.fsync( self.oSocket.fileno() )

      self.oSocket.close()
    except Exception as e:
      pass

  def renewServerContext(self):
    BaseTransport.renewServerContext(self)
    result = gSocketInfoFactory.renewServerContext(self.oSocketInfo)
    if not result['OK']:
      return result
    self.oSocketInfo = result['Value']
    self.oSocket = self.oSocketInfo.getSSLSocket()
    return S_OK()

  def handshake(self):
    """
      Initiate the client-server handshake and extract credentials

      :return: S_OK (with credentialDict if new session)
    """
    print "CHRIS handshake"
    retVal = self.oSocketInfo.doServerHandshake()
    if not retVal['OK']:
      return retVal
    creds = retVal['Value']
    # CHRIS Comment this out
    # The M2Crypto.SSL.Connection object does not expose that
    # if not self.oSocket.session_reused():
    #   gLogger.debug("New session connecting from client at %s" % str(self.getRemoteAddress()))
    for key in creds.keys():
      self.peerCredentials[key] = creds[key]
    return S_OK()

  def setClientSocket(self, oSocket):
    if self.serverMode():
      raise RuntimeError("Must be initialized as client mode")
    self.oSocketInfo.setSSLSocket(oSocket)
    self.oSocket = oSocket
    self.remoteAddress = self.oSocket.getpeername()
    self.oSocket.settimeout(self.oSocketInfo.infoDict['timeout'])

  def acceptConnection(self):
    oClientTransport = SSLTransport(self.stServerAddress)
    oClientSocket, _stClientAddress = self.oSocket.accept()
    retVal = self.oSocketInfo.clone()
    if not retVal['OK']:
      return retVal
    oClientTransport.oSocketInfo = retVal['Value']
    oClientTransport.setClientSocket(oClientSocket)
    print "CHRIS accept connection"
    return S_OK(oClientTransport)

  def _read(self, bufSize=4096, skipReadyCheck=False):
    print "CHRIS IN ENTER READr"

    # Chris do not use the lock
    # self.__lock()
    try:
      # No need to redo te timeout here, it has been done in the init
      return S_OK(self.oSocket.recv(bufSize))
    except socket.timeout:
      return S_ERROR("Socket read timeout exceeded")
    except SSL.SSLError as e:
      print "CHRIS READ EXCEPT %s" % e
      if e.args[0] == m2.ssl_error_want_read:
        time.sleep(0.001)
      elif  e.args[0] == m2.ssl_error_want_write:
        time.sleep(0.001)
      else:
        raise
    # Not sure why wantWrite is needed here !
    # Nor what is this zeroreturn
    # except GSI.SSL.WantWriteError:
    #   time.sleep( 0.001 )
    # except GSI.SSL.ZeroReturnError:
    #   return S_OK( "" )
    except Exception as e:
      print "CHRIS READ WILD EXCEPT %s" % e
      return S_ERROR("Exception while reading from peer: %s" % str(e))
    finally:
      pass
      # CHRIS do not use the lock
      # self.__unlock()

  # def _read_old( self, bufSize = 4096, skipReadyCheck = False ):
  #   print "CHRIS IN ENTER READr"
  #   self.__lock()
  #   try:
  #     timeout = self.oSocketInfo.infoDict[ 'timeout' ]
  #     if timeout:
  #       start = time.time()
  #     while True:
  #       if timeout:
  #         if time.time() - start > timeout:
  #           return S_ERROR( "Socket read timeout exceeded" )
  #       try:
  #         return S_OK( self.oSocket.recv( bufSize ) )
  #       except GSI.SSL.WantReadError:
  #         time.sleep( 0.001 )
  #       except GSI.SSL.WantWriteError:
  #         time.sleep( 0.001 )
  #       except GSI.SSL.ZeroReturnError:
  #         return S_OK( "" )
  #       except Exception as e:
  #         return S_ERROR( "Exception while reading from peer: %s" % str( e ) )
  #   finally:
  #     self.__unlock()

  def isLocked(self):
    return self.__locked

  # def _write_old( self, buffer ):
  #   print "chris write"
  #   self.__lock()
  #   try:
  #     #Renegotiation
  #     if not self.oSocketInfo.infoDict[ 'clientMode' ]:
  #       #self.__writesDone += 1
  #       if self.__writesDone > 1000:
  #
  #         self.__writesDone = 0
  #         ok = self.oSocket.renegotiate()
  #         if ok:
  #           try:
  #             ok = self.oSocket.do_handshake()
  #           except Exception as e:
  #             return S_ERROR( "Renegotiation failed: %s" % str( e ) )
  #
  #
  #     sentBytes = 0
  #     timeout = self.oSocketInfo.infoDict[ 'timeout' ]
  #     if timeout:
  #       start = time.time()
  #     while sentBytes < len( buffer ):
  #       try:
  #         if timeout:
  #           if time.time() - start > timeout:
  #             return S_ERROR( "Socket write timeout exceeded" )
  #         sent = self.oSocket.write( buffer[ sentBytes: ] )
  #         if sent == 0:
  #           return S_ERROR( "Connection closed by peer" )
  #         if sent > 0:
  #           sentBytes += sent
  #       except GSI.SSL.WantWriteError:
  #         time.sleep( 0.001 )
  #       except GSI.SSL.WantReadError:
  #         time.sleep( 0.001 )
  #       except Exception as e:
  #         return S_ERROR( "Error while sending: %s" % str( e ) )
  #     return S_OK( sentBytes )
  #   finally:
  #     self.__unlock()


def _write(self, buffer):
  print "chris write"
  # CHRIS NO LOCK
  # self.__lock()
  try:
    # CHRIS NO Renegotiation

    sentBytes = 0
    while sentBytes < len(buffer):
      try:
        sent = self.oSocket.send(buffer[sentBytes:])
        if sent < 0:
          print "CHRIS negative sent ! %s" % sent
          err = self.oSocket.ssl_get_error(sent)
          # if the error is try again, let's do it !
          if err == SSL.m2.ssl_error_want_write:
            print "CHRIS ITS OK"
            continue
          if err == SSL.m2.ssl_error_want_read:
            print "CHRIS ITS OK BUT READ"
            continue
          return S_ERROR("Unhandled error on send %s %s" % (sent, err))

        elif sent == 0:
          return S_ERROR("Connection closed by peer")
        elif sent > 0:
          sentBytes += sent
      except socket.timeout:
        return S_ERROR("Socket write timeout exceeded")
      except Exception as e:
        return S_ERROR("Error while sending: %s" % str(e))
    return S_OK(sentBytes)
  finally:
    pass
    # CHRIS NO LOCK
    self.__unlock()


def checkSanity(urlTuple, kwargs):
  """
  Check that all ssl environment is ok
  """
  useCerts = False
  certFile = ''
  if "useCertificates" in kwargs and kwargs['useCertificates']:
    certTuple = Locations.getHostCertificateAndKeyLocation()
    if not certTuple:
      gLogger.error("No cert/key found! ")
      return S_ERROR("No cert/key found! ")
    certFile = certTuple[0]
    useCerts = True
  elif "proxyString" in kwargs:
    if not isinstance(kwargs['proxyString'], basestring):
      gLogger.error("proxyString parameter is not a valid type", str(type(kwargs['proxyString'])))
      return S_ERROR("proxyString parameter is not a valid type")
  else:
    if "proxyLocation" in kwargs:
      certFile = kwargs["proxyLocation"]
    else:
      certFile = Locations.getProxyLocation()
    if not certFile:
      gLogger.error("No proxy found")
      return S_ERROR("No proxy found")
    elif not os.path.isfile(certFile):
      gLogger.error("Proxy file does not exist", certFile)
      return S_ERROR("%s proxy file does not exist" % certFile)

  # For certs always check CA's. For clients skipServerIdentityCheck
  if 'skipCACheck' not in kwargs or not kwargs['skipCACheck']:
    if not Locations.getCAsLocation():
      gLogger.error("No CAs found!")
      return S_ERROR("No CAs found!")

  if "proxyString" in kwargs:
    certObj = X509Chain()
    retVal = certObj.loadChainFromString(kwargs['proxyString'])
    if not retVal['OK']:
      gLogger.error("Can't load proxy string")
      return S_ERROR("Can't load proxy string")
  else:
    if useCerts:
      certObj = X509Certificate()
      certObj.loadFromFile(certFile)
    else:
      certObj = X509Chain()
      certObj.loadChainFromFile(certFile)

  retVal = certObj.hasExpired()
  if not retVal['OK']:
    gLogger.error("Can't verify proxy or certificate file", "%s:%s" % (certFile, retVal['Message']))
    return S_ERROR("Can't verify file %s:%s" % (certFile, retVal['Message']))
  else:
    if retVal['Value']:
      notAfter = certObj.getNotAfterDate()
      if notAfter['OK']:
        notAfter = notAfter['Value']
      else:
        notAfter = "unknown"
      gLogger.error("PEM file has expired", "%s is not valid after %s" % (certFile, notAfter))
      return S_ERROR("PEM file %s has expired, not valid after %s" % (certFile, notAfter))

  idDict = {}
  retVal = certObj.getDIRACGroup(ignoreDefault=True)
  if retVal['OK'] and retVal['Value']:
    idDict['group'] = retVal['Value']
  if useCerts:
    idDict['DN'] = certObj.getSubjectDN()['Value']
  else:
    idDict['DN'] = certObj.getIssuerCert()['Value'].getSubjectDN()['Value']

  return S_OK(idDict)


def delegate(delegationRequest, kwargs):
  """
  Check delegate!
  """
  if "useCertificates" in kwargs and kwargs['useCertificates']:
    chain = X509Chain()
    certTuple = Locations.getHostCertificateAndKeyLocation()
    chain.loadChainFromFile(certTuple[0])
    chain.loadKeyFromFile(certTuple[1])
  elif "proxyObject" in kwargs:
    chain = kwargs['proxyObject']
  else:
    if "proxyLocation" in kwargs:
      procLoc = kwargs["proxyLocation"]
    else:
      procLoc = Locations.getProxyLocation()
    chain = X509Chain()
    chain.loadChainFromFile(procLoc)
    chain.loadKeyFromFile(procLoc)
  return chain.generateChainFromRequestString(delegationRequest)
