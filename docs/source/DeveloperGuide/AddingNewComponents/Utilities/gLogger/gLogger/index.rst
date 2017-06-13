Introduction
============

*gLogger* is the logging solution within DIRAC. Based on the python
*logging* library, it represents an interface to create and send
informational, warn or error messages from the middleware to different
outputs. In this documentation, we will focus on the functionalities
proposed by *gLogger*.

Basics
======

Get a child *Logging* object
----------------------------

*Logging* presentation
~~~~~~~~~~~~~~~~~~~~~~

*gLogger* is an instance of a *Logging* object. The purpose of these
objects is to create log records. Moreover, they are part of a tree,
which means that each *Logging* has a parent and can have a list of
children. *gLogger* is considered as the root *Logging*, on the top of
this tree.

Initialize a child *Logging*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since *Logging* objects are part of a tree, it is possible to get
children from each *Logging* object. For a simple use, we will simply
get one child *Logging* from *gLogger*, the root *Logging*, via the
command:

::

    logger = gLogger.getSubLogger("logger")

This child can be used like *gLogger* in the middleware. In this way, we
recommend you to avoid to use directly *gLogger* and to create at least
one child from it for each component in *DIRAC* with a correct name.

Otherwise, note that the created child is identified by its name,
*logger* in our case, and can be retrieve via the *getSubLogger()*
method. For instance :

::

    logger = gLogger.getSubLogger("logger")
    newLogger = gLogger.getSubLogger("logger")
    # Here, logger and newlogger are a same and unique object 

Get its sub name
~~~~~~~~~~~~~~~~

We can obtain the name of a child *Logging* via the *getSubName* method.
Here is an example of use:

::

    logger = gLogger.getSubLogger("logger")
    logger.getSubName()
    # > logger

Get its system and component names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each *Logging* object belongs to one component from one system, the one
which is running. Thus, we can get these names thanks to the *getName*
method. They will appear as a *system/component* path like this:

::

    logger = gLogger.getSubLogger("logger")
    logger.getName()
    # > Framework/Atom

Send a log record
-----------------

Log record presentation
~~~~~~~~~~~~~~~~~~~~~~~

A log record is composed by a date, a system and a component name, a
*Logging* name, a level and a message. This information represents its
identity.

::

    [Date] UTC [System]/[Component]/[Log] [Level]: [Message]
    2017-04-25 15:51:01 UTC Framework/Atom/log ALWAYS: message

Levels and context of use
~~~~~~~~~~~~~~~~~~~~~~~~~

The level of a log record represents a major characteristic in its
identity. Indeed, it constitutes its nature and defines if it will be
displayed or not. *gLogger* puts 10 different levels at our disposal in
DIRAC and here is a table describing them and their context of use.

[!ht]

| \|l\|X\| Level name & Context of use
| Fatal & Must be used before an error forcing the program exit and only
in this case.
| Always & Used with moderation, only for message that must appears all
the time.
| Error & Used when an error occur but do not need to force the program
exit.
| Exception & Actually a specification of the Error level which must be
used before raising an exception.
| Notice & Used to provide an important information.
| Warn & Used when an error can occur.
| Info & Used to provide information.
| Verbose & Used to provide extra information.
| Debug & Must be used with moderation to debug the program.

These levels have a priority order from *debug* to *fatal*. In this way,
*fatal* and *always* log records appear almost all the time whereas
*debug* log records rarely appears. Actually, their appearance depends
on the level of the *Logging* object which sends the log records.

Log record creation
~~~~~~~~~~~~~~~~~~~

10 methods are at our disposal to create log records from a *Logging*
object. These methods carry the name of the different levels and they
are all the same signature. They take a message which has to be fixed
and a variable message in parameters and return a boolean value
indicating if the log will appear or not. Here is an example of the
*error* method to create error log records:

::

    boolean error(sMsg, sVarMsg='')

For instance, we create *notice* log records via the following commands:

