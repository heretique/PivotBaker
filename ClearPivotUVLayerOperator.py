import bpy
from bmesh import from_edit_mesh, update_edit_mesh


class ClearPivotUVLayerOperator(bpy.types.Operator):
    bl_idname = "vertices.clear_pivot_uv_layer"
    bl_label = "Clear Pivot UV Layer"
    bl_description = "Clears the selected UV layer for the active object"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if bool(obj) and obj.type == "MESH" and obj.mode == "EDIT":
            return True

    def execute(self, context):
        print("Clear Pivot UV Layer executed")
        obj = context.active_object
        bm = from_edit_mesh(obj.data)
        activeUvLayer = bm.loops.layers.uv.verify()
        if activeUvLayer is not None:
            print("active uv layer:", activeUvLayer.name)
            for v in bm.verts:
                for l in v.link_loops:
                    # print(l[activeUvLayer])
                    l[activeUvLayer].uv = (0.0, 0.0)
            update_edit_mesh(obj.data)

        bm.free()
        return {"FINISHED"}
