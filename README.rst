Clutch.io
=========

Clutch.io is two projects:

* Native A/B testing for iOS and Android
* A toolkit for developing hybrid native/HTML applications for iOS

You may be interested in one or the other, but this project is the server
component for both projects.


Prerequisites
=============

* Python 2.6 or Greater
* PostgreSQL (including the required headers to compile psycopg2)
* libevent 2.0.20
* S3 Account (for hybrid native/html application framework ONLY)


Installing and Running Clutch.io
================================

Before you get started, make sure all of the prerequisites are installed and
that PostgreSQL is running.  Now we need to create a Clutch user and database:

    createuser -s clutch

    createdb -E utf8 --owner=clutch clutch

Next we need to install Clutch:

    easy_install clutchserver

Now we will generate a configuration file used to setup ports and such:

    clutch-config > conf.py

You can check the configuration defaults provided by clutch-config and decide
whether they are right for your setup.  For most people, the defaults should be
just fine.  When you're ready, let's start up the server:

    clutch-all conf.py

That's it, you're now running Clutch.io!  Visit http://127.0.0.1:8000/ to see
it in action.


More Documentation
==================

See http://clutchio.github.com/


Local Documentation
===================

To generate a local copy of the above documentation, first check out this repo:

    git clone https://github.com/clutchio/clutch.git

Make sure you have Sphinx installed so that you can generate the docs:

    easy_install Sphinx==1.1.3

Now change to the docs directory and make the docs

    cd clutch/docs
    make html

Finally, open the docs:

    open _build/html/index.html


Tests
=====

To run the tests, generate a test configuration file using clutch-config like
above, but instead of using clutch-all to run it, use clutch-test:

    clutch-test conf.py

This is one area where this project could use a lot of help.  If you're
interested in contributing, helping out by improving our test coverage is a
great place to start!