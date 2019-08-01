"""
  Defines the plugin to take storage space information given by WLCG Accounting Json
  https://twiki.cern.ch/twiki/bin/view/LCG/AccountingTaskForce#Storage_Space_Accounting
  https://twiki.cern.ch/twiki/pub/LCG/AccountingTaskForce/storage_service_v4.txt
  https://docs.google.com/document/d/1yzCvKpxsbcQC5K9MyvXc-vBF1HGPBk4vhjw3MEXoXf8
"""
import json
import gfal2  # pylint: disable=import-error
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
    self.name = self.se.name

  def getOccupancy(self, **kwargs):
    """ Returns the space information given by LCG Accouting Json

        :returns: S_OK with dict (keys: Total, Free)
    """
    spaceReservation = self.se.options.get('SpaceReservation')
    if not spaceReservation:
      self.log.debug("Check SpaceToken instead of SpaceReservation because it is not defined in CS")
      for storage in self.se.storages:
        SEparams = storage.getParameters()
        if not SEparams:
          return S_ERROR('Could not get storage parameters at %s' % (self.name))
        if 'SpaceToken' not in SEparams:
          return S_ERROR('Could not find SpaceToken key in storage parameters at %s' % (self.name))
        spaceReservation = SEparams['SpaceToken']

    # occupancyLFN = '/dpm/na.infn.it/home/belle/storagesummary.json'

    if not occupancyLFN:
      return S_ERROR("Failed to get occupancyLFN")

    tmpDirName = tempfile.mkdtemp()
    filePath = os.path.join(tmpDirName, os.path.basename(occupancyLFN))

    for storage in self.se.storages:
      try:
        ctx = gfal2.creat_context()
        params = ctx.transfer_parameters()
        params.overwrite = True
        res = storage.updateURL(occupancyLFN)
        if not res['OK']:
          return res
        occupancyURL = res['Value']
        ctx.filecopy(params, occupancyURL, 'file://' + filePath)

      except gfal2.GError as e:
        detailMsg = "Failed to copy file %s to destination url %s: [%d] %s" % (
            occupancyURL, filePath, e.code, e.message)
        self.log.debug("Exception while copying", detailMsg)
        continue

      else:
        break

    if not os.path.isfile(filePath):
      return S_ERROR('No WLCGAccountingJson file of %s is downloaded.' % (self.name))

    with open(filePath, 'r') as path:
      occupancyDict = json.load(path)

    # delete temp dir
    shutil.rmtree(tmpDirName)

    if 'storageservice' not in occupancyDict:
      return S_ERROR('Could not find storageservice component in %s at %s' % (occupancyLFN, self.name))
    storageService = occupancyDict['storageservice']

    if 'storageshares' not in storageService:
      return S_ERROR('Could not find storageshares component in %s at %s' % (occupancyLFN, self.name))
    storageShares = occupancyDict['storageservice']['storageshares']

    storageSharesSR = None
    for key in storageShares:
      if key['name'] == spaceReservation:
        storageSharesSR = key
        break
    if not storageSharesSR:
      return S_ERROR('Could not find %s component in storageshares of %s at %s' % (
          spaceReservation, occupancyLFN, self.name))

    sTokenDict = {}
    if 'totalsize' not in storageSharesSR:
      return S_ERROR('Could not find totalsize key in %s storageshares' % spaceReservation)
    sTokenDict['Total'] = storageSharesSR['totalsize']

    if 'usedsize' not in storageSharesSR:
      return S_ERROR('Could not find usedsize key in %s storageshares' % spaceReservation)
    sTokenDict['Free'] = sTokenDict['Total'] - storageSharesSR['usedsize']

    return S_OK(sTokenDict)
