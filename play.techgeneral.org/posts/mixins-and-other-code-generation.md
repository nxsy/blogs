title: "mixins and other code generation"
date: 2013-12-28 02:03:13
published: 2013-12-28 02:03:13
subtitle: "Compile-time function execution, mixin templates, templated classes and more!"
description:
     "Compile-time function execution, mixin templates, templated classes and more!"
created: !!timestamp 2013-12-28 02:03:13

## tl;dr ##

After writing two demos, I'm starting to get a feel for what could potentially
be reusable, and what might become useful as libraries.  One interesting
feature of D is that your options for building classes aren't just inheritance
and composition using other classes, you can also use the [`mixin`][mixin] compile-time
function and [`mixin templates`][mixintemplates].

[mixin]: http://dlang.org/mixin.html
[mixintemplates]: http://dlang.org/template-mixin.html

Using these, I made it possible to generate classes that encapsulate the OpenGL
`program` idea and also expose in code the uniform variables that the shaders
use, allowing for compile-time checking of types (and potentially
non-initialization later on).

## Shader ##

Here is roughly the class description of a Shader (subsequent to writing the
code in the repo, I realised I could boil it back down to this):

    :::d
    enum ShaderType {
        Vertex = GL_VERTEX_SHADER,
        Fragment = GL_FRAGMENT_SHADER,
    }

    interface ShaderBase {
        @property uint location();
    }

    class Shader {
        private ShaderType _type;
        private string _source;

        private uint _location;
        @property uint location() {
            return _location;
        }

        uint loadShader() {
            int compileStatus;

            uint shader = glCreateShader(_type);
            immutable(char) *sourcePtr = _source.ptr;
            int length = cast(int) _source.length;
            glShaderSource(shader, 1, &sourcePtr, &length);

            glCompileShader(shader);
            glGetShaderiv(shader, GL_COMPILE_STATUS, &compileStatus);
            if (!compileStatus) {
                char compileLog[1024];
                glGetShaderInfoLog(shader, cast(int)compileLog.sizeof, null,
                    compileLog.ptr);
                writefln("Error compiling shader type %d: %s", _type,
                    compileLog);
                throw new Error("Shader compilation failure");
            }
            return shader;
        }

        this(string source, ShaderType type) {
            _source = source;
            _type = type;
            _location = loadShader();
        }

        ~this() {
            if (_location) {
                glDeleteShader(_location);
            }
        }
    }

This class encapsulates the creation, population, and compilation of the OpenGL
`shader`, and won't create an object of its type unless it is given GLSL code
that compiles.

When a Shader object goes out of scope, it cleans up after itself and deletes
the OpenGL `shader` reference.

## Program ##

The OpenGL `program` is linked from a set of compiled `shader`s (only one of
each type, though).  Currently I only have one `program`, but I could see at
least in the short term that I'd like the flexibility of having a few of them
around (even if later I find some way to merge back to fewer).

Here is a specific version of a class that encapulates a `program` as the
Shader class above does for `shader`s - this one is based on the rainbow cubes
from the last post.

    :::d
    const string vertexShaderSource = "...";
    const string fragmentShaderSource = "...";

    class RainbowProgram {
        Shader[] shaders;
        class Uniforms {
            RainbowProgram _program;

            Uniform!mat4 u_transform;
            Uniform!int is_line;
            Uniform!vec4 u_offset;
            Uniform!mat4 u_frustum;

            this(RainbowProgram program) {
                _program = program;

                u_transform = new Uniform!mat4("u_transform", _program);
                is_line = new Uniform!int("is_line", _program);
                u_offset = new Uniform!vec4("u_offset", _program);
                u_frustum = new Uniform!mat4("u_frustum", _program);
            }
        }
        this() {
            shaders ~= new Shader(vertexShaderSource, ShaderType.Vertex);
            shaders ~= new Shader(fragmentShaderSource, ShaderType.Fragment);
            loadProgram();
            uniforms = new Uniforms(this);
        }

        ~this() {
            glDeleteProgram(_location);
        }
    }

Ignore `Uniform` for a bit, but as you can see, a user of an object made from
this `RainbowProgram` class is able to write code like:

    :::d
    mat4 frustumMatrix = foo();
    rainbowProgram.uniforms.u_frustum = frustumMatrix;

We could do this using something like `rainbowProgram.uniforms["u_frustum"]`,
but we would only discover the problem at run-time.  What's more, the uniform
now is of type `mat4`, so we can't pass a `vec4` or `int` or something else in
there.  The compiler will let us know of the problem.

## Uniform ##

My first template class in D.  I liked the idea of using an assignment as the
example above for interacting with normals.  I liked the idea of being able to
use different storage classes (`mat4`, `vec4`, `int`, ...) and having that
enforced at compile-time.  But I didn't want to have to repeat myself much.

