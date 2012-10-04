Clutch Command Client
=====================

The Clutch Command Client is the easiest way to communicate with Clutch.  You
will use it whenever you do development, whenever you want to push a new
version, and for various other tasks.  Here's a list of the commands
provided and what they are capable of:


Installing
----------

Installing the command client is as simple as running one command::

    sudo easy_install clutchclient

Once you've done that, typing ``clutch`` into the command line should show you
the command's usage instructions and you'll know that it's been successfully
installed.


Commands
--------

startapp
~~~~~~~~

``clutch startapp DIRNAME``

Starts a new application directory under the name ``DIRNAME``.  It will include
all of the clutchjs JavaScript and CSS files, as well as an empty configuration
plist.


startscreen
~~~~~~~~~~~

``clutch startscreen SCREENSLUG``

Starts a new screen directory under the name ``SCREENSLUG``.  It will include a
basic ``index.html`` base as well as a convenient place for your custom
JavaScript and css files.

.. note::

    Your current working directory must be a Clutch application directory, or
    else the Clutch Command Client will not be able to create a new screen
    directory.


dev
~~~

``clutch dev -a APPNAME [-d DIRNAME]``

Starts local development on a Clutch application.  If you use one of the iOS
devices `managed by your account`_ then all of the screens in your application
will be loaded on-demand from your computer rather than from the latest
published version.

By default, it will serve the current working directory, but you can specify
another directory to serve using the ``-d`` command flag.


upload
~~~~~~

``clutch upload -a APPNAME [-d DIRNAME]``

Uploads a new version of your Clutch application to production.  All of your
users will begin running the new code the next time they bring the application
into the foreground.

By default, it will upload the current working directory, but you can specify
another directory to serve using the ``-d`` command flag.

.. _`managed by your account`: http://clutch.io/devices/