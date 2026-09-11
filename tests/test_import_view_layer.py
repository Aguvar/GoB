"""Run with Blender: blender --background --factory-startup --python this_file.py"""

import sys
import unittest
from pathlib import Path

import bpy


ADDON_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ADDON_ROOT.parent))

from gob.gob_import import GoB_OT_import  # noqa: E402


def find_layer_collection(layer_collection, name):
    if layer_collection.name == name:
        return layer_collection
    for child in layer_collection.children:
        match = find_layer_collection(child, name)
        if match is not None:
            return match
    return None


class EnsureObjectInViewLayerTests(unittest.TestCase):
    def tearDown(self):
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for collection in list(bpy.data.collections):
            bpy.data.collections.remove(collection)

    def test_relinks_orphaned_object(self):
        obj = bpy.data.objects.new("Orphan", bpy.data.meshes.new("OrphanMesh"))

        self.assertNotIn(obj.name, bpy.context.view_layer.objects)
        GoB_OT_import._ensure_object_in_view_layer(obj)

        self.assertIn(obj.name, bpy.context.view_layer.objects)
        obj.select_set(True)

    def test_preserves_excluded_collection_membership(self):
        excluded_collection = bpy.data.collections.new("Excluded")
        bpy.context.scene.collection.children.link(excluded_collection)
        obj = bpy.data.objects.new("ExcludedObject", bpy.data.meshes.new("Mesh"))
        excluded_collection.objects.link(obj)
        bpy.context.view_layer.update()

        layer_collection = find_layer_collection(
            bpy.context.view_layer.layer_collection, excluded_collection.name
        )
        self.assertIsNotNone(layer_collection)
        layer_collection.exclude = True
        bpy.context.view_layer.update()
        self.assertNotIn(obj.name, bpy.context.view_layer.objects)

        GoB_OT_import._ensure_object_in_view_layer(obj)

        self.assertIn(obj.name, bpy.context.view_layer.objects)
        self.assertIn(excluded_collection, obj.users_collection)
        obj.select_set(True)


if __name__ == "__main__":
    unittest.main(argv=[__file__])
