""" X509Certificate is a class for managing X509 certificates alone m2
"""

__RCSID__ = "$Id$"

import datetime
import os
import M2Crypto


from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Utilities import Time
from DIRAC.Core.Utilities import DErrno
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.Core.Security.m2crypto import asn1_utils


class X509Certificate(object):
  """ The X509Certificate object represents ... a X509Certificate.
      It is a wrapper around a lower level implementation (M2Crypto in this case) of a certificate.
      It can be a host or user certificate.
  """

  def __init__(self, x509Obj=None, certString=None):
    """
      Constructor.

      :param x509Obj: (optional) certificate instance
      :type x509Obj: M2Crypto.X509.X509
      :param certString: text representation of certificate
      :type certString: String

    """

    self.__valid = False
    if x509Obj:
      self.__certObj = x509Obj
      self.__valid = True
    else:
      self.__certObj = M2Crypto.X509.X509()
      self.__valid = True
    if certString:
      self.loadFromString(certString)

  def getCertObject(self):
    """ Return the wrapped certificate

        :returns: ~M2Crypto.X509.X509 object
    """
    return self.__certObj

  def load(self, certificate):
    """ Load a x509 certificate either from a file or from a string

        :param certificate: path to the file or PEM encoded string

        :returns: S_OK on success, otherwise S_ERROR
    """

    if os.path.exists(certificate):
      return self.loadFromFile(certificate)

    return self.loadFromString(certificate)

  def loadFromFile(self, certLocation):
    """
       Load a x509 cert from a pem file

       :param certLocation: path to the certificate file

      :returns: S_OK / S_ERROR.

    """
    try:
      with open(certLocation, 'r') as fd:
        pemData = fd.read()
        return self.loadFromString(pemData)
    except IOError:
      return S_ERROR(DErrno.EOF, "Can't open %s file" % certLocation)

  def loadFromString(self, pemData):
    """
      Load a x509 cert from a string containing the pem data

      :param pemData: pem encoded string

      :returns: S_OK / S_ERROR
    """
    try:
      self.__certObj = M2Crypto.X509.load_cert_string(str(pemData), M2Crypto.X509.FORMAT_PEM)
    except Exception as e:
      return S_ERROR(DErrno.ECERTREAD, "Can't load pem data: %s" % e)

    self.__valid = True
    return S_OK()

  def setCertificate(self, x509Obj):
    """
      Set certificate object

      :param x509Obj: ~M2Crypto.X509.X509 object

      :returns: S_OK/S_ERROR
    """
    if not isinstance(x509Obj, M2Crypto.X509.X509):
      return S_ERROR(DErrno.ETYPE, "Object %s has to be of type M2Crypto.X509.X509" % str(x509Obj))

    self.__certObj = x509Obj
    self.__valid = True
    return S_OK()

  def hasExpired(self):
    """
      Check if the loaded certificate is still valid

      :returns: S_OK( True/False )/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)

    notAfter = self.__certObj.get_not_after().get_datetime()

    now = datetime.datetime.utcnow()

    # M2Crypto does things correctly by setting a timezone info in the datetime
    # However, we do not in DIRAC, and so we can't compare the dates.
    # We have to remove the timezone info from M2Crypto
    notAfter = notAfter.replace(tzinfo=None)

    return S_OK(notAfter < now)

  def getNotAfterDate(self):
    """
      Get not after date of a certificate

      :returns: S_OK( datetime )/S_ERROR
    """

    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)

    notAfter = self.__certObj.get_not_after().get_datetime()

    # M2Crypto does things correctly by setting a timezone info in the datetime
    # However, we do not in DIRAC, and so we can't compare the dates.
    # We have to remove the timezone info from M2Crypto
    notAfter = notAfter.replace(tzinfo=None)

    return S_OK(notAfter)

  def setNotAfter(self, notAfter):
    # TODO: Should probably get ride of that method. Used only to generate a proxy
    """
      Set not after date of a certificate.

      :param notAfter: M2Crypto.ASN1.ASN1_UTCTIME object.

      Return: S_OK/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)

    self.__certObj.set_not_after(notAfter)

    return S_OK()

  def getNotBeforeDate(self):
    """
    Get not before date of a certificate
    Return: S_OK( datetime )/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    return S_OK(self.__certObj.get_not_before().get_datetime())

  def setNotBefore(self, notbefore):
    """
    Set not before date of a certificate
    Return: S_OK/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    self.__certObj.set_not_before(notbefore)
    return S_OK()

  def getSubjectDN(self):
    """
    Get subject DN
    Return: S_OK( string )/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    return S_OK(str(self.__certObj.get_subject()))

  def getIssuerDN(self):
    """
    Get issuer DN
    Return: S_OK( string )/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    return S_OK(str(self.__certObj.get_issuer()))

  def getSubjectNameObject(self):
    """
    Get subject name object
    Return: S_OK( X509Name )/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    return S_OK(self.__certObj.get_subject())

  def getIssuerNameObject(self):
    """
    Get issuer name object
    Return: S_OK( X509Name )/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    return S_OK(self.__certObj.get_issuer())

  def setIssuer(self, nameObject):
    """
    Set issuer name object
    Return: S_OK/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    self.__certObj.set_issuer(nameObject)
    return S_OK()

  def getPublicKey(self):
    """
    Get the public key of the certificate
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    return S_OK(self.__certObj.get_pubkey())

  def setPublicKey(self, pubkey):
    """
    Set the public key of the certificate
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    self.__certObj.set_pubkey(pubkey)
    return S_OK()

  def getVersion(self):
    """
    Get the version of the certificate
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    return S_OK(self.__certObj.get_version())

  def setVersion(self, version):
    """
    Set the version of the certificate
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    self.__certObj.set_version(version)
    return S_OK()

  def getSerialNumber(self):
    """
    Get certificate serial number
    Return: S_OK( serial )/S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    return S_OK(self.__certObj.get_serial_number())

  def setSerialNumber(self, serial):
    """
    Set certificate serial number
    Return: S_OK/S_ERROR
    """
    if self.__valid:
      self.__certObj.set_serial_number(serial)
      return S_OK()
    return S_ERROR(DErrno.ENOCERT)

  def sign(self, key, algo):
    """
    Sign the cerificate using provided key and algorithm.
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    self.__certObj.sign(key, algo)
    return S_OK()

  def getDIRACGroup(self, ignoreDefault=False):
    """
    Get the dirac group if present
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    try:
      return S_OK(asn1_utils.decodeDIRACGroup(self.__certObj))
    except LookupError:
      pass

    # extCount = self.__certObj.get_ext_count()
    # for extIdx in xrange(extCount):
    #
    #   ext = self.__certObj.get_ext_at(extIdx)
    #   if ext.get_name() == "diracGroup":
    #     return S_OK(ext.get_value())
    if ignoreDefault:
      return S_OK(False)
    result = self.getIssuerDN()
    if not result['OK']:
      return result
    return Registry.findDefaultGroupForDN(result['Value'])

  def hasVOMSExtensions(self):
    """
    Has voms extensions
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    try:
      self.__certObj.get_ext('vomsExtensions')
      return S_OK(True)
    except LookupError:
      # no extension found
      pass
    return S_OK(False)

  def getVOMSData(self):
    # return S_ERROR( DErrno.EVOMS, "No VOMS data available" )
    """
    Get voms extensions
    """
    try:
      vomsExt = asn1_utils.decodeVOMSExtension(self.__certObj)
      return S_OK(vomsExt)
    except LookupError:
      return S_ERROR(DErrno.EVOMS, "No VOMS data available")
    #
    # decoder = asn1.Decoder()
    # decoder.start(self.__certObj.as_der())
    # data = parseForVOMS(decoder)
    # if data:
    #   return S_OK(data)
    # else:
    #   return S_ERROR(DErrno.EVOMS, "No VOMS data available")

  def generateProxyRequest(self, bitStrength=1024, limited=False):
    """
    Generate a proxy request
    Return S_OK( X509Request ) / S_ERROR
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)

    if not limited:
      subj = self.__certObj.get_subject()
      lastEntry = subj[len(subj) - 1]
      if lastEntry.get_data() == "limited proxy":
        limited = True

    from DIRAC.Core.Security.m2crypto.X509Request import X509Request

    req = X509Request()
    req.generateProxyRequest(bitStrength=bitStrength, limited=limited)
    return S_OK(req)

  def getRemainingSecs(self):
    """
    Get remaining lifetime in secs
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    notAfter = self.__certObj.get_not_after().get_datetime()
    notAfter = notAfter.replace(tzinfo=Time.dateTime().tzinfo)
    remaining = notAfter - Time.dateTime()
    return S_OK(max(0, remaining.days * 86400 + remaining.seconds))

  def getExtensions(self):
    """
    Get a decoded list of extensions
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    extList = []
    for i in xrange(self.__certObj.get_ext_count()):
      sn = self.__certObj.get_ext_at(i).get_name()
      try:
        value = self.__certObj.get_ext_at(i).get_value()
      except Exception:
        value = "Cannot decode value"
      extList.append((sn, value))
    return S_OK(sorted(extList))

  def verify(self, pkey):
    """
    Verify certificate using provided key

    :returns: S_OK(bool) where the boolean shows the success of the verification
    """
    ret = self.__certObj.verify(pkey)
    return S_OK(ret == 1)

  def setSubject(self, subject):
    """
    Set subject using provided X509Name object
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    self.__certObj.set_subject(subject)
    return S_OK()

  def get_subject(self):
    """
    Deprecated way of getting subject DN. Only for backward compatibility reasons.
    """
    # XXX This function should be deleted when all code depending on it is updated.
    return self.getSubjectDN()['Value']  # XXX FIXME awful awful hack

  def asPem(self):
    """
    Return cerificate as PEM string
    """
    return self.__certObj.as_pem()

  def getExtension(self, name):
    """
    Return X509 Extension with given name
    """
    try:
      ext = self.__certObj.get_ext(name)
    except LookupError as e:
      return S_ERROR(e)
    return S_OK(ext)

  def addExtension(self, extension):
    """
    Add extension to the certificate
    """
    if not self.__valid:
      return S_ERROR(DErrno.ENOCERT)
    self.__certObj.add_ext(extension)
    return S_OK()


# https://www.ogf.org/documents/GFD.182.pdf