::

    logger = gLogger.getSubLogger("logger")
    logger.notice("message")
    # > 2017-04-25 15:51:01 UTC Framework/logger NOTICE: message
    logger.notice("mes", "sage")
    # > 2017-04-25 15:51:01 UTC Framework/logger NOTICE: mes sage

Another interesting point is the use of the *exception* method which
gives a stack trace with the message. Here is a use of the *exception*
method:

::

    logger = gLogger.getSubLogger("logger")
    try:
        badIdea = 1/0
        print badIdea
    except:
        logger.exception("bad idea")
    # > 2017-04-25 15:51:01 UTC Framework/logger ERROR: message
    #Traceback (most recent call last):
    #File "....py", line 32, in <module>
    #a = 1/0
    #ZeroDivisionError: integer division or modulo by zero

Log records with variable data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*gLogger* use the old *%-style* to include variable data. Thus, you can
include variable data like this:

::

    logger = gLogger.getSubLogger("logger")
    arg = "argument"
    logger.notice("message with %s" % arg)
    #> 2017-04-25 15:51:01 UTC Framework/logger NOTICE: message with argument

Control the *Logging* level
---------------------------

*Logging* level presentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As we said before, each *Logging* has a level which is set at *notice*
by default. According to this level, the log records are displayed or
not. To be displayed, the level of the log record has to be equal or
higher than the *Logging* level. Here is an example:

::

    # logger level: NOTICE 
    logger = gLogger.getSubLogger("logger")
    logger.error("appears")
    logger.notice("appears")
    logger.verbose("not appears")
    # > 2017-04-25 15:51:01 UTC Framework/logger ERROR: appears
    # > 2017-04-25 15:51:01 UTC Framework/logger NOTICE: appears

As we can see, the *verbose* log record is not displayed because its
level is inferior to *notice*. Moreover, we will see in the advanced
part that the level is propagate to the *Logging* children. Thus, for a
basic use, you do not need to set the level of a child *Logging*.

Set a level via the command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The more used and recommended method to set the level of *gLogger* is to
use the command line arguments. It works with any *DIRAC* component but
we can not define a specific level. Here is a table of these different
arguments:

[!ht]

+------------+------------------------------------------+
| Argument   | Level associated to the root *Logging*   |
+============+==========================================+
| default    | notice                                   |
+------------+------------------------------------------+
| -d         | verbose                                  |
+------------+------------------------------------------+
| -dd        | verbose                                  |
+------------+------------------------------------------+
| -ddd       | debug                                    |
+------------+------------------------------------------+

We can find a complete table containing all the effects of the command
line arguments .

Set a level via the *cfg* file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can also set the *gLogger* level in the *cfg* file via the *LogLevel*
line. We can define a specific level with this method, but it does not
work for scripts. Here is an example of an agent with the root
*Logging*\ level set to *always*:

::

    Agents
    {
      SimplestAgent
      {
        LogLevel = ALWAYS
        ...
      }
    }   

Set a level via the *setLevel* method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a last method to set any *Logging* level. We just have to give
it a string representing a level like this:

::

    logger = gLogger.getSubLogger("logger")
    logger.setLevel("info")

In this example, the level of *logger* is set to *info*. By the way, we
recommend you to not use this method for a basic use.

Get the level attaching to a specific *Logging*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can obviously get a level associate to a *Logging* via the *getLevel*
method. This method returns a string representing a level. Here is an
example of use:

::

    logger = gLogger.getSubLogger("logger")
    logger.getLevel()
    # > "NOTICE"

Get all the existing levels
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the same way, we can get all the existing level names thanks to the
*getAllPossibleLevels* method. This method returns a list of string
representing the different levels. Here is an example of use:

::

    # 'level' comes from a user
    def method(level):
        if level in self.logger.getAllPossibleLevels():
         # ...

Test the *Logging* level superiority
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, it can be interesting to test the *Logging* level before
creating a log record. For instance, we need to send a *verbose* log
record using an expensive function and we do not need to make it if it
can not be send to an output. To avoid such an operation, we can use the
*shown* method which controls if the *Logging* level is superior to a
specific level. If it is the case, the method returns *True*, else
returns *False*. Here is an example of this use:

