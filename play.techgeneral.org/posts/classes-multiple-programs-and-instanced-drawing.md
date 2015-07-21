title: "Classes, multiple programs, and instanced drawing"
date: 2014-01-02 21:02:33
published: 2014-01-02 21:02:33
subtitle: "Wrapping OpenGL specifics in classes, and the most basic introduction to instanced drawing"
description:
     "Wrapping OpenGL specifics in classes, and the most basic introduction to instanced drawing"
created: !!timestamp 2014-01-02 21:02:33

## tl;dr ##

In my [previous post][previous post] I wrote a set of classes for `shader`s and
`program`s, along with some compile-time function execution to being in
compile-time-checked variables from the shaders.  My next step is to take
OpenGL concepts like Vertex Array Objects, Array Buffers, Element Array
Buffers, and wrap them in simple classes to ease their usage, and then to prove
it out a bit by having two different sets of programs, shaders, buffers, and so
forth to draw different things.

Here's the demo video I posted at the end of previous post that teased about
these two sets of objects I'm describing in this post, in case you missed it:

<div id="fb-root"></div> <script>(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) return; js = d.createElement(s); js.id = id; js.src = "//connect.facebook.net/en_US/all.js#xfbml=1"; fjs.parentNode.insertBefore(js, fjs); }(document, 'script', 'facebook-jssdk'));</script>
<div class="fb-post" data-href="https://www.facebook.com/photo.php?v=560037190746166" data-width="750"><div class="fb-xfbml-parse-ignore"><a href="https://www.facebook.com/photo.php?v=560037190746166">Post</a> by <a href="https://www.facebook.com/play.TechGeneral">play.TechGeneral</a>.</div></div>

[previous post]: https://play.techgeneral.org/mixins-and-other-code-generation.html

## OpenGL wrapper ##


Here are the classes that wrap the OpenGL concepts of arrays, buffers, and so
forth:

    :::d
    module abandonedtemple.demos.demo3_glwrapper;

    import std.range : ElementType;
    import std.stdio : writefln;
    import std.traits : isArray;

    import derelict.opengl3.gl3:
        glGenBuffers,
        glGenVertexArrays,
        glBindBuffer,
        glBindVertexArray,
        glBufferData,
        glDeleteBuffers,
        glDeleteVertexArrays,
        GL_ARRAY_BUFFER,
        GL_ELEMENT_ARRAY_BUFFER
        ;

    class VertexArray {
        private uint _location;
        this() {
            glGenVertexArrays(1, &_location);
        }

        ~this() {
            writefln("Destroying Vertex Array at location %d", _location);
            glDeleteVertexArrays(1, &_location);
        }

        void bind() {
            glBindVertexArray(_location);
        }

        void unbind() {
            glBindVertexArray(0);
        }
    }

    mixin template Buffer() {
        private uint _location;
        this() {
            glGenBuffers(1, &_location);
        }
        ~this() {
            writefln("Destroying buffer of type %s at location %d", _type, _location);
            glDeleteBuffers(1, &_location);
        }

        void bind() {
            glBindBuffer(_type, _location);
        }

        void unbind() {
            glBindBuffer(_type, 0);
        }

        void setData(T)(const auto ref T data, uint usage) if (isArray!T) {
            glBindBuffer(_type, _location);
            auto size = data.length * ElementType!T.sizeof;
            glBufferData(_type,
                size,
                data.ptr,
                usage);
        }
    }

    class ArrayBuffer {
        static uint _type = GL_ARRAY_BUFFER;
        mixin Buffer;
    }

    class ElementArrayBuffer {
        static uint _type = GL_ELEMENT_ARRAY_BUFFER;
        mixin Buffer;
    }

I'm erring on the side of explicitness in my imports - only grabbing what I'm
using from the `derelict.opengl3.gl3` module.  I'm not a particular fan (yet?)
of not knowing where my functions are coming from.

The `VertexArray` class is fairly simple, since basically all you can do with
vertex array objects are create, bind, unbind, and delete them.

`ArrayBuffer` and `ElementArrayBuffer` are basically identical except for the
type.  I used a `mixin template` here instead of inheritance because I didn't
see the value of treating `ArrayBuffer` and `ElementArrayBuffer` objects ever
as something similar.  I don't need to create a generic Buffer argument that
could take either, so there is no reason they should share an interface or base
class.  Might turn out to be the wrong choice, but it should be easy to change.

