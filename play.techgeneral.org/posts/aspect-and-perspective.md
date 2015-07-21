title: "Aspect and perspective"
date: 2013-12-24 16:41:25
published: 2013-12-24 16:41:25
subtitle: ""
description:
     ""
created: !!timestamp 2013-12-24 16:41:25

## tl;dr ##

My current understanding of the OpenGL viewport displays whatever is in device
coordinates [-1,1] in x and y dimensions, with the z axis being whatever was
drawn last without depth checking or whatever the front-most object at that
location with depth checking.

Perspective is the process of taking in-world coordinates and translating them
to these device coordinates based on some description of a camera.  Part of
this is ensuring the aspect ratio of the viewport is not distorting the
dimensions of the objects being displayed.

## Before perspective ##

![Before perspective](http://play-static.techgeneral.org/2013/12/20131214-before-perspective.jpg)

The image above shows nine cubes, which are defined as being sized from -1 to 1
in each dimension (x, y, z).  One immediately obvious problem here is that they
don't look like the fronts of cubes, since they should then be a square.

Each cube is moved left, right, and forward by -1 to 1.  Some cubes are thus
closer to the camera, and others further away.  The next obvious problem is
that they all appear the same size.

Finally, since the cubes are not directly in front of the camera, we should be
able to see the right sides of the left-most cubes and vice versa, as well as
the top sides of the bottom-most cubes and vice versa.

## After perspective ##

![After perspective](http://play-static.techgeneral.org/2013/12/20131214-after-perspective.jpg)

This is something closer to what it should look like.  The closer cubes are
larger, and the further away ones are smaller.  The further to the edges the
cube is, the more of one or two sides (closest to the centre) are visible.

## Projection and view frustum ##

The translation of a 3D scene onto a 2D image is a projection.  If you ever did
woodwork (or "shop") class at school and built projections of your work as a
"technical drawing", you were making a set of projections conforming to a
specific set of rules.  Those same rules won't work in this case, so I
implemented the most common one I've read about - the frustum projection.

Basically, the [frustum][frustum] describes a projection that satisfies the
aspect, size, and sides problems above.  It is a matrix that requires only four
pieces of information to build - the scale, the aspect, the near distance, and
the far distance.  I haven't played much with any of these values (besides
aspect, which is fixed for any given window size), so I chose some values I saw
in other people's code and placed my objects at that distance from the camera.

[frustum]: http://www.euclideanspace.com/maths/geometry/elements/projections/frustum/index.htm

## Putting it together ##

[Here][commit1] is the state of the code repo after adding the demo, but before
adding perspective.

[Here][commit2] is the state of the code repo after adding the perspective.

[commit1]: https://github.com/nxsy/abandonedtemple/tree/d80f70ccfb8e38d4ff731406162a3a8aa2579aee
[commit2]: https://github.com/nxsy/abandonedtemple/tree/250aac12a9f79003bcfcaf9ea59c3b221b1d081b