::

    # logger level: ERROR
    logger = gLogger.getSubLogger("logger")
    if logger.shown('verbose'):
        logger.verbose("Expensive message: %s" % expensiveFunc())
    # > False

Modify the log record display
-----------------------------

Default display
~~~~~~~~~~~~~~~

| As we saw before, the basic display for a log record is:

::

    [Date] UTC [System]/[Component]/[Log] [Level]: [Message]
    2017-04-25 15:51:01 UTC Framework/Atom/log ALWAYS: message

The date is UTC formatted and the system and the component names come
from the *cfg* file. By default, the system name is *Framework* while
the component name does not exist. This display can vary according to
different option parameters.

Remove the prefix of the log record
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the scripts, we can observe log record without any prefix, only a
message like this:

::

    [Message]
    message

This behaviour is explained by the *parseCommandLine* function, that we
can find in every scripts, which set the boolean *headerIsShown* from
*Logging* to *False*. To do a such operation, it used the *showHeaders*
method from *Logging*. Here is the signature of the method:

::

    showHeaders(yesno=True)

To summarize, the default value of *headerIsShown* is *True*, which
means that the prefix is displayed, and we can set it at False to hide
it.

There are two ways to modify it, the *showHeaders* method as we saw, and
the command line argument *-d*. Here is a table presenting the changes
according to the argument value:

[!ht]

+--------------------------------------+------------------------------------------+
| Argument                             | Level associated to the root *Logging*   |
+======================================+==========================================+
| Default(Executors/Agents/Services)   | True                                     |
+--------------------------------------+------------------------------------------+
| Default(Scripts)                     | False                                    |
+--------------------------------------+------------------------------------------+
| -d                                   | default value                            |
+--------------------------------------+------------------------------------------+
| -dd                                  | True                                     |
+--------------------------------------+------------------------------------------+
| -ddd                                 | True                                     |
+--------------------------------------+------------------------------------------+

We can find a complete table containing all the effects of the command
line arguments .

Add the thread ID in the log record
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to add a thread ID in our log records thanks to the
*showThreadIDs* method which modify the boolean *threadIDIsShown* value.
As the *showHeaders* method, it takes a boolean in parameter to set
*threadIDIsShown*. This attribute is set at *False* by default. Here is
an example with the boolean at *True*:

::

    [Date] UTC [System]/[Component]/[Log][Thread] [Level]: [Message]
    2017-04-25 15:51:01 UTC Framework/Atom/log[140218144]ALWAYS: message

We can see the thread ID between the *Logging* name and the level:
[140218144]. Nevertheless, set the boolean value is not the only
requirement. Indeed, *headerIsShown* must be set at *True* to effect the
change. In this way, it is impossible to have the thread ID without the
prefix.

A second way to set the boolean is to use the command line argument
*-d*. Here is a table presenting the changes according to the argument:

[!ht]

+--------------------------------------+------------------------------------------+
| Argument                             | Level associated to the root *Logging*   |
+======================================+==========================================+
| Default(Executors/Agents/Services)   | False                                    |
+--------------------------------------+------------------------------------------+
| Default(Scripts)                     | False                                    |
+--------------------------------------+------------------------------------------+
| -d                                   | default value                            |
+--------------------------------------+------------------------------------------+
| -dd                                  | default value                            |
+--------------------------------------+------------------------------------------+
| -ddd                                 | True                                     |
+--------------------------------------+------------------------------------------+

We can find a complete table containing all the effects of the command
line arguments .

Add the caller path name and its line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The *LogShowLine* option is only available from the *cfg* file and
allows us to add extra information about the *Logging* call between the
*Logging* name and the level of the message, like this:

::

    .../[Log][Path]:[Line] [Level]: [Message]
    .../log[opt/dirac/DIRAC/.../standardLogging/Logging.py:325]INFO: message

