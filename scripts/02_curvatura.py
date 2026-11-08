import bpy, sys, numpy as np, pickle
from scipy.sparse import coo_matrix, diags
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[-2])
o=[x for x in bpy.data.objects if x.type=='MESH'][0]
bpy.context.view_layer.objects.active=o; o.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
me=o.data; d=pickle.load(open(sys.argv[-3],'rb')); co,no,th=d['co'],d['no'],d['th']; nv=len(co)
ev=np.empty(len(me.edges)*2,np.int32); me.edges.foreach_get('vertices',ev); ev=ev.reshape(-1,2)
dp=np.linalg.norm(co[ev[:,0]]-co[ev[:,1]],axis=1)+1e-9; dn=np.linalg.norm(no[ev[:,0]]-no[ev[:,1]],axis=1)
k=dn/dp
A=coo_matrix((np.ones(len(ev)*2,np.float32),(np.r_[ev[:,0],ev[:,1]],np.r_[ev[:,1],ev[:,0]])),shape=(nv,nv)).tocsr()
deg=np.asarray(A.sum(1)).ravel()
kv=np.bincount(ev[:,0],k,nv)+np.bincount(ev[:,1],k,nv); kv/=np.maximum(deg,1)
An=diags(1/(deg+1))@(A+diags(np.ones(nv)))
for _ in range(4): kv=An@kv
R=1/np.maximum(kv,1e-3)
d['R']=R.astype(np.float32); d['ev']=ev; pickle.dump(d,open(sys.argv[-1],'wb'))
z=co[:,2]
for nm,msk in [('all',z>-9),('top',z>-0.03),('mid',(z<-0.06)&(z>-0.34)),('bot',z<-0.37),('above',z>0.115)]:
    print(nm, np.percentile(R[msk],[5,25,50,75,95]).round(3))
h,e=np.histogram(np.log10(R),bins=30)
for a,b in zip(h,e): print(round(10**b,4),a)