The `Buffer` `mixin template` is fairly straight-forward except for `setData`.
Here's that function declaration again:

    :::d
    void setData(T)(const auto ref T data, uint usage) if (isArray!T) {

`setData` is a method templated by a single type `T`, which is the base type of
the `data` argument.  `data` is qualified as being `const auto ref`.  `const`
means that the function will not be changing `data`.  `auto ref` means that the
"`ref`ness" of `data` will depend on whether it is "`ref`able".  It will be a
`ref` if it can be (ie, `data` is an `lvalue`), and not `ref` if it can't.

More at [Function Templates with Auto Ref
Parameters](http://dlang.org/template.html#auto-ref-parameters).

The `is (isArray!T)` is the final puzzle - it says that this method only
applies if `T` has the trait `isArray`.  This is a [template
constraint](http://dlang.org/concepts.html).  More traits live in
[std.traits](http://dlang.org/phobos/std_traits.html), and you can create your
own too.

In this case, `setData` being given a D array is able to get the pointer to the
first value, as well as the size in bytes.  The latter uses `ElementType`,
which is a template that returns the type of the element in the array (and in a
`range`, per its location in `std.range`).  From the length (all D arrays know
their length) and the size of the element type, the size in bytes can be
calculated.

## RainbowCube ##

Now I want to encapsulate all that's involved in drawing the rainbow cubes into
a class.

    :::d
    class RainbowCube {
        VertexArray va;
        ArrayBuffer vertices;
        ElementArrayBuffer cube;
        ElementArrayBuffer lines;

        RainbowProgram program;

        this(RainbowProgram p) {
            program = p;

            va = new VertexArray();
            va.bind();

            const float vertices_[] = [
                -1f, -1f, -1f, 1f,   1f,  0f, 0f,
                -1f,  1f, -1f, 1f,   0f,  1f, 0f,
                 1f,  1f, -1f, 1f,   0f,  0f, 1f,
                 1f, -1f, -1f, 1f,   1f,  1f, 0f,

                -1f, -1f,  1f, 1f,   0f,  0f, 1f,
                -1f,  1f,  1f, 1f,   1f,  1f, 0f,
                 1f,  1f,  1f, 1f,   1f,  0f, 0f,
                 1f, -1f,  1f, 1f,   0f,  1f, 0f,
            ];
            vertices = new ArrayBuffer();
            vertices.setData!(const float[])(vertices_, GL_STATIC_DRAW);

            ushort cube_elements[] = [
                // back face
                0, 1, 2,
                0, 2, 3,
                // front face
                4, 5, 6,
                4, 6, 7,
                // left face
                0, 4, 5,
                0, 1, 5,
                // right face
                2, 6, 7,
                2, 3, 7,
                // bottom face
                0, 3, 4,
                3, 4, 7,
                // top face
                1, 2, 5,
                2, 5, 6,
            ];
            cube = new ElementArrayBuffer();
            cube.setData!(ushort[])(cube_elements, GL_STATIC_DRAW);

            ushort line_elements[] = [
                // back face
                0, 1,
                1, 2,
                2, 3,
                3, 0,

                // front face
                4, 5,
                5, 6,
                6, 7,
                7, 4,

                // remainder of left face
                // 0, 1, // already in back face
                // 4, 5, // already in front face
                0, 4,
                1, 5,

                // remainder of right face
                // 2, 3, // already in back face
                // 6, 7, // already in front face
                2, 6,
                3, 7,

                // top and bottom faces already have all lines
            ];
            lines = new ElementArrayBuffer();
            lines.setData!(ushort[])(line_elements, GL_STATIC_DRAW);

            lines.unbind();
            va.unbind();
        }

        void draw() {
            program.uniforms.is_line = 0;
            vertices.bind();
            cube.bind();
            // Layout of the stuff to draw
            glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 7 * float.sizeof, cast(void*)(0 * float.sizeof));
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 7 * float.sizeof, cast(void*)(4 * float.sizeof));

            // Draw it!
            glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_SHORT, cast(void *)0);

            program.uniforms.is_line = 1;
            lines.bind();

            glDrawElements(GL_LINES, 24, GL_UNSIGNED_SHORT, cast(void *)0);
        }

        void bind() {
            va.bind();
            program.use();
            glEnableVertexAttribArray(0);
            glEnableVertexAttribArray(1);
        }

        void unbind() {
            glDisableVertexAttribArray(1);
            glDisableVertexAttribArray(0);
            va.unbind();
        }
    }

The top-level functions are initialisation (done in the constructor), drawing,
and the inevitable binding and unbinding.  The latter can't (yet) be put into
`draw`, since some activities that might be involved in drawing aren't (yet)
encapsulated in the class - for example, setting up the rotation `uniform`s.

There's still a lot of code in initialisation - although mostly in setting up
the vertices and the arrays.  The downside of `class`es also shows here - we
need to construct them (not needed with a `struct`).  And the `bind` and
`unbind` calls are still a little annoying.

This should be greatly simplified when I store the vertex information in
external files instead of code (and remember, I still have the option to put
them in the binary by using compile-time function execution, if it makes
sense).  I will probably look at converting to `struct` for the wrappers, and
make a bind/unbind wrapper template class I can use when I want to use them.

`draw`, `bind`, and `unbind` are a wash in terms of number of lines of code,
but not having to call the different underlying OpenGL functions saves some
headache.

## Demo class ##

Here's a simplified version of what `Demo` looks like now:

    :::d
    class Demo : DemoBase {
        private {
            RainbowCube rainbowCube;
            RainbowProgram rainbowProgram;

            mat4 frustumMatrix;

            void bufferInit() {
                rainbowCube = new RainbowCube(rainbowProgram);
            }

            void drawRainbowCubes() {
                rainbowCube.bind();

                rainbowProgram.uniforms.u_frustum.setTranspose(true);
                rainbowProgram.uniforms.u_frustum = frustumMatrix;

                auto cube_translations = [
                    [ -1.2f, -1.0f, -1.2f, 2f, -4.5f ], // left, bottom, back
                    [ -1.2f,    0f,  1.2f, -2f, -3.5f ], // left, middle, front
                    [ -1.2f,  1.2f,    0f, 1f, 2.5f ], // left, top, middle
                    [    0f, -1.0f,  1.2f, -1f, 2.5f ], // middle, bottom, front
                    [    0f,    0f,    0f, 9f, 5.5f ], // middle, middle, middle
                    [    0f,  1.2f, -1.2f, -3f, 6.5f ], // middle, top, back
                    [  1.2f, -1.0f,    0f, 1f, -2.5f ], // right, bottom, middle
                    [  1.2f,    0f, -1.2f, -2f, -4.5f ], // right, middle, back
                    [  1.2f,  1.2f,  1.2f, 2f, 7.5f ], // right, top, front
                ];

                foreach (float[] translation; cube_translations) {
                    auto matrix = mat4.identity
                        .rotatez(timeDiff * translation[3])
                        .rotatex(timeDiff * translation[4])
                        .scale(0.3, 0.3, 0.3)
                        ;
                    rainbowProgram.uniforms.u_transform = matrix;
                    rainbowProgram.uniforms.u_offset = vec4((translation[0] + 0.1) * (1 + sin(timeDiff * (4 / translation[3])) / 2), translation[1] * (1 + sin(timeDiff / 2) / 4), -3.5 + translation[2], 0f);

                    // What to draw
                    rainbowCube.draw();
                }

                // Disable all the things
                rainbowCube.unbind();
                glUseProgram(0);
            }

            void display() {
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);

                drawRainbowCubes();
            }

            void init() {
                rainbowProgram = new RainbowProgram();
                glClearColor(0.0f, 0.0f, 0.3f, 0.0f);

                bufferInit();
            }
        }
    }