It is composed by the caller object path and the line of the call. This
option requires that you set *LogShowLine* at *True* in the *cfg* file
and the root *Logging* level to *DEBUG* in order to be effective:

::

    ShowLogLine = True
    LogLevel = DEBUG

As the *threadIDIsShown* option, the *headerIsShown* boolean has to be
at *True* too. Moreover, it is totally possible to have the thread ID
and the caller path name at the same time.

Nevertheless, this option is useless because always displays the same
caller. It can be explained due to the *Logging* object which wrap the
original Python *logging* library.

Remove colors on the log records
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*LogColor* option is only available from the *cfg* file too, and only
for the *stdout* and the *stderr* with agents, services and executors.
By default, the *LogColor* option is set a *True* and adds colors on the
log records according to their levels. You can remove colors setting the
option at *False* in the *cfg* file:

::

    LogColor = False

We can find a *cfg* file example containing different options .

Get the option values
~~~~~~~~~~~~~~~~~~~~~

It is possible to obtain the names and the values associated of all
these options with the *getDisplayOptions* method. This method returns
the dictionary used by the *Logging* object itself and not a copy, so we
have to be careful with its use. Here is an example:

::

    logger = gLogger.getSubLogger("logger")
    logger.getDisplayOptions()
    # > {'Color': False, 'Path': False, 
    #    'headerIsShown': True, 'threadIsShown': False}

Send a log record in different outputs
--------------------------------------

Backend presentation
~~~~~~~~~~~~~~~~~~~~

*Backend* objects are used to receive the log record created before,
format it according to the choice of the client, and send it in the
right output. Currently, there are four different *Backend* object
inherited from a base. Here is a table presenting them:

[!ht]

+-----------------+-------------------------+
| Backend name    | Output                  |
+=================+=========================+
| stdout          | standard output         |
+-----------------+-------------------------+
| Stderr          | error output            |
+-----------------+-------------------------+
| RemoteBackend   | SystemLogging service   |
+-----------------+-------------------------+
| FileBackend     | file                    |
+-----------------+-------------------------+

As we may notice, *gLogger* has already a *stdout Backend* by default.

Add a *Backend* to your *Logging*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To send a created log record to an output, our root *Logging* has to add
some *Backend* objects in a list. To do such an operation, we have to
write the desired *Backend* objects in the *cfg* file using the
*LogBackends* option, like this:

::

    LogBackends = stdout,stderr,file,server

Here, we add all of the *Backend* object types in the root *Logging*.
Thus, a log record created will be sent to 4 different outputs. We can
find a *cfg* file example containing different options .

Configure the *Backend* objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some *Backend* objects need some parameters according to their nature.
By default, each type of *Backend* has default parameters but it is
possible to change them via the *BackendsOptions*\ section of the *cfg*.
Here is a table presenting the different parameters that we can
configure for each *Backend* and their default values:

[!ht]

| \|c\|c\|X\|c\| Type & Option & Description & Default value
| file & FileName & name of the file where the log records must be sent
& Dirac-log\_[pid].log
| server & SleepTime & sleep time in seconds & 150

We can also notice that the *server Backend* requires that the
*Framework/SystemLogging* service is running in order to send log
records to a log server.

Some examples and summaries
---------------------------

*cfg* file example
~~~~~~~~~~~~~~~~~~

Here is a component section which contains *Logging* and *Backend*
configuration:

::

    Agents
    {
        SimplestAgent
        {
          LogLevel = INFO
          LogBackends = stdout,stderr,file
          BackendsOptions
          {
            FileName = /tmp/logtmp.log
          }
          LogColor = False
          LogShowLine = True
        }
    }   

[cfgfile]

To summarize, this file configures an agent named *SimplestAgent*, sets
the level of *gLogger* at *info*, adds 3 *Backend* objects to it, which
are *stdout*, *stderr* and *file*. Thus, each log record superior to
*info* level, created by a *Logging* object in the agent, will be send
to 3 different outputs. We learn also from the *BackendOptions* that the
*file Backend* will send these log records to the */tmp/logtmp.log*
file.

