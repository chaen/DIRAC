"""
Profiling class for updated information on process status
"""

__RCSID__ = "$Id$"

import datetime
import errno
import psutil

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.Utilities.DErrno import EEZOMBIE, EENOPID, EEEXCEPTION


def checkInvocation(func):
  """ Decorator for invoking psutil methods
  """
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except psutil.ZombieProcess as e:
      gLogger.error('Zombie process: %s' % e)
      return S_ERROR(EEZOMBIE, 'Zombie process: %s' % e)
    except psutil.NoSuchProcess as e:
      gLogger.error('No such process: %s' % e)
      return S_ERROR(errno.ESRCH, 'No such process: %s' % e)
    except psutil.AccessDenied as e:
      gLogger.error('Access denied: %s' % e)
      return S_ERROR(errno.EPERM, 'Access denied: %s' % e)
    except Exception as e:  # pylint: disable=broad-except
      gLogger.error(e)
      return S_ERROR(EEEXCEPTION, e)

  return wrapper


class Profiler(object):
  """
  Class for profiling both general stats about a machine and individual processes.
  Every instance of this class is associated to a single process by using its PID.
  Calls to the different methods of the class will return the current state of the process.
  """

  def __init__(self, pid=None):
    """
    :param str pid: PID of the process to be profiled
    """
    self.process = None
    if pid:
      try:
        self.process = psutil.Process(int(pid))
      except psutil.NoSuchProcess as e:
        gLogger.error('No such process: %s' % e)

  def pid(self):
    """
    Returns the process PID
    """
    if self.process:
      return S_OK(self.process.pid)
    else:
      gLogger.error('No PID of process to profile')
      return S_ERROR(EENOPID, 'No PID of process to profile')

  @checkInvocation
  def status(self):
    """ Returns the process status
    """
    result = self.process.status()
    return S_OK(result)

  @checkInvocation
  def runningTime(self):
    """
    Returns the uptime of the process
    """
    start = datetime.datetime.fromtimestamp(self.process.create_time())
    result = (datetime.datetime.now() - start).total_seconds()
    return S_OK(result)

  @checkInvocation
  def memoryUsage(self, withChildren=False):
    """
    Returns the memory usage of the process in MB
    """
    # Information is returned in bytes
    rss = self.process.memory_info().rss
    if withChildren:
      for child in self.process.children(recursive=True):
        rss += child.memory_info().rss
    # converted to MB
    return S_OK(rss / float(2 ** 20))

  @checkInvocation
  def vSizeUsage(self, withChildren=False):
    """
    Returns the memory usage of the process in MB
    """
    # Information is returned in bytes
    vms = self.process.memory_info().vms
    if withChildren:
      for child in self.process.children(recursive=True):
        vms += child.memory_info().vms
    # converted to MB
    return S_OK(vms / float(2 ** 20))

  @checkInvocation
  def numThreads(self, withChildren=False):
    """
    Returns the number of threads the process is using
    """
    nThreads = self.process.num_threads()
    if withChildren:
      for child in self.process.children(recursive=True):
        nThreads += child.num_threads()
    return S_OK(nThreads)

  @checkInvocation
  def cpuPercentage(self, withChildren=False):
    """
    Returns the percentage of cpu used by the process
    """
    cpuPercentage = self.process.cpu_percent()
    if withChildren:
      for child in self.process.children(recursive=True):
        cpuPercentage += child.cpu_percent()
    return S_OK(cpuPercentage)

  @checkInvocation
  def cpuUsageUser(self, withChildren=False):
    """
    Returns the percentage of cpu used by the process
    """
    cpuUsageUser = self.process.cpu_times().user
    if withChildren:
      for child in self.process.children(recursive=True):
        cpuUsageUser += child.cpu_times().user
    return S_OK(cpuUsageUser)

  @checkInvocation
  def cpuUsageSystem(self, withChildren=False):
    """
    Returns the percentage of cpu used by the process
    """
    cpuUsageSystem = self.process.cpu_times().system
    if withChildren:
      for child in self.process.children(recursive=True):
        cpuUsageSystem += child.cpu_times().system
    return S_OK(cpuUsageSystem)

  def getAllProcessData(self, withChildren=False):
    """
    Returns data available about a process
    """
    data = {}

    data['datetime'] = datetime.datetime.utcnow()
    data['stats'] = {}

    result = self.pid()
    if result['OK']:
      data['stats']['pid'] = result['Value']

    result = self.status()
    if result['OK']:
      data['stats']['status'] = result['Value']

    result = self.runningTime()
    if result['OK']:
      data['stats']['runningTime'] = result['Value']

    result = self.memoryUsage(withChildren)
    if result['OK']:
      data['stats']['memoryUsage'] = result['Value']

    result = self.vSizeUsage(withChildren)
    if result['OK']:
      data['stats']['vSizeUsage'] = result['Value']

    result = self.numThreads(withChildren)
    if result['OK']:
      data['stats']['threads'] = result['Value']

    result = self.cpuPercentage(withChildren)
    if result['OK']:
      data['stats']['cpuPercentage'] = result['Value']

    result = self.cpuUsageUser(withChildren)
    if result['OK']:
      data['stats']['cpuUsageUser'] = result['Value']

    result = self.cpuUsageSystem(withChildren)
    if result['OK']:
      data['stats']['cpuUsageSystem'] = result['Value']

    return S_OK(data)
