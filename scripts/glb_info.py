import bpy, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[-1])
tot=0
for o in bpy.data.objects:
    if o.type=='MESH':
        n=len(o.data.polygons); tot+=n
        print(f"MESH {o.name}: verts={len(o.data.vertices)} faces={n} uv={[u.name for u in o.data.uv_layers]} mats={[m.name for m in o.data.materials if m]} dims={tuple(round(d,3) for d in o.dimensions)}")
    else: print(o.type, o.name)
print("TOTAL faces", tot)
for m in bpy.data.materials:
    if not m.use_nodes: continue
    print("MAT", m.name, [ (n.type, n.image.name if getattr(n,'image',None) else '') for n in m.node_tree.nodes])
for i in bpy.data.images: print("IMG", i.name, i.size[:], i.file_format)
print("anims", [a.name for a in bpy.data.actions])