In addition, the log records will be not displayed with color, and the
caller path name will not appear if we do not change the level to
*debug*.

Summary of the command line argument configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a complete table explaining the changes provided by the command
line argument *-d*:

[!ht]

[argstable]

+--------------------------------------+----------------+----------------+-----------+
| Argument                             | ShowHeader     | showThread     | Level     |
+======================================+================+================+===========+
| Default(Executors/Agents/Services)   | True           | False          | Notice    |
+--------------------------------------+----------------+----------------+-----------+
| Default(Scripts)                     | False          | False          | Notice    |
+--------------------------------------+----------------+----------------+-----------+
| -d                                   | DefaultValue   | DefaultValue   | Verbose   |
+--------------------------------------+----------------+----------------+-----------+
| -dd                                  | True           | DefaultValue   | Verbose   |
+--------------------------------------+----------------+----------------+-----------+
| -ddd                                 | True           | True           | Debug     |
+--------------------------------------+----------------+----------------+-----------+

About multiple processes and threads
------------------------------------

Multiple processes
~~~~~~~~~~~~~~~~~~

*DIRAC* is composed by many micro services running in multiple
processes. *gLogger* object is naturally different for two distinct
processes and can not save the application from process conflicts.
Indeed, *gLogger* is not process-safe, that means that two processes can
encounter conflicts if they try to write on a same file at the same
time. So, be careful to avoid the case.

Multiple threads
~~~~~~~~~~~~~~~~

*gLogger* is based on the Python *logging* library which is completely
thread-safe. Thus, it is also thread-safe.

Advanced use
============

Get a children tree
-------------------

As we said in the , all *Logging* objects can own a list of children and
a parent, and is part of a *Logging* tree like this:

[!ht]

(4)[xshift=-6cm,yshift=1cm]subsublogger;
(3)[xshift=-2cm,yshift=3cm]sublogger2;
(2)[xshift=-6cm,yshift=3cm]sublogger1;
(1)[xshift=-4cm,yshift=4cm]gLogger;

(1) edge node (2)

(1) edge node (3)

(2) edge node (4);

Here is a snippet presenting the creation of the tree seen above:

::

    # level 1
    logger = gLogger.getSubLogger("logger")
    # level 2
    sublogger1 = logger.getSubLogger("sublogger1")
    sublogger2 = logger.getSubLogger("sublogger2")
    # level 3
    subsublogger = sublogger1.getSubLogger("subsublogger")

Set a child level
-----------------

The truth about the levels
~~~~~~~~~~~~~~~~~~~~~~~~~~

In the basic part, we talked about the different ways to set a *Logging*
level. Only the *gLogger* level was allowed to be set.

This is because, in truth, *Logging* objects have two different levels:
their own level, set to *debug* and unchangeable, and the level of its
*Backend* objects. Thus, when we want to change the *Logging* level, we
change the *Backend* objects level of this *Logging* in reality.

In this way, every log records of every levels are created by every
*Logging* objects and can be send to a central logging server. The other
*Backend* objects can sort the log records according to the level
choosen by the user to send them or not to the output.

The level propagation
~~~~~~~~~~~~~~~~~~~~~

As every *Logging* object is part of a tree, the level of a parent can
be propagated to its children. Thus, we do not have to set all the
children levels:

::

    # gLogger level: NOTICE
    logger = gLogger.getSubLogger("logger")
    print logger.getLevel()
    # > NOTICE

While the children levels are not define by the user, they are modified
according to the parent level:

::

    logger = gLogger.getSubLogger("logger")
    sublogger = logger.getSubLogger("sublogger")
    print logger.getLevel()
    print sublogger.getLevel()
    # > NOTICE
    # > NOTICE
    logger.setLevel("error")
    print logger.getLevel()
    print sublogger.getLevel()
    # > ERROR
    # > ERROR

