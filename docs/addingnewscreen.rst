Adding a New Screen
===================

Once you have your app all set up and configured, the most common task you will
want to do is add a new screen.  Fortunately, this is quite easy!

First, come up with a short name that you would like to identify this new
screen, which we refer to as the "slug", and the Objective-C class name.  For
example if you are creating a screen to present a photo to the user, you might
choose ``photo`` as your slug, and you might want to choose something like
``PhotoViewController`` for your new file in XCode.

To help make this easier, we've created a tool to help get the details right.
All you have to do is enter your choices below:

.. raw:: html

    <label for="slug">Slug:</label>
    <input type="text" id="id_slug" name="slug" value="photo" />
    <br />
    <div class="clear"></div>
    <label for="name">Controller Name:</label>
    <input type="text" id="id_name" name="name" value="PhotoViewController" />
    <div class="clear"></div>
    <br />

Now you should type this command into
Terminal.app (make sure you change to the directory holding your Clutch
JavaScript first)::

    clutch startscreen $SLUG$

Now you should go to your XCode project and add a new file.  Choose
"UIViewController subclass" when it asks.  Name it what you decided above, and
then copy this into $NAME$.h:

.. code-block:: obj-c

    #import <UIKit/UIKit.h>
    #import <Clutch/Clutch.h>

    @interface $NAME$ : UIViewController <ClutchViewDelegate>

    @property (nonatomic, retain) ClutchView *clutchView;

    @end

Now copy this into $NAME$.m:

.. code-block:: obj-c

    #import "$NAME$.h"

    @implementation $NAME$

    @synthesize clutchView = _clutchView;

    - (void)didReceiveMemoryWarning
    {
        // Releases the view if it doesn't have a superview.
        [super didReceiveMemoryWarning];
        
        // Release any cached data, images, etc that aren't in use.
    }

    #pragma mark - ClutchViewDelegate

    - (void)clutchView:(ClutchView *)clutchView
          methodCalled:(NSString *)method
            withParams:(NSDictionary *)params
              callback:(void(^)(id))callback {
        // Handle any events coming from the JavaScript of your Clutch view here
        if([method isEqualToString:@"tapped"]) {
            NSLog(@"Tapped: %@\n", [params objectForKey:@"value"]);
        }
    }

    #pragma mark - View lifecycle

    - (void)loadView
    {
        self.view = [[[UIView alloc] initWithFrame:[[UIScreen mainScreen] bounds]] autorelease];
        
        self.clutchView = [[ClutchView alloc] initWithFrame:CGRectMake(0, 0, 320, 367)
                                                    andSlug:@"$SLUG$"];
        [self.clutchView release];
        self.clutchView.delegate = self;
        [self.view addSubview:self.clutchView];
    }

    /*
    // Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
    - (void)viewDidLoad
    {
        [super viewDidLoad];
    }
    */

    - (void)viewDidUnload
    {
        [super viewDidUnload];
        self.clutchView = nil;
    }

    - (void)viewDidAppear:(BOOL)animated
    {
        [super viewDidAppear:animated];
        [self.clutchView viewDidAppear:animated];
    }

    - (void)viewDidDisappear:(BOOL)animated {
        [super viewDidDisappear:animated];
        [self.clutchView viewDidDisappear:animated];
    }

    - (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
    {
        // Return YES for supported orientations
        return (interfaceOrientation == UIInterfaceOrientationPortrait);
    }

    @end

This is a standard ``UIViewController`` subclass, which instantiates a single
``ClutchView`` instance and adds it to the view, sets itself up as a delegate
to handle events that come in from the JavaScript layer, and passes along any
``viewDidAppear:`` and ``viewDidDisappear:`` messages into the Clutch view.

**That's it!** You've got your screen hooked up and now it's up to you to use
it for good, not evil.