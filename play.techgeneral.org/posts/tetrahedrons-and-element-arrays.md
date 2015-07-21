title: "Tetrahedrons and element arrays"
date: 2013-12-18 04:44:12
published: 2013-12-18 04:44:12
subtitle: Adding some depth
description:
     Adding some depth
created: !!timestamp 2013-12-18 04:44:12

## tl;dr ##

Building a triangle takes 3 vertices, and only uses each one once.  Building a
tetrahedron (a polyhedron with four triangular faces) takes 4 vertex locations,
but references each one 3 times.  An Element Array helps us define the vertex
locations once, and build a tetrahedron by referring to those vertices by
index.

## Tetrahedrons ##

The next step after a triangle is something with another dimension (depth, you
could say), which is a tetrahedron.

Consider our triangle:

    :::
          C
         / \
        /   \
       A-----B

A tetrahedron would share the ABC vertices, and add a D vertex "behind" the
center of the triangle, like so:

    :::
          C
         /|\
        / D \
       / / \ \
      A-------B

In addition to the ABC triangle, we would need to draw the ABD, ACD, and BCD
triangle faces of the tetrahedron.

Assuming the original triangle vertices:

    :::
    A (bottom-left)  -1, -1, 0, 1
    B (bottom-right)  1, -1, 0, 1
    C (top-middle)    0,  1, 0, 1

And the new vertex:

    :::
    D (middle-back)   0,  0, 1, 1

Our triangle vertex buffer changes from:

    :::d
    const GLfloat triangleVertices[] = [
        -1.0f, -1.0f, 0, 1,
         1.0f, -1.0f, 0, 1,
         0.0f,  1.0f, 0, 1,
    ]

To:

    :::d
    const GLfloat triangleVertices[] = [
        -1.0f, -1.0f, 0, 1, // A
         1.0f, -1.0f, 0, 1, // B
         0.0f,  1.0f, 0, 1, // C

        -1.0f, -1.0f, 0, 1, // A
         1.0f, -1.0f, 0, 1, // B
         0.0f,  0.0f, 1, 1, // D

        -1.0f, -1.0f, 0, 1, // A
         0.0f,  1.0f, 0, 1, // C
         0.0f,  0.0f, 1, 1, // D

         1.0f, -1.0f, 0, 1, // B
         0.0f,  1.0f, 0, 1, // C
         0.0f,  0.0f, 1, 1, // D
    ]

With some other minor changes per [my first commit][commit1], the result is a
somewhat-oddly-shaped tetrahedron.

## Element Arrays ##

Changing D's location now (maybe to fix the odd shape?) would be annoying now -
we have it in three places.  One could use a variable (or even macro if C/C++)
in your code, or have a function generate this list given the four vertex
locations), but another concern is that we're sending and storing a lot more
data on the graphics card.

Since the tetrahedron shape is a little hard to understand now given its
constant colour, I'd like to put lines on the edges to make them more distinct.
I would need to make lines AB, AC, AD, BC, BD, and CD, and thus I would again
need to copy these vertices to the graphics card - for 6 copies of each vertex
at this point.

Element Arrays are a solution to this.  We store each vertex once in the vertex
buffer, and then define the shapes (triangle, line) referencing those vertices
by index.

Our vertex buffer and array element setup now looks like this:

    :::d
    const GLfloat triangleVertices[] = [
        -1f, -1f, 0f, 1f,
         1f, -1f, 0f, 1f,
         0f,  1f, 0f, 1f,
         0f,  0f, 1f, 1f,
    ];
    GLushort tetrahedron_elements[] = [
        0, 1, 2,
        0, 1, 3,
        0, 2, 3,
        1, 2, 3,
    ];

    glGenBuffers(1, &vertexBuffer);
    glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer);
    glBufferData(GL_ARRAY_BUFFER,
        triangleVertices.length * GLfloat.sizeof,
        triangleVertices.ptr,
        GL_STATIC_DRAW);

    glGenBuffers(1, &tetrahedronElements);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, tetrahedronElements);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
        tetrahedron_elements.length * GLushort.sizeof,
        tetrahedron_elements.ptr,
        GL_STATIC_DRAW);

