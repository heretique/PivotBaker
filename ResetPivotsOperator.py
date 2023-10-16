import bpy
from bmesh import from_edit_mesh, update_edit_mesh


class ResetPivotsOperator(bpy.types.Operator):
    bl_idname = "vertices.reset_pivots"
    bl_label = "Reset Pivots"
    bl_description = "Resets pivots, clearing pivot layers and vertex colors, and setting the 3D cursor to the origin"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if bool(obj) and obj.type == "MESH" and obj.mode == "EDIT":
            return True

    def execute(self, context):
        print("Reset Pivots executed")
        obj = context.active_object
        bm = from_edit_mesh(obj.data)
        pivotBaseName = context.scene.pivot_base_name
        pivotLayerName0 = f"{pivotBaseName}_0"
        pivotLayerName1 = f"{pivotBaseName}_1"
        self.ensureAttributes(context, bm, pivotLayerName0, pivotLayerName1)
        bpy.ops.geometry.color_attribute_render_set(
            name=context.scene.color_channel_name
        )
        colorLayer = bm.loops.layers.color[context.scene.color_channel_name]
        pivotLayer0 = bm.loops.layers.float_vector[pivotLayerName0]
        pivotLayer1 = bm.loops.layers.float_vector[pivotLayerName1]
        for v in bm.verts:
            for l in v.link_loops:
                l[colorLayer] = (0.0, 0.0, 0.0, 1.0)
                l[pivotLayer0] = (0.0, 0.0, 0.0)
                l[pivotLayer1] = (0.0, 0.0, 0.0)

        update_edit_mesh(obj.data)
        bm.free()
        return {"FINISHED"}

    def ensureAttributes(self, context, bm, pivotLayerName0, pivotLayerName1):
        if context.scene.color_channel_name not in bm.loops.layers.color:
            bm.loops.layers.color.new(context.scene.color_channel_name)

        self.ensurePivotLayer(bm, pivotLayerName0)
        self.ensurePivotLayer(bm, pivotLayerName1)

    def ensurePivotLayer(self, bm, pivotLayerName):
        if pivotLayerName not in bm.loops.layers.float_vector:
            bm.loops.layers.float_vector.new(pivotLayerName)
