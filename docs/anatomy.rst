Anatomy of an App Using Clutch
==============================

If you used our QuickStart guide, we may have breezed past some of the details
about all of the different parts that combine to form an app using Clutch.
This article should serve to highlight each part of the system, how it works,
and how it all fits together.


The Suggested Directory Structure
---------------------------------

The way the suggested directory structure looks is something like this::

    MyApp/
        MyApp/
            MyApp.xcodeproj
            Clutch.framework
            MyApp/
        clutchmyapp/
            clutch-core/
            global/
            myscreen/
                index.html
                screen.js
                style.css
            clutch.plist

If you have a directory structure that looks different, that's fine, but this
is the one that the QuickStart guide will start you with.  (The most common
way that yours could differ is if your clutchmyapp directory is in a different
spot, or is named something different.)

First, there's the outer ``MyApp`` directory.  This is honestly just a
container to hold the inner two directories, so that they can both be checked
into a single source code repository.  Feel free to rename this container
directory to anything you want.

Inside that container, there's an inner ``MyApp`` directory which stores your
iOS XCode project and the Clutch framework, as well as an inner inner ``MyApp``
directory which contains your actual native Objective-C code.  This is pretty
straightforward.

Then, there's the ``clutchmyapp`` directory.  This is where all the
JavaScript/HTML/CSS goes that will make up the screens in your app.  There are
three things in there that are auto-generated.  ``clutch-core`` contains our
libraries and static files, like backbone, zepto, and our base css.  ``global``
contains any JavaScript/HTML/CSS that you want to reuse across most (or all) of
your screens.  Also there's a ``clutch.plist``, which holds any configuration
information you'd like to access but be able to dynamically update.

Finally there's the ``myscreen`` directory, which is automatically created with
an HTML file, a JavaScript file, and a CSS file.  You will create more and more
of these as your application gets larger.  You can choose to fill those files
with code, or you can just leave them blank.  For example in one screen, let's
say it's an FAQ page, you might just have static content, so you'd just
hand-code the HTML file.  Other screens might be more dynamic and so the HTML
file would be left minimal, but the JavaScript file would fill up with your
display logic.


The Folder Reference
--------------------

This correlates to the ``clutchmyapp`` folder from the previous section.  It
needs to be linked into your app as a folder reference for a few reasons.
Firstly, it's because we want to bundle a version of the HTML/CSS/JavaScript
needed to run your app.  This means that the first time the user opens the app,
they have a version of the HTML/CSS/JavaScript ready to go.  So there's no need
for internet connectivity to run an app that uses Clutch.

The second reason that this folder needs to be linked into your app as a folder
reference is due to the ``clutch.plist`` file contained within.  This file is
used to store configuration.  You can use the  :ref:`ClutchConf <ClutchConf>`
module to access the contents of this file, and then later you can update this
configuration file remotely without having to push out a new application.  This
might be used, for example, to determine the text to display on a native
button.


How an App Fits Together
------------------------

At first glance, Clutch might look similar to an framework like PhoneGap or
Appcelerator Titanium, where you write your whole app in JavaScript and/or
HTML.  Sometimes these solutions use an abstraction layer that aims to make it
possible to target other platforms.  In fact, Clutch works in a way that's
quite a bit different.  Instead, you create your own
``UINavigationController``, your own ``UITabBarController``, and set up your
own project the way you like it, and the way you've done it in the past.

The only thing that changes from normal iOS development is that instead of
using a XIB or interface builder to build your UI layer for some screen, you
can have Clutch help you to use web technologies instead.

That means, you carve out an area that you want to be able to update
dynamically, and in that ``UIViewController``'s ``loadView`` method, you simply
instantiate a ``ClutchView`` and add it as a subview.

Then you use our bridge layer to pass any important events from the Clutch view
back into the Objective-C layer, and handle those events natively.


The Bridge
----------

The bridge between your JavaScript code and you Objective-C code means that you
can handle any event in the layer that makes the most sense.  For things that
do fancy animations, or pop open modal windows, or slide to a new screen, you
will want to do these things natively.  For things that involve simple text
changes or content changes, you can handle that directly in JavaScript.

It also works in the other direction.  You can capture events that happen in
the native layer, like a ``UIToolbar`` button being pressed, and call into a
function on the JavaScript side of things.


Development Mode
----------------

So there's this whole step that you did where you entered in your phone's
identifier and associated it with your account, but what was that for?

It allows Clutch to enable development mode.  Nobody writes perfect code on
their first try.  We know that there's a back-and-forth where you want to
experiment, try out a change, see how a CSS tweak looks, and you don't want to
send that out to your users every time.  Instead, we provide a development mode
which, when it sees your specific registered phone, it doesn't serve the normal
app using the normal methods.

Instead it connects to your local computer, to your working set of files, and
renders what you've written--rather than what you've deployed.  On top of that,
it shows a nice toolbar that lets you know you're in development mode, and
gives you the option to quickly refresh the ``ClutchView``, so you can avoid
lengthy recompiles or re-navigating back to that same screen that you're
viewing.