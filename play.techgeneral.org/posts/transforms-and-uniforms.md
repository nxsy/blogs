title: "Transforms and uniforms"
date: 2013-12-17 04:44:12
published: 2013-12-17 04:44:12
subtitle: Introducing some dynamicism
description:
     Introducing some dynamicism
created: !!timestamp 2013-12-17 04:44:12

## tl;dr ##

A constant triangle is pretty boring.  To "transform", or to make the object
rotate and move, matrix operations are needed.  To introduce values that change
depending on the frame (say, the rotation/movement of an object), you can use a
uniform value.

## Transforms ##

In my previous post, I mentioned that we want to use vertex buffers to store
the vertex information of objects on the graphics card.  That way we don't have
to send it on every frame we want to render.  However, we often want that
object to move around in space - maybe it represents a planet orbiting a sun,
or a bullet heading towards a space ship - how do we avoid updating that data
every frame now?

Instead of sending the new vertex locations indicating the rotation and
movement, we can send a matrix that represents the transformation we want to
apply to the object.  We defined our position as a vector of 4 floats, so if we
multiply it by a matrix of 4x4 floats, we'll have a new vector of 4 floats.
The linear algebra involved in determining the matrix to send over is fairly
involved, and so I happily used [gl3n], an OpenGL maths library for D, to
generate it instead.

[gl3n]: http://dav1dde.github.io/gl3n/

## Uniforms ##

Now we know what matrix to send through - how do we get it to our shader?  Our
vertex shader looked like this:

    :::
    #version 330 core
    layout(location = 0) in vec4 pos;

    void main() {
        gl_Position = pos;
    }

We now need to make it `pos * transform`, and somehow provide `transform`.  A
uniform value is how to do this - you set it in your code, and it is passed
through to the shader whenever an object is to be drawn.

    :::
    #version 330 core
    layout(location = 0) in vec4 pos;

    uniform mat4 u_transform;

    void main() {
        gl_Position = pos * u_transform;
    }

Through the magic of linear algebra, our object will now be rotated and relocated.

Much like the `vec4` type is a vector of 4 floats, the `mat4` type is a matrix
of 4x4 floats.

## Uniforms - the D side ##

Once you've created your shaders and linked them into a program, you can
extract the index of the uniforms referenced in them using
`glGetUniformLocation`.

    :::d
    string transformMatrixName = "u_transform";
    transformMatrix = glGetUniformLocation(program, transformMatrixName.ptr);
    if (transformMatrix == -1) {
        writefln("Could not bind uniform %s", transformMatrixName);
        throw new Error("Uniform bind failure");
    }

Whenever we want to populate that `mat4` value, say every frame, we need to
call `glUniformMatrix4fv` and pass that index and the location of the data to
it.  Each uniform type has a separate function - so if you have a single `int`
value, you need `glUniform1i`.

    :::d
    glUniformMatrix4fv(transformMatrix, 1, GL_FALSE, matrix.value_ptr);

## Transforms - the D side ##

How do we build that `matrix` that we call `value_ptr` on.  gl3n makes it easy:

    :::d
    auto matrix = mat4.identity
        .rotatey(timeDiff)
        .rotatex(timeDiff / PI)
        .scale(0.2, 0.2, 0.2);

In this example `timeDiff` is simply the seconds (a `double`) since the program
started running.  This rotates the object along two dimensions, one pi times slower
than the other.

## Putting it together ##

[Here][tree] is the state of of my code repo at this point.

Here is a short demo of what it looks like at this point:

<div id="fb-root"></div> <script>(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) return; js = d.createElement(s); js.id = id; js.src = "//connect.facebook.net/en_US/all.js#xfbml=1"; fjs.parentNode.insertBefore(js, fjs); }(document, 'script', 'facebook-jssdk'));</script>
<div class="fb-post" data-href="https://www.facebook.com/photo.php?v=555098081240077" data-width="750"><div class="fb-xfbml-parse-ignore"><a href="https://www.facebook.com/photo.php?v=555098081240077">Post</a> by <a href="https://www.facebook.com/play.TechGeneral.org">Play.techgeneral.org</a>.</div></div>
</script>

[glfw]: http://www.glfw.org/
[tree]: https://github.com/nxsy/abandonedtemple/tree/f36463639a5de759ae2e0b5eb5067a6a0a9d0931