And then to draw the tetrahedron, we have:

    :::d
    // What to draw
    glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, tetrahedronElements);
    // Layout of the stuff to draw
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, null);

    // Draw it!
    glDrawElements(GL_TRIANGLES, 12, GL_UNSIGNED_SHORT, cast(void *)0);

`glDrawElements` replaces `glDrawArrays`, and the `tetrahedronElements` element
array buffer now provides indices into the `vertexBuffer` array buffer.

With some other minor changes per [my second commit][commit2], the result is
the exact same somewhat-oddly-shaped tetrahedron.

## Adding lines ##

Adding lines is fairly easy now.  We set up the element array for the lines:

    :::d
    GLushort line_elements[] = [
        0, 1,
        0, 2,
        1, 2,
        0, 3,
        2, 3,
        1, 3,
    ];

    glGenBuffers(1, &lineElements);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, lineElements);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
        line_elements.length * GLushort.sizeof,
        line_elements.ptr,
        GL_STATIC_DRAW);

Then, in the display loop:

    :::d
    // What to draw
    glUniform1i(isLine, 0);
    glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, tetrahedronElements);
    // Layout of the stuff to draw
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, null);

    // Draw it!
    glDrawElements(GL_TRIANGLES, 12, GL_UNSIGNED_SHORT, cast(void *)0);

    glUniform1i(isLine, 1);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, lineElements);

    glDrawElements(GL_LINES, 12, GL_UNSIGNED_SHORT, cast(void *)0);

Ignoring the `glUniform1i` calls for a second, you can see that first we draw
triangles (`glDrawElements` with `GL_TRIANGLES` with the `tetrahedronElements`
element array buffer bound, and then we bind instead `lineElements` and make
another call to `glDrawElements` except with `GL_LINES.

The `glUniform1i` calls are to change the `is_line` uniform that I have now
enabled in my shaders.  Now, instead of the fragment shader always drawing
pixels in red, it will draw pixels in red when `is_line` is 0, and it will draw
pixels in white when `is_line` is 1.

## The new shaders ##

Here is the new vertex shader:

    :::
    #version 330 core
    layout(location = 0) in vec4 pos;

    uniform mat4 u_transform;
    uniform int is_line;

    out vec3 Color;

    void main(){
        if (is_line == 0) {
            Color = vec3(1, 0, 0);
        } else {
            Color = vec3(1, 1, 1);
        }
        gl_Position = pos * u_transform;
    }

We've added the `is_line` uniform, and now specify an `out` vector called
`Color`.  This will be carried over as input to the fragment shader.

The frament shader now looks like:

    :::
    #version 330 core
    out vec3 color;
    in vec3 Color;

    void main()
    {
        color = Color;
    }

## Putting it together ##

[Here][commit3] is the state of of my code repo at this point.

Here is a short demo of what it looks like at this point:

<div id="fb-root"></div> <script>(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) return; js = d.createElement(s); js.id = id; js.src = "//connect.facebook.net/en_US/all.js#xfbml=1"; fjs.parentNode.insertBefore(js, fjs); }(document, 'script', 'facebook-jssdk'));</script>
<div class="fb-post" data-href="https://www.facebook.com/photo.php?v=555530654530153" data-width="750"><div class="fb-xfbml-parse-ignore"><a href="https://www.facebook.com/photo.php?v=555530654530153">Post</a> by <a href="https://www.facebook.com/play.TechGeneral.org">Play.techgeneral.org</a>.</div></div>


[commit1]: https://github.com/nxsy/abandonedtemple/tree/93baa159531e4cc5e4bc60ea79ae29acc7953c2c
[commit2]: https://github.com/nxsy/abandonedtemple/tree/3cddda64123428c904c3d6a603c146ee7e8ec092
[commit3]: https://github.com/nxsy/abandonedtemple/tree/6b90406d1932f307da46948a588d70a63de0883e
