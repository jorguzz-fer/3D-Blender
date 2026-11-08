import bpy, sys, numpy as np, pickle, time
from mathutils.bvhtree import BVHTree
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[-2])
o=[x for x in bpy.data.objects if x.type=='MESH'][0]
bpy.context.view_layer.objects.active=o; o.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
me=o.data; nv=len(me.vertices)
co=np.empty(nv*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
no=np.empty(nv*3,np.float32); me.vertices.foreach_get('normal',no); no=no.reshape(-1,3)
dg=bpy.context.evaluated_depsgraph_get(); bvh=BVHTree.FromObject(o,dg)
t=time.time(); th=np.full(nv,1.0,np.float32); eps=1e-4
for i in range(nv):
    p=Vector(co[i]); d=Vector(-no[i])
    h=bvh.ray_cast(p+d*eps,d,1.0)
    if h[0] is not None: th[i]=h[3]
print("raycast s",time.time()-t)
pickle.dump({'co':co,'no':no,'th':th},open(sys.argv[-1],'wb'))
print("z pct",np.percentile(co[:,2],[0,5,25,50,75,95,100]).round(3))
print("th pct",np.percentile(th,[5,25,50,75,95,99]).round(4))
h,e=np.histogram(co[:,2],bins=40); 
for a,b in zip(h,e): print(round(b,3),a)
