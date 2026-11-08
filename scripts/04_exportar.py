import bpy, sys, mathutils, os
blend,outdir=sys.argv[-2],sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=blend)
sc=bpy.context.scene; cam=sc.camera; sc.cycles.samples=64
o=[x for x in bpy.data.objects if x.type=='MESH'][0]
bb=[mathutils.Vector(c) for c in o.bound_box]; ctr=sum(bb,mathutils.Vector())/8; r=max((v-ctr).length for v in bb)
def shot(d,name):
    cam.location=ctr+mathutils.Vector(d).normalized()*r*2.6; cam.rotation_euler=(ctr-cam.location).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=os.path.join(outdir,name); bpy.ops.render.render(write_still=True)
shot((0,-1,0.55),'render_frente.png'); shot((0.9,0.5,0.6),'render_lateral.png')
bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
m=o.modifiers.new('dec','DECIMATE'); m.ratio=0.3; bpy.ops.object.modifier_apply(modifier='dec')
print("faces after", len(o.data.polygons))
bpy.ops.export_scene.gltf(filepath=os.path.join(outdir,'membrana_colorida.glb'),use_selection=True,export_format='GLB',export_vertex_color='ACTIVE',export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(outdir,'membrana_colorida.blend'),compress=True)
