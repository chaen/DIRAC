""" Client to interact with the S3GW  """

from DIRAC.Core.Base.Client import Client, createClient


@createClient('DataManagement/S3GW')
class S3GWClient(Client):
  """ Client code to the S3GW
  """

  def __init__(self, url=None, **kwargs):
    """ Constructor function.
    """
    Client.__init__(self, **kwargs)
    self.setServer('DataManagement/S3GW')
    if url:
      self.setServer(url)

  def createPresignedUrl(self, storageName, methodName, objectName, expiration=3600, **kwargs):
    return self._getRPC(**kwargs).createPresignedUrl(storageName, methodName, objectName, expiration)
