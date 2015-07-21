title: "Introduction to textures"
date: 2014-01-07 02:45:01
published: 2014-01-07 02:45:01
subtitle: "Using images for more interesting spinning objects"
description:
     "Using images for more interesting spinning objects"
created: !!timestamp 2014-01-07 02:45:01

## tl;dr ##

Solid colour and rainbow-coloured spinning objects are cool for a while, but
easier control of what each object looks like (the colour information, not the
shape) is probably needed.  So, I've implemented texture support in the latest
demo, made a texture, and made my spinning cubes slightly more interesting.

## Texture2D ##

I'm using a 2D texture (there are also 1D and 3D textures, but I don't really
understand those yet), so first step is to make the wrapper class around the
bind/unbind/setData as I did for the `ArrayBuffer` and `ElementArrayBuffer` classes.

    :::d
    class Texture2D {
        private uint _location;
        this() {
            glGenTextures(1, &_location);
        }
        ~this() {
            writefln("Destroying texture at location %d", _location);
            glDeleteTextures(1, &_location);
        }
        void bind() {
            glBindTexture(GL_TEXTURE_2D, _location);
        }
        void unbind() {
            glBindTexture(GL_TEXTURE_2D, 0);
        }
        void setData(char* data, int width, int height) {
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        }
    }

The create/delete/bind/unbind is fairly standard, but it took a bunch of
experimenting (and undoubtably would have led to hair-pulling if I had any at
the time) to get the `glTexImage2D` and `glTexParameteri` calls just right for
what I needed.

