import bpy
from bmesh import from_edit_mesh, update_edit_mesh


# keeps only 3 digits resolution
def packTwoFloats(a, b):
    # Pack two floats in the range of 0-1 into one float
    aScaled = a * 1000.0
    bScaled = b * 1000.0
    abPacked = (int(aScaled) << 16) | (
        int(bScaled) & 0xFFFF
    )  # Combine a and b into one unsigned 32-bit integer
    finalFloat = float(abPacked)
    return finalFloat


# keeps only 3 digits resolution
def unpackTwoFloats(abPacked):
    abPackedInt = int(abPacked)
    aScaled = (
        abPackedInt >> 16
    ) & 0xFFFF  # Extract the upper 16 bits as an unsigned 16-bit integer
    bScaled = (
        abPackedInt & 0xFFFF
    )  # Extract the lower 16 bits as an unsigned 16-bit integer
    a = float(aScaled) / 1000.0  # Scale a back to a float
    b = float(bScaled) / 1000.0  # Scale b back to a float
    return (a, b)


class Bake3DCursorOperator(bpy.types.Operator):
    bl_idname = "vertices.bake_3d_cursor"
    bl_label = "Bake 3D Cursor"
    bl_description = "Bake 3D Cursor as Pivot Point to Selected Vertices"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if bool(obj) and obj.type == "MESH" and obj.mode == "EDIT":
            return True

    def execute(self, context):
        print("Bake 3D Cursor executed")
        obj = context.active_object
        bm = from_edit_mesh(obj.data)
        vsel = [v.index for v in bm.verts if v.select]

        if vsel:
            print("selected: ", *vsel)

            # get the 3D cursor location
            cursor = context.scene.cursor.location
            print("cursor: ", cursor)
            activeUvLayer = bm.loops.layers.uv.verify()
            if activeUvLayer is not None:
                print("active uv layer:", activeUvLayer.name)
                uv = (
                    packTwoFloats(cursor.x, cursor.y),
                    packTwoFloats(cursor.z, 1.0),
                )
                for i in vsel:
                    v = bm.verts[i]
                    for l in v.link_loops:
                        # print(l[activeUvLayer])
                        l[activeUvLayer].uv = uv
                update_edit_mesh(obj.data)

        bm.free()
        return {"FINISHED"}
