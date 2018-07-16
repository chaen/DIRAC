"""
    (Case 1) This is a integration test with a Service under Tornado(tornado-start-all) AND a configuration server under DISET (dirac-service)

    (Case 2) We run the same test with Service under DISET and CS under Tornado


    We test with
        - for the CS: Configuration/Server (handlerPath define path to load ConfigurationHandler.py, or TornadoConfigurationHandler.py in the second case)
        - for the service: Framework/User (for the second case handlerPath should define path to UserDiracHandler.py, see example bellow)

        The CS, service and client (this test) must read different dirac.cfg files and are not necessary on the same computer

        In the config file distributed by the CS you should see something like::
        ```

        Systems{
          Framework
          {
            DevInstance
            {
              Services
              {
                URLs
                {
                  #User = https://MrBoincHost/Framework/User # Case 1
                  User = dips://MrBoincHost/Framework/User  # Case 2
                }
                #for case 1
                #User
                #{
                # Protocol = https
                #}
                #for case 2
                User
                {
                  HandlerPath = DIRAC/FrameworkSystem/Service/UserDiracHandler.py
                  Port = 1234
                  Protocol = dips # Not necessary defined, it's the default value, but good for human reading
                }
              }
              
            }
          }
        }
        Registry {...}
        ```
        For the service you need to define the database (case 1 and 2) and Tornado (case 1), so in the config file loaded by service you should see::
        ```
          DIRAC
          { 
            Setup = DeveloperSetup
            Configuration
            { 
              Servers = dips://localhost:9135/Configuration/Server # Case 1
              #Servers = https://localhost:444/Configuration/Server # Case 2
            }
          }
          Systems {
            # Only in case 1 (Service run under tornado)
            # Tornado{
            #   DevInstance
            #   {
            #     # 443 is already the default, next line is technically useless
            #     Port = 443  
            #   }
            # }
            Framework
            {
              DevInstance
              {
                Databases
                {
                  UserDB
                  {
                    Host = localhost
                    User = root
                    Password = 
                    DBName = dirac
                  }
                }
              }
            }
          }
        ```
    
        The client should have a very minimal config file, and read only this file::
          ```
            DIRAC
            { 
              Setup = DeveloperSetup
              Configuration
              { 
                Servers = dips://localhost:9135/Configuration/Server
                #Servers = https://localhost:444/Configuration/Server
              }
            }
          ```
"""

from DIRAC.Core.Base import Script
Script.parseCommandLine()

from string import printable

from hypothesis import given, settings
from hypothesis.strategies import text

from DIRAC.TornadoServices.Client.RPCClientSelector import RPCClientSelector as RPCClient
from DIRAC.Core.Utilities.DErrno import ENOAUTH
from DIRAC import S_ERROR

from pytest import mark
parametrize = mark.parametrize





def test_authorization():
  service = RPCClient("Framework/User")

  authorisation = service.unauthorized() # In the handler this method have no allowed properties
  assert authorisation['OK'] == False 
  assert authorisation['Message'] == S_ERROR(ENOAUTH, "Unauthorized query")['Message']



def test_unknown_method():
  service = RPCClient("Framework/User")

  unknownmethod = service.ThisMethodMayNotExist()
  assert unknownmethod['OK'] == False
  assert unknownmethod['Message'] == "Unknown method ThisMethodMayNotExist"



def test_ping():
  service = RPCClient("Framework/User")

  assert service.ping()['OK'] == True


@settings(deadline=None, max_examples=42)
@given(data=text(printable, max_size=64))
def test_echo(data):
  service = RPCClient("Framework/User")

  assert service.echo(data)['Value'] == data
