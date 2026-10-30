"""Pure source-face selection for thin rigid wheel LODs; no Blender imports.

Faces are never collapsed, welded, moved or re-UVed. This deliberately permits
open source sheets at distance; full closed native LOD0 remains authoritative.
"""
import numpy as np


def point_triangle_distances(points, triangles):
    """Euclidean closest triangle distance, including edges outside its plane."""
    p=np.asarray(points,float)[:,None,:];t=np.asarray(triangles,float)[None,:,:,:]
    a,b,c=t[:,:,0],t[:,:,1],t[:,:,2];ab=b-a;ac=c-a;ap=p-a
    n=np.cross(ab,ac);nn=np.sum(n*n,axis=2)
    dot=np.sum(ap*n,axis=2);q=p-n*np.divide(dot,nn,out=np.zeros_like(dot),where=nn>1e-25)[:,:,None]
    v=q-a;aa=np.sum(ab*ab,axis=2);bb=np.sum(ab*ac,axis=2);cc=np.sum(ac*ac,axis=2)
    av=np.sum(v*ab,axis=2);cv=np.sum(v*ac,axis=2);den=aa*cc-bb*bb
    u=np.divide(cc*av-bb*cv,den,out=np.zeros_like(av),where=abs(den)>1e-25)
    w=np.divide(aa*cv-bb*av,den,out=np.zeros_like(av),where=abs(den)>1e-25)
    inside=(u>=-1e-10)&(w>=-1e-10)&(u+w<=1+1e-10)&(nn>1e-25)
    distance=np.where(inside,np.divide(dot*dot,nn,out=np.full_like(dot,np.inf),where=nn>1e-25),np.inf)
    for start,end in ((a,b),(b,c),(c,a)):
        edge=end-start;d=p-start;length=np.sum(edge*edge,axis=2)
        factor=np.clip(np.divide(np.sum(d*edge,axis=2),length,out=np.zeros_like(dot),where=length>1e-25),0,1)
        distance=np.minimum(distance,np.sum((d-edge*factor[:,:,None])**2,axis=2))
    return np.sqrt(np.maximum(0,distance))


def planar_patches(vertices, faces):
    """Connected coplanar native faces, preserving their original corners/UVs."""
    v=np.asarray(vertices,float);f=np.asarray(faces,int);t=v[f]
    normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(normals,axis=1)
    normals=np.divide(normals,length[:,None],out=np.zeros_like(normals),where=length[:,None]>1e-15)
    edges={};adj=[set() for _ in faces]
    for i,face in enumerate(f):
        for j in range(3):
            edge=tuple(sorted((tuple(np.round(v[face[j]],7)),tuple(np.round(v[face[(j+1)%3]],7)))))
            for other in edges.get(edge,[]):
                if np.dot(normals[i],normals[other])>1-1e-8 and max(abs((t[i]-t[other,0])@normals[other]))<1e-5:
                    adj[i].add(other);adj[other].add(i)
            edges.setdefault(edge,[]).append(i)
    remaining=set(range(len(faces)));result=[]
    while remaining:
        todo=[min(remaining)];remaining.remove(todo[0]);patch=[]
        while todo:
            i=todo.pop();patch.append(i)
            for j in sorted(adj[i]&remaining):remaining.remove(j);todo.append(j)
        result.append(sorted(patch))
    return result


def select(vertices, faces, locked_points, tolerance):
    """Greedy planar-patch cover with exact retained source-face provenance."""
    v=np.asarray(vertices,float);f=np.asarray(faces,int);t=v[f]
    # More samples than the later BVH check, including all native edge midpoints.
    samples=np.concatenate((v,t.mean(axis=1),(t[:,0]+t[:,1])/2,(t[:,1]+t[:,2])/2,(t[:,2]+t[:,0])/2))
    hard=np.asarray(locked_points,float).reshape((-1,3));points=np.concatenate((hard,samples))
    distances=point_triangle_distances(points,t)
    patches=planar_patches(vertices,faces)
    limits=np.concatenate((np.full(len(hard),1e-6),np.full(len(samples),tolerance)))
    coverage=np.asarray([np.min(distances[:,p],axis=1)<=limits for p in patches])
    uncovered=np.ones(len(points),dtype=bool);chosen=[]
    # First honor bearing/rim/extrema; then choose useful whole fabricator faces.
    for hard_only in (True,False):
        while np.any(uncovered[:len(hard)] if hard_only else uncovered):
            active=uncovered.copy()
            if hard_only:active[len(hard):]=False
            gains=np.sum(coverage&active,axis=1)
            score=gains/np.asarray([len(p) for p in patches])
            score[chosen]=-1
            k=int(np.argmax(score))
            if gains[k]==0:raise RuntimeError('No exact native patch covers required wheel surface')
            chosen.append(k);uncovered&=~coverage[k]
    # Remove entire redundant patches, leaving readable native planar faces.
    for k in sorted(chosen,key=lambda i:(-len(patches[i]),i)):
        other=[i for i in chosen if i!=k]
        if other and np.all(np.any(coverage[other],axis=0)):chosen.remove(k)
    selected=sorted(i for k in chosen for i in patches[k]);d=np.min(distances[:,selected],axis=1)
    return selected,dict(method='Exact native planar face subset; no weld/collapse/interpolation',
        original_triangles=len(faces),selected_triangles=len(selected),source_triangle_indices=selected,
        sampled_reference_surface_max_metres=float(max(d[len(hard):],default=0)),
        protected_point_max_metres=float(max(d[:len(hard)],default=0)),
        source_surface_sample_count=len(samples),planar_patch_count=len(patches),selected_patch_count=len(chosen),
        intentional_open_source_sheets=True,positions_and_per_corner_UVs_exact=True,
        continuous_Hausdorff_bound=False)
