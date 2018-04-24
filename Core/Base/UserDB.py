""" A test DB in DIRAC, using MySQL as backend
"""

from DIRAC.Core.Base.DB import DB


class UserDB(DB):

  def __init__(self):
    DB.__init__(self, 'UserDB', 'Framework/UserDB', 10)
    retVal = self.__initializeDB()
    if not retVal['OK']:
      raise Exception("Can't create tables: %s" % retVal['Message'])

  def __initializeDB(self):
    """
    Create the tables
    """
    retVal = self._query("show tables")
    if not retVal['OK']:
      return retVal

    tablesInDB = [t[0] for t in retVal['Value']]
    tablesD = {}

    if 'user_mytable' not in tablesInDB:
      tablesD['user_mytable'] = {'Fields': {'Id': 'INTEGER NOT NULL AUTO_INCREMENT', 'Name': 'VARCHAR(64) NOT NULL'},
                                 'PrimaryKey': ['Id']
                                 }

    return self._createTables(tablesD)

  def addStuff(self, something):
    return self._insert('user_mytable', ['Name'], [something])
