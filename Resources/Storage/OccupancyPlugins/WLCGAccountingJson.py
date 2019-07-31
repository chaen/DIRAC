"""
  Defines the plugin to take storage space information given by WLCG Accounting Json
  https://twiki.cern.ch/twiki/bin/view/LCG/AccountingTaskForce#Storage_Space_Accounting
  https://twiki.cern.ch/twiki/pub/LCG/AccountingTaskForce/storage_service_v4.txt
  https://docs.google.com/document/d/1yzCvKpxsbcQC5K9MyvXc-vBF1HGPBk4vhjw3MEXoXf8/edit
"""
import json
import gfal2
import os
import tempfile
import shutil

from DIRAC import gLogger, gConfig
from DIRAC import S_OK, S_ERROR


class WLCGAccountingJson(object):
  """ .. class:: WLCGAccountingJson

  Occupancy plugin to return the space information given by WLCG Accouting Json
  """
  def __init__(self, se):
    self.se = se
    self.log = se.log.getSubLogger('WLCGAccountingJson')

    # assume given SE speaks SRM
    ret = se.getStorageParameters(protocol='srm')
    if not ret['OK']:
      self.log.error(ret['Message'])
      return ret
    self.storageParameters = ret['Value']

  def getOccupancy(self, **kwargs):
    """ Returns the space information given by LCG Accouting Json

        :returns: S_OK with dict (keys: Total, Free)
    """
    print 'Use Plugin'

    if 'StorageName' not in self.storageParameters:
      return S_ERROR('No storage name cannot be retrieve.')
    sename = self.storageParameters['StorageName']

    if 'Host' not in self.storageParameters:
      return S_ERROR('Could not find Host key in StorageParameters of %s' % sename)
    if 'SpaceToken' not in self.storageParameters:
      return S_ERROR('Could not find SpaceToken key in StorageParameters of %s' % sename)
    spacetoken = self.storageParameters['SpaceToken']

    occupancyLFN = kwargs['occupancyLFN']

    if not occupancyLFN:
      return S_ERROR("Failed to get LFN of occupancy json file")

    try:
      # get a json file
      tmpDirName = tempfile.mkdtemp()
      res = self.se.getFile(occupancyLFN, localPath=tmpDirName)

      if not res['OK']:
        return res

      # load the json file
      filePath = os.path.join(tmpDirName, os.path.basename(occupancyLFN))
      with open(filePath, 'r') as occupancyFile:
        occupancyDict = json.load(occupancyFile)

      if 'storageservice' not in occupancyDict:
        return S_ERROR('Could not find storageservice component in %s at %s' % (occupancyLFN, sename))
      storageservice = occupancyDict['storageservice']
      if 'storageshares' not in storageservice:
        return S_ERROR('Could not find storageshares component in %s at %s' % (occupancyLFN, sename))
      storageshares = occupancyDict['storageservice']['storageshares']

    except Exception as e:
      return S_ERROR(repr(e))

    finally:
      # delete temp dir
      shutil.rmtree(tmpDirName)

    storagesharesST = None
    for key in storageshares:
      if key['name'] != spacetoken:
        continue
      storagesharesST = key

    if not storagesharesST:
      return S_ERROR('Could not find %s component in storageshares of %s at %s' % (
          spacetoken, occupancyLFN, sename))

    sTokenDict = {}
    if 'totalsize' not in storagesharesST:
      return S_ERROR('Could not find totalsize key in storageshares')
    sTokenDict['Total'] = storagesharesST['totalsize']

    if 'usedsize' not in storagesharesST:
      return S_ERROR('Could not find usedsize key in storageshares')
    sTokenDict['Free'] = sTokenDict['Total'] - storagesharesST['usedsize']

    return S_OK(sTokenDict)
