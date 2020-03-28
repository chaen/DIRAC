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

"""
Configuration of an S3 storage
Like others, but in protocol S3 add:

SecureConnection: true if https, false otherwise
Aws_access_key_id
Aws_secret_access_key

if the Aws variables are not defined, it will try to go throught the S3GW

"""
__RCSID__ = "$Id$"

import boto3
from botocore.exceptions import ClientError

import copy
import functools
import json
import os
import requests
import shutil
import tempfile

from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Utilities.Adler import fileAdler
from DIRAC.Core.Utilities.Pfn import pfnparse, pfnunparse
from DIRAC.Core.Utilities.ReturnValues import returnSingleResult
from DIRAC.DataManagementSystem.Client.S3GWClient import S3GWClient
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

    aws_access_key_id = parameters.get('Aws_access_key_id')
    aws_secret_access_key = parameters.get('Aws_secret_access_key')
    secureConnection = (parameters.get('SecureConnection', False) == 'True')
    proto = 'https' if secureConnection else 'http'
    endpoint_url = '%s://%s:%s' % (proto, parameters['Host'], parameters.get('Port', 443))
    self.bucketName = parameters['Path']

    self.s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)

    self.srmSpecificParse = False
    self.pluginName = 'S3'

    # if we have the credentials loaded, we can perform direct access
    # otherwise we have to go through the S3GW
    self.directAccess = aws_access_key_id and aws_secret_access_key
    self.s3GWClient = S3GWClient()

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

    # If we have a direct access, we can just do the request directly
    if self.directAccess:
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
    else:
      # Otherwise, ask the gw for a presigned URL,
      # and perform it with requests
      for key in keys:
        try:
          res = self.s3GWClient.createPresignedUrl(self.name, 'head_object', key)
          if not res['OK']:
            failed[key] = res['Message']
            continue
          presignedURL = res['Value']
          response = requests.get(presignedURL)
          if response.status_code == 200:
            successful[key] = True
          elif response.status_code == 404:  # not found
            successful[key] = False
          else:
            failed[key] = response.reason
        except Exception as e:
          failed[key] = repr(e)

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
        if self.directAccess:
          self.s3_client.download_file(self.bucketName, src_key, dest_file)
        else:
          res = self.s3GWClient.createPresignedUrl(self.name, 'get_object', src_key)
          if not res['OK']:
            failed[src_key] = res['Message']
            continue
          presignedURL = res['Value']
          # Stream download to save memory
          # https://requests.readthedocs.io/en/latest/user/advanced/#body-content-workflow
          with requests.get(presignedURL, stream=True) as r:
            r.raise_for_status()
            with open(dest_file, 'wb') as f:
              for chunk in r.iter_content():
                if chunk:  # filter out keep-alive new chuncks
                  f.write(chunk)

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

        if self.directAccess:

          with open(src_file) as src_fd:
            self.s3_client.put_object(
                Body=src_fd,
                Bucket=self.bucketName,
                Key=dest_key,
                Metadata={
                    'Checksum': cks})

        else:
          res = self.s3GWClient.createPresignedUrl(self.name, 'put_object', dest_key)

          if not res['OK']:
            raise res

          presignedResponse = res['Value']
          presignedURL = presignedResponse['url']
          presignedFields = presignedResponse['fields']
          with open(src_file, 'rb') as src_fd:
            files = {'file': (dest_key, src_fd)}
            response = requests.post(presignedURL, data=presignedFields,
                                     files=files)

            if not response.ok:
              raise Exception(response.reason)

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
        if self.directAccess:
          response = self.s3_client.head_object(Bucket=self.bucketName, Key=key)
          responseMetadata = response['ResponseMetadata']['HTTPHeaders']
        else:
          res = self.s3GWClient.createPresignedUrl(self.name, 'head_object', key)
          if not res['OK']:
            failed[key] = res['Message']
            continue
          presignedURL = res['Value']
          response = requests.get(presignedURL)
          if not response.ok:
            raise Exception(response.reason)

          # Although the interesting fields are the same as when doing the query directly
          # the case is not quite the same, so make it lower everywhere
          responseMetadata = {headerKey.lower(): headerVal for headerKey, headerVal in response.headers.iteritems()}

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
        if self.directAccess:
          self.s3_client.delete_object(Bucket=self.bucketName, Key=key)
        else:
          res = self.s3GWClient.createPresignedUrl(self.name, 'delete_object', key)
          if not res['OK']:
            failed[key] = res['Message']
            continue
          presignedURL = res['Value']
          response = requests.delete(presignedURL)
          if not response.ok:
            raise Exception(response.reason)

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

  def createPresignedUrl(self, methodName, objectName, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param methodName: name of the method for which to generate a presigned URL
    :param objectName: key for which to generate a presigned URL
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    log = LOG.getSubLogger('createPresignedUrl')

    try:
      if methodName != 'put_object':
        response = self.s3_client.generate_presigned_url(ClientMethod=methodName,
                                                         Params={'Bucket': self.bucketName,
                                                                 'Key': objectName},
                                                         ExpiresIn=expiration)
      else:
        response = self.s3_client.generate_presigned_post(self.bucketName, objectName, ExpiresIn=expiration)
    except ClientError as e:
      log.debug(e)
      return S_ERROR(repr(e))

    # The response contains the presigned URL
    return S_OK(response)
