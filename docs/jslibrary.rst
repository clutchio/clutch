JavaScript Library Reference
============================

Applications using Clutch are made using a combination of native code and
HTML/CSS/JavaScript.  The Clutch JavaScript library is designed to create
content areas for your application using web technology that both looks and
feels native.

To achieve this kind of performance and flexibility, we've built the core of
the library on top of the best mobile JavaScript code we could find:
Zepto_, Backbone_, and Underscore_.


Core
----

The first thing that Clutch does when it loads is set up some bookkeeping and
set up a communication channel between your native code and your JavaScript
code.  Once that's all finished, it calls the function you attach using
``Clutch.Core.init``.

.. js:function:: Clutch.Core.init(func)

    :param func: The function to run once Clutch is initialized.

Keep in mind you should not start your rendering until after this function has
been called.  Here's an example of how that could look in your code:

.. code-block:: javascript

    Clutch.Core.init(function() {
        alert('Hello from Clutch!');
    });

Once that is set up, you can go ahead and use any of Clutch's resources--the
communication channel, the UI helpers, and more.

But the real core of Clutch is really just the communication channel between
the JavaScript that you write and the iOS code that you write.

.. js:function:: Clutch.Core.callMethod(methodName[, params, callback])

    :param string methodName:
        The name of the Objective-C method you want to call.
    :param params: An optional mapping of parameters to pass to the method.
    :param callback:
        An optional callback that will be called with the object passed into
        the callback block in Objective-C.
    :returns: Nothing

As you can see, it's simple and straightforward.  As an example, if a user
taps on a button and you want something to happen, you might write something
like this:

.. code-block:: javascript

    Clutch.Core.callMethod('userTapped', {userId: 10});

In this example, we're calling the ``userTapped`` method in your iOS code, and
passing an NSDictionary whose key ``userId`` is set to ``10``.  You can also
pass a callback function, which might look something like this:

.. code-block:: javascript

    Clutch.Core.callMethod('getUsername', function(data) {
        alert('Hello, ' + data.username);
    });

To register a function on the JavaScript side that iOS can call, Clutch
provides a ``registerMethod`` function.

.. js:function:: Clutch.Core.registerMethod(methodName, func)

    :param string methodName:
        The name of the JavaScript method that you are exposing.
    :param func: The actual JavaScript function to be exposed.

.. note::

    The function that you expose will always receive a single argument: an
    object of parameters passed from iOS.

Here's how it might look if you were to expose an ``alertUser`` function which
pops open an alert dialog with the given alert text:

.. code-block:: javascript

    function alertUser(params) {
        alert(params.alertText);
    }
    Clutch.Core.registerMethod('alertUser', alertUser);


Loading
-------

One thing we need to do all the time in building iOS apps is to wait for some
data.  Whenever we do that, we need to somehow indicate to the user that
there's something loading.  Clutch provides an easy mechanism for showing and
hiding loading screens.

.. js:function:: Clutch.Load.begin([loadingText], [top])

    :param string loadingText:
        Optional text to show to the user inside of the loading dialog.

    :param float top:
        Optional offset from the top of the ClutchView, in pixels.

    Pops up the loading dialog with optional loading text.

.. js:function:: Clutch.Load.end()

    Removes the loading dialog.


UI
--

Clutch helps you present a UI to your users that looks and feels like it's
native.  Here's what's provided:

.. js:function:: Clutch.UI.View([options])

    :param options: A mapping of options to be provided to the view instance.

    This view is the core of all of the Clutch-provided UI constructs.  It's
    actually a subclass of `Backbone.View`_, with a few added extras.  Here are
    the added properties and functions:

    .. js:attribute:: template

        The default template provided for all Clutch.UI.View subclasses is
        a simple `underscore template`_ that looks like ``<%= c.value %>``.
    
    .. js:function:: render()

        The default render for all Clutch.UI.View subclasses renders the
        template but passes the view options as the ``c`` varible.  It's
        equivalent to this implementation:

        .. code-block:: javascript

            $(this.el).html(this.template({c: this.options}));


