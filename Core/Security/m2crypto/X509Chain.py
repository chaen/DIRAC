""" X509Chain is a class for managing X509 chains with their Pkeys

Link to the RFC 3820: https://tools.ietf.org/html/rfc3820
In particular, limited proxy: https://tools.ietf.org/html/rfc3820#section-3.8

"""
__RCSID__ = "$Id$"

import copy
import os
import stat
import tempfile
import hashlib

import re

import M2Crypto

from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Utilities import DErrno
from DIRAC.Core.Utilities.Decorators import executeOnlyIf
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.Core.Security.m2crypto import PROXY_OID, LIMITED_PROXY_OID, DIRAC_GROUP_OID
from DIRAC.Core.Security.m2crypto.X509Certificate import X509Certificate


# Decorator to check that _certList is not empty
needCertList = executeOnlyIf('_certList', S_ERROR(DErrno.ENOCHAIN))
# Decorator to check that the PKey has been loaded
needPKey = executeOnlyIf('_keyObj', S_ERROR(DErrno.ENOPKEY))


class X509Chain(object):
  """
    An X509Chain is basically a list of X509Certificate object, as well as a PKey object,
    which is associated to the X509Certificate the lowest in the chain.

    This is what you will want to use for user certificate (because they will turn into proxy....), and for
    proxy.

    A priori, once we get ride of pyGSI, we could even meld the X509Certificate into this one, and use the X509Chain
    for host certificates. After all, a certificate is nothing but a chain of length 1...

  """

  def __init__(self, certList=False, keyObj=False):
    """
        C'tor

        :param certList: list of X509Certificate to constitute the chain
        :param keyObj: ~M2Crypto.EVP.PKey object. The public or public/private key associated to the last certificate of the chain

    """

    # __isProxy is True if this chain represents a proxy
    self.__isProxy = False
    # Whether the proxy is limited or not
    self.__isLimitedProxy = False

    self.__firstProxyStep = 0

    # Cache for sha1 hash of the object
    # This is just used as a unique identifier for
    # indexing in the ProxyCache
    self.__hash = False

    # List of X509Certificate constituing the chain
    self._certList = []

    # Place holder for the EVP.PKey object
    self._keyObj = None

    if certList:
      # copy the content of the list, without copying the objects themselves
      self._certList = copy.copy(certList)
      # Immediately check if it is a proxy
      self.__checkProxyness()

    if keyObj:
      self._keyObj = keyObj

  @classmethod
  def instanceFromFile(cls, chainLocation):
    """ Class method to generate a X509Chain from a file

        :param chainLocation: path to the file

        :returns: S_OK(X509Chain)
    """
    chain = cls()
    result = chain.loadChainFromFile(chainLocation)
    if not result['OK']:
      return result

    return S_OK(chain)

  @staticmethod
  def generateX509ChainFromSSLConnection(sslConnection):
    """ Returns an instance of X509Chain from the SSL connection

        :param sslConnection: ~M2Crypto.SSl.Connection instance

        :returns: a X509Chain instance
    """
    certList = []

    certStack = sslConnection.get_peer_cert_chain()
    for cert in certStack:
      certList.append(X509Certificate(x509Obj=cert))

    # Servers don't receive the whole chain, the last cert comes alone
    # if not self.infoDict['clientMode']:
    if True:
      certList.insert(0, X509Certificate(x509Obj=sslConnection.get_peer_cert()))
    peerChain = X509Chain(certList=certList)

    return peerChain

  def loadChainFromFile(self, chainLocation):
    """
      Load a x509 chain from a pem file

      :param chainLocation: path the the file

      :returns: S_OK/S_ERROR
    """
    try:
      with open(chainLocation) as fd:
        pemData = fd.read()
    except IOError as e:
      return S_ERROR(DErrno.EOF, "%s: %s" % (chainLocation, repr(e).replace(',)', ')')))
    return self.loadChainFromString(pemData)

  def loadChainFromString(self, data):
    """
      Load a x509 cert from a string containing the pem data

      :param data: data representing the chain of certificate in the

      Return : S_OK / S_ERROR
    """
    try:
      self._certList = self.__certListFromPemString(data)
    except Exception as e:
      return S_ERROR(DErrno.ECERTREAD, "%s" % repr(e).replace(',)', ')'))

    if not self._certList:
      return S_ERROR(DErrno.EX509)

    # Update internals
    self.__checkProxyness()
    return S_OK()

  @staticmethod
  def __certListFromPemString(certString):
    """
    Create certificates list from string. String sould contain certificates, just like plain text proxy file.
    """
    # To get list of X509 certificates (not X509 Certificate Chain) from string it has to be parsed like that
    # (constructors are not able to deal with big string)
    certList = []
    for cert in re.findall(r"(-----BEGIN CERTIFICATE-----((.|\n)*?)-----END CERTIFICATE-----)", certString):
      certList.append(X509Certificate(certString=cert[0]))
    return certList


  # Not used in m2crypto version
  # def setChain(self, certList):
  #   """
  #   Set the chain
  #   Return : S_OK / S_ERROR
  #   """
  #   self._certList = certList
  #   self.__loadedChain = True
  #   return S_OK()

  def loadKeyFromFile(self, chainLocation, password=False):
    """
        Load a PKey from a pem file

        :param chainLocation: path to the file
        :param password: password to decode they file.

        :returns: S_OK / S_ERROR
    """
    try:
      with open(chainLocation) as fd:
        pemData = fd.read()
    except Exception as e:
      return S_ERROR(DErrno.EOF, "%s: %s" % (chainLocation, repr(e).replace(',)', ')')))
    return self.loadKeyFromString(pemData, password)

  def loadKeyFromString(self, pemData, password=False):
    """
      Load a PKey from a string containing the pem data

      :param pemData: pem data of the key, potentially encoded with the password
      :param password: password to decode they file.

      :returns: S_OK / S_ERROR
    """
    self._keyObj = None
    try:
      self._keyObj = M2Crypto.EVP.load_key_string(pemData, lambda x: password)
    except Exception as e:
      return S_ERROR(DErrno.ECERTREAD, "%s (Probably bad pass phrase?)" % repr(e).replace(',)', ')'))

    return S_OK()

  def setPKey(self, pkeyObj):
    """
    Set the chain
    Return : S_OK / S_ERROR
    """
    self._keyObj = pkeyObj
    return S_OK()

  def loadProxyFromFile(self, chainLocation):
    """
      Load a Proxy from a pem file, that is both the Cert chain and the PKey

      :param chainLocation: path to the proxy file

      :returns: S_OK  / S_ERROR
    """
    try:
      with open(chainLocation) as fd:
        pemData = fd.read()
    except Exception as e:
      return S_ERROR(DErrno.EOF, "%s: %s" % (chainLocation, repr(e).replace(',)', ')')))
    return self.loadProxyFromString(pemData)

  def loadProxyFromString(self, pemData):
    """
    Load a Proxy from a pem buffer, that is both the Cert chain and the PKey

    :param pemData: PEM encoded cert chain and pkey

    :returns: S_OK / S_ERROR
    """

    retVal = self.loadChainFromString(pemData)
    if not retVal['OK']:
      return retVal

    return self.loadKeyFromString(pemData)

  @staticmethod
  def __getProxyExtensionList(diracGroup=False, rfcLimited=False):
    """
    Get an extension stack containing the necessary extension for a proxy.
    Basically the keyUsage, the proxyCertInfo, and eventually the diracGroup

    :param diracGroup: name of the dirac group for the proxy
    :param rfcLimited: boolean to generate for a limited proxy

    :returns: M2Crypto.X509.X509_Extension_Stack object.
    """

    extStack = M2Crypto.X509.X509_Extension_Stack()

    # Standard certificate extensions
    kUext = M2Crypto.X509.new_extension('keyUsage',
                                        'digitalSignature, keyEncipherment, dataEncipherment', critical=1)
    extStack.push(kUext)

    # Mandatory extension to be a proxy
    policyOID = LIMITED_PROXY_OID if rfcLimited else PROXY_OID
    ext = M2Crypto.X509.new_extension('proxyCertInfo', 'critical, language:%s' % (policyOID), critical=1)
    extStack.push(ext)

    # Add a dirac group
    if diracGroup and isinstance(diracGroup, basestring):
      # the str cast is needed because M2Crypto does not play it cool with unicode here it seems
      # Also one needs to specify the ASN1 type. That's what it is...
      dGext = M2Crypto.X509.new_extension(DIRAC_GROUP_OID, str('ASN1:IA5:%s' % diracGroup))
      extStack.push(dGext)

    return extStack

  @needCertList
  def getCertInChain(self, certPos=0):
    """
      Get then a certificate in the chain

      :warning: Contrary to the pygsi version, this is not a copy!

      :param certPos: position of the certificate in the chain. Default: 0

      :returns: S_OK(X509Certificate)/S_ERROR
    """
    return S_OK(self._certList[certPos])

  @needCertList
  def getIssuerCert(self):
    """
      Returns the issuer certificate of the last one if it is a proxy, otherwise
      the last one in the chain

      :returns: S_OK(X509Certificate)/S_ERROR
    """
    if self.__isProxy:
      return S_OK(self._certList[self.__firstProxyStep + 1])
    return S_OK(self._certList[-1])

  @needPKey
  def getPKeyObj(self):
    """
      Get the pkey obj

      :returns: ~M2Crypto.EVP.PKey object
    """
    return S_OK(self._keyObj)

  @needCertList
  def getCertList(self):
    """
    Get the cert list
    """
    return S_OK(self._certList)

  @needCertList
  def getNumCertsInChain(self):
    """
    Numbers of certificates in chain
    """
    return S_OK(len(self._certList))

  @needCertList
  @needPKey
  def generateProxyToString(self, lifetime, diracGroup=False, strength=1024, limited=False, proxyKey=False, rfc=True):  # pylint: disable=unused-argument
    """
    Generate a proxy and get it as a string

    Check here: https://github.com/eventbrite/m2crypto/blob/master/demo/x509/ca.py#L45

    Args:
        lifeTime (int): expected lifetime in seconds of proxy
        diracGroup (str): diracGroup to add to the certificate
        strength (int): length in bits of the pair
        limited (bool): Create a limited proxy
        rfc: placeholder and ignored

    """

    issuerCert = self._certList[0]

    if not proxyKey:
      # Generating key is a two step process: create key object and then assign RSA key.
      # This contains both the private and public key
      proxyKey = M2Crypto.EVP.PKey()
      proxyKey.assign_rsa(M2Crypto.RSA.gen_key(strength, 65537, callback=M2Crypto.util.quiet_genparam_callback))

    proxyExtensions = self.__getProxyExtensionList(diracGroup, limited)
    res = X509Certificate.generateProxyCertFromIssuer(issuerCert, proxyExtensions, proxyKey, lifetime=lifetime)
    if not res['OK']:
      return res
    proxyCert = res['Value']

    proxyCert.sign(self._keyObj, 'sha256')
    proxyString = "%s%s" % (proxyCert.asPem(), proxyKey.as_pem(
        cipher=None, callback=M2Crypto.util.no_passphrase_callback))
    for i in range(len(self._certList)):
      crt = self._certList[i]
      proxyString += crt.asPem()
    return S_OK(proxyString)

  # def old_generateProxyToString(self, lifeTime, diracGroup=False, strength=1024, limited=False, proxyKey=False, rfc=True):  # pylint: disable=unused-argument
  #   """
  #   Generate a proxy and get it as a string

  #   Check here: https://github.com/eventbrite/m2crypto/blob/master/demo/x509/ca.py#L45

  #   Args:
  #       lifeTime (int): expected lifetime in seconds of proxy
  #       diracGroup (str): diracGroup to add to the certificate
  #       strength (int): length in bits of the pair
  #       limited (bool): Create a limited proxy
  #       rfc: placeholder and ignored

  #   """
  #   if not self.__loadedChain:
  #     return S_ERROR(DErrno.ENOCHAIN)
  #   if not self.__loadedPKey:
  #     return S_ERROR(DErrno.ENOPKEY)

  #   issuerCert = self._certList[0]

  #   if not proxyKey:
  #     # Generating key is a two step process: create key object and then assign RSA key.
  #     # This contains both the private and public key
  #     proxyKey = M2Crypto.EVP.PKey()
  #     proxyKey.assign_rsa(M2Crypto.RSA.gen_key(strength, 65537, callback=M2Crypto.util.quiet_genparam_callback))

  #   proxyCert = X509Certificate.generateNewCertificate()

  #   proxyCert.setSerialNumber(int(random.random() * 10 ** 10))
  #   # No easy way to deep-copy certificate subject
  #   cloneSubject = M2Crypto.X509.X509_Name()
  #   parts = issuerCert.getSubjectNameObject()['Value'].as_text().split(', ')
  #   for part in parts:
  #     nid, val = part.split('=', 1)
  #     cloneSubject.add_entry_by_txt(field=nid, type=M2Crypto.ASN1.MBSTRING_ASC, entry=val, len=-1, loc=-1, set=0)
  #   cloneSubject.add_entry_by_txt(field="CN", type=M2Crypto.ASN1.MBSTRING_ASC,
  #                                 entry=str(int(random.random() * 10 ** 10)), len=-1, loc=-1, set=0)
  #   proxyCert.setSubject(cloneSubject)
  #   for extension in self.__getProxyExtensionList(diracGroup, limited):
  #     proxyCert.addExtension(extension)

  #   subject = issuerCert.getSubjectNameObject()
  #   if subject['OK']:
  #     proxyCert.setIssuer(subject['Value'])
  #   else:
  #     return subject
  #   version = issuerCert.getVersion()
  #   if version['OK']:
  #     proxyCert.setVersion(version['Value'])
  #   else:
  #     return version
  #   proxyCert.setPublicKey(proxyKey)
  #   proxyNotBefore = M2Crypto.ASN1.ASN1_UTCTIME()
  #   proxyNotBefore.set_time(int(time.time()) - 900)
  #   proxyCert.setNotBefore(proxyNotBefore)
  #   proxyNotAfter = M2Crypto.ASN1.ASN1_UTCTIME()
  #   proxyNotAfter.set_time(int(time.time()) + lifeTime)
  #   proxyCert.setNotAfter(proxyNotAfter)
  #   proxyCert.sign(self._keyObj, 'sha256')
  #   proxyString = "%s%s" % (proxyCert.asPem(), proxyKey.as_pem(
  #       cipher=None, callback=M2Crypto.util.no_passphrase_callback))
  #   for i in range(len(self._certList)):
  #     crt = self._certList[i]
  #     proxyString += crt.asPem()
  #   return S_OK(proxyString)

  def generateProxyToFile(self, filePath, lifeTime, diracGroup=False, strength=1024, limited=False, rfc=True):  # pylint: disable=unused-argument
    """
    Generate a proxy and put it into a file

    Args:
        filePath: file to write
        lifeTime: expected lifetime in seconds of proxy
        diracGroup: diracGroup to add to the certificate
        strength: length in bits of the pair
        limited: Create a limited proxy
        rfc: placeholder and ignored
    """
    retVal = self.generateProxyToString(lifeTime, diracGroup, strength, limited)
    if not retVal['OK']:
      return retVal
    try:
      with open(filePath, 'w') as fd:
        fd.write(retVal['Value'])
    except Exception as e:
      return S_ERROR(DErrno.EWF, "%s :%s" % (filePath, repr(e).replace(',)', ')')))
    try:
      os.chmod(filePath, stat.S_IRUSR | stat.S_IWUSR)
    except Exception as e:
      return S_ERROR(DErrno.ESPF, "%s :%s" % (filePath, repr(e).replace(',)', ')')))
    return S_OK()

  @needCertList
  def isProxy(self):
    """
    Check wether this chain is a proxy
    """
    return S_OK(self.__isProxy)

  @needCertList
  def isLimitedProxy(self):
    """
    Check wether this chain is a proxy
    """
    return S_OK(self.__isProxy and self.__isLimitedProxy)


  @needCertList
  def isValidProxy(self, ignoreDefault=False):
    """
    Check wether this chain is a valid proxy
      checks if its a proxy
      checks if its expired
    """
    if not self.__isProxy:
      return S_ERROR(DErrno.ENOCHAIN, "Chain is not a proxy")
    elif self.hasExpired()['Value']:
      return S_ERROR(DErrno.ENOCHAIN)
    elif ignoreDefault:
      groupRes = self.getDIRACGroup(ignoreDefault=ignoreDefault)
      if not groupRes['OK']:
        return groupRes
      if not groupRes['Value']:
        return S_ERROR(DErrno.ENOGROUP)
    return S_OK(True)

  def isVOMS(self):
    """
    Check wether this chain is a proxy
    """
    retVal = self.isProxy()
    if not retVal['OK'] or not retVal['Value']:
      return retVal
    for i in range(len(self._certList)):
      cert = self.getCertInChain(i)['Value']
      if cert.hasVOMSExtensions()['Value']:
        return S_OK(True)
    return S_OK(False)

  def isRFC(self):
    """ Check whether this is an RFC proxy. It can only be true, providing it is a proxy"""

    return self.isProxy()

  def getVOMSData(self):
    """
    Check wether this chain is a proxy
    """
    retVal = self.isProxy()
    if not retVal['OK'] or not retVal['Value']:
      return retVal
    for i in range(len(self._certList)):
      cert = self.getCertInChain(i)['Value']
      res = cert.getVOMSData()
      if res['OK']:
        return res
    return S_ERROR(DErrno.EVOMS)

  def __checkProxyness(self):
    # XXX to describe
    self.__hash = False
    self.__firstProxyStep = len(self._certList) - 2  # -1 is user cert by default, -2 is first proxy step
    self.__isProxy = True
    self.__isLimitedProxy = False
    prevDNMatch = 2
    # If less than 2 steps in the chain is no proxy
    if len(self._certList) < 2:
      self.__isProxy = False
      return
    # Check proxyness in steps
    for step in range(len(self._certList) - 1):
      issuerMatch = self.__checkIssuer(step, step + 1)
      if not issuerMatch:
        self.__isProxy = False
        return
      # Do we need to check the proxy DN?
      if prevDNMatch:
        dnMatch = self.__checkProxyDN(step, step + 1)
        # No DN match
        if dnMatch == 0:
          # If we are not in the first step we've found the entity cert
          if step > 0:
            self.__firstProxyStep = step - 1
          # If we are in the first step this is not a proxy
          else:
            self.__isProxy = False
            return
        # Limited proxy DN match
        elif dnMatch == 2:
          self.__isLimitedProxy = True
          if prevDNMatch != 2:
            self.__isProxy = False
            self.__isLimitedProxy = False
            return
        prevDNMatch = dnMatch

  def __checkProxyDN(self, certStep, issuerStep):
    """
    Check the proxy DN in a step in the chain
     0 = no match
     1 = proxy match
     2 = limited proxy match
    """

    issuerSubject = self._certList[issuerStep].getSubjectNameObject()
    if issuerSubject['OK']:
      issuerSubject = issuerSubject['Value']
    else:
      return 0
    proxySubject = self._certList[certStep].getSubjectNameObject()
    if proxySubject['OK']:
      proxySubject = proxySubject['Value']
    else:
      return 0
    lastEntry = str(proxySubject).split('/')[-1].split('=')
    limited = False
    if lastEntry[0] != 'CN':
      return 0
    if lastEntry[1] not in ('proxy', 'limited proxy'):
      ext = self._certList[certStep].getExtension('proxyCertInfo')
      if ext['OK']:
        ext = ext['Value']
      else:
        return 0
      # Check the RFC
      contraint = [line.split(":")[1].strip() for line in ext.get_value().split("\n")
                   if line.split(":")[0] == "Policy Language"]
      if not contraint:
        return 0
      if contraint[0] == LIMITED_PROXY_OID:
        limited = True
    else:
      if lastEntry[1] == "limited proxy":
        limited = True
    if not str(issuerSubject) == str(proxySubject)[:str(proxySubject).rfind('/')]:
      return 0
    return 1 if not limited else 2

  def __checkIssuer(self, certStep, issuerStep):
    """
    Check the issuer is really the issuer
    """
    issuerCert = self._certList[issuerStep]
    cert = self._certList[certStep]
    pubKey = issuerCert.getPublicKey()['Value']

    return cert.verify(pubKey)['Value']

  @needCertList
  def getDIRACGroup(self, ignoreDefault=False):
    """
    Get the dirac group if present
    """
    if not self.__isProxy:
      return S_ERROR(DErrno.EX509, "Chain does not contain a valid proxy")
    if self.isPUSP()['Value']:
      return self.getCertInChain(self.__firstProxyStep - 2)['Value'].getDIRACGroup(ignoreDefault=ignoreDefault)

    # The code below will find the first match of the DIRAC group
    for i in range(len(self._certList) - 1, -1, -1):
      retVal = self.getCertInChain(i)['Value'].getDIRACGroup(ignoreDefault=True)
      if retVal['OK'] and 'Value' in retVal and retVal['Value']:
        return retVal
    # No DIRAC group found, try to get the default one
    return self.getCertInChain(self.__firstProxyStep)['Value'].getDIRACGroup(ignoreDefault=ignoreDefault)

  @needCertList
  def hasExpired(self):
    """
    Is any of the elements in the chain expired?
    """
    for iC in range(len(self._certList) - 1, -1, -1):
      expired = self._certList[iC].hasExpired()
      if expired['OK']:
        if expired['Value']:
          return S_OK(True)
      else:
        return expired
    return S_OK(False)

  @needCertList
  def getNotAfterDate(self):
    """
    Get the smallest not after date
    """
    notAfter = self._certList[0].getNotAfterDate()
    if not notAfter['OK']:
      return notAfter
    notAfter = notAfter['Value']
    for iC in range(len(self._certList) - 1, -1, -1):
      stepNotAfter = self._certList[iC].getNotAfterDate()
      if not stepNotAfter['OK']:
        return stepNotAfter
      stepNotAfter = stepNotAfter['Value']
      expired = self._certList[iC].hasExpired()
      if not expired['OK']:
        return expired
      if expired['Value']:
        return S_OK(stepNotAfter)
      if notAfter > stepNotAfter:
        notAfter = stepNotAfter
    return S_OK(notAfter)

  @needCertList
  def generateProxyRequest(self, bitStrength=1024, limited=False):
    """
    Generate a proxy request
    Return S_OK( X509Request ) / S_ERROR
    """
    if not bitStrength:
      return S_ERROR(DErrno.EX509, "bitStrength has to be greater than 1024 (%s)" % bitStrength)
    x509 = self.getCertInChain(0)['Value']
    return x509.generateProxyRequest(bitStrength, limited)

  @needCertList
  @needPKey
  def generateChainFromRequestString(self, pemData, lifetime=86400, requireLimited=False, diracGroup=False, rfc=True):
    """
    Generate a x509 chain from a request

    :param rfc: ignored
    :returns: S_OK( string ) / S_ERROR

    """
    try:
      req = M2Crypto.X509.load_request_string(pemData, format=M2Crypto.X509.FORMAT_PEM)

    except Exception as e:
      return S_ERROR(DErrno.ECERTREAD, "Can't load request data: %s" % repr(e).replace(',)', ')'))
    limited = requireLimited and self.isLimitedProxy().get('Value', False)

    return self.generateProxyToString(lifetime, diracGroup, 1024, limited, req.get_pubkey())

  @needCertList
  def getRemainingSecs(self):
    """
    Get remaining time
    """
    remainingSecs = self.getCertInChain(0)['Value'].getRemainingSecs()['Value']
    for i in range(1, len(self._certList)):
      stepRS = self.getCertInChain(i)['Value'].getRemainingSecs()['Value']
      remainingSecs = min(remainingSecs, stepRS)
    return S_OK(remainingSecs)

  @needCertList
  def dumpAllToString(self):
    """
    Dump all to string
    """
    data = self._certList[0].asPem()
    if self._keyObj:
      data += self._keyObj.as_pem(cipher=None, callback=M2Crypto.util.no_passphrase_callback)
    for i in range(1, len(self._certList)):
      data += self._certList[i].asPem()
    return S_OK(data)

  def dumpAllToFile(self, filename=False):
    """
    Dump all to file. If no filename specified a temporal one will be created
    """
    retVal = self.dumpAllToString()
    if not retVal['OK']:
      return retVal
    pemData = retVal['Value']
    try:
      if not filename:
        fd, filename = tempfile.mkstemp()
        os.write(fd, pemData)
        os.close(fd)
      else:
        fd = file(filename, "w")
        fd.write(pemData)
        fd.close()
    except Exception as e:
      return S_ERROR(DErrno.EWF, "%s :%s" % (filename, repr(e).replace(',)', ')')))
    try:
      os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR)
    except Exception as e:
      return S_ERROR(DErrno.ESPF, "%s :%s" % (filename, repr(e).replace(',)', ')')))
    return S_OK(filename)

  @needCertList
  def dumpChainToString(self):
    """
    Dump only cert chain to string
    """
    data = ''
    for cert in self._certList:
      data += cert.asPem()
    return S_OK(data)

  @needPKey
  def dumpPKeyToString(self):
    """
    Dump key to string
    """
    return S_OK(self._keyObj.as_pem(cipher=None, callback=M2Crypto.util.no_passphrase_callback))

  def __str__(self):
    repStr = "<X509Chain"
    if self._certList:
      repStr += " %s certs " % len(self._certList)
      for cert in self._certList:
        repStr += "[%s]" % str(cert.getSubjectDN()['Value'])
    if self._keyObj:
      repStr += " with key"
    repStr += ">"
    return repStr

  def __repr__(self):
    return self.__str__()

  def isPUSP(self):
    if self.__isProxy:
      # Check if we have a subproxy
      dn = self._certList[self.__firstProxyStep].getSubjectDN()
      if dn['OK']:
        dn = dn['Value']
      else:
        return dn
      subproxyUser = isPUSPdn(dn)
      if subproxyUser:
        result = S_OK(True)
        result['Identity'] = dn
        result['SubproxyUser'] = subproxyUser
        return result

    return S_OK(False)

  @needCertList
  def getCredentials(self, ignoreDefault=False):
    credDict = {'subject': str(self._certList[0].getSubjectDN()['Value']),  # ['Value'] :(
                'issuer': self._certList[0].getIssuerDN()['Value'],  # ['Value'] :(
                'secondsLeft': self.getRemainingSecs()['Value'],
                'isProxy': self.__isProxy,
                'isLimitedProxy': self.__isProxy and self.__isLimitedProxy,
                'validDN': False,
                'validGroup': False}
    if self.__isProxy:
      credDict['identity'] = str(self._certList[self.__firstProxyStep + 1].getSubjectDN()['Value'])  # ['Value'] :(

      # Check if we have the PUSP case
      result = self.isPUSP()
      if result['OK'] and result['Value']:
        credDict['identity'] = result['Identity']
        credDict['subproxyUser'] = result['SubproxyUser']

      retVal = Registry.getUsernameForDN(credDict['identity'])
      if not retVal['OK']:
        return S_OK(credDict)
      credDict['username'] = retVal['Value']
      credDict['validDN'] = True
      retVal = self.getDIRACGroup(ignoreDefault=ignoreDefault)
      if retVal['OK']:
        diracGroup = retVal['Value']
        credDict['group'] = diracGroup
        retVal = Registry.getGroupsForUser(credDict['username'])
        if retVal['OK'] and diracGroup in retVal['Value']:
          credDict['validGroup'] = True
          credDict['groupProperties'] = Registry.getPropertiesForGroup(diracGroup)
    else:
      retVal = Registry.getHostnameForDN(credDict['subject'])
      if retVal['OK']:
        credDict['group'] = 'hosts'
        credDict['hostname'] = retVal['Value']
        credDict['validDN'] = True
        credDict['validGroup'] = True
        credDict['groupProperties'] = Registry.getHostOption(credDict['hostname'], 'Properties')
      retVal = Registry.getUsernameForDN(credDict['subject'])
      if retVal['OK']:
        credDict['username'] = retVal['Value']
        credDict['validDN'] = True
    return S_OK(credDict)

  @needCertList
  def hash(self):
    if self.__hash:
      return S_OK(self.__hash)
    sha1 = hashlib.sha1()
    for cert in self._certList:
      sha1.update(str(cert.getSubjectNameObject()))
    sha1.update(str(self.getRemainingSecs()['Value'] / 3600))
    sha1.update(self.getDIRACGroup()['Value'])
    if self.isVOMS():
      sha1.update("VOMS")
      from DIRAC.Core.Security.VOMS import VOMS
      result = VOMS().getVOMSAttributes(self)
      if result['OK']:
        sha1.update(str(result['Value']))
    self.__hash = sha1.hexdigest()
    return S_OK(self.__hash)


def isPUSPdn(userDN):
  """ Evaluate if the DN is of the PUSP type or not

  :param str userDN: user DN string
  :return: the subproxy user name or None
  """
  lastEntry = userDN.split('/')[-1].split('=')
  if lastEntry[0] == "CN" and lastEntry[1].startswith("user:"):
    return userDN.split('/')[-1].split(':')[1]
  return None


g_X509ChainType = type(X509Chain())
