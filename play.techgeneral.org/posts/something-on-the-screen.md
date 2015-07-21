title: "Getting something on the screen"
date: 2013-12-14 05:29:38
published: 2013-12-14 05:29:38
subtitle: The simplest thing that works.
description:
    The simplest thing that works.
created: !!timestamp 2013-12-14 05:29:38

## tl;dr ##

The triangle is the canonical "Hello World" for an OpenGL program.  I do my
first shader-based triangle.

## Initializing OpenGL ##

The OpenGL standard doesn't specify a platform-agnostic way to get an OpenGL
window and context created - it only kicks in once that context is created.
[GLFW][glfw] is a bare-bones library that provides a consistent way to create windows
and contexts and to handle input so I don't have to write platform-specific
code (at least for a while), and won't get in my way in learning OpenGL itself.

Also, the OpenGL functions like `glShaderSource` aren't specified in some
official OpenGL library.  Instead, they are implemented in some OpenGL driver,
and running `glShaderSource` on the same machine, with the same binary, may
execute very different commands depending on which device is being rendered to.
What you see as `glShaderSource` is essentially a function pointer to the real
implementation.  It may also just not exist in some cases - such as if you want
to use an OpenGL 4.1 function where your driver only provides OpenGL 3.3.

GLEW (in the C++ world) and Derelect's gl3 module (in the D world) can do this
automatically for you

## What are shaders? ##

Since I'm still new at this, I may be totally wrong, but the way I'm thinking
about shaders (specifically, shaders in OpenGL, written in GLSL) is that
they're programs that create or manipulate information about vertices (the
points at the corner of shapes) and the pixels that these vertices contain.

GLSL shaders are written in a C-like language.  In this triangle-displaying
program, I need two shaders - one to place the vertices, and one to colour the
pixels.

    :::
    #version 330 core
    layout(location = 0) in vec4 pos;

    void main() {
        gl_Position = pos;
    }

This is a pass-through vertex shader.

The first line of this and all shaders is the version - in this case the GLSL
version attached to OpenGL 3.3 (OpenGL 3.2 came with GLSL 1.5).

This shader program (the vertex shader) declares that it will receive a single
argument `pos` which is a `vec4` (a vector made up of 4 floats).  `gl_Position`
is where the vertex will be placed - in this case, exactly where it initially
was described.

    :::
    #version 330 core
    out vec3 color;

    void main() {
        color = vec3(1, 0, 0);
    }

This simplistic fragment shader always returns red (r = 1, g = 0, b = 0), and
doesn't take any arguments, although it is possible to pass arguments from the
vertex shader to the fragment shader.

Shaders are compiled and the linked into programs, which you can then choose
between before sending vertices at your graphics card.

## Buffer and array objects ##

My previous attempts at using OpenGL used "direct mode", where I would execute
individual `glVertex` calls for each vertex in every frame.

A vertex array means using a single command to take action on a number of
specified vertices using something like `glDrawArray`.

Using a vertex buffer means storing the vertex information on the graphics card
instead of sending it over every frame.

## Putting it together ##

[Here](https://github.com/nxsy/abandonedtemple/tree/68ddfb1e68482de8ac8f585b205c2be1906e92db)
is the state of of my code repo at this point.  If you compile libglfw on any
platform, and put it next to the binary compiled from the two source files, it
should display a simple red triangle on a dark blue background at 640x480, like this:

![](https://s3.amazonaws.com/play-static.techgeneral.org/demo1-640x480.png)

[glfw]: http://www.glfw.org/
