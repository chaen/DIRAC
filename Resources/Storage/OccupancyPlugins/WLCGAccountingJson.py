import json
import gfal2
import os
import tempfile
import shutil


from DIRAC import gLogger, gConfig
from DIRAC import S_OK, S_ERROR

class WLCGAccountingJson(object):
  def __init__(self, se):
    self.se = se
    self.log = se.log.getSubLogger('WLCGAccountingJson')

    # assume given SE speaks SRM
    ret = se.getStorageParameters(protocol='srm')
    if not ret['OK']:
      self.log.error(ret['Message'])
      return ret

    storageParameters = ret['Value']

    if 'StorageName' not in storageParameters:
      return S_ERROR('No storage name cannot be retrieve.')

    self.name = storageParameters['StorageName']

    if 'Host' not in storageParameters:
      return S_ERROR('Could not find Host key in StorageParameters of %s'% self.name)
    if 'SpaceToken' not in storageParameters:
      return S_ERROR('Could not find SpaceToken key in StorageParameters of %s'% self.name)
    self.spacetoken = storageParameters['SpaceToken']
    

  def getOccupancy(self, **kwargs):
    """ Returns the space information given by json file
        :returns: S_OK with dict (keys: Total, Free)
    """
    print 'Use Plugin'
    occupancyLFN = kwargs['occupancyLFN']

    if not occupancyLFN:
      return S_ERROR("Failed to get LFN of occupancy json file")

    try:
      #get a json file
      tmpDirName = tempfile.mkdtemp()
      res = self.se.getFile(occupancyLFN, localPath=tmpDirName)
      """
      ctx = gfal2.creat_context()
      params = ctx.transfer_parameters()
      params.overwrite = True
      filePath = os.path.join(tmpDirName, os.path.basename(occupancyLFN))
      ctx.filecopy(params, occupancyLFN, 'file://')
      return
      """
      if not res['OK']:
        return res

      #load the json file
      filePath = os.path.join(tmpDirName, os.path.basename(occupancyLFN))
      with open(filePath, 'r') as occupancyFile:
        occupancyDict = json.load(occupancyFile)

      if 'storageservice' not in occupancyDict:
        return S_ERROR('Could not find storageservice component in %s at %s'% (occupancyLFN, self.name))
      storageservice = occupancyDict['storageservice']
      if 'storageshares' not in storageservice:
        return S_ERROR('Could not find storageshares component in %s at %s'% (occupancyLFN, self.name))
      storageshares = occupancyDict['storageservice']['storageshares']
      
    except Exception as e:
      return S_ERROR(repr(e))
    
    finally:
      #delete temp dir
      shutil.rmtree(tmpDirName)

    storagesharesST = None
    for key in storageshares:
      if key['name'] != self.spacetoken:
        continue
      storagesharesST = key

    if not storagesharesST:
      return S_ERROR('Could not find %s component in storageshares of %s at %s'% (self.spacetoken, occupancyLFN, self.name))

    sTokenDict = {}
    if 'totalsize' not in storagesharesST:
      return S_ERROR('Could not find totalsize key in storageshares');
    sTokenDict['Total'] = float(storagesharesST.get('totalsize', 0))

    if 'usedsize' not in storagesharesST:
      return S_ERROR('Could not find usedsize key in storageshares');
    sTokenDict['Free'] = sTokenDict['Total'] - float(storagesharesST.get('usedsize', 0))

    return S_OK(sTokenDict)
