# specs:
# * https://twiki.cern.ch/twiki/bin/view/LCG/AccountingTaskForce#Storage_Space_Accounting
# * https://twiki.cern.ch/twiki/pub/LCG/AccountingTaskForce/storage_service_v4.txt
# * https://docs.google.com/document/d/1yzCvKpxsbcQC5K9MyvXc-vBF1HGPBk4vhjw3MEXoXf8/edit

import json
import os
import shutil
import tempfile

import gfal2  # pylint: disable=import-error
from DIRAC import gLogger
from DIRAC.Core.Utilities.Pfn import pfnunparse
from DIRAC.Core.Utilities.ReturnValues import returnSingleResult, S_OK, S_ERROR

LOG = gLogger.getSubLogger(__name__)


class LcgAccounting(object):

  def __init__(self, seObj):
    self.seObj = seObj

  def _readJsonFile(self):
    # occupancyFile = self.se.options['OccupancyLFN']
    occupancyFile = '/eos/lhcb/proc/accounting'

    try:

      # download the file locally
      tmpDirName = tempfile.mkdtemp()
      for storage in self.seObj.storages:
        res = storage.updateURL(occupancyFile)
        if not res['OK']:
          return res
        occupancyURL = res['Value']
        filePath = os.path.join(tmpDirName, os.path.basename(occupancyFile))

        # because this JSON file is sometimes not a real file that does not
        # behave like it (e.g. https://ggus.eu/index.php?mode=ticket_info&ticket_id=141580)
        # we can't use all the nice checksum logic and filesize checks we have in DIRAC.
        # So do it by hand...

        try:
          ctx = gfal2.creat_context()
          params = ctx.transfer_parameters()
          params.overwrite = True
          ctx.filecopy(params, occupancyURL, 'file://' + filePath)
        except gfal2.GError as e:

          detailMsg = "Failed to copy file %s to destination url %s: [%d] %s" % (
              occupancyURL, filePath, e.code, e.message)
          LOG.debug("Exception while copying", detailMsg)
          continue

        # Read its json content
        with open(filePath, 'r') as fp:
          return S_OK(json.load(fp))

    except BaseException as e:
      return S_ERROR(repr(e))

    finally:
      # Clean the temporary dir
      shutil.rmtree(tmpDirName)

  def getOccupancy(self):
    res = self._readJsonFile()

    if not res['OK']:
      return res

    jsonContent = res['Value']
    allShares = jsonContent['storageservice']['storageshares']

    spaceReservation = self.seObj.options.get('SpaceReservation')
    # spaceReservation = 'LHCb-EOS'
    # spaceReservation = None

    seShare = None

    # If we have the name already of the space reservation, it's easy,
    # we just find the good share
    if spaceReservation:
      for share in allShares:
        if share.get('name') == spaceReservation:
          seShare = share
          break

    # Otherwise it is tricky and we need to find the share best matching the basePath of the storage
    else:
      # Basically, look for the longest commonpath between the share path and the base path of the SE
      shareLen = []
      # Go with the assumption that every protocol has the same basepath, and just take the first one
      basePath = self.seObj.storages[0].getParameters()['Path']
      # Construct a list of tuple (share, length of common path)
      for share in allShares:
        shareLen.append((share, len(os.path.commonprefix([share['path'][0], basePath]))))
      # Find the longest of the longest common path
      seShare = max(shareLen, key=lambda x: x[1])[0]
      spaceReservation = seShare.get('name')
      print seShare

    usedsize = seShare['usedsize']
    total = seShare['totalsize']
    return {'Total': total, 'Free': total - usedsize, 'SpaceReservation': spaceReservation}

    pass