.. js:function:: Clutch.UI.Table([options])

    :param options: A mapping of options to be provided to the view instance.

    This view creates a user interface that looks and acts like Cocoa's
    ``UITableView``.

    You must extend this view to populate it with any data, and here are the
    parameters you can provide in your extension:

    **Required**

    .. js:attribute:: numSections

        The number of table sections that should be displayed.
    
    .. js:function:: numCells(section)

        :param section: The 0-indexed integer of the current section.

        Determines the number of cells to be rendered for the given section.
    
    .. js:function:: cell(section, row)

        :param section: The 0-indexed integer of the current section.
        :param row: The 0-indexed integer of the current row.

        Returns the ``Clutch.UI.TableCell`` subclass that should render the
        requested table cell.

    **Optional**

    .. js:attribute:: style

        Determines the visual style of the table.  Currently only supports
        ``'normal'`` and ``'grouped'``.

    .. js:function:: tableHeader()

        Returns the ``Clutch.UI.TableHeader`` subclass that should render into
        the table's header area.
    
    .. js:function:: tableFooter()

        Returns tje ``Clutch.UI.TableFooter`` subclass that should render into
        the table's footer area.
    
    .. js:function:: sectionHeader(section)

        :param section: The 0-indexed integer of the current section.

        Returns a ``Clutch.UI.SectionHeader`` subclass that should render into
        the given table section's header area.
    
    .. js:function:: sectionFooter(section)

        :param section: The 0-indexed integer of the current section.

        Returns a ``Clutch.UI.SectionHeader`` subclass that should render into
        the given table section's footer area.


.. js:function:: Clutch.UI.TableHeader([options])

    :param options: A mapping of options to be provided to the view instance.

    A ``Clutch.UI.View`` subclass for rendering table headers.


.. js:function:: Clutch.UI.TableFooter([options])

    :param options: A mapping of options to be provided to the view instance.

    A ``Clutch.UI.View`` subclass for rendering table footers.


.. js:function:: Clutch.UI.SectionHeader([options])

    :param options: A mapping of options to be provided to the view instance.

    A ``Clutch.UI.View`` subclass for rendering table section headers.


.. js:function:: Clutch.UI.SectionFooter([options])

    :param options: A mapping of options to be provided to the view instance.

    A ``Clutch.UI.View`` subclass for rendering table section footers.


.. js:function:: Clutch.UI.TableCell([options])

    :param options: A mapping of options to be provided to the view instance.
    
    In that ``options`` object, here are the expected and optional parameters:

    **Required**
    
    .. js:attribute:: value

        The value that should be displayed in the cell.
    
    **Optional**

    .. js:attribute:: accessory

        Determines which accessory to display for the cell.  Should be one of
        ``Clutch.UI.Accessories``. 

    .. js:function:: tap(e)

        An optional function which will receive an event whenever this table
        cell is tapped by the end user.
    

.. note::
    
    If you subclass ``Clutch.UI.TableCell``, then you can set the ``multiline``
    attribute to ``true`` and it will be able to display more than one line
    of content.

    .. code-block:: javascript

        var MultiLineCell = Clutch.UI.TableCell.extend({
            multiline: true
        });


.. js:attribute:: Clutch.UI.Accessories

    Accessories that can be used to decorate a table cell.

    .. js:attribute:: Checkmark

        Shows a check mark.
    
    .. js:attribute:: DisclosureButton

        Shows a button with a right-facing triangle indicating that there is
        more content.
    
    .. js:attribute:: DisclosureIndicator

        Shows a right-facing triangle indicating that there is more content.


Example
-------

Here's an example of how you could use this JavaScript library to create a
table which has some cells and a few headers.

.. code-block:: javascript

    // Let's create a simple table by subclassing Clutch.UI.Table
    var SimpleTable = Clutch.UI.Table.extend({
        // Our table should have two sections
        numSections: 2,
        // We want it to display in the "grouped" style which looks cooler
        style: 'grouped',
    
        numCells: function(section) {
            // Each section has 4 cells
            return 4;
        },

        sectionHeader: function(section) {
            // The section header just displays its own index
            return new Clutch.UI.TableSectionHeader(
                {value: 'Section ' + section + ' Header'}
            );
        },

        sectionFooter: function(section) {
            // The first section doesn't have a footer
            if(section === 0) {
                return null;
            }
            // The second section does have a footer though
            return new Clutch.UI.TableSectionFooter(
                {value: 'Section ' + section + ' Footer'}
            );
        },

        cell: function(section, row) {
            var value = 'Section ' + section + ' Cell ' + row;
            return new Clutch.UI.TableCell({
                value: value,
                accessory: Clutch.UI.Accessories.DisclosureButton,
                tap: function(e) {
                    // Call the "tapped" method on iOS, and pass
                    // the text value of the cell as an argument.
                    Clutch.Core.callMethod('tapped', {value: value});
                }
            });
        }
    });

    // Remember to wait for this event before rendering out our table.
    Clutch.Core.init(function() {
        // Instantiate our new table
        var table = new SimpleTable();
        // Render the table
        $('body').append(table.render().el);
    });


.. _Zepto: http://zeptojs.com/
.. _Backbone: http://documentcloud.github.com/backbone/
.. _Underscore: http://documentcloud.github.com/underscore/
.. _`Backbone.View`: http://documentcloud.github.com/backbone/#View
.. _`underscore template`: http://documentcloud.github.com/underscore/#template