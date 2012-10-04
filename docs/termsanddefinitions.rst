Terms and Definitions
---------------------

.. glossary::

    Clutch App
        A container holding all of the files that will make up the
        HTML/JavaScript/CSS portion of your app.  This container is registered
        with Clutch and is given a name and a short name to easily talk about it.

    Screen
        A content area that will be shown to the user using your app. Each
        :term:`Clutch App` contains one or more screens.  Examples of a screen could be
        a user profile or a list of friends.  This roughly corresponds one-to-one
        with the number of UIViewControllers in your app that use Clutch.
    
    Short Name
        The short version of an app name that is used in the URL for your
        :term:`Clutch App` and is typed into the command line.  For instance an
        app named "Example App" might have the short name "exampleapp", which
        you might type into the command line like ``clutch dev -a exampleapp``.
        Some people might refer to this as a Slug_.

.. _Slug: http://en.wikipedia.org/wiki/Slug_(web_publishing)