from TornadoService import TornadoService
from DIRAC import S_OK, gLogger
from DIRAC.FrameworkSystem.Service.UserDB import UserDB


class UserHandler(TornadoService):

  LOCATION = "/Framework/User"

  @classmethod
  def initializeHandler(cls): # Dans DIRAC on a aussi un "ServiceInfo", a voir...
    cls.userDB = UserDB()
    return S_OK()


  def export_addUser(self, whom):
    """
    Add a user

      :param str whom: The name of the user we want to add
      :return: S_OK with S_OK['Value'] = The_ID_of_the_user or S_ERROR
    """
    newUser = self.userDB.addUser(whom)
    if newUser['OK']:
      return S_OK(newUser['lastRowId'])
    return newUser

  auth_editUser = ['all']

  def export_editUser(self, uid, value):
    """
      Edit a user

      :param int uid: The Id of the user in database
      :param str value: New user name
      :return: S_OK or S_ERROR
    """
    return self.userDB.editUser(uid, value)

  auth_getUserName = ['all']
  types_getUserName = [int]

  def export_getUserName(self, uid):
    """
      Get a user

      :param int uid: The Id of the user in database
      :return: S_OK with S_OK['Value'] = TheUserName or S_ERROR if not found
    """
    return self.userDB.getUserName(uid)

  auth_listUsers = ['nobody']

  def export_listUsers(self):
    """
      List all users

      :return: S_OK with S_OK['Value'] list of [UserId, UserName]
    """
    return self.userDB.listUsers()