The only way to stop the propagation is to use the *setLevel* method on
a *Logging*. For instance, in the previous example, *logger* has now its
own level, and it can not be changed by its parent:

::

    logger = gLogger.getSubLogger("logger")
    print logger.getLevel()
    # > NOTICE
    logger.setLevel("error")
    print logger.getLevel()
    # > ERROR
    gLogger.setLevel("debug")
    print logger.getLevel()
    # > ERROR

Nevertheless, the propagation is still existing for the children of
*logger*:

::

    logger = gLogger.getSubLogger("logger")
    sublogger = logger.getSubLogger("sublogger")
    print logger.getLevel()
    print sublogger.getLevel()
    # > NOTICE
    # > NOTICE
    logger.setLevel("error")
    print logger.getLevel()
    print sublogger.getLevel()
    # > ERROR
    # > ERROR
    gLogger.setLevel("debug")
    print gLogger.getLevel()
    print logger.getLevel()
    print sublogger.getLevel()
    # > DEBUG
    # > ERROR
    # > ERROR
    logger.setLevel("verbose")
    print gLogger.getLevel()
    print logger.getLevel()
    print sublogger.getLevel()
    # > DEBUG
    # > VERBOSE
    # > VERBOSE

To summarize, a *Logging* receives its parent level until the user sets
its level with the *setLevel* method.

The *setLevel* utility
~~~~~~~~~~~~~~~~~~~~~~

As we said before, the *setLevel* method modifies the *Backend* objects
level of the current *Logging* so if this last mentionned have no
*Backend* objects, set its level become useless.

Furthermore, the *setLevel* method is useful only if we add it some
*Backend* objects.

Add a *Backend* object on a child *Logging*
-------------------------------------------

*registerBackends* presentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now, it is possible to add some *Backend* objects to any *Logging* via
the *registerBackends* method. This method takes two parameters, a list
of names of different *Backend* objects, and a dictionary of attribute
names and their values associated. Here is an example of use:

::

    logger = gLogger.getSubLogger("logger")
    logger.registerBackends(['stdout', 'file'], {'FileName': 'file.log'})

This, will create *stdout* and *file Backend* objects in *logger*. We
can add two *Backend* objects of the same type in a same
*registerBackends* call but it is not recommended. Indeed, we can not
add two same attributes in the dictionary of attributes. For instance,
two *file Backend* objects will have the same file name and log records
will appear two times inside. To have two different files in a same list
of *Backend* objects, we have to add them with two *registerBackends*
calls.

Log records propagation
~~~~~~~~~~~~~~~~~~~~~~~

Obviously, each log record created by a child *Logging* goes up in its
parent if the true *Logging* level allowed it, but as it is always at
*debug*, it goes up anyway. The log record goes up until *gLogger* and
it is displayed in all the *Backend* objects encounter in the parents if
the level allowed it.

In this way, *gLogger* display every log records of every *Logging*
object, even if you add *Backend* objects in a child, the log record
will appears multiple times in this case. Here is an example:

::

    # gLogger has a stdout Backend
    logger = gLogger.getSubLogger("logger")
    logger.registerBackends(['stdout'])
    logger.verbose("message")
    # > 2017-04-25 15:51:01 UTC Framework/Atom/logger VERBOSE: message
    # > 2017-04-25 15:51:01 UTC Framework/Atom/logger VERBOSE: message
    gLogger.info("message")
    # > 2017-04-25 15:51:01 UTC Framework/Atom/logger INFO: message

We can also notice that the log records do not go down in the tree.

The truth about the returned value of the level methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The boolean contained in the level methods seen indicates, in reality,
if the log record will appear or not in the *Backend* objects of the
current *Logging*. Thus, the boolean can be at *False* and the log
record can appear in one of its parent anyway.

The *registerBackends* utility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This functionality gives the possibility to isolate some log records
from a specific *Logging* or isolate log records above a specific level.
For example, we want only, at minimum, *error* log records providing by
a specific child named *logger* in a file named *file.log*. Here is a
snippet of this example:

