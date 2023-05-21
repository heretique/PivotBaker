import bpy
from bmesh import from_edit_mesh, update_edit_mesh
import struct


def packTwoFloats(float1, float2):
    # Convert two single-precision floats to half-precision floats
    half1 = struct.unpack("H", struct.pack("e", float1))[0]
    half2 = struct.unpack("H", struct.pack("e", float2))[0]

    # Pack the half-precision floats into a single-precision float
    combined_half = ((half2 & 0xFFFF) << 16) | half1

    # Convert the packed value to a single-precision float
    packed_float = struct.unpack("f", struct.pack("I", combined_half))[0]

    return packed_float


def unpackTwoFloats(packed_float):
    # Convert the single-precision float to a packed binary string
    packed_binary = struct.pack("f", packed_float)

    # Unpack the binary string as an unsigned integer
    combined_half = struct.unpack("I", packed_binary)[0]

    # Extract the individual half-precision floats
    half1 = combined_half & 0xFFFF
    half2 = (combined_half >> 16) & 0xFFFF

    # Convert the half-precision floats to single-precision floats
    float1 = struct.unpack("e", struct.pack("H", half1))[0]
    float2 = struct.unpack("e", struct.pack("H", half2))[0]

    return float1, float2


def pack_floats(float1, float2):
    # Scale the floats to the range of -100 to +100
    scaled1 = (float1 + 100) / 200  # Scale to 0-1 range
    scaled2 = (float2 + 100) / 200  # Scale to 0-1 range

    # Convert the scaled floats to integers within the range of 0 to 65535 (2^16 - 1)
    int1 = int(scaled1 * 65535)
    int2 = int(scaled2 * 65535)

    # Pack the two integers into a single 32-bit integer
    packed_int = (int2 << 16) | int1

    # Convert the packed integer to a float
    packed_float = struct.unpack("f", struct.pack("I", packed_int))[0]

    return packed_float


def unpack_float(packed_float):
    # Convert the packed float to a packed integer
    packed_int = struct.unpack("I", struct.pack("f", packed_float))[0]

    # Extract the two packed integers from the packed integer
    int1 = packed_int & 0xFFFF
    int2 = (packed_int >> 16) & 0xFFFF

    # Convert the packed integers back to scaled floats
    scaled1 = int1 / 65535
    scaled2 = int2 / 65535

    # Rescale the floats to the original range of -100 to +100
    float1 = scaled1 * 200 - 100
    float2 = scaled2 * 200 - 100

    return float1, float2


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
        usePacking = context.scene.use_packing
        if usePacking:
            self.bakePacked(context)
        else:
            self.bakeUnpacked(context)

        return {"FINISHED"}

    def bakePacked(self, context):
        print("Bake 3D Cursor Packed executed")
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
                    pack_floats(cursor.x, cursor.y),
                    pack_floats(cursor.z, 1.0),
                )
                for i in vsel:
                    v = bm.verts[i]
                    for l in v.link_loops:
                        l[activeUvLayer].uv = uv
                        print(
                            "vertex: ",
                            v,
                            "uv: ",
                            l[activeUvLayer].uv,
                            "unpacked: ",
                            (unpack_float(uv[0]), unpack_float(uv[1])),
                        )
                update_edit_mesh(obj.data)
        bm.free()

    def bakeUnpacked(self, context):
        print("Bake 3D Cursor Unpacked executed")
        obj = context.active_object
        bm = from_edit_mesh(obj.data)
        vsel = [v.index for v in bm.verts if v.select]

        if vsel:
            print("selected: ", *vsel)
            # get the 3D cursor location
            cursor = context.scene.cursor.location
            print("cursor: ", cursor)
            pivotBaseName = context.scene.pivot_base_name
            pivotLevel = context.scene.pivot_level
            pivotLevelName0 = f"{pivotBaseName}_{pivotLevel}_0"
            pivotLevelName1 = f"{pivotBaseName}_{pivotLevel}_1"
            if pivotLevelName0 not in bm.loops.layers.uv:
                pivotLevel0 = bm.loops.layers.uv.new(pivotLevelName0)
            if pivotLevelName1 not in bm.loops.layers.uv:
                pivotLevel1 = bm.loops.layers.uv.new(pivotLevelName1)

            self.clearUVLayer(bm, pivotLevel0)
            self.clearUVLayer(bm, pivotLevel1)
            for i in vsel:
                v = bm.verts[i]
                for l in v.link_loops:
                    l[pivotLevel0].uv = (cursor.x, cursor.y)
                    l[pivotLevel1].uv = (cursor.z, 1.0)
            update_edit_mesh(obj.data)

        bm.free()

    def clearUVLayer(self, bm, layer):
        for v in bm.verts:
            for l in v.link_loops:
                l[layer].uv = (0.0, 0.0)
