title: "Time for some play"
date: 2013-12-11 07:08:55
published: 2013-12-11 07:08:55
subtitle: How I'm amusing myself lately
description:
    How I'm amusing myself lately
created: !!timestamp 2013-12-11 07:08:55

## tl;dr ##

This is where I'm going to write about what I'm playing around with at the
moment.  Initially, it is going to cover me learning D and OpenGL, but who
knows where it'll go from there.

## Why? ##

I let my Internet presence disappear when the web server behind my site died
several years ago.

I've tried to start writing again a few times since then - a more "serious"
technology/industry-focused blog named "TechGeneral" that I initially built
using my TurboGears-based blogging software, gibe.  Since then, I've rebuilt it
on a number of static website generators, but committing to content was
unexpectedly hard.

Anyway, this is my low-pressure alternative to that, where I'll post some
updates of me learning D and OpenGL.  I jokingly told a colleague at work I
hope to build a Minecraft clone in seven-to-ten years.

## Technology? ##

During a rare bit of downtime in my recent vacation in Portland, my "Hello
World" D program ended up being a port of the [GLFW quickstart](http://www.glfw.org/docs/latest/quick.html).  Unfortunately I
didn't keep track of what I wrote then, since it morphed into a different
project, but here's something I wrote around that time, which gets information
about the OpenGL context.

    :::d
    module app;

    import std.stdio, std.conv;
    import derelict.glfw3.glfw3;
    import derelict.opengl3.gl3;

    string programName = "glfw3Test";
    int width = 640;
    int height = 480;

    void main() {
        DerelictGL3.load();
        DerelictGLFW3.load();

        if(!glfwInit()) {
            glfwTerminate();
            throw new Exception("Failed to create glcontext");
        }

        writefln("GLFW:     %s", to!string(glfwGetVersionString()));
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 2);
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
        auto window = glfwCreateWindow(width, height, programName.ptr, null, null);
        if(!window) {
            glfwTerminate();
            throw new Exception("Failed to create window");
        }

        glfwMakeContextCurrent(window);

        DerelictGL3.reload();

        writefln("Vendor:   %s", to!string(glGetString(GL_VENDOR)));
        writefln("Renderer: %s", to!string(glGetString(GL_RENDERER)));
        writefln("Version:  %s", to!string(glGetString(GL_VERSION)));
        writefln("GLSL:     %s", to!string(glGetString(GL_SHADING_LANGUAGE_VERSION)));
    }

This is what it returns on my MacBookPro:

    :::text
    GLFW:     3.0.4 Cocoa NSGL chdir menubar dynamic
    Vendor:   Intel Inc.
    Renderer: Intel HD Graphics 4000 OpenGL Engine
    Version:  4.1 INTEL-8.18.26
    GLSL:     4.10

Almost all of that is GLFW or [Derelict](https://github.com/aldacron/Derelict3/wiki) boilerplate except the last 4 lines
where I inspect the OpenGL context to get some information about the
implementation in use.

Porting the quickstart was pretty painless - I just generally just copy the C
code, and then fix the warnings.  Instead of `printf`, I used `writefln`.
Instead of `(float)x`, I used `cast(float)x`.  I needed to convert D strings to
C `char *` using `stringVar.ptr`.

If I needed to pass a C function as a handler, I needed to put it in `extern
C`, and indicate it to be `nothrow`, and of course not throw, like so:

    :::d
    extern(C) {                                                                                                                           
        void mouse_callback(GLFWwindow* window, double x, double y) nothrow {
            try {
                writeln("x: ", x, ", y: ", y);
            } catch(Exception e) {
            }
            cameraAngleX -= (x - lastCursorX);
            lastCursorX = x;
            cameraAngleY -= (y - lastCursorY);
            lastCursorY = y;
        }
    }
    glfwSetCursorPosCallback(window, &mouse_callback);

The nice thing about all this was that the D compiler just wouldn't let me get
it wrong - I couldn't forget nothrow, and I couldn't not catch the exception of
a function that did throw.

One key piece of the D ecosystem for me has been [dub](https://github.com/rejectedsoftware/dub), the D package and build
manager.  My D source code may be a single file now, but it does require
various D packages (Derelict, in particular) be installed.  It's as simple as:

    :::json
    {
        "name": "glfwquick",
        "description": "Port of glfw quickstart to d.",
        "homepage": "none",
        "copyright": "Copyright © 2013 Neil Blakey-Milner",
        "authors": [ "Neil Blakey-Milner" ],

        "targetPath": "bin",

        "dependencies": {
            "derelict-glfw3": "~master",
            "derelict-gl3": "~master"
        }
    }

I built and installed dub to a user folder, and just run `dub build &&
bin/glfwquick` over and over as I iterate.  As I add/change dependencies, it
goes off and fetches them from [code.dlang.org](http://code.dlang.org).

After a few hours, spread over two weeks since then, I've made a bit of
progress.  Here's one of my example programs:

<div id="fb-root"></div> <script>(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) return; js = d.createElement(s); js.id = id; js.src = "//connect.facebook.net/en_US/all.js#xfbml=1"; fjs.parentNode.insertBefore(js, fjs); }(document, 'script', 'facebook-jssdk'));</script>
<div class="fb-post" data-href="https://www.facebook.com/photo.php?v=10152077039547457" data-width="466"><div class="fb-xfbml-parse-ignore"><a href="https://www.facebook.com/photo.php?v=10152077039547457">Post</a> by <a href="https://www.facebook.com/neilblakeymilner">Neil Blakey-Milner</a>.</div></div>
</script>

## Next ##

Unfortunately I've been learning bad habits using OpenGL's "direct mode", so
I'll need to start over.  Hopefully that means I will be able to build this new
code base in a public repository and post here as I make progress.

