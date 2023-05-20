import bpy


class PivotBakerPanel(bpy.types.Panel):
    bl_idname = "PIVOTBAKER_PT_PivotBakerPanel"
    bl_label = "Pivot Baker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dojo"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if bool(obj) and obj.type == "MESH" and obj.mode == "EDIT":
            return True

    def draw(self, context):
        col = self.layout.column()
        col.operator("vertices.clear_pivot_uv_layer", text="Clear Pivot UV Layer")
        col.separator()
        col.operator("vertices.bake_3d_cursor", text="Bake 3D Cursor")