It's a lot shorter now, and how to add new `program`s and things to draw with
them is fairly straight-forward.  And there is relatively little use of
underlying OpenGL functions at this layer.

The `rainbowProgram.uniforms` having compile-time type checking has been pretty
useful while playing around, so I'm currently fairly happy with it despite the
gnarliness of the code.

## Something new ##

The above changes just changed the code, but the demo does basically the same
thing it did before.

I wanted to put a floor in, and here's what I did:

    :::d
    class ChessCube {
        VertexArray va;
        ArrayBuffer vertices;
        ElementArrayBuffer cube;
        ElementArrayBuffer lines;

        ChessProgram program;

        this(ChessProgram p) {
            program = p;

            va = new VertexArray();
            va.bind();

            const float vertices_[] = [
                -1f, -1f, -1f, 1f,   0f,  0f, 0f,
                -1f,  1f, -1f, 1f,   1f,  1f, 1f,
                 1f,  1f, -1f, 1f,   1f,  1f, 1f,
                 1f, -1f, -1f, 1f,   0f,  0f, 0f,

                -1f, -1f,  1f, 1f,   0f,  0f, 0f,
                -1f,  1f,  1f, 1f,   1f,  1f, 1f,
                 1f,  1f,  1f, 1f,   1f,  1f, 1f,
                 1f, -1f,  1f, 1f,   0f,  0f, 0f,
            ];
            vertices = new ArrayBuffer();
            vertices.setData!(const float[])(vertices_, GL_STATIC_DRAW);

            ushort cube_elements[] = [
                // back face
                0, 1, 2,
                0, 2, 3,
                // front face
                4, 5, 6,
                4, 6, 7,
                // left face
                0, 4, 5,
                0, 1, 5,
                // right face
                2, 6, 7,
                2, 3, 7,
                // bottom face
                0, 3, 4,
                3, 4, 7,
                // top face
                1, 2, 5,
                2, 5, 6,
            ];
            cube = new ElementArrayBuffer();
            cube.setData!(ushort[])(cube_elements, GL_STATIC_DRAW);

            cube.unbind();
            va.unbind();
        }

        void draw() {
            vertices.bind();
            cube.bind();
            // Layout of the stuff to draw
            glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 7 * float.sizeof, cast(void*)(0 * float.sizeof));
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 7 * float.sizeof, cast(void*)(4 * float.sizeof));

            // Draw it!
            glDrawElementsInstanced(GL_TRIANGLES, 36, GL_UNSIGNED_SHORT, cast(void *)0, 8192);
        }

        void bind() {
            va.bind();
            program.use();
            glEnableVertexAttribArray(0);
            glEnableVertexAttribArray(1);
        }

        void unbind() {
            glDisableVertexAttribArray(1);
            glDisableVertexAttribArray(0);
            va.unbind();
        }
    }

