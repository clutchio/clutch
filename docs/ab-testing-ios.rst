iOS SDK
=======

If you don't have an account on your Clutch.io instance yet, you'll need to
`do that first`_.  If you don't have a Clutch.io instance set up yet, follow
the steps on the `Clutch project README`_.  Otherwise, follow the steps below.


Getting Started
---------------

First make sure you have the `Clutch library`_ added to your project.  To do
so, download the library, extract the zip file, and drag the Clutch.framework
folder into your project.  Make sure that the library is in your project's
linked frameworks section.  The `Clutch library`_ depends on libsqlite3.dylib,
so make sure to link that as well.

Now import the Clutch A/B Testing library in your project's ``AppDelegate.h``,
like so:

.. code-block:: obj-c

    #import <Clutch/ClutchAB.h>

Now in your project's ``AppDelegate.m``, under
``application:didFinishLaunchingWithOptions:``, add the following code:

.. code-block:: obj-c

    [ClutchAB setupForKey:@"YOUR_APPLICATION_KEY" rpcURL:@"YOUR_RPC_URL"];

That's it--you're now set up to run tests!


Normal Tests
------------

The function for running a test is ``testWithName:A:B:``.  This can be given up
to 10 different code blocks, by adding the next letter in the alphabet.  A test
with four code blocks would look like this: ``testWithName:A:B:C:D:``.

Example:

.. code-block:: obj-c

    // Create a button and add it to the navigation bar
    UIBarButtonItem *loginButton = [
        [UIBarButtonItem alloc] initWithTitle:@"Log In" 
                                        style:UIBarButtonItemStyleBordered 
                                       target:self 
                                       action:@selector(ensureUser)];

    self.navigationItem.rightBarButtonItem = loginButton;
    
    // Test which color of tint performs better
    [ClutchAB testWithName:@"loginButtonColor" A:^{
        // Red?
        loginButton.tintColor = [UIColor redColor];
    } B:^{
        // Or green?
        loginButton.tintColor = [UIColor greenColor];
    }];

    [loginButton release];


Data-driven Tests
-----------------

The function for running a data-driven test is ``testWithName:data``.  The code
block that's passed in must accept one NSDictionary argument.

Example:

.. code-block:: obj-c

    // Create a button and add it to the navigation bar
    UIBarButtonItem *loginButton = [
        [UIBarButtonItem alloc] initWithTitle:@"Log In" 
                                        style:UIBarButtonItemStyleBordered 
                                       target:self 
                                       action:@selector(ensureUser)];

    self.navigationItem.rightBarButtonItem = loginButton;
    
    [ClutchAB testWithName:@"loginButtonTitle" data:^(NSDictionary *testData) {
        // Extract the title from the testData dictionary, and assign it to the button.
        loginButton.title = [testData objectForKey:@"title"];
    }];

    [loginButton release];


Goal Reached
------------

The function for noting that a goal was reached is ``goalReached:``, where the
argument is the test's short name.

Example:

.. code-block:: obj-c

    - (void)newAccountCreated {
        // A new account was created, so whatever button color was chosen, worked!
        [ClutchAB goalReached:@"loginButtonColor"];
    }


Extras
------

It's very common for data-driven tests to be color-related.  To aid in this, we
have provided a simple function for getting a UIColor out of a hex-string.

Example:

.. code-block:: obj-c

    UIColor *buttonColor = [ClutchAB colorFromHex:@"FF0044"];

Here's how it might be used with a data-driven test:

.. code-block:: obj-c

    [ClutchAB testWithName:@"loginButtonVariableColor" data:^(NSDictionary *testData) {
        // Extract the color from the testData dictionary, and assign it to the button.
        loginButton.tintColor = [ClutchAB colorFromHex:[testData objectForKey:@"color"]];
    }];


.. _`do that first`: http://127.0.0.1:8000/register/
.. _`Clutch project README`: https://github.com/clutchio/clutch/blob/master/README.rst
.. _`Clutch library`: https://github.com/downloads/clutchio/clutchios/Clutch-iOS-Latest.zip