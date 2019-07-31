#!/usr/bin/env python
"""Script to obtain release notes from PRs for DIRAC or other packages

Use the command line parameters or a config file to configure the options.
The long names used on the command line can also be used in the config file

To pick up release notes from gitlab follow this example

  [ReleaseNotes]
  gitlabProjectID = 320
  gitlab = True
  branches = Rel-v29r0, master
  date = 2019-01-01
  gitlabUrl = https://gitlab.cern.ch

To extend the coverter list of short system names to their full equivalent beyond what is configured for DIRAC
add this section to the config file

  [ReleaseNotes.Categories]
  ITS = ILCTransformationSystem
  CI = Testing
  All = Core

"""

from __future__ import print_function
from collections import defaultdict
from datetime import datetime, timedelta
import argparse
from pprint import pformat
import logging
import textwrap
import requests

try:
  from configparser import ConfigParser  # python3
except ImportError:
  from ConfigParser import SafeConfigParser as ConfigParser  # python2


G_ERROR = textwrap.dedent("""
                          ***********************
                          Failed to import GITHUBTOKEN please!
                          Point the pythonpath to your GitTokens.py file which contains
                          your "Personal Access Token" for Github

                          I.e.:
                          Filename: GitTokens.py
                          Content:
                          ```
                          GITHUBTOKEN = "e0b83063396fc632646603f113437de9"
                          ```
                          (without the triple quotes)
                          ***********************
                          """)

SESSION = requests.Session()

logging.basicConfig(level=logging.WARNING, format='%(levelname)-5s - %(name)-8s: %(message)s')
LOGGER = logging.getLogger('GetReleaseNotes')


def listify(values):
  """Turn a comma separated string into a list."""
  if isinstance(values, list):
    return values
  return [entry.strip() for entry in values.split(',') if entry]


def githubSetup():
  """Import the GITHUB Token and add proper header."""
  LOGGER.info('Setting up GITHUB')
  try:
    from GitTokens import GITHUBTOKEN
    SESSION.headers.update({'Authorization': 'token %s ' % GITHUBTOKEN})
  except ImportError:
    raise ImportError(G_ERROR)


def gitlabSetup():
  """Import the GITLAB Token and add proper header."""
  LOGGER.info('Setting up GitLab')
  try:
    from GitTokens import GITLABTOKEN
    SESSION.headers.update({'PRIVATE-TOKEN': GITLABTOKEN})
  except ImportError:
    raise ImportError(G_ERROR)


def req2Json(url, parameterDict=None, requestType='GET'):
  """Call to github API using requests package."""
  log = LOGGER.getChild("Requests")
  log.debug("Running %s with %s ", requestType, parameterDict)
  req = getattr(SESSION, requestType.lower())(url, json=parameterDict)
  if req.status_code not in (200, 201):
    log.error("Unable to access API: %s", req.text)
    raise RuntimeError("Failed to access API")

  log.debug("Result obtained:\n %s", pformat(req.json()))
  return req.json()


def getCommands(*args):
  """Create a flat list.

  :param *args: list of strings or tuples/lists
  :returns: flattened list of strings
  """
  comList = []
  for arg in args:
    if isinstance(arg, (tuple, list)):
      comList.extend(getCommands(*arg))
    else:
      comList.append(arg)
  return comList


def _parsePrintLevel(level):
  """Translate debug count to logging level."""
  level = level if level <= 2 else 2
  return [logging.WARNING,
          logging.INFO,
          logging.DEBUG,
          ][level]


def parseForReleaseNotes(commentBody):
  """Look for "BEGINRELEASENOTES / ENDRELEASENOTES" and extend releaseNoteList if there are entries."""
  if not all(tag in commentBody for tag in ("BEGINRELEASENOTES", "ENDRELEASENOTES")):
    return ''
  return commentBody.split("BEGINRELEASENOTES")[1].split("ENDRELEASENOTES")[0]


