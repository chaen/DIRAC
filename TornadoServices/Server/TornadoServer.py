"""
TornadoServer create a web server and load services.
It may work better with TornadoClient but as it accepts HTTPS you can create your own client
"""

__RCSID__ = "$Id$"


import time
import datetime
import os
from socket import error as socketerror
import M2Crypto

# Patching -- Should disable pylint wrong-import-position...
from tornado_m2crypto.m2netutil import m2_wrap_socket  # pylint: disable=wrong-import-position
import tornado.netutil  # pylint: disable=wrong-import-position
tornado.netutil.ssl_wrap_socket = m2_wrap_socket  # pylint: disable=wrong-import-position

import tornado.httputil  # pylint: disable=wrong-import-position
tornado.httputil.HTTPServerRequest.configure(
    'tornado_m2crypto.m2httputil.M2HTTPServerRequest')  # pylint: disable=wrong-import-position
import tornado.iostream  # pylint: disable=wrong-import-position
tornado.iostream.SSLIOStream.configure(
    'tornado_m2crypto.m2iostream.M2IOStream')  # pylint: disable=wrong-import-position

from tornado.httpserver import HTTPServer
from tornado.web import Application, url
from tornado.ioloop import IOLoop
import tornado.ioloop

import DIRAC
from DIRAC.TornadoServices.Server.HandlerManager import HandlerManager
from DIRAC import gLogger, S_ERROR, S_OK
from DIRAC.FrameworkSystem.Client.MonitoringClient import MonitoringClient
from DIRAC.Core.Security import Locations
from DIRAC.Core.Utilities import MemStat


class TornadoServer(object):
  """
    Tornado webserver

    Initialize and run a HTTPS Server for DIRAC services.
    By default it load all services from configuration, but you can also give an explicit list.
    If you gave explicit list of services, only these ones are loaded

    Example 1: Easy way to start tornado::

      # Initialize server and load services
      serverToLaunch = TornadoServer()

      # Start listening when ready
      serverToLaunch.startTornado()

    Example 2:We want to debug service1 and service2 only, and use another port for that ::

      services = ['component/service1', 'component/service2']
      serverToLaunch = TornadoServer(services=services, port=1234, debug=True)
      serverToLaunch.startTornado()
  """

  def __init__(self, services=None, debug=False, port=443):
    """
    :param list services: List of services you want to start, start all by default
    :param str debug: Activate debug mode of Tornado (autoreload server + more errors display) and M2Crypto
    :param int port: Used to change port, default is 443
    """

    if services and not isinstance(services, list):
      services = [services]
    # URLs for services: 1URL/Service
    self.urls = []
    # Other infos
    self.debug = debug  # Used by tornado and M2Crypto
    self.port = port
    self.handlerManager = HandlerManager()
    self._monitor = MonitoringClient()
    self.__monitoringLoopDelay = 60 #In secs

    # If services are defined, load only these ones (useful for debug purpose)
    if services and services != []:
      self.handlerManager.loadHandlersByServiceName(services)

    # if no service list is given, load services from configuration
    handlerDict = self.handlerManager.getHandlersDict()
    for key in handlerDict:
      # handlerDict[key].initializeService(key)
      self.urls.append(url(key, handlerDict[key], dict(debug=debug)))

  def startTornado(self, multiprocess=False):
    """
      Start the tornado server when ready.
      The script is blocked in the Tornado IOLoop.
      Multiprocess option is available
    """

    gLogger.debug("Starting Tornado")
    self._initMonitoring()

    if self.debug:
      gLogger.warn("Server is running in debug mode")

    router = Application(self.urls, debug=self.debug)

    certs = Locations.getHostCertificateAndKeyLocation()

    ca = Locations.getCAsLocation()

    ssl_options = {
        'certfile': certs[0],
        'keyfile': certs[1],
        'cert_reqs': M2Crypto.SSL.verify_peer,
        'ca_certs': ca,
        'sslDebug': self.debug
    }

    # Start server
    server = HTTPServer(router, ssl_options=ssl_options)
    try:
      if multiprocess:
        server.bind(self.port)
      else:
        server.listen(self.port)
    except socketerror as e:
      gLogger.fatal(e)
      return S_ERROR()
    gLogger.always("Listening on port %s" % self.port)
    for service in self.urls:
      gLogger.debug("Available service: %s" % service)

    self.__monitorLastStatsUpdate = time.time()
    self.__report = self.__startReportToMonitoringLoop()

    if multiprocess:
      server.start(0)
      tornado.ioloop.PeriodicCallback(self.__reportToMonitoring, self.__monitoringLoopDelay*1000).start()
      IOLoop.current().start()
    else:
      tornado.ioloop.PeriodicCallback(self.__reportToMonitoring, self.__monitoringLoopDelay*1000).start()
      IOLoop.instance().start()
    return True  # Never called because of IOLoop, but to make pylint happy

  def _initMonitoring(self):
    # Init extra bits of monitoring

    self._monitor.setComponentType(MonitoringClient.COMPONENT_WEB)  # ADD COMPONENT TYPE FOR TORNADO ?
    self._monitor.initialize()
    self._monitor.setComponentName('Tornado')

    self._monitor.registerActivity('CPU', "CPU Usage", 'Framework', "CPU,%", MonitoringClient.OP_MEAN, 600)
    self._monitor.registerActivity('MEM', "Memory Usage", 'Framework', 'Memory,MB', MonitoringClient.OP_MEAN, 600)

    self._monitor.setComponentExtraParam('DIRACVersion', DIRAC.version)
    self._monitor.setComponentExtraParam('platform', DIRAC.getPlatform())
    self._monitor.setComponentExtraParam('startTime', datetime.datetime.utcnow())
    return S_OK()


  def __reportToMonitoring(self):
    """
      *Called every minute*
      Every minutes we determine CPU and Memory usage
    """

    # Calculate CPU usage by comparing realtime and cpu time since last report
    self.__endReportToMonitoringLoop(*self.__report)

    # Save memory usage and save realtime/CPU time for next call
    self.__report = self.__startReportToMonitoringLoop()

  def __startReportToMonitoringLoop(self):
    """
      Get time to prepare CPU usage monitoring and send memory usage to monitor
    """
    now = time.time()
    stats = os.times()
    cpuTime = stats[0] + stats[2]
    if now - self.__monitorLastStatsUpdate < 0:
      return (now, cpuTime)
    # Send CPU consumption mark
    self.__monitorLastStatsUpdate = now
    # Send Memory consumption mark
    membytes = MemStat.VmB('VmRSS:')
    if membytes:
      mem = membytes / (1024. * 1024.)
      self._monitor.addMark('MEM', mem)
    return (now, cpuTime)

  def __endReportToMonitoringLoop(self, initialWallTime, initialCPUTime):
    """
      Determine CPU usage by comparing walltime and cputime and send it to monitor
    """
    wallTime = time.time() - initialWallTime
    stats = os.times()
    cpuTime = stats[0] + stats[2] - initialCPUTime
    percentage = cpuTime / wallTime * 100.
    if percentage > 0:
      self._monitor.addMark('CPU', percentage)
