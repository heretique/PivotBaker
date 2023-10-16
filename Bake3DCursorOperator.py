import bpy
from bmesh import from_edit_mesh, update_edit_mesh
import struct
import math
from mathutils import Vector


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


MIN = -25.0
RANGE = 50.0
SAMPLES = 65535.0


def pack_floats(float1, float2):
    # Scale the floats to the range of MIN to MIN + RANGE
    scaled1 = (float1 - MIN) / RANGE  # Scale to 0-1 range
    scaled2 = (float2 - MIN) / RANGE  # Scale to 0-1 range

    # Convert the scaled floats to integers within the range of 0 to 65535 (2^16 - 1)
    int1 = math.floor(scaled1 * SAMPLES) & 0xFFFF
    int2 = math.floor(scaled2 * SAMPLES) & 0xFFFF

    # Pack the two integers into a single 32-bit integer
    packed_int = (int2 << 16) | int1

    # Convert the packed integer to a float
    # packed_float = struct.unpack("f", struct.pack("I", packed_int))[0]

    return float(packed_int)


def unpack_floats(packed_float):
    # Convert the packed float to a packed integer
    packed_int = int(packed_float)

    # Extract the two packed integers from the packed integer
    int1 = packed_int & 0xFFFF
    int2 = (packed_int >> 16) & 0xFFFF

    # Convert the packed integers back to scaled floats
    scaled1 = int1 / SAMPLES
    scaled2 = int2 / SAMPLES

    # Rescale the floats to the original range of MIN to MIN + RANGE
    float1 = scaled1 * RANGE + MIN
    float2 = scaled2 * RANGE + MIN

    return math.floor(float1 * 64.0) / 64.0, math.floor(float2 * 64.0) / 64.0


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
        self.bakePivot(context)
        print("Bake 3D Cursor executed")
        return {"FINISHED"}

    def bakePivot(self, context):
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
            pivotLayerName = f"{pivotBaseName}_{pivotLevel}"

            pivotLayer = self.ensurePivotLayer(bm, pivotLayerName)
            colorLayer = self.ensureVertexColors(context, bm)
            bpy.ops.geometry.color_attribute_render_set(
                name=context.scene.color_channel_name
            )

            for i in vsel:
                v = bm.verts[i]
                for l in v.link_loops:
                    l[pivotLayer] = cursor
                    currentColor = l[colorLayer]
                    if pivotLevel == 0:
                        l[colorLayer] = (1.0, currentColor.y, currentColor.z, 1.0)
                    elif pivotLevel == 1:
                        l[colorLayer] = (currentColor.x, 1.0, currentColor.z, 1.0)

            update_edit_mesh(obj.data)

        bm.free()

    def ensurePivotLayer(self, bm, layer):
        if layer not in bm.loops.layers.float_vector:
            return bm.loops.layers.float_vector.new(layer)
        else:
            return bm.loops.layers.float_vector[layer]

    def ensureVertexColors(self, context, bm):
        colorLayerName = context.scene.color_channel_name
        if colorLayerName not in bm.loops.layers.color:
            colorLayer = bm.loops.layers.color.new(colorLayerName)
            for v in bm.verts:
                for l in v.link_loops:
                    l[colorLayer] = (0.0, 0.0, 0.0, 1.0)
            return colorLayer
        else:
            return bm.loops.layers.color[colorLayerName]
