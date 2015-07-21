title: "Command line arguments and object factories"
date: 2013-12-21 16:14:27
published: 2013-12-21 16:14:27
subtitle: Towards multiple demos
description:
     Towards multiple demos
created: !!timestamp 2013-12-21 16:14:27

## tl;dr ##

Using D's [getopt](http://dlang.org/phobos/std_getopt.html) standard library
and [Object.factory](http://dlang.org/phobos/object.html#.Object.factory), I've
made it easy to choose between multiple programs from a single executable.

## Moving on to the next demo ##

The next OpenGL topic will most likely be about perspective, which a spinning
multi-colour tetrahedron is not terribly helpful with.  But I'm pretty happy
with that (and the tearing will remind me to get back to that later), so I want
to start a new demo.  (It will also help to see multiple programs to decide how
to create a small framework and set of library functions to simplify building
new ones.)

Up to now, the source/app.d (the default entry-point used by `dub`) was really
simple - just five lines of code:

    :::d
    module app;

    import abandonedtemple.demo1;

    void main() {
        Demo1 d = new Demo1(640, 480, "Hello");
        d.run();
    }

What I want to do instead is allow the demo to be chosen on the command line,
and to instantiate that demo and run it.  I remembered reading about
`Object.factory` in The D Programming Language, so at least I knew it would be
possible.

## Object.factory ##

First step was just instantiating the existing demo:

    :::d
    auto o = Object.factory("abandonedtemple.demo1.Demo1");

That surprisingly (at the time) did not work.  It didn't take long to realize
why - the only constructor expected a bunch of parameters.  So I shoved in a
default constructor that called the original one with default values, and that
worked fine.

## Command line arguments ##

Next step was getting the demo to run from the command line.  Instead of no
arguments, `main` now needs to take an array of strings:

    :::d
    void main(string[] args) {
    }

I ran into the `dub` "pass on the rest of the arguments to the executable"
argument separator earlier, so I used it:

    :::
    dub -- --demo=demo1

Printing that out, the arguments were:

    :::json
    ["./abandonedtemple", "--demo=demo1"]

## std.getopt ##

I also recalled `std.getopt` existed but not much about it, and not having the
book on me, I visited [dlang.org](http://dlang.org/) and found
[std.getopt](http://dlang.org/phobos/std_getopt.html).

Besides a bit of sadness about the way single-letter arguments work (`-i5` is
the only way short options work with values - `-i 5` does not), it has a nice
user experience.

Here's the example code from the module documentation:

    :::d
    import std.getopt;

    string data = "file.dat";
    int length = 24;
    bool verbose;
    enum Color { no, yes };
    Color color;

    void main(string[] args)
    {
      getopt(
        args,
        "length",  &length,    // numeric
        "file",    &data,      // string
        "verbose", &verbose,   // flag
        "color",   &color);    // enum
      ...
    }

As you can see, there's no messing with type descriptions in the call to getopt
- the referenced variable tells getopt what type is expected, including enums
and arrays and even maps and custom functions.  Another potential missed
opportunity here is auto-generating help.

## The new entry-point ##

Anyway, with that help, here's the new entry-point `source/app.d`:

    :::d
    module app;

    import std.stdio : writefln;
    import std.getopt : getopt;

    import abandonedtemple.demos.base;

    void main(string[] args) {
        auto demo = "demo1";
        getopt(args, "demo", &demo);

        auto demo_classname = "abandonedtemple.demos." ~ demo ~ ".Demo";
        auto o = Object.factory(demo_classname);
        if (o) {
            (cast(DemoBase)o).run();
            return;
        }
        writefln("Could not find specified demo: %s", demo);
    }

I take the demo name from the command line (or default to "demo1" for now), and
construct the class name from that.  By convention all demos will live in
`abandonedtemple.demos` and have a `Demo` class.  I created a base interface
(just `void run()`) that they all implement so that I can cast to that and run
the demo from here.

## Putting it together ##

[Here][commit1] is the state of my code repo at this point.  A later
[commit][commit2] added a bit of documentation.

[commit1]: https://github.com/nxsy/abandonedtemple/tree/69c9d72943ce5e38ef6fd8a316e0cd6a635e6783
[commit2]: https://github.com/nxsy/abandonedtemple/tree/e5090888ea14752a1947a0785c10c08b8dc58cab
