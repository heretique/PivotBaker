import bpy
from bmesh import from_edit_mesh, update_edit_mesh


class ClearVertexColorsOperator(bpy.types.Operator):
    bl_idname = "vertices.clear_vertex_colors"
    bl_label = "Clear Vertex Colors"
    bl_description = "Clears the vertex colors for the active object setting all channels to black (0,0,0,1)"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if bool(obj) and obj.type == "MESH" and obj.mode == "EDIT":
            return True

    def execute(self, context):
        print("Clear Pivot Layer executed")
        obj = context.active_object
        bm = from_edit_mesh(obj.data)
        activeColorLayer = bm.loops.layers.color.active
        if (
            activeColorLayer is not None
            and activeColorLayer.name == context.scene.color_channel_name
        ):
            print("Active color layer:", activeColorLayer.name)
            for v in bm.verts:
                for l in v.link_loops:
                    # print(l[activeColorLayer])
                    l[activeColorLayer] = (0.0, 0.0, 0.0, 1.0)
            update_edit_mesh(obj.data)

        bm.free()
        return {"FINISHED"}