[`glTexImage2D`](http://www.opengl.org/sdk/docs/man/xhtml/glTexImage2D.xml)
registers the texture with the related data.  The first argument is the target
texture (`GL_TEXTURE_2D` in this case).  The second is the level-of-detail -
for now, just the base level-of-detail.  The format is next - `RGBA8` means 8
bits dedicated to each channel of red, green, blue, and alpha.  The width and
height of the picture data is next, and then the border value (which apparently
has to be `0` anyway).

The `format` is `GL_RGBA` - didn't we just say that earlier?  `GL_RGBA8` seems
to specify how the bytes in the texture are layed out, while `GL_RGBA`
specifies that the texture has four channels, and that it will be stored as a
float of range [0, 1].

Finally the `data` - this is just `char *` raw byte data.

## stb_image ##

Libraries to load images exist with D bindings - such as
[FreeImage](http://freeimage.sourceforge.net/) and
[DevIL](http://openil.sourceforge.net/), but neither came with Mac OS builds,
and I wasn't looking forward to potentially spending the afternoon building
them.

Instead, I spent the afternoon building my own bindings to a simple single-file
"library" for loading a bunch of image types named
[stb_image.c](http://nothings.org/stb_image.c).  Building a dynamic library
from it was two simple commands, and I then created a simple
[Derelict](https://github.com/aldacron/Derelict3/wiki) wrapper
for it:

    :::d
    module derelict.stb_image.stb_image;

    private {
        import derelict.util.loader;
        import derelict.util.system;

        static if( Derelict_OS_Mac ) {
            enum libNames = "stb_image.0.dylib";
        } else {
            static assert( 0, "Need to implement stb_image libNames for this operating system." );
        }
    }

    extern( C ) nothrow {
        alias da_stbi_load = char* function(const(char)*, int*, int*, int*, int);
        alias da_stbi_image_free = void function(void*);
    }

    __gshared {
        da_stbi_load stbi_load;
        da_stbi_image_free stbi_image_free;
    }

    class DerelictStb_imageLoader : SharedLibLoader {
        public this() {
            super( libNames );
        }

        protected override void loadSymbols() {
            bindFunc( cast( void** )&stbi_load, "stbi_load" );
            bindFunc( cast( void** )&stbi_image_free, "stbi_image_free" );
        }
    }

    __gshared DerelictStb_imageLoader DerelictStb_image;

    shared static this() {
        DerelictStb_image = new DerelictStb_imageLoader();
    }

Not too much to say here - Derelict's `SharedLibLoader` finds the
`stb_image.0.dylib` library in the same directory as the binary, `dlopen`s
them, and binds the symbols by name to the pre-prepared variables.

## The texture ##

I fired up [Pixelmator](http://www.pixelmator.com/) and created a 1800x1200
image and cleared the background. For six sides of the die, I now have a 2-by-3
grid of 600x600px images.

Having almost no design or image editing skills, I came up with:

![Dice texture](https://play-static.techgeneral.org/2014/01/20140104-dice-texture-750.png)

As a hint, I ended up setting guide rules at the center of each image to make
moving the die faces to exactly the right place.  I then made the die images in
a separate 600x600 window and moved them to this one.

![Making the texture](https://play-static.techgeneral.org/2014/01/20140104-making_the_texture-750.jpg)

## DiceFace class ##

Unfortunately this is still a fairly large amount of code, again dominated by
storing the vertex information in code.  I did make some effort to simplify
making the element arrays using for loops, since they are in a easy-to-program
order now.

    :::d
    class DiceFace {
        VertexArray va;
        ArrayBuffer vertices;
        ElementArrayBuffer cube;
        ElementArrayBuffer lines;
        Texture2D texture;

        DiceFaceProgram program;
        import std.path : buildPath, dirName;

        this(DiceFaceProgram p) {
            program = p;

            va = new VertexArray();
            va.bind();

            texture = new Texture2D();
            glActiveTexture(GL_TEXTURE0);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
            texture.bind();

            int width, height, comp;
            string filepath = "dice_texture.png";
            char* image_data = stbi_load(filepath.ptr, &width, &height, &comp, 4);
            writefln("Width: %d, Height: %d, Comp: %d", width, height, comp);
            texture.setData(image_data, width, height);

            const float vertices_[] = [
                // back face - 1
                -1f, -1f, -1f, 1f,   1, 0.5, 0.5,  (0/3f),  (0/2f),
                -1f,  1f, -1f, 1f,   1, 0.5, 0.5,  (0/3f),  (1/2f),
                 1f,  1f, -1f, 1f,   1, 0.5, 0.5,  (1/3f),  (1/2f),
                 1f, -1f, -1f, 1f,   1, 0.5, 0.5,  (1/3f),  (0/2f),

                // front face - 6
                -1f, -1f,  1f, 1f,   1, 0.5, 0.5,  (2/3f),  (1/2f),
                -1f,  1f,  1f, 1f,   1, 0.5, 0.5,  (2/3f),  (2/2f),
                 1f,  1f,  1f, 1f,   1, 0.5, 0.5,  (3/3f),  (2/2f),
                 1f, -1f,  1f, 1f,   1, 0.5, 0.5,  (3/3f),  (1/2f),

                // top face - 3
                -1f,  1f, -1f, 1f,   1, 0.5, 0.5,  (1/3f),  (0/2f),
                -1f,  1f,  1f, 1f,   1, 0.5, 0.5,  (1/3f),  (1/2f),
                 1f,  1f,  1f, 1f,   1, 0.5, 0.5,  (2/3f),  (1/2f),
                 1f,  1f, -1f, 1f,   1, 0.5, 0.5,  (2/3f),  (0/2f),

                // bottom face - 4
                -1f, -1f, -1f, 1f,   1, 0.5, 0.5,  (1/3f),  (1/2f),
                -1f, -1f,  1f, 1f,   1, 0.5, 0.5,  (1/3f),  (2/2f),
                 1f, -1f,  1f, 1f,   1, 0.5, 0.5,  (2/3f),  (2/2f),
                 1f, -1f, -1f, 1f,   1, 0.5, 0.5,  (2/3f),  (1/2f),

                // left face - 2
                -1f, -1f, -1f, 1f,   1, 0.5, 0.5,  (0/3f),  (1/2f),
                -1f, -1f,  1f, 1f,   1, 0.5, 0.5,  (0/3f),  (2/2f),
                -1f,  1f,  1f, 1f,   1, 0.5, 0.5,  (1/3f),  (2/2f),
                -1f,  1f, -1f, 1f,   1, 0.5, 0.5,  (1/3f),  (1/2f),

                // right face - 5
                 1f, -1f, -1f, 1f,   1, 0.5, 0.5,  (2/3f),  (0/2f),
                 1f, -1f,  1f, 1f,   1, 0.5, 0.5,  (2/3f),  (1/2f),
                 1f,  1f,  1f, 1f,   1, 0.5, 0.5,  (3/3f),  (1/2f),
                 1f,  1f, -1f, 1f,   1, 0.5, 0.5,  (3/3f),  (0/2f),

            ];
            vertices = new ArrayBuffer();
            vertices.setData!(const float[])(vertices_, GL_STATIC_DRAW);

            ushort cube_elements[];
            foreach (int x; [0,1,2,3,4,5]) {
                foreach (int y; [0, 1, 2, 0, 2, 3]) {
                    cube_elements ~= cast(ushort)((x*4) + y);
                }
            }
            cube = new ElementArrayBuffer();
            cube.setData!(ushort[])(cube_elements, GL_STATIC_DRAW);

            ushort line_elements[];
            foreach (int x; [0,1,2,3,4,5]) {
                foreach (int y; [0, 1, 1, 2, 2, 3, 3, 0]) {
                    line_elements ~= cast(ushort)((x*4) + y);
                }
            }
            lines = new ElementArrayBuffer();
            lines.setData!(ushort[])(line_elements, GL_STATIC_DRAW);

            lines.unbind();
            va.unbind();
        }

        void draw() {
            program.uniforms.is_line = 0;
            program.uniforms.tex = 0;
            vertices.bind();
            cube.bind();
            texture.bind();
            // Layout of the stuff to draw
            glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 9 * float.sizeof, cast(void*)(0 * float.sizeof));
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * float.sizeof, cast(void*)(4 * float.sizeof));
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 9 * float.sizeof, cast(void*)(7 * float.sizeof));

            // Draw it!
            glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_SHORT, cast(void *)0);

            program.uniforms.is_line = 1;
            lines.bind();

            glDrawElements(GL_LINES, 48, GL_UNSIGNED_SHORT, cast(void *)0);
        }

        void bind() {
            va.bind();
            program.use();
            glEnableVertexAttribArray(0);
            glEnableVertexAttribArray(1);
            glEnableVertexAttribArray(2);
        }

        void unbind() {
            glDisableVertexAttribArray(2);
            glDisableVertexAttribArray(1);
            glDisableVertexAttribArray(0);
            va.unbind();
        }
    }

## Texture loading ##

The actual texture loading part is only these few lines:

    :::d
    texture = new Texture2D();
    glActiveTexture(GL_TEXTURE0);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    texture.bind();
    int width, height, comp;
    string filepath = "dice_texture.png";
    char* image_data = stbi_load(filepath.ptr, &width, &height, &comp, 4);
    texture.setData(image_data, width, height);

`glActiveTexture` is which texture "slot" to write this into.  For now, just
the base one.

The `glBlendFunc` call is used so that the alpha transparency in the die face
is blended with the color.

`stbi_load` is the call into `stb_image.c`, giving the path of the file and the
`4` components (ie, RGBA), and storing the width, height, and the number of
components in the file itself.

Finally, set the data into the texture object!

## Texture mapping ##

With the texture now loaded, I need to define the faces onto which to apply the
texture.  I need to create unique vertices for each corner as part of each
face, since they need different instructions on how the texture will apply to
the face.  Before I just reused the vertices for each of the three faces it was
part of.

Here are the vertices for one of the faces:

    :::d
    // back face - 1
    -1f, -1f, -1f, 1f,   1, 0.5, 0.5,  (0/3f),  (0/2f),
    -1f,  1f, -1f, 1f,   1, 0.5, 0.5,  (0/3f),  (1/2f),
     1f,  1f, -1f, 1f,   1, 0.5, 0.5,  (1/3f),  (1/2f),
     1f, -1f, -1f, 1f,   1, 0.5, 0.5,  (1/3f),  (0/2f),

The back face is made up of four vertices - in the case bottom left, top left,
top right, and bottom right.  In addition to the previous values of vertex
positions (x, y, z, w) and color (r, g, b), we now have texture lookup
information (u, v).  The texture for the 1 die face is the first one - located
in the first of two rows, and the first of three columns.

The other way to think of that is the x co-ordinates start at 0 and continue to
1/3 (first of three columns), and the y co-ordinates start at 0 and continue to
1/2 (first of two rows).

## Putting it together ##

![DiceFace](https://s3.amazonaws.com/play-static.techgeneral.org/2014/01/20140104-first-texture-shot-750.jpg)

[Here][commit1] is the commit that introduces all the texture plumbing above.
If you want to actually build and run it, though, grab [the next
commit][commit2] which brings in the image loading code and provides dynamic
libraries (for OS X, at least) into the repo.

## Next up ##

Assets!  Importing models authored in tools such as Blender into the program.

[commit1]: https://github.com/nxsy/abandonedtemple/tree/6a4c909c1dfab9c501bf57ae816c1e98d0e08d0d
[commit2]: https://github.com/nxsy/abandonedtemple/tree/ffd9d10a70dfdd5696eb3e7fa2f575a0d1480b8d
