import bpy
from bmesh import from_edit_mesh, update_edit_mesh


class ClearPivotLayerOperator(bpy.types.Operator):
    bl_idname = "vertices.clear_pivot_layer"
    bl_label = "Clear Pivot Layer"
    bl_description = "Clears the selected pivot layer for the active object"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if bool(obj) and obj.type == "MESH" and obj.mode == "EDIT":
            return True

    def execute(self, context):
        print("Clear Pivot Layer executed")
        obj = context.active_object
        bm = from_edit_mesh(obj.data)
        activePivotLayer = bm.loops.layers.float_vector.active
        if activePivotLayer is not None and activePivotLayer.name.startswith(
            context.scene.pivot_base_name
        ):
            print("active pivot layer:", activePivotLayer.name)
            for v in bm.verts:
                for l in v.link_loops:
                    # print(l[activePivotLayer])
                    l[activePivotLayer] = (0.0, 0.0, 0.0)
            update_edit_mesh(obj.data)

        bm.free()
        return {"FINISHED"}
