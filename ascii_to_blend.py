#!/usr/bin/env python

import sys
import time
import bpy

s = time.time()

files = sys.argv[sys.argv.index("--") + 1:]  # get all args after "--"

with open(files[0]) as f:
  lines = f.readlines()

ncols = int(lines[0].split()[1])
nrows = int(lines[1].split()[1])
xllcorner = float(lines[2].split()[1])
yllcorner = float(lines[3].split()[1])
cellsize = float(lines[4].split()[1])
NODATA_value = int(lines[5].split()[1])

print(ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value)

# Clear Blender scene
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete(use_global=False)

for item in bpy.data.meshes:
  bpy.data.meshes.remove(item)
    
verts = []
faces = []
skip = 5
# Create vertices
for row in range(0, nrows, skip):
  values = lines[row + 6].split()
  for col in range(0, ncols, skip):
    x = xllcorner + cellsize * row
    y = yllcorner + cellsize * col
    elev = float(values[col])
    vert = (x, y, elev)
    verts.append(vert)
  if row % 1000 == 0:
    print("{}/{} rows done, {}s elapsed".format(row, nrows, round(time.time() - s)))

nx = len(range(0, nrows, skip))
ny = len(range(0, ncols, skip))

for x, row in enumerate(range(0, nrows, skip)):
  for y, col in enumerate(range(0, ncols, skip)):
    if x < nx - 1 and y < ny - 1:
      v0 = x * ny + y
      v1 = v0 + 1
      v2 = (x + 1) * ny + y + 1
      v3 = v2 - 1
      face = (v0, v1, v2, v3)
      faces.append(face)

print("{} faces done, {}s elapsed".format(len(faces), round(time.time() - s)))

mesh_data = bpy.data.meshes.new("mesh")
mesh_data.from_pydata(verts, [], faces)
mesh_data.update()  # (calc_edges=True) not needed here

obj = bpy.data.objects.new("object", mesh_data)

scene = bpy.context.scene
scene.objects.link(obj)

# animation

obj.shape_key_add()
obj.data.shape_keys.key_blocks[0].name = files[0]

for k, filename in enumerate(files[1:]):
    obj.shape_key_add()
    k += 1
    obj.data.shape_keys.key_blocks[k].name = filename
    with open(filename) as f:
      lines = f.readlines()
    for x, row in enumerate(range(0, nrows, skip)):
      if len(lines) < nrows * .8 and row > nrows / 2:
        #rebound
        row = nrows - row
      values = lines[row + 6].split()
      for y, col in enumerate(range(0, ncols, skip)):
        elev = float(values[col])
        idx = x * ny + y
        obj.data.shape_keys.key_blocks[k].data[idx].co.z = elev
    print("{} loaded, {}s elapsed".format(filename, round(time.time() - s)))

frame = 0
frames = []
for k, filename in enumerate(files):
  frames.append(frame)
  if "C5" in filename:
    frame += 30
  else:
    frame += 90

for k, frame in enumerate(frames):
  if k > 0:
    obj.data.shape_keys.key_blocks[k].value = 0.0
    obj.data.shape_keys.key_blocks[k].keyframe_insert(data_path='value', frame=frames[k - 1])
  obj.data.shape_keys.key_blocks[k].value = 1.0
  obj.data.shape_keys.key_blocks[k].keyframe_insert(data_path='value', frame=frames[k])
  if k < len(frames) - 1:
    obj.data.shape_keys.key_blocks[k].value = 0.0
    obj.data.shape_keys.key_blocks[k].keyframe_insert(data_path='value', frame=frames[k + 1])
