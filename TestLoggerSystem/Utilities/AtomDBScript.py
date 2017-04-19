from DIRAC.FrameworkSystem.DB.AtomDB import AtomDB

try:
  atomdb = AtomDB()
except Exception:
   print "Oops. Something went wrong..."
   raise
result = atomdb.addStuff( 'something' )

if not result['OK']:
  print "Error while inserting into db:", result['Message'] #Here, in DIRAC, you better use the gLogger
else:
  print result[ 'Value' ] #Here, in DIRAC, you better use the gLogger