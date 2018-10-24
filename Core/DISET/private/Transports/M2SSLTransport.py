#!/usr/bin/env python
"""
M2Crypto SSLTransport Library
"""

__RCSID__ = "$Id$"

import os
import socket
from M2Crypto import SSL, threading as M2Threading

from DIRAC.Core.Utilities.ReturnValues import S_OK
from DIRAC.Core.DISET.private.Transports.BaseTransport import BaseTransport
from DIRAC.Core.DISET.private.Transports.SSL.M2Utils import getM2SSLContext, getM2PeerInfo

# For now we have to set an environment variable for proxy support in OpenSSL
# Eventually we may need to add API support for this to M2Crypto...
os.environ['OPENSSL_ALLOW_PROXY_CERTS'] = '1'
M2Threading.init()

# TODO: CRL checking should be implemented but this will require support adding
# to M2Crypto: Quite a few functions will need mapping through from OpenSSL to
# allow the CRL stack to be set on the X509 CTX used for verification.

# TODO: Catch exceptions (from M2 itself and my M2Utils module) and convert them
# into proper DIRAC style errors.

# TODO: Log useful messages to the logger

class SSLTransport(BaseTransport):
  """ SSL Transport implementaiton using the M2Crypto library. """

  def __getConnection(self):
    """ Helper function to get a connection object,
        Tries IPv6 (AF_INET6) first, then falls back to IPv4 (AF_INET).
    """
    try:
      conn = SSL.Connection(self.__ctx, family=socket.AF_INET6)
    except socket.error:
      # Maybe no IPv6 support? Try IPv4 only socket.
      conn = SSL.Connection(self.__ctx, family=socket.AF_INET)
    return conn

  def __init__(self, *args, **kwargs):
    """ Create an SSLTransport object, parameters are the same
        as for other transports. If ctx is specified (as an instance of
        SSL.Context) then use that rather than creating a new context.
    """
    self.remoteAddress = None
    self.peerCredentials = {}
    self.__timeout = 1
    self.__locked = False # We don't support locking, so this is always false.
    self.__ctx = kwargs.pop('ctx', None)
    if not self.__ctx:
      self.__ctx = getM2SSLContext(**kwargs)
    self.__kwargs = kwargs
    BaseTransport.__init__(self, *args, **kwargs)

  def setSocketTimeout(self, timeout):
    """ Set the timeout for socket operations.
        The timeout parameter is in seconds (float).
    """
    self.__timeout = timeout

  def initAsClient(self):
    """ Prepare this client socket for use. """
    if self.serverMode():
      raise RuntimeError("SSLTransport is in server mode.")
    self.oSocket = self.__getConnection()
    self.oSocket.connect(self.stServerAddress)
    self.remoteAddress = self.oSocket.getpeername()
    return S_OK()

  def initAsServer(self):
    """ Prepare this server socket for use. """
    if not self.serverMode():
      raise RuntimeError("SSLTransport is in client mode.")
    # Before getting the connection object, we need to set
    # a server session ID in the context
    host = self.stServerAddress[0]
    port = self.stServerAddress[1]
    self.__ctx.set_session_id_ctx("DIRAC-%s-%s" % (host, port))
    self.oSocket = self.__getConnection()
    # Make sure reuse address is set correctly
    if self.bAllowReuseAddress:
      param = 1
    else:
      param = 0
    self.oSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, param)
    self.oSocket.bind(self.stServerAddress)
    self.oSocket.listen(self.iListenQueueSize)
    return S_OK()

  def close(self):
    """ Close this socket. """
    if self.oSocket:
      self.oSocket.close()
      self.oSocket = None
    return S_OK()

  def renewServerContext(self):
    """ Renews the server context.
        This reloads the certificates and re-initialises the SSL context.
    """
    if not self.serverMode():
      raise RuntimeError("SSLTransport is in client mode.")
    self.__ctx = getM2SSLContext(self.__ctx, **self.__kwargs)
    return S_OK()

  def handshake(self):
    """ Used to perform SSL handshakes.
        These are now done automatically.
    """
    # This isn't used any more, the handshake is done inside the M2Crypto library
    return S_OK()

  def setClientSocket(self, oSocket):
    """ Set the inner socket (i.e. SSL.Connection object) of this instance
        to the value of oSocket.
        This method is intended to be used to create client connection objects
        from a server and should be considered to be an internal function.
    """
    self.oSocket = oSocket
    self.remoteAddress = self.oSocket.getpeername()
    self.peerCredentials = getM2PeerInfo(self.oSocket)

  def acceptConnection(self):
    """ Accept a new client, returns a new SSLTransport object representing
        the client connection.
    """
    oClient, _ = self.oSocket.accept()
    oClientTrans = SSLTransport(self.stServerAddress, self.__ctx)
    oClientTrans.setClientSocket(oClient)
    return S_OK(oClientTrans)

  def _read(self, bufSize=4096, skipReadyCheck=False):
    """ Read bufSize bytes from the buffer.
        skipReadyCheck is ignored.
    """
    return S_OK(self.oSocket.read(bufSize))

  def isLocked(self):
    """ Returns if this instance is locked.
        Always returns false.
    """
    return self.__locked

  def _write(self, buf):
    """ Write all bytes contained within iterable "buf" to the
        connected peer.
    """
    return S_OK(self.oSocket.write(buf))
