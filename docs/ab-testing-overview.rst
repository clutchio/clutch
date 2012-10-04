Overview
========

A/B testing is a way of showing users different variations of your app, and
then measuring how each variation affects your goals.  For example, if you're
interested in having your users make more in-app purchases, you might test the
phrase "buy more coins now!" versus "save time by buying coins".  Clutch's A/B
testing tools can tell you which one will make you more money.

Types of Tests (Normal vs. Data-Driven)
---------------------------------------

With Clutch's A/B testing framework, you have the option of two different types
of tests: normal, and data-driven.

**Normal** tests are simpler: you give the framework two (or more) different
pieces of code to run.  We then choose one of those pieces of code, and run it,
and report back to you which version improves whichever metrics you care about.
This is best for qualitative things like whether a label should go on the left
or right side of an image.

**Data-driven** tests only have one code path, but that code is passed data from
the server, which can be changed after the app is live in the app store.  Your
code should extract some variable from that data, and use it in it's test.
This is good for quantitative things like button color, font size, or text
copy.


Tracking Goals
--------------

Tests are only good when they can measure some metric and show you which path
is performing better.  To help out our system, that metric should be a "goal".
Good examples of goals are things like an in-app purchase, a new account
created, or even a tap on an advertisement.