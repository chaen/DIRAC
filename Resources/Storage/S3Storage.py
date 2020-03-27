# https://docs.aws.amazon.com/AmazonS3/latest/API/API_Operations.html
# https://pypi.org/project/requests-aws/
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects

# docker run --rm -it --privileged --name dirac-testing-host \
#   -v /home/chaen/dirac/diracostar:/diracostar \
#   -e DIRACOS_TARBALL_PATH=/diracostar \
#   -e CI_PROJECT_DIR=/repo/DIRAC -e CI_REGISTRY_IMAGE=diracgrid \
#   -v /var/run/docker.sock:/var/run/docker.sock -v $PWD:/repo/DIRAC -w /repo \
#   diracgrid/docker-compose-dirac:latest bash \
#   DIRAC/tests/CI/run_docker_setup.sh

""" Base Storage Class provides the base interface for all storage plug-ins

      exists()

These are the methods for manipulating files:
      isFile()
      getFile()
      putFile()
      removeFile()
      getFileMetadata()
      getFileSize()
      prestageFile()
      getTransportURL()

These are the methods for manipulating directories:
      isDirectory()
      getDirectory()
      putDirectory()
      createDirectory()
      removeDirectory()
      listDirectory()
      getDirectoryMetadata()
      getDirectorySize()

These are the methods for manipulating the client:
      changeDirectory()
      getCurrentDirectory()
      getName()
      getParameters()
      getCurrentURL()

These are the methods for getting information about the Storage:
      getOccupancy()

"""
__RCSID__ = "$Id$"

import boto3
from botocore.exceptions import ClientError

import copy
import functools
import json
import os
import shutil
import tempfile

from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Utilities.Adler import fileAdler
from DIRAC.Core.Utilities.Pfn import pfnparse, pfnunparse
from DIRAC.Core.Utilities.ReturnValues import returnSingleResult
from DIRAC.Resources.Storage.Utilities import checkArgumentFormat
from DIRAC.Resources.Storage.StorageBase import StorageBase

LOG = gLogger.getSubLogger(__name__)


def _extractKeyFromS3Path(meth):
  """ Decorator to split an s3 "external" url (s3://server:port/bucket/path)
      and return only the path part.
  """

  @functools.wraps(meth)
  def extractKey(self, urls, *args, **kwargs):

    # If set to False, we are already working with keys, so
    # skip all the splitting
    extractKeys = kwargs.pop('extractKeys', True)

    keysToUrls = {}
    keyArgs = {}

    successful = {}
    failed = {}

    if extractKeys:
      for url in urls:
        res = pfnparse(url, srmSpecific=False)
        if not res['OK']:
          failed[url] = res['Message']
          continue

        splitURL = res['Value']
        path = splitURL['Path'].lstrip('/')
        key = os.path.join(path, splitURL['FileName'])
        keysToUrls[key] = url
        keyArgs[key] = urls[url]

    else:
      keyArgs = copy.copy(urls)

    result = meth(self, keyArgs, *args, **kwargs)

    # Restore original paths

    for key in result['Value']['Failed']:
      failed[keysToUrls.get(key, key)] = result['Value']['Failed'][key]
    for key in result['Value']['Successful']:
      successful[keysToUrls.get(key, key)] = result['Value']['Successful'][key]

    result['Value'].update({"Successful": successful, "Failed": failed})
    return result

  return extractKey


