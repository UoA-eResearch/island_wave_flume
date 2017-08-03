#!/usr/bin/env python

import sys
import time
import bpy

s = time.time()

with open('b4_bf_ascii.txt') as f:
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
    x = xllcorner + cellsize * (nrows - row)
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

mesh_data = bpy.data.meshes.new("b4_bf_mesh")
mesh_data.from_pydata(verts, [], faces)
mesh_data.update()  # (calc_edges=True) not needed here

obj = bpy.data.objects.new("b4_bf", mesh_data)

scene = bpy.context.scene
scene.objects.link(obj)

