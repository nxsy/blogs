title: Blender to baked OBJ, Blender-Render version
date: 2016-03-16 02:33:14
published: 2016-03-16 02:33:14
subtitle: Why does it have to be so hard?
description:
    Why does it have to be so hard?
created: !!timestamp 2016-03-16 02:33:14

Models coming from Blender won't consistently use textures for all aspects of
the exported model - for example they may use colours instead.  Or they may use
multiple materials without any reuse with other models, which may be a waste.

Here's a rough guide to taking a Blender model and exporting it to .obj with
all relevant information, if it's using Blender-Render.  I'll follow up with
Cycles Render a bit later.  Short version: baking to a single material with a
single texture of each type.

## Standard pipeline

### Choose your poison

You either have to:
* create a UV set, create and configure a material on each object, adding a
  texture pointing to a shared image texture
* apply modifiers to each object, join the object into a single object, and
  then create a new material on it

Probably easiest to apply all modifiers on each object one by one (it is a lot
less troublesome), then join all the object, and then save a new .blend file to
start from.

### Create UV set

Select the relevant object (either in the Outliner, or in the 3D view).  This
should change the object in the Properties area.

In the "Object Data" tab in the Properties area, under "UV Maps", create a new
UV Map.  I tend to call it "BAKE".

### Create a new material

With the object still selected, in the "Material" tab, create a new material. I
tend to call it "BAKE".

### Create a texture

With the material you just created still selected, in the "Texture" tab, create
a new texture.  Surprisingly, I tend to call this "BAKE".

Select "Image or Movie" from the dropdown for the type.  Under the "Image"
arrow, either create a new image (Yep, still "BAKE"), or re-use the existing one.

Under "Mapping", ensure "Map" is set to "BAKE", not "UV Map" or whatever map(s)
existed before you started.

Under "Influence", select at least Color.

### Remap UVs

Thankfully, you generally don't need to unwrap again, just move the existing
unwrapped locations around.

Change screen layout to "UV Editing".  Select (all) the relevant object(s), and
enter edit mode.

Change the UV map from whatever it currently is, to "BAKE".

Select all objects/islands.

Remap UVs.  In simple cases, try Ctrl-A ("Average Islands Scale") and Ctrl-P
("Pack Islands").

### Bake

Back in the default layout, select the object's BAKE material in the outliner
(or change to that tab in the properties area).  Ensure the relevant material
is selected in the outliner.

Then change to the "Render" tab.  Right at the bottom, there is "Bake".  Select
"Selected to Active", set "Bake Mode" to textures, and unset "Clear".  Then "Bake".

This should transfer the bits of the existing textures referenced in the
existing UV map to the single new texture in the new UV map.

Save this image to a file.

### Assign the materials

Enter edit mode and select all faces.  In the "Materials" properties tab,
select the "BAKE" material, and press the "Assign" key.

### Export the model

Select all relevant objects.  Under the "File" menu, select "Export".  Choose
"Wavefront (.obj)".  In the following file dialog, ensure "Triangulate faces" is selected.

### Verify materials

There should be a single material in the .mtl file next to the .obj file.

## Special cases

### Lines

Sometimes there are inexplicable line objects in the .obj file.  Delete them.

### NaN

Sometimes vertices are exported with value "nan".

### Multiple faces using the same existing UVs

If you bake an object where there are overlapping UVs, the bake tool will
basically overwrite-bake them with the same values and take a long time.
Either wait, or separate out a single instance of this particular UV map and
just bake that one.