class S3Storage(StorageBase):
  """
  .. class:: StorageBase

  """

  pluginName = 'S3'

  def __init__(self, storageName, parameters):

    super(S3Storage, self).__init__(storageName, parameters)

    self.isok = True

    endpoint_url = 'http://%s:%s' % (parameters['Host'], parameters.get('Port', 443))
    aws_access_key_id = '123'
    aws_secret_access_key = 'abc'
    self.bucketName = parameters['Path']

    self.s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)

    self.srmSpecificParse = False
    self.pluginName = 'S3'

  @_extractKeyFromS3Path
  def exists(self, keys):
    """ Check if the keys exists on the storage

    :param self: self reference
    :param keys: list of keys
    :returns: Failed dictionary: {pfn : error message}
              Successful dictionary: {pfn : bool}
              S_ERROR in case of argument problems
    """

    successful = {}
    failed = {}

    for key in keys:
      try:
        self.s3_client.head_object(Bucket=self.bucketName, Key=key)
        successful[key] = True
      except ClientError as exp:
        if exp.response['Error']['Code'] == '404':
          successful[key] = False
        else:
          failed[key] = repr(exp)
      except Exception as exp:
        failed[key] = repr(exp)

    resDict = {'Failed': failed, 'Successful': successful}
    return S_OK(resDict)

  @_extractKeyFromS3Path
  def isFile(self, urls):
    """ Check if the urls provided are a file or not

    In practice, if the object exists, it is necessarily a file

    :param urls: list of urls to be checked
    :returns: Failed dict: {path : error message}
              Successful dict: {path : bool}
              S_ERROR in case of argument problems

    """

    return self.exists(urls, extractKeys=False)  # pylint: disable=unexpected-keyword-arg

  @_extractKeyFromS3Path
  def getFile(self, keys, localPath=False):
    """ Make a local copy of the keys.

    :param  keys: list of keys  on storage
    :param localPath: destination folder. Default is from current directory
    :returns: Successful dict: {path : size}
              Failed dict: {path : errorMessage}
              S_ERROR in case of argument problems
    """

    log = LOG.getSubLogger('getFile')

    failed = {}
    successful = {}

    for src_key in keys:
      try:
        fileName = os.path.basename(src_key)
        dest_file = os.path.join(localPath if localPath else os.getcwd(), fileName)
        log.debug("Trying to download %s to %s" % (src_key, dest_file))
        self.s3_client.download_file(self.bucketName, src_key, dest_file)
        successful[src_key] = os.path.getsize(dest_file)
      except Exception as exp:
        failed[src_key] = repr(exp)

    return S_OK({'Failed': failed, 'Successful': successful})

  @_extractKeyFromS3Path
  def putFile(self, keys, sourceSize=0):
    """ Upload a local file.
        :warning: no 3rd party copy possible

        :param urls: dictionary { keys : localFile }
        :param sourceSize: size of the file in byte. Mandatory for third party copy (WHY ???)
                             Also, this parameter makes it essentially a non bulk operation for
                             third party copy, unless all files have the same size...
        :returns: Successful dict: { path : size }
                  Failed dict: { path : error message }
                  S_ERROR in case of argument problems
    """

    log = LOG.getSubLogger('putFile')

    failed = {}
    successful = {}

    for dest_key, src_file in keys.iteritems():
      try:
        cks = fileAdler(src_file)
        if not cks:
          log.warn("Cannot get ADLER32 checksum for %s" % src_file)

        with open(src_file) as src_fd:
          self.s3_client.put_object(
              Body=src_fd,
              Bucket=self.bucketName,
              Key=dest_key,
              Metadata={
                  'Checksum': cks})
        successful[dest_key] = os.path.getsize(src_file)
      except Exception as e:
        failed[dest_key] = repr(e)

    return S_OK({'Failed': failed, 'Successful': successful})

  @_extractKeyFromS3Path
  def getFileMetadata(self, keys):
    """ Get metadata associated to the file(s)

    :param  keys: list of keys on the storage
    :returns: successful dict { path : metadata }
             failed dict { path : error message }
             S_ERROR in case of argument problems
    """

    failed = {}
    successful = {}

    for key in keys:
      try:
        response = self.s3_client.head_object(Bucket=self.bucketName, Key=key)
        responseMetadata = response['ResponseMetadata']['HTTPHeaders']
        metadataDict = self._addCommonMetadata(responseMetadata)
        metadataDict['File'] = True
        metadataDict['Size'] = int(metadataDict['content-length'])
        metadataDict['Checksum'] = metadataDict.get('x-amz-meta-checksum', '')

        successful[key] = metadataDict
      except Exception as exp:
        failed[key] = repr(exp)

    return S_OK({'Failed': failed, 'Successful': successful})

  @_extractKeyFromS3Path
  def removeFile(self, keys):
    """ Physically remove the file specified by keys

    A non existing file will be considered as successfully removed

    :param keys: list of keys on the storage
    :returns: Successful dict {path : True}
               Failed dict {path : error message}
               S_ERROR in case of argument problems
    """

    failed = {}
    successful = {}

    for key in keys:
      try:
        self.s3_client.delete_object(Bucket=self.bucketName, Key=key)
        successful[key] = True
      except Exception as exp:
        failed[key] = repr(exp)

    return S_OK({'Failed': failed, 'Successful': successful})

  @_extractKeyFromS3Path
  def getFileSize(self, keys):
    """Get the physical size of the given file

      :param keys: list of keys on the storage
      :returns: Successful dict {path : size}
             Failed dict {path : error message }
             S_ERROR in case of argument problem
    """

    res = self.getFileMetadata(keys, extractKeys=False)  # pylint: disable=unexpected-keyword-arg
    if not res['OK']:
      return res

    failed = res['Value']['Failed']
    successful = {key: metadata['Size'] for key, metadata in res['Value']['Successful'].iteritems()}

    return S_OK({'Successful': successful, 'Failed': failed})

  #############################################################
  #
  # These are the methods for directory manipulation
  #

  def createDirectory(self, urls):
    """ Create directory on the storage.
        S3 does not have such a concept, but we return OK for everything

    :param urls: list of urls to be created on the storage
    :returns: Always Successful dict {path : True }
    """

    return S_OK({'Failed': {}, 'Successful': {url: True for url in urls}})

  @staticmethod
  def notAvailable(*args, **kwargs):
    """ Generic method for unavailable method on S3"""
    return S_ERROR("Functionality not available on S3")

  listDirectory = isDirectory = getDirectory = removeDirectory = getDirectorySize = getDirectoryMetadata = putDirectory = notAvailable

  # def getTransportURL(self, pathDict, protocols):
  #   """ Get a transport URL for a given URL. For a simple storage plugin
  #   it is just returning input URL if the plugin protocol is one of the
  #   requested protocols

  #   :param dict pathDict: URL obtained from File Catalog or constructed according
  #                   to convention
  #   :param protocols: a list of acceptable transport protocols in priority order
  #   :type protocols: `python:list`
  #   """
  #   res = checkArgumentFormat(pathDict)
  #   if not res['OK']:
  #     return res
  #   urls = res['Value']
  #   successful = {}
  #   failed = {}

  #   if protocols and not self.protocolParameters['Protocol'] in protocols:
  #     return S_ERROR('No native protocol requested')

  #   for url in urls:
  #     successful[url] = url

  #   resDict = {'Failed': failed, 'Successful': successful}
  #   return S_OK(resDict)

