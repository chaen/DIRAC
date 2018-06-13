"""
TORNADO SERVER
Receive RPC and return JSON to client
"""

__RCSID__ = "$Id$"
import time
import ssl
import os

from tornado.httpserver import HTTPServer
from tornado.web import Application, url
from tornado.ioloop import IOLoop

import DIRAC
from DIRAC.TornadoServices.Server.HandlerManager import HandlerManager
from DIRAC import gLogger, S_ERROR, S_OK
from DIRAC.FrameworkSystem.Client.MonitoringClient import MonitoringClient
from DIRAC.Core.Utilities import Time



class TornadoServer(object):
  """
    Tornado webserver
    at init if we pass service list it will load only these services
    if not it will try yo discover all handlers available
  """

  def __init__(self, services=None, debug=False, setup=None):
    if services and not isinstance(services, list):
      services = [services]
    # URLs for services: 1URL/Service
    self.urls = []
    # Other infos
    self.debug = debug  # Used only by tornado
    self.setup = setup
    self.port = 443  # Default port for HTTPS, may be changed later via config file ?
    self.handlerManager = HandlerManager()
    self._monitor = MonitoringClient()
    self.stats = {'requests' : 0, 'monitorLastStatsUpdate':time.time()}

    # If services are defined, load only these ones (useful for debug purpose)
    if services and services != []:
      self.handlerManager.loadHandlersByServiceName(services)

    # if no service list is given, load services from configuration
    handlerDict = self.handlerManager.getHandlersDict()
    for key in handlerDict.keys():
      handlerDict[key].initializeService(key)
      self.urls.append(url(key, handlerDict[key], dict(monitor=self._monitor, stats=self.stats)))

  def startTornado(self):
    """
      Start the tornado server when ready
      The script is blocked in the Tornado IOLoop
    """

    gLogger.debug("Starting Tornado")
    self._initMonitoring()

    if self.debug:
      gLogger.warn("TORNADO use debug mode, autoreload can generate unexpected effects, use it only in dev")

    router = Application(self.urls, debug=self.debug)

    cert_dir = "%s/etc/grid-security/" % DIRAC.rootPath
    print cert_dir

    # Define SSLContext
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=os.path.join(cert_dir, "hostcert.pem"))

    # Force client to use certificate
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    # Load host certificates
    ssl_ctx.load_cert_chain(os.path.join(cert_dir, "hostcert.pem"),
                            os.path.join(cert_dir, "hostkey.pem"))

    # Start server
    server = HTTPServer(router, ssl_options=ssl_ctx)
    try:
      server.listen(self.port)
    except Exception as e:
      gLogger.fatal(e)
      return S_ERROR()
    gLogger.always("Listening on port %s" % self.port)
    for service in self.urls:
      gLogger.debug("Available service: %s" % service)
    IOLoop.current().start()

  def _initMonitoring(self):
    # Init extra bits of monitoring
    self._monitor.setComponentType(MonitoringClient.COMPONENT_WEB)  # ADD COMPONENT TYPE FOR TORNADO ?
    self._monitor.initialize()

    self._monitor.registerActivity("Queries", "Queries served", "Framework", "queries", MonitoringClient.OP_RATE)
    self._monitor.registerActivity('CPU', "CPU Usage", 'Framework', "CPU,%", MonitoringClient.OP_MEAN, 600)
    self._monitor.registerActivity('MEM', "Memory Usage", 'Framework', 'Memory,MB', MonitoringClient.OP_MEAN, 600)

    self._monitor.setComponentExtraParam('DIRACVersion', DIRAC.version)
    self._monitor.setComponentExtraParam('platform', DIRAC.getPlatform())
    self._monitor.setComponentExtraParam('startTime', Time.dateTime())

    return S_OK()