Here's what the current iteration of the `Uniform` class looks like:

    :::d
    class Uniform(T) {
        private string _name;
        private ProgramBase _program;
        private uint _location;

        this(string name, ProgramBase p) {
            _name = name;
            _program = p;
            _location = glGetUniformLocation(_program.location, _name.ptr);
            if (_location == -1) {
                throw new Error("Uniform bind failure");
            }
        }

        private bool is_transposed;
        void setTranspose(bool t) {
            is_transposed = t;
        }

        ref Uniform!T opAssign(T)(T value) if (is(T == mat4)) {
            ubyte glbool = GL_FALSE;
            if (is_transposed) {
                glbool = GL_TRUE;
            }
            glUniformMatrix4fv(_location, 1, glbool, value.value_ptr);
            return this;
        }

        ref Uniform!T opAssign(T)(T value) if (is(T == vec4)) {
            glUniform4f(_location, value.x, value.y, value.z, value.w);
            return this;
        }

        ref Uniform!T opAssign(T)(T value) if (is(T == vec3)) {
            glUniform3f(_location, value.x, value.y, value.z);
            return this;
        }

        ref Uniform!T opAssign(T)(T value) if (is(T == int)) {
            glUniform1i(_location, value);
            return this;
        }
    }

The `Uniform(T)` class declaration means that Uniform is templated by one type,
and we'll refer to the type as T.  Our initializer and setTranspose methods
don't depend on the type, so they just omit the templating.

`opAssign` is the method that is called on an object in D when something is
being assigned to that object.  It must return a reference to an object of the
same type.  We refer to the `Uniform` class templated by type `T` as
`Uniform!T` - in the `RainbowProgram` code above, you can see `Uniform!mat4`
and others.  Since it is a reference being returned, it is `ref Uniform!T`;

We currently need four different `opAssign` implementations, because the
underlying OpenGL functions to interact with uniforms are different functions
depending on the type of uniform, and they have different calling parameters.

A `mat4` is assigned in OpenGL with `glUniformMatrix4fv`, which takes a uniform
location, a number of matrices, whether the matrix is transposed (OpenGL is
column-oriented, most programming languages are row-oriented), and finally a
pointer to the memory.

An `int` is a lot simpler - `glUniform1i` takes a uniform location, and the
value to store.

The `if (is(T == mat4))` at the end of the function declaration says that this
is the `opAssign` to use when the class is being templated by type T.  We
describe the function parameter as being `T value`, so it is as if we had
written:

    :::d
    class Uniform!mat4 {
        ref Uniform!mat4 opAssign(mat4 value) {
        }
    }

Similarly, a `vec3` would be:

    :::d
    class Uniform!vec3 {
        ref Uniform!vec3 opAssign(vec3 value) {
        }
    }

Notice there is no confusion - the compiler will simply not find an `opAssign`
that takes a `vec3` on a `Uniform!mat` object, and will complain.

## Mixin ##

The `mixin` function allows you to take a string available at compile-time and
place it where the `mixin` function was called.

In other words, these are equivalent:

    :::d
    void main() {
        int a;
    }

    :::d
    mixin(`
    void main() {
        int a;
    }
    `);

What is powerful is that it can execute code to generate the string.  So this
is also equivalent:

    :::d
    string build_void_main() {
        return `
    void main() {
        int a;
    }
    `);
    }
    mixin(build_void_main());

With a minor amount of work, you can essentially generate a ton of code at
compile-time (no build step to generate the code before passing to the
compiler) based on a set of values you pass in.

One powerful ally of `mixin` is `import`.  `import` allows the reading of a
file into a string at compile-time.

So, imagine you had a file containing:

    :::text
    void main() {
        int a;
    }

And a D file with:

    :::d
    mixin(import("filename"));

That would be equivalent in outcome to the code examples above.

With these, I can generate `RainbowProgram` above with a single line of code:

    :::d
    mixin(program_from_shader_filenames("RainbowProgram",
        ["demo3/FragmentShader.frag","demo3/VertexShader.vert"]));

## Program (with mixin) ##

Ignoring the different function name and calling convention for the moment,
here is the code that currently builds `RainbowProgram` in that single line
above:

    :::d
    struct ShaderData {
        ShaderType type;
        string source;
    }
    string program_from_shaders(string name, ShaderData[] shaders) {
        import std.algorithm : startsWith;
        import std.string : chomp, split, splitLines;
        string[string] uniforms;
        string shaderSetup;
        string shaderLoad;
        string shaderClasses;
        foreach(ShaderData shaderData; shaders) {
            ShaderType st = shaderData.type;
            string shaderclass = name ~ to!string(st);

            auto lines = shaderData.source.splitLines();
            foreach (string l; lines) {
                if (l.startsWith("uniform")) {
                    l = l.chomp(";");
                    auto p = l.split();
                    uniforms[p[2]] = p[1];
                }
            }
            shaderSetup ~= shader(shaderclass, st, shaderData.source);
            shaderLoad ~= "shaders ~= new " ~ shaderclass ~ "();";
            shaderClasses ~= shaderclass;
        }
        return `
            import abandonedtemple.demos.demo3_program : ProgramBase, ShaderBase, Shader, Uniform, _Program;
            class ` ~ name ~ ` : ProgramBase {
                ` ~ shaderSetup ~ `
                ` ~ generateUniformClass(name, uniforms) ~ `
                Uniforms uniforms;
                mixin _Program;

                this() {
                    ` ~ shaderLoad ~ `
                    loadProgram();
                    uniforms = new Uniforms(this);
                }

                ~this() {
                    writefln("Deleting shader at location %d", _location);
                    glDeleteProgram(_location);
                }

            }
            `;
    }

