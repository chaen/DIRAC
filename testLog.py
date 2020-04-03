from DIRAC import gLogger
gLogger.showHeaders(False)
gLogger.registerBackend('file', {'FileName' : '/tmp/manualLogs.txt'})
gLogger.error('error with gLogger')
log = gLogger.getSubLogger('sublogger')
log.showHeaders(True)
log.setLevel('DEBUG')
log.error('error with sub')
