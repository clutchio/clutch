iOS Library Reference
=====================

The Clutch iOS library syncs up your latest code, helps you analyze usage about
your app, and provides a bi-directional bridge between your JavaScript code and
your Objective-C code.


ClutchSync
----------

.. code-block:: obj-c

    - (void)sync

Intended to be called when the app finishes launching.  Syncs to the latest
version of the application code.

.. code-block:: obj-c

    - (void)foreground

Intended to be called when the app is brought into the foreground.  Syncs
to the latest version of the application code.


.. code-block:: obj-c

    - (void)background

Intended to be called when the app is sent to the background.  Performs
cleanup and sends statistics information.

.. code-block:: obj-c

    + (ClutchSync *)sharedClientForKey:(NSString *)appKey
                         tunnelURL:(NSString *)tunnelURL
                            rpcURL:(NSString *)rpcURL;

Returns a ``ClutchSync`` client instance for the given application key, tunnel
URL, and RPC URL.


ClutchView
----------

.. code-block:: obj-c

    - (id)initWithFrame:(CGRect)frame andSlug:(NSString *)slug

Initializes a Clutch view instance with the given frame and screen slug.

.. code-block:: obj-c

    - (id)callMethod:(NSString *)method withParams:(NSDictionary *)params

Calls a JavaScript method (that has been registered with Clutch) and returns
its response.  The ``params`` dictionary is the parameters you woud like to
pass as an argument to the JavaScript function.

.. code-block:: obj-c

    - (id)callMethod:(NSString *)method

The same as the previous call except no ``params``.

.. code-block:: obj-c

    - (void)viewDidAppear:(BOOL)animated

Should be called when its containing view controller's viewDidAppear is called.

.. code-block:: obj-c

    - (void)viewDidDisappear:(BOOL)animated

Should be called when its containing view controller's viewDidDisappear is
called.

.. code-block:: obj-c

    + (void)logDeviceIdentifier

Logs the current device's identifier, for use on the `add device page`_.

.. code-block:: obj-c

    + (void)prepareForAnimation:(UIViewController *)viewController success:(void(^)(void))block_

    + (void)prepareForDisplay:(UIViewController *)viewController success:(void(^)(void))block_

Prepares the given view controller subclass for animation or display (such as
adding it to a navigation controller) and then calls the given ``success``
block.

.. code-block:: obj-c

    + (void)prepareForDisplay:(UIViewController *)viewController;

Prepares the given view controller subclass for display, and does not call any
callback.

Properties
~~~~~~~~~~

.. code-block:: obj-c

    id delegate

You may set this property to point to any instance of ClutchViewDelegate_ and
it will allow you to communicate between JavaScript and Objective-C.

.. code-block:: obj-c

    id scrollDelegate

You may set this property to any instance of ``UIScrollViewDelegate``, which
will send updates for all of the scrolling that happens on the web view.

.. code-block:: obj-c

    UIWebView *webView

The underlying webview that is the main workhorse of each ClutchView.

.. code-block:: obj-c

    UIScrollView *scrollView

The webview's scrollview.  Useful for being updated as the user scrolls the
webview's contents, as in a pull-to-refresh implementation.


ClutchViewDelegate
------------------

.. code-block:: obj-c

    - (void)clutchView:(ClutchView *)clutchView
          methodCalled:(NSString *)method
            withParams:(NSDictionary *)params

Called when JavaScript calls the ``Clutch.Core.callMethod(method, params)``
method, which is useful for communication between your JavaScript code and
your Objective-C code.

.. code-block:: obj-c

    - (void)clutchView:(ClutchView *)clutchView
          methodCalled:(NSString *)method
            withParams:(NSDictionary *)params
              callback:(void(^)(id))callback

Similar to the above method, except that this time it provides a callback that
you can call.  Whatever object you pass to this callback will be sent to your
JavaScript callback.


.. _ClutchConf:

ClutchConf
----------

.. code-block:: obj-c

    + (NSDictionary *)conf

Gets the latest configuration (provided by clutch.plist).

.. code-block:: obj-c

    + (NSInteger)version

Gets the latest version of the configuration.


.. _`add device page`: http://127.0.0.1:8000/devices/create/