::

    # gLogger: stdout Backend, NOTICE level 
    logger = gLogger.getSubLogger("logger")
    logger.registerBackends(['file'], {'FileName': 'file.log'})
    logger.setLevel("error")
    logger.verbose("appears only in stdout")
    logger.notice("appears only in stdout")
    logger.error("appears in stdout and in file.log")
    # in stdout: 
    # > ... UTC Framework/Atom/logger VERBOSE: appears only in stdout
    # > ... UTC Framework/Atom/logger NOTICE: appears only in stdout
    # > ... UTC Framework/Atom/logger ERROR: appears in stdout, in file.log
    # in file.log: 
    # > ... UTC Framework/Atom/logger ERROR: appears in stdout, in file.log

Modify a display for different *Logging* objects
------------------------------------------------

*showThreadIDs* and *showHeaders* propagation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that it is possible to add *Backend* objects to any *Logging*, we
have also the possibility to modify their display formats. To do such an
operation, we have to use the *showThreadIDs* and *showHeaders* methods
in a child. Of course, this child must contain at least one *Backend* to
be efficient.

Thus, these methods function exactly as the *setLevel* method, so they
can be propagate in the children if the options are not modified by the
user.

*showThreadIDs* and *showHeaders* utility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here, the utility is to modify the display format of the isolate log
records from a specific *Logging* to not be embarrassed with extra
information that we do not want for example:

::

    # gLogger: stdout Backend, NOTICE level, showHeaders at True 
    logger = gLogger.getSubLogger("logger")
    logger.registerBackends(['file'], {'FileName': 'file.log'})
    logger.setLevel("error")
    logger.showHeaders(False)
    logger.verbose("appears only in stdout")
    logger.notice("appears only in stdout")
    logger.error("appears in stdout and in file.log")
    # in stdout: 
    # > ... UTC Framework/Atom/logger VERBOSE: appears only in stdout
    # > ... UTC Framework/Atom/logger NOTICE: appears only in stdout
    # > ... UTC Framework/Atom/logger ERROR: appears in stdout, in file.log
    # in file.log: 
    # > appears in stdout, in file.log

The *LogShowLine* and *LogColor* cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These options can not be modified in the children of *gLogger*, even by
*gLogger* itself after the *cfg* configuration, so the children receive
the *gLogger* configuration.

Some examples and summaries
---------------------------

Summary diagram
~~~~~~~~~~~~~~~

Here is a diagram showing the complete path of a log record from its
creation to its emission in an output:

[!ht]

(L)[xshift=-4cm,yshift=3cm]**Logging**;
(B)[xshift=4cm,yshift=3cm]**Backend**; (1)[xshift=-4cm,yshift=2cm]*log
event*; (2)[xshift=-4cm,yshift=1cm]create;
(25)[xshift=-4cm,yshift=0.5cm]log records;
(3)[xshift=-4cm,yshift=-0.5cm]send to; (35)[xshift=-4cm,yshift=-1cm]each
Backend; (4)[xshift=-4cm,yshift=-2cm]propagate to;
(45)[xshift=-4cm,yshift=-2.5cm]the parent;
(5)[xshift=4cm,yshift=-0.5cm]check the level;
(6)[xshift=7cm,yshift=-0.5cm]end; (7)[xshift=4cm,yshift=-2cm]emit;
(75)[xshift=4cm,yshift=-2.5cm]to the output;

(ok)[xshift=6cm,yshift=0cm]*not ok*;
(notok)[xshift=5cm,yshift=-1.25cm]*ok*;

(parent)[xshift=-7.2cm,yshift=-1cm]*in the*;
(parent2)[xshift=-7.2cm,yshift=-1.5cm]*parent*;

(-5.5,-2) – (-6.5,-2) – (-6.5,-0.5) – (-4.8,-0.5);

(1) edge node (2)

(25) edge node (3)

(35) edge node (4)

(3) edge node (5)

(5) edge node (6)

(5) edge node (7) ;
