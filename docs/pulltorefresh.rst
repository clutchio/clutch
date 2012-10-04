Integrating Pull-to-Refresh
===========================

One common UI element that people like to have in their apps is
pull-to-refresh.  By using some open source software along with a little bit
of integration with Clutch, you can add this UI element to your Clutch screens
quite easily!


Download and Install EGOTableViewPullRefresh
--------------------------------------------

For the purposes of this tutorial, we're going to use the open source
`EGOTableViewPullRefresh`_ project, by the talented team at `enormego.com`_.
First you need to clone the repository::

    git clone https://github.com/enormego/EGOTableViewPullRefresh.git

Then open the directory::

    open EGOTableViewPullRefresh

Now drag the EGOTableViewPullRefresh folder into your XCode project.


Integrate EGOTableViewPullRefresh in Your Header File
-----------------------------------------------------

In your ViewController's header file, import the pull-to-refresh library
headers so that we have something to work with:

.. code-block:: obj-c

    #import "EGORefreshTableHeaderView.h"

Then add make sure your Clutch ViewController is a scroll view delegate, and a
``EGORefreshTableHeaderDelegate``:

.. code-block:: obj-c

    @interface ImageTableController : UIViewController <ClutchViewDelegate, UIScrollViewDelegate, EGORefreshTableHeaderDelegate>

Now add three properties:

.. code-block:: obj-c

    @property (nonatomic, retain) EGORefreshTableHeaderView *refreshHeaderView;
    @property (nonatomic, retain) NSDate *dateLastUpdated;
    @property (nonatomic, assign) BOOL reloading;


Synthesize and Instantiate Refresh Variables
--------------------------------------------

First, synthesize the new variables that you have added:

.. code-block:: obj-c

    @synthesize refreshHeaderView = _refreshHeaderView;
    @synthesize dateLastUpdated = _dateLastUpdated;
    @synthesize reloading = _reloading;

Now instantiate the view and set the last updated date in your ``loadView``,
and set this class as both the delegate and the scroll delegate for Clutch:

.. code-block:: obj-c

    - (void)loadView
    {

        // ...

        self.dateLastUpdated = [NSDate date];

        // Initialize the pull-to-refresh implementation
        self.refreshHeaderView = [[EGORefreshTableHeaderView alloc] initWithFrame:CGRectMake(0, -324, 320, 368)];
        [self.refreshHeaderView release];
        [self.view addSubview:self.refreshHeaderView];
        self.refreshHeaderView.delegate = self;
        [self.refreshHeaderView refreshLastUpdatedDate];

        // Set up the Clutch view
        self.clutchView = [[ClutchView alloc] initWithFrame:CGRectMake(0, 0, 320, 411)
                                                    andSlug:@"SOMESLUG"];
        [self.clutchView release];
        self.clutchView.delegate = self;
        self.clutchView.scrollDelegate = self;
        [self.view addSubview:self.clutchView];

        // ...

    }


Add Delegate Methods
--------------------

We're almost there!  Everything is set up, except there are a bunch of delegate
methods that are being called and we haven't yet implemented them yet.  First
up is the ``EGORefreshTableHeaderView`` delegate methods:

.. code-block:: obj-c

    - (void)egoRefreshTableHeaderDidTriggerRefresh:(EGORefreshTableHeaderView *)view
    {
        [self.clutchView.webView reload];
        self.reloading = TRUE;
    }

    - (BOOL)egoRefreshTableHeaderDataSourceIsLoading:(EGORefreshTableHeaderView *)view
    {
        return self.reloading;
    }

    - (NSDate*)egoRefreshTableHeaderDataSourceLastUpdated:(EGORefreshTableHeaderView *)view
    {
        return self.dateLastUpdated;
    }

    - (void)doneLoadingTableViewData
    {
        self.reloading = FALSE;
        self.dateLastUpdated = [NSDate date];
        [self.refreshHeaderView egoRefreshScrollViewDataSourceDidFinishedLoading:self.clutchView.scrollView];
    }

.. note::

    You may not want to just call ``[self.clutchView.webView reload]``.  You
    could also call a method in the JavaScript to refresh the data, or get the
    data using Objective-C code.  This is the easiest and simplest way to
    achieve a reload though.

Now we need to implement one of the ``ScrollViewDelegate`` delegate methods:

.. code-block:: obj-c

    
    - (void)scrollViewDidScroll:(UIScrollView *)scrollView
    {
        [self.refreshHeaderView egoRefreshScrollViewDidScroll:scrollView];
        
        // This slides the pull-to-refresh view into the proper location
        self.refreshHeaderView.frame = CGRectMake(self.refreshHeaderView.frame.origin.x,
                                                  -324.0f - scrollView.contentOffset.y,
                                                  self.refreshHeaderView.frame.size.width,
                                                  self.refreshHeaderView.frame.size.height);
    }


Pulling it All Together
-----------------------

We have one last step before this will all work properly.  Right now you have
a Clutch view that, when dragged, will reveal a pull-to-refresh panel.  When
you drag it down, it will reload the page.  But it won't yet know when it's
done refreshing.  That's a bummer, so let's fix it:

.. code-block:: obj-c

    - (void)clutchView:(ClutchView *)clutchView
          methodCalled:(NSString *)method
            withParams:(NSDictionary *)params
              callback:(void(^)(id))callback
    {
        // ...

        if([method isEqualToString:@"clutch.loading.end"]) {
            [self doneLoadingTableViewData];
        }

        // ...
    }

As you can see, we're hooking into the ``clutch.loading.end`` method call
to determine when loading is complete.  Now all that's left to do is call that
method in our JavaScript code:

.. code-block:: javascript

    Clutch.Core.init(function() {
        // Do your loading here, and then call...
        Clutch.Loading.end();
    });

Boom!  Now we're done integrating a pull-to-refresh into our Clutch screen.
Thanks to the power of great open source code and a bit of integration, it's
quite easy to get this great effect in your app.


Example
-------

We've built an example application called Imgs which uses this technique, so
you can `check out the code`_ and see how we did it in a real app.


.. _`EGOTableViewPullRefresh`: https://github.com/enormego/EGOTableViewPullRefresh
.. _`enormego.com`: http://enormego.com/
.. _`check out the code`: https://github.com/boilerplate/imgs