That's quite a bit to swallow.  The foreach code is looking through the
`shaders` passed in and doing a few things.

First it is extracting all the uniforms.  This is pretty horrible code at the
moment - it just looks at the first word on the line, and if it is `uniform`,
then it decides that this is a uniform declaration, and that the next two words
are the type and the name of the uniform.  This will ultimately generate the
`Uniforms` nested class for this `Program`.

It then calls `shader()`, which will generate the code to declare the `Shader`
classes, and populates `shaderLoad` with the code to instantiate the `Shader`
objects.

Then the long string in the return statement:

The first line imports a bunch of things.  The caller of `program_from_shaders`
might not have a bunch of classes and functions imported from modules, so I
have to do it for them.  I make sure to only include those things that I need,
to avoid namespace pollution.  (In retrospect, I think I can do the import
within the `class` statement and it will only bring those into scope for that
class.

`ProgramBase` is an interface the new class implements, and it is named
whatever is passed in as the name.  Through similar string replacement, the
rest of the class code is constructed.

## mixin template ##

`mixin _Program` is an interesting line in there.  The `mixin` keyword is a
perhaps somewhat confusingly named cousin of the `mixin` function.

It doesn't take arguments (it isn't a function), it includes code defined
elsewhere in a `mixin template`.

Here's the definition of `_Program` (what a great name, in hindsight):

    :::d
    mixin template _Program() {
        import std.stdio : writefln;
        import derelict.opengl3.gl3 :
            glUseProgram,
            glCreateProgram,
            glAttachShader,
            glLinkProgram,
            glGetProgramiv,
            GL_LINK_STATUS,
            glGetProgramInfoLog;

        int _location;
        ShaderBase[] shaders;

        @property int location() {
            return _location;
        }

        void use() {
            glUseProgram(_location);
        }

        void loadProgram() {
            _location = glCreateProgram();
            foreach (ShaderBase shader; shaders) {
                glAttachShader(_location, shader.location);
            }
            glLinkProgram(_location);

            int linkStatus;
            glGetProgramiv(_location, GL_LINK_STATUS, &linkStatus);

            if (!linkStatus) {
                char linkerLog[1024];
                glGetProgramInfoLog(_location, cast(int)linkerLog.sizeof, null,
                    linkerLog.ptr);
                writefln("Error linking program: %s", linkerLog);
                throw new Error("Program linker failure");
            }
        }
    }

Like the code returned to be passed to the `mixin` function, we need to be
careful about importing classes and functions into the namespace, since these
will be resolved where the class is being declared, not here.

There's nothing terribly exciting here - it's as if the code in the `mixin
template` had been typed wherever the class is being declared.

So why do it?  Well, it would suck having to type this all in without syntax
highlighting in a big wall of string text.  I could have made this a base
class, but I'm trying to avoid unnecessary inheritance.

## Putting it together ##

Templated classes and functions, the `mixin` function, mixin templates, and
`import` are all ways to generate code at compile time.  This being my first
encounter with them I may have got a few things wrong, but they're starting to
give me an idea of how to build the infrastructure behind this project.

[Here][commit1] is the commit where I introduced much of the code I discussed
above, although I've fixed it up a bit since then.

In lieu of a demo video of this code (since it does exactly what it did
before), here's one from a bit later in my exploration, with multiple programs
in use:

<div id="fb-root"></div> <script>(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) return; js = d.createElement(s); js.id = id; js.src = "//connect.facebook.net/en_US/all.js#xfbml=1"; fjs.parentNode.insertBefore(js, fjs); }(document, 'script', 'facebook-jssdk'));</script>
<div class="fb-post" data-href="https://www.facebook.com/photo.php?v=560037190746166" data-width="750"><div class="fb-xfbml-parse-ignore"><a href="https://www.facebook.com/photo.php?v=560037190746166">Post</a> by <a href="https://www.facebook.com/play.TechGeneral">play.TechGeneral</a>.</div></div>

[commit1]: https://github.com/nxsy/abandonedtemple/tree/dece3ce7656a8ab6645d4d82d8ed29d6d8fecea1
