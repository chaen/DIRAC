"""
Service handler for generating pre-signed URLs for S3 storages

.. literalinclude:: ../ConfigTemplate.cfg
  :start-after: ##BEGIN S3GW
  :end-before: ##END
  :dedent: 2
  :caption: S3GW options

"""

__RCSID__ = "$Id$"

# from DIRAC
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.ConfigurationSystem.Client.Helpers.Registry import getDNForUsername
from DIRAC.Core.DISET.RequestHandler import RequestHandler, getServiceOption
from DIRAC.Core.Security.Properties import FULL_DELEGATION, LIMITED_DELEGATION, TRUSTED_HOST
from DIRAC.Core.Utilities import DErrno
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers

from DIRAC.Resources.Storage.StorageElement import StorageElement
########################################################################

LOG = gLogger.getSubLogger(__name__)


class S3GWHandler(RequestHandler):
  """
  .. class:: S3GWHandler

  """

  _S3Storages = {}

  @classmethod
  def initializeHandler(cls, serviceInfoDict):
    """ initialize handler """

    log = LOG.getSubLogger('initializeHandler')

    for seName in DMSHelpers().getStorageElements():
      se = StorageElement(seName)
      # TODO: once we finally merge _allProtocolParameters with the
      # standard paramaters in the StorageBase, this will be much neater

      for storagePlugin in se.storages:
        storageParam = storagePlugin._allProtocolParameters  # pylint: disable=protected-access

        if storageParam.get('Protocol') == 's3' \
                and 'Aws_access_key_id' in storageParam \
                and 'Aws_secret_access_key'in storageParam:

          cls._S3Storages[seName] = storagePlugin
          log.debug("Add %s to the list of usable S3 storages" % seName)
          break

    log.info("S3GW initialized storages", "%s" % cls._S3Storages.keys())
    return S_OK()

  types_createPresignedUrl = [basestring, basestring, basestring, (int, long)]

  def export_createPresignedUrl(self, storageName, methodName, objectName, expiration=3600):
    """ Generate a presigned URL for a given object, given method, and given storage

        :param storageName: SE name
        :param methodName: name of the method we want to perform
        :param objectName: key of the object
        :param expiration: duration of the token
    """
    log = LOG.getSubLogger('createPresignedUrl')
    log.debug("Creating presigned URL for %s %s %s %s" % (storageName, methodName, objectName, expiration))
    try:
      res = self._S3Storages.get(storageName).createPresignedUrl(methodName, objectName, expiration=expiration)
      log.debug("Returns %s" % res)
      return res
    except Exception as e:
      return S_ERROR(repr(e))