class GithubInterface(object):
  """Object to make calls to github API."""

  def __init__(self, owner='DiracGrid', repo='Dirac'):
    """Set default values to parse release notes for DIRAC."""
    self.owner = owner
    self.repo = repo
    self.branches = ['Integration', 'rel-v6r21']
    self.openPRs = False
    self.startDate = str(datetime.now() - timedelta(days=14))[:10]
    self.printLevel = logging.WARNING
    logging.getLogger().setLevel(self.printLevel)
    self.useGitlab = False
    self.useGithub = True

    self.gitlabUrl = 'https://gitlab.cern.ch'
    self.glProjectID = 0

    # translate abbreviations to full system names.
    self.names = {'API': 'Interfaces',
                  'AS': 'AccountingSystem',
                  'CS': 'ConfigurationSystem',
                  'Config': 'ConfigurationSystem',
                  'Configuration': 'ConfigurationSystem',
                  'DMS': 'DataManagementSystem',
                  'DataManagement': 'DataManagementSystem',
                  'FS': 'FrameworkSystem',
                  'Framework': 'FrameworkSystem',
                  'MS': 'MonitoringSystem',
                  'Monitoring': 'MonitoringSystem',
                  'RMS': 'RequestManagementSystem',
                  'RequestManagement': 'RequestManagementSystem',
                  'RSS': 'ResourceStatusSystem',
                  'ResourceStatus': 'ResourceStatusSystem',
                  'SMS': 'StorageManagamentSystem',
                  'StorageManagement': 'StorageManagamentSystem',
                  'TS': 'TransformationSystem',
                  'TMS': 'TransformationSystem',
                  'Transformation': 'TransformationSystem',
                  'WMS': 'WorkloadManagementSystem',
                  'Workload': 'WorkloadManagementSystem',
                  }

  def getFullSystemName(self, name):
    """Return full name based on abbrevation for system."""
    return self.names.get(name, name)

  @property
  def _options(self):
    """Return options dictionary."""
    return dict(owner=self.owner, repo=self.repo)

  def checkRate(self):
    """Return the result for check_rate call."""
    if self.useGitlab:
      return
    rate = req2Json(url="https://api.github.com/rate_limit")
    LOGGER.getChild("Rate").info("Remaining calls to github API are %s of %s",
                                 rate['rate']['remaining'], rate['rate']['limit'])

  def parseOptions(self):
    """Parse the command line options."""
    log = LOGGER.getChild('Options')

    conf_parser = argparse.ArgumentParser('Dirac Release Notes',
                                          formatter_class=argparse.RawTextHelpFormatter,
                                          add_help=False,
                                          )
    conf_parser.add_argument('-c', '--configFile', help='Specify config file', metavar='FILE', dest='configFile')
    conf_parser.add_argument('-d', '--debug', action='count', dest='debug', help='d, dd, ddd', default=0)
    args, _remaining_argv = conf_parser.parse_known_args()
    self.printLevel = _parsePrintLevel(args.debug)
    LOGGER.setLevel(self.printLevel)
    log.debug('Parsing options')
    defaults = {}
    if args.configFile:
      log.debug('Parsing configFile: %r', args.configFile)
      config = ConfigParser()
      config.optionxform = str
      config.read([args.configFile])
      defaults.update(dict(config.items('ReleaseNotes')))
      log.info('Settings from config file: %r', defaults)

      if config.has_section('ReleaseNotes.Categories'):
        items = config.items('ReleaseNotes.Categories')
        log.info('Found Categories: %r', items)
        for short, system in items:
          self.names[short] = system

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     # Inherit options from config_parser
                                     parents=[conf_parser])
    parser.add_argument("--branches", action="store", default=self.branches,
                        dest="branches", nargs='+',
                        help="branches to get release notes for")

    parser.add_argument("--date", action="store", default=self.startDate, dest="date",
                        help="date after which PRs are checked, default (two weeks ago): %s" % self.startDate)

    parser.add_argument("--openPRs", action="store_true", dest="openPRs", default=self.openPRs,
                        help="get release notes for open (unmerged) PRs, for testing purposes")

    parser.add_argument("-r", "--repo", action="store", dest="repo", help="Github repository to check: [Group/]Repo",
                        default='DiracGrid/Dirac')

    parser.add_argument('-g', '--gitlab', action='store_true', dest='gitlab', help='Using gitlab instance',
                        default=False)

    parser.add_argument('-u', '--gitlabUrl', action='store', dest='gitlabUrl', help='URL of the gitlab instance',
                        default='https://gitlab.cern.ch')

    parser.add_argument('-i', '--gitlabProjectID', action='store', dest='gitlabProjectID',
                        help='ID of the project in Gitlab', default='0')
    parser.set_defaults(**defaults)

    parsed = parser.parse_args()

    for var, val in sorted(vars(parsed).items()):
      log.info('Parsed options: %s = %s', var, pformat(val))

    self.branches = listify(parsed.branches)
    log.info('Getting PRs for: %s', self.branches)
    self.startDate = parsed.date
    log.info('Starting from: %s', self.startDate)
    self.openPRs = parsed.openPRs
    log.info('Also including openPRs?: %s', self.openPRs)

    self.useGitlab = parsed.gitlab if isinstance(parsed.gitlab, bool) else parsed.gitlab.lower() == 'true'
    self.useGithub = not self.useGitlab

    self.gitlabUrl = parsed.gitlabUrl
    self.glProjectID = int(parsed.gitlabProjectID)

    repo = parsed.repo
    repos = repo.split('/')
    if len(repos) == 1:
      self.repo = repo
    elif len(repos) == 2:
      self.owner = repos[0]
      self.repo = repos[1]
    else:
      raise RuntimeError("Cannot parse repo option: %s" % repo)

    for var, val in sorted(vars(parsed).items()):
      log.info('Using options: %s = %s', var, pformat(val))

  def _github(self, action):
    """Return the url to perform actions on github.

    :param str action: command to use in the gitlab API, see documentation there
    :returns: url to be used
    """
    log = LOGGER.getChild('GitHub')
    options = dict(self._options)
    options["action"] = action
    ghURL = "https://api.github.com/repos/%(owner)s/%(repo)s/%(action)s" % options
    log.debug('Calling: %s', ghURL)
    return ghURL

  def _gitlab(self, action):
    """Return URL for gitlab using proper ID and action needed

    :param str action: command to use in the gitlab API, see documentation there
    :returns: url to be used by curl
    """
    return '%s/api/v4/projects/%d/%s' % (self.gitlabUrl, self.glProjectID, action)

  def getGitlabPRs(self, state='opened'):
    """Get PRs in the gitlab repository."""
    glURL = self._gitlab('merge_requests?state=%s' % state)
    return req2Json(glURL)

  def getGithubPRs(self, state="open", mergedOnly=False, perPage=100):
    """Get all PullRequests from github.

    :param str state: state of the PRs, open/closed/all, default open
    :param bool merged: if PR has to be merged, only sensible for state=closed
    :returns: list of githubPRs
    """
    url = self._github("pulls?state=%s&per_page=%s" % (state, perPage))
    prs = req2Json(url=url)

    if not mergedOnly:
      return prs

    # only merged PRs
    prsToReturn = []
    for pr in prs:
      if pr.get('merged_at', None) is not None:
        prsToReturn.append(pr)

    return prsToReturn

  def getNotesFromPRs(self, prs):
    """Loop over prs, get base branch, get PR comment and collate into dictionary.

    :returns: dict of branch:dict(#PRID, dict(comment, mergeDate))
    """
    rawReleaseNotes = defaultdict(dict)

    for pr in prs:
      if self.useGithub:
        baseBranch = pr['base']['label'][len(self.owner) + 1:]
        if baseBranch not in self.branches:
          continue
        comment = parseForReleaseNotes(pr['body'])
        prID = pr['number']

      if self.useGitlab:
        baseBranch = pr['target_branch']
        if baseBranch not in self.branches:
          continue
        comment = parseForReleaseNotes(pr['description'])
        prID = pr['iid']

      mergeDate = pr.get('merged_at', None)
      mergeDate = mergeDate if mergeDate is not None else '9999-99-99'
      if mergeDate[:10] < self.startDate:
        continue
      rawReleaseNotes[baseBranch].update({prID: dict(comment=comment, mergeDate=mergeDate)})

    return rawReleaseNotes

  def getReleaseNotes(self):
    """Create the release notes."""
    if self.useGithub:
      githubSetup()
      if self.openPRs:
        prs = self.getGithubPRs(state='open', mergedOnly=False)
      else:
        prs = self.getGithubPRs(state='closed', mergedOnly=True)
    elif self.useGitlab:
      gitlabSetup()
      if self.openPRs:
        prs = self.getGitlabPRs(state='all')
      else:
        prs = self.getGitlabPRs(state='merged')

    prs = self.getNotesFromPRs(prs)
    releaseNotes = self.collateReleaseNotes(prs)
    print(releaseNotes)
    self.checkRate()

  def collateReleaseNotes(self, prs):
    """Put the release notes in the proper order.

    FIXME: Tag numbers could be obtained by getting the last tag with a name similar to
    the branch, will print out just the base branch for now.
    """
    releaseNotes = ''
    prMarker = '#' if self.useGithub else '!'
    for baseBranch, pr in prs.iteritems():
      releaseNotes += '[%s]\n\n' % baseBranch
      systemChangesDict = defaultdict(list)
      for prid, content in pr.iteritems():
        notes = content['comment']
        system = ''
        for line in notes.splitlines():
          line = line.strip()
          if line.startswith('*'):
            system = self.getFullSystemName(line.strip('*:').strip())
          elif line:
            splitline = line.split(':', 1)
            if splitline[0] == splitline[0].upper() and len(splitline) > 1:
              line = '%s: (%s%s) %s' % (splitline[0], prMarker, prid, splitline[1].strip())
            systemChangesDict[system].append(line)

      for system, changes in systemChangesDict.iteritems():
        if system:
          releaseNotes += "*%s\n\n" % system
        releaseNotes += "\n".join(changes)
        releaseNotes += "\n\n"
      releaseNotes += "\n"

    return releaseNotes


if __name__ == "__main__":

  RUNNER = GithubInterface()
  try:
    RUNNER.parseOptions()
  except RuntimeError as e:
    LOGGER.error("Error during argument parsing: %s", e)
    exit(1)

  try:
    RUNNER.getReleaseNotes()
  except RuntimeError as e:
    LOGGER.error("Error during runtime: %s", e)
    exit(1)
