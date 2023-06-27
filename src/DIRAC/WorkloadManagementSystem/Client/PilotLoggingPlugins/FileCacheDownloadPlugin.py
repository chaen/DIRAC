"""
File cache pilot log downloader.
"""
import os
import tempfile
from DIRAC import S_OK, S_ERROR, gLogger, gConfig
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.Core.Utilities.Proxy import executeWithUserProxy
from DIRAC.WorkloadManagementSystem.Client.PilotLoggingPlugins.DownloadPlugin import DownloadPlugin

sLog = gLogger.getSubLogger(__name__)


class FileCacheDownloadPlugin(DownloadPlugin):
    """
    Class to handle log file download from an SE
    """

    def __init__(self):
        """
        Sets the pilot log files location for a WebServer.

        """
        pass

    def getRemotePilotLogs(self, pilotStamp, vo=None):
        """
        Pilot log getter method, carrying the unique pilot identity and a VO name.

        :param str pilotStamp: pilot stamp.
        :param str vo: VO name of a user/pilot which generated the logs.
        :return: S_OK or S_ERROR
        :rtype: dict
        """

        opsHelper = Operations(vo=vo)
        uploadPath = opsHelper.getValue("Pilot/UploadPath", "")
        lfn = os.path.join(uploadPath, pilotStamp + ".log")
        sLog.info("LFN to download: ", lfn)
        filepath = tempfile.TemporaryDirectory().name
        os.makedirs(filepath, exist_ok=True)
        # get pilot credentials which uploaded logs to an external storage:
        res = opsHelper.getOptionsDict("Shifter/DataManager")
        if not res["OK"]:
            message = f"No shifter defined for VO: {vo} - needed to retrieve the logs !"
            sLog.error(message)
            return S_ERROR(message)

        proxyUser = res["Value"].get("User")
        proxyGroup = res["Value"].get("Group")

        sLog.info(f"Proxy used for retrieving pilot logs: VO: {vo}, User: {proxyUser}, Group: {proxyGroup}")

        res = self._downloadLogs(  # pylint: disable=unexpected-keyword-arg
            lfn, filepath, proxyUserName=proxyUser, proxyUserGroup=proxyGroup
        )
        sLog.debug("getFile result:", res)
        if not res["OK"]:
            sLog.error(f"Failed to contact storage")
            return res
        if lfn in res["Value"]["Failed"]:
            sLog.error("Failed to retrieve a log file:", res["Value"]["Failed"])
            return S_ERROR(f"Failed to retrieve a log file: {res['Value']['Failed']}")
        try:
            filename = os.path.join(filepath, pilotStamp + ".log")
            with open(filename) as f:
                stdout = f.read()
        except FileNotFoundError as err:
            sLog.error(f"Error opening a log file:{filename}", err)
            return S_ERROR(repr(err))

        resultDict = {}
        resultDict["StdOut"] = stdout
        return S_OK(resultDict)

    @executeWithUserProxy
    def _downloadLogs(self, lfn, filepath):
        return DataManager().getFile(lfn, destinationDir=filepath)
