title: "Introducing Abandoned Temple"
date: 2013-12-12 07:08:55
published: 2013-12-12 07:08:55
subtitle: The initial commit
description:
    The initial commit
created: !!timestamp 2013-12-12 07:08:55

## tl;dr ##

I've codenamed my D  and OpenGL explorations "Abandoned Temple", and started a
[repo](https://github.com/nxsy/abandonedtemple).

## package.json ##

Here's the first file I created, the `package.json` file that [dub] will use to
fetch dependent packages and to build the application:

    :::json
    {
        "name": "abandonedtemple",
        "description": "A slowly-developing exploratory OpenGL game",
        "homepage": "https://github.com/nxsy/abandonedtemple",
        "copyright": "Copyright © 2013 Neil Blakey-Milner",
        "authors": [ "Neil Blakey-Milner" ],

        "targetPath": "build/bin",

        "dependencies": {
            "derelict-glfw3": "~master",
            "derelict-gl3": "~master"
        }
    }

It's basically just a copy of what I was using in my demo, but I moved the
target path to `build/bin`, not just `bin`.  I did this so that I can lay out
the MacOS application package, potentially with accompanying libraries and
other resources.

## scripts/config.sh ##

One currently problematic step in starting to use Derelict is that it just
wraps libraries, and does not provide them.  You need to find those libraries
yourself.  I haven't solved that part yet, but scripts/config.sh will at least
put the needed library in the right place once you've found it.  For now, I
suspect I'll need libglfw, so I need `libglfw.3.dylib` put in the same
directory as the binary 

This script stashes a copy in `.lib` in case you want to blow away `build` and
reconfigure.

    :::sh
    #!/bin/sh

    set -e
    set -u

    cd `dirname $0`
    cd ..

    if [ ! -d build/bin ]; then
        mkdir -p build/bin
    fi

    # .libs will contain links to 
    if [ ! -d .libs ]; then
        mkdir .libs
    fi

    if [ -n "${LIBGLFWPATH:-}" ]; then
        if [ -e "${LIBGLFWPATH}" ]; then
            cp "${LIBGLFWPATH}" .libs/libglfw.3.dylib
        fi
    fi

    while [ ! -e .libs/libglfw.3.dylib ]; do
        read -p "Please provide full path to libglfw.3.dylib:" LIBGLFWPATH
        if [ -e "${LIBGLFWPATH}" ]; then
            cp "${LIBGLFWPATH}" .libs/libglfw.3.dylib
            break
        fi
        echo "Could not find libglfw.3.dylib at ${LIBGLFWPATH}"
    done

    if [ ! -e build/bin/libglfw.3.dylib ]; then
        cp .libs/libglfw.3.dylib build/bin/libglfw.3.dylib
    fi

I firmly believe all shell scripts should start with `set -e` and `set -u`.
Without them, the script will crash on ahead despite encountering errors
running commands, or being unable to find a variable you've mistyped.

The `` cd `dirname $0` `` is magic to change to the directory that contains the
script, no matter where it is executed from, allowing the use of relative paths
from then on.

## source/app.d ##

I think this is the simplest compilable/runnable `source/app.d` file, just here
to have something to build and run:

    :::d
    module app;

    void main() {
    }

## README ##

It's always good to describe what your projects do, and how to do the
configure, build, run, and package dance.

    :::text
    Abandoned Temple
    ----------------

    One-time configure:

        LIBGLFWPATH=/path/to/libglfw3.dylib  # optional, config.sh will ask otherwise
        sh scripts/config.sh

    Build && run:

        dub

    Just build:

        dub build

## LICENSE ##

I don't expect to be doing anything I don't want others to be able to build on,
and I don't expect to care if they do it in public or privately, so I chose the
MIT license for now.

Since I would own the copyright on the content of the repo, I can always change
this later.

## .gitignore ##

Here to make `git status` and other git commands generally only operate on
files that belong in the repo, and to reduce the likelihood that I will commit
build artifacts.

    :::
    /.dub/
    /.libs/
    /build

Ran the configure steps, and added things that showed up new to `.gitignore`
until `git status` was happy.

## Next? ##

The hardest part of the project (naming it) behind me, I can start
experimenting.

An intermediate goal I'm contemplating is to write a dice rolling program.
This would initially just be a fixed die (d4 at first, and then maybe a d20?)
that would spin randomly and then settle on some number.  Expressing the number
would be my first foray into textures.

When I'm feeling a bit brave I will introde some physics to have the single die
be "thrown" and hit the "ground" and roll.  Then, multiple dice potentially
interacting with each other and other table-top objects.