The first thing that strikes me is that it is almost identical to the
`RainbowCube`, which makes me want to run off and find some way to share code.
But ignoring that for a second...

`glDrawElementsInstanced` is new!  Here is the old and new lines next to each other:

    :::d
    glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_SHORT, cast(void *)0);
    glDrawElementsInstanced(GL_TRIANGLES, 36, GL_UNSIGNED_SHORT, cast(void *)0, 8192);

The only difference is the `8192` at the end.  That says to do `8192` instances
of the draw command.  That sounds a bit silly at first, since what is the point
of drawing `8192` cubes at the same location?

The vertex shader tells the story:

    :::glsl
    #version 330 core
    layout(location = 0) in vec4 pos;
    layout(location = 1) in vec3 color;

    uniform mat4 u_transform;
    uniform vec4 u_offset;
    uniform mat4 u_frustum;
    uniform int width;

    out vec3 Color;

    void main(){
        float x;
        x = floor(gl_InstanceID / width);
        float y = mod(gl_InstanceID, width);
        if (mod(gl_InstanceID + x, 2) > 0.1) {
            Color = vec3(0.9, 0.9, 0.9);
        } else {
            Color = vec3(0.7, 0.7, 0.7);
        }
        vec4 offset = u_offset + vec4(y * 0.8, 0, -x * 0.8, 0);
        gl_Position = (pos * u_transform + offset) * u_frustum;
    }

This could surely be written better, but I am still figuring out life with only
floats!  `gl_InstanceID` contains the instance number (from `0` to `8191` in
this case) of the draw command.  I use that to calculate x and y offsets to the
original offset given to me (based on the new `width` uniform).  This ends up
creating a chess/checker board effect.

The fragment shader is the same as the one used for the rainbow cubes, and
`RainbowProgram` is defined with:

    :::d
    mixin(program_from_shader_filenames("ChessProgram",
        ["demo3/FragmentShader.frag","demo3/ChessBoard.vert"]));

Mechanically putting code lines wherever rainbow cubes are being set up to set
up the chess program, we're left with `drawChessCubes`:

    :::d
    void drawChessCubes() {
        chessCube.bind();

        chessProgram.uniforms.u_frustum.setTranspose(true);
        chessProgram.uniforms.u_frustum = frustumMatrix;

        auto matrix = mat4.identity.scale(0.4, 0.4, 0.4);
        chessProgram.uniforms.u_transform = matrix;
        chessProgram.uniforms.u_offset = vec4(-48, -2, -2, 0);
        chessProgram.uniforms.width = 128;

        // What to draw
        chessCube.draw();

        // Disable all the things
        chessCube.unbind();
        glUseProgram(0);
    }

With a width of 128 and with 8192 instances, we'll end up with a 128x64 board
of cubes.

## Putting it together ##

![Rainbow Cubes and Chess Board](https://play-static.techgeneral.org/2014/01/20140102-holy-moire-pattern-batman-750.jpg)

[Here][commit1] is the commit that creates the classes that wrap the
glBindBuffer and glBufferData calls and implements ChessCube.  In the [next
commit][commit2] I set the rainbow cubes spinning as shown in the example video
and picture.

## Next up ##

Textures!  I make a textured six-sided die, including the texture itself.

[commit1]: https://github.com/nxsy/abandonedtemple/tree/e7dd51c84a5d0ed20a67cabf793c4906655659ba
[commit2]: https://github.com/nxsy/abandonedtemple/tree/e351c0d10c66ad0804e5434d26dd21bf7cd9ee32
