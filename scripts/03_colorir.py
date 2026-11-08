import sys; sys.path.insert(0,__import__('os').path.dirname(__file__))
import bpy, sys, numpy as np, pickle, mathutils
from scipy.sparse import coo_matrix, diags
glb, pk, out = sys.argv[-3], sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
o=[x for x in bpy.data.objects if x.type=='MESH'][0]
bpy.context.view_layer.objects.active=o; o.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
me=o.data; d=pickle.load(open(pk,'rb')); co,no,th=d['co'],d['no'],d['th']; z=co[:,2]; nv=len(co)
# classes

from classify import *; names=NAMES; idx=I
d2=pickle.load(open(sys.argv[-2].replace('thick','feat'),'rb')); lab=classify(co,no,d2['R'],th)
# smooth labels over mesh graph
ev=np.empty(len(me.edges)*2,np.int32); me.edges.foreach_get('vertices',ev); ev=ev.reshape(-1,2)
A=coo_matrix((np.ones(len(ev)*2,np.float32),(np.r_[ev[:,0],ev[:,1]],np.r_[ev[:,1],ev[:,0]])),shape=(nv,nv)).tocsr()
A=A+diags(np.ones(nv,np.float32)); A=diags(1/np.asarray(A.sum(1)).ravel())@A
P=np.zeros((nv,len(names)),np.float32); P[np.arange(nv),lab]=1
for _ in range(int(sys.argv[-4]) if len(sys.argv)>4 and sys.argv[-4].isdigit() else 3): P=A@P
lab=P.argmax(1)
print({n:int((lab==i).sum()) for n,i in idx.items()})
pal=np.array([CLS[n] for n in names],np.float32)
col=np.c_[pal[lab],np.ones(nv,np.float32)]
ca=me.color_attributes.new('Col','FLOAT_COLOR','POINT'); ca.data.foreach_set('color',col.ravel())
me.color_attributes.active_color=ca
m=me.materials[0]; nt=m.node_tree; b=nt.nodes['Principled BSDF']
a=nt.nodes.new('ShaderNodeVertexColor'); a.layer_name='Col'; nt.links.new(a.outputs['Color'],b.inputs['Base Color'])
b.inputs['Roughness'].default_value=0.45
bpy.ops.object.shade_smooth()
np.save(out+'_labels.npy',lab.astype(np.uint8))
sc=bpy.context.scene
bb=[mathutils.Vector(c) for c in o.bound_box]; ctr=sum(bb,mathutils.Vector())/8; r=max((v-ctr).length for v in bb)
cam=bpy.data.objects.new("cam",bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera=cam
cam.location=ctr+mathutils.Vector((0.0,-1.0,0.55)).normalized()*r*2.6; cam.rotation_euler=(ctr-cam.location).to_track_quat('-Z','Y').to_euler()
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(1,1,1,1); bg.inputs[1].default_value=0.8
sun=bpy.data.objects.new("sun",bpy.data.lights.new("sun",'SUN')); sun.data.energy=3; sun.rotation_euler=(0.7,0.3,0.5); sc.collection.objects.link(sun)
sc.view_settings.view_transform='Standard'
sc.render.engine='CYCLES'; sc.cycles.samples=48; sc.cycles.use_denoising=True
sc.render.resolution_x=1200; sc.render.resolution_y=800
sc.render.filepath=out+'.png'; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=out+'.blend')
