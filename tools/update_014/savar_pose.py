"""Find the authored Savar mount and rider positions for the native mesh."""
import re
import bpy
from mathutils.kdtree import KDTree
import numpy as np

LOD_SUFFIX = re.compile(r"_LOD([012])(?:\.\d+)?$")


def objects_for_lod(scene, asset, level):
    prefix = f"PSU_savar_{asset}_"
    groups = {}
    for obj in scene.objects:
        match = LOD_SUFFIX.search(obj.name)
        if obj.type != "MESH" or not match or not obj.name.startswith(prefix):
            continue
        if int(match[1]) == level:
            groups[obj.name[len(prefix):match.start()]] = obj
    return groups


def world_points(obj):
    return np.array([(obj.matrix_world @ v.co)[:] for v in obj.data.vertices])


def native_coords(blender_points):
    return blender_points[:, [0, 2, 1]] * [-1, 1, -1]


def blender_coords(native_points):
    return native_points[:, [0, 2, 1]] * [-1, -1, 1]


def kd_tree(points):
    kd = KDTree(len(points))
    for i, p in enumerate(points):
        kd.insert(p, i)
    kd.balance()
    return kd


def mount_trees(scene, asset, level):
    groups = objects_for_lod(scene, asset, level)
    mount = [native_coords(world_points(obj)) for name, obj in groups.items() if name in ("mount", "tail")]
    rider = native_coords(world_points(groups["rider"]))
    return kd_tree(np.concatenate(mount)), kd_tree(rider)


def match_mount(trees, xyz):
    mount, rider = trees
    near_mount = np.array([mount.find(p)[2] for p in xyz])
    near_rider = np.array([rider.find(p)[2] for p in xyz])
    return (near_mount <= .003) & (near_mount < near_rider + 1e-5)
