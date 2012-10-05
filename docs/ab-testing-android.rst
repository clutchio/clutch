Android SDK
===========

If you don't have an account on your Clutch.io instance yet, you'll need to
`do that first`_.  If you don't have a Clutch.io instance set up yet, follow
the steps on the `Clutch project README`_.  Otherwise, follow the steps below.


Getting Started
---------------

First, download the `Clutch library`_ JAR file, and add it to your project.
Now, in your project's main Activity, you should add three calls: one in
``onCreate``, another in ``onPause``, and finally one in ``onResume``.  Here's
how it should look:

In your ``onCreate``, call the ``ClutchAB.setup(Context ctx, String key)``
method:

.. code-block:: java

    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ClutchAB.setup(this.getApplicationContext()
            "YOUR_APPLICATION_KEY",
            "YOUR_RPC_URL"
        );

        // The rest of your code here, maybe something like:
        // setContentView(R.layout.main);
    }

In your ``onPause``, call the ``ClutchAB.onPause()`` method:

.. code-block:: java

    protected void onPause() {
        super.onPause();
        ClutchAB.onPause();
    }

In your ``onResume``, call the ``ClutchAB.onResume()`` method:

.. code-block:: java

    protected void onResume() {
        super.onResume();
        ClutchAB.onResume();
    }

Those three integration points will set everything up, and prepare your code to
begin A/B testing.


Normal Tests
------------

The function for running a test is
``ClutchAB.test(String name, ClutchABTest test)``.  The ``ClutchABTest`` object
should be an anonymous subclass and you can implement ``public void A()`` all
the way up to ``public void J()`` for up to ten different tests per experiment.

Example:

.. code-block:: java

    // Find our login button
    final Button loginButton = (Button)findViewById(R.id.login_button);
    
    // Test which color performs better
    ClutchAB.test("loginButtonColor", new ClutchABTest() {
        public void A() {
            // Red?
            loginButton.setBackgroundColor(Color.RED);
        }
        public void B() {
            // Or green?
            loginButton.setBackgroundColor(Color.GREEN);
        }
    });


Data-driven Tests
-----------------

The function for running a data-driven test is
``ClutchAB.test(String name, ClutchABDataTest test)``.  The
``ClutchABDataTest`` object should be an anonymous subclass that must implement
``public void action(JSONObject testData)``.

Example:

.. code-block:: java

    // Find our login button
    final Button loginButton = (Button)findViewById(R.id.login_button);
    
    ClutchAB.test("loginButtonTitle", new ClutchABDataTest() {
        public void action(JSONObject testData) {
            loginButton.setText(testData.optString("title"));
        }
    });


Goal Reached
------------

The function for noting that a goal was reached is
``ClutchAB.goalReached(String name)``, where the argument is the test's short
name.

Example:

.. code-block:: java

    public void onNewAccountCreated() {
        // A new account was created, so whatever button color was chosen, worked!
        ClutchAB.goalReached("loginButtonColor");
    }


.. _`do that first`: http://127.0.0.1:8000/register/
.. _`Clutch project README`: https://github.com/clutchio/clutch/blob/master/README.rst
.. _`Clutch library`: https://github.com/downloads/clutchio/clutchandroid/Clutch-Android-Latest.jar