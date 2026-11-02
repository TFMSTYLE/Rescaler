# SPDX-FileCopyrightText: 2025-2026 The French Monkey
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Rescaler",
    "author": "The French Monkey",
    "version": (1, 0, 3),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Rescaler",
    "description": "Uniformly rescale objects to match the target's bounding box scale",
    "category": "Object",
    "license": "GPL-3.0-or-later",
}

import bpy
from mathutils import Vector

try:
    from . import relay_updater
except ImportError:  # the Addon Collection has its own updates
    relay_updater = None

# ------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------

def get_bounding_box_world(obj):
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_corner = Vector((min(v.x for v in bbox_corners),
                         min(v.y for v in bbox_corners),
                         min(v.z for v in bbox_corners)))
    max_corner = Vector((max(v.x for v in bbox_corners),
                         max(v.y for v in bbox_corners),
                         max(v.z for v in bbox_corners)))
    return min_corner, max_corner

# ------------------------------------------------------------------------
# Operators
# ------------------------------------------------------------------------

class OBJECT_OT_rescaler_set_target(bpy.types.Operator):
    bl_idname = "object.rescaler_set_target"
    bl_label = "Set Target from Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object.")
            return {'CANCELLED'}
        context.scene.rescaler_target = obj.name
        self.report({'INFO'}, f"Target set to '{obj.name}'.")
        return {'FINISHED'}

class OBJECT_OT_rescaler_clear_target(bpy.types.Operator):
    bl_idname = "object.rescaler_clear_target"
    bl_label = "Clear Target"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.rescaler_target = ""
        self.report({'INFO'}, "Target cleared.")
        return {'FINISHED'}

class OBJECT_OT_rescaler_reset_scale(bpy.types.Operator):
    bl_idname = "object.rescaler_reset_scale"
    bl_label = "Reset Scale"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = list(context.selected_objects)
        if not selected:
            self.report({'ERROR'}, "No objects selected.")
            return {'CANCELLED'}
        for obj in selected:
            obj.scale = Vector((1, 1, 1))
        self.report({'INFO'}, f"Reset scale on {len(selected)} object(s).")
        return {'FINISHED'}

class OBJECT_OT_rescaler_apply(bpy.types.Operator):
    bl_idname = "object.rescaler_apply"
    bl_label = "Rescale to Target"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        target_name = scene.rescaler_target.strip()
        selected = list(context.selected_objects)

        if not target_name or target_name not in bpy.data.objects:
            self.report({'ERROR'}, "No valid target object set.")
            return {'CANCELLED'}

        target = bpy.data.objects[target_name]

        tgt_min, tgt_max = get_bounding_box_world(target)
        tgt_size = tgt_max - tgt_min
        tgt_center = (tgt_min + tgt_max) * 0.5
        tgt_largest = max(tgt_size.x, tgt_size.y, tgt_size.z)
        if tgt_largest == 0:
            self.report({'ERROR'}, f"Target '{target.name}' has zero dimension.")
            return {'CANCELLED'}

        to_scale = [o for o in selected if o != target]
        if not to_scale:
            self.report({'ERROR'}, "No objects selected to rescale.")
            return {'CANCELLED'}

        scaled = 0
        for obj in to_scale:
            src_min, src_max = get_bounding_box_world(obj)
            src_size = src_max - src_min
            src_center = (src_min + src_max) * 0.5
            src_largest = max(src_size.x, src_size.y, src_size.z)
            if src_largest == 0:
                self.report({'WARNING'}, f"Skipped '{obj.name}' (zero dimension).")
                continue

            scale_factor = tgt_largest / src_largest
            obj.scale = obj.scale * scale_factor

            if scene.rescaler_center_to_target:
                new_min, new_max = get_bounding_box_world(obj)
                new_center = (new_min + new_max) * 0.5
                offset = tgt_center - new_center
                obj.location += offset

            scaled += 1

        self.report({'INFO'}, f"Scaled {scaled} object(s) to fit '{target.name}'.")
        return {'FINISHED'}

# ------------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------------

def rescaler_selection_tracker(scene):
    try:
        ctx = bpy.context
        sel = list(ctx.selected_objects)
        tgt = scene.rescaler_target.strip()

        if tgt and tgt not in bpy.data.objects:
            scene.rescaler_target = ""
            tgt = ""

        if not tgt and len(sel) == 1:
            scene.rescaler_target = sel[0].name

    except Exception:
        pass

# ------------------------------------------------------------------------
# UI
# ------------------------------------------------------------------------

class VIEW3D_PT_rescaler(bpy.types.Panel):
    bl_label = "Rescaler"
    bl_idname = "VIEW3D_PT_rescaler"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rescaler"

    def draw(self, context):
        if relay_updater:
            relay_updater.draw(self.layout)
        layout = self.layout
        scene = context.scene
        selected = list(context.selected_objects)
        target_name = scene.rescaler_target.strip()

        layout.operator("object.rescaler_apply", text="Rescale objects", icon="FULLSCREEN_EXIT")

        row = layout.row(align=True)
        row.operator("object.rescaler_set_target", text="Set target scale")
        row.operator("object.rescaler_clear_target", text="Clear target")

        layout.separator(factor=0.5)

        layout.prop(scene, "rescaler_center_to_target", text="Center objects to target", toggle=True)

        layout.operator("object.rescaler_reset_scale", text="Reset Scale")

        layout.separator(factor=0.5)

        col = layout.column(align=True)

        if target_name and target_name in bpy.data.objects:
            others = [o for o in selected if o.name != target_name]
            col.label(text=f"Target: {target_name}")
            col.label(text=f"Objects to rescale: {len(others)}")
        else:
            col.label(text="Target: No object selected")
            col.label(text=f"Objects to rescale: {len(selected)}")

# ------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------

classes = (
    OBJECT_OT_rescaler_set_target,
    OBJECT_OT_rescaler_clear_target,
    OBJECT_OT_rescaler_reset_scale,
    OBJECT_OT_rescaler_apply,
    VIEW3D_PT_rescaler,  
)

def register():
    if relay_updater:
        relay_updater.register("blender-rescaler")
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.rescaler_target = bpy.props.StringProperty(
        name="Rescaler Target",
        description="Name of the target object for Rescaler",
        default=""
    )

    bpy.types.Scene.rescaler_center_to_target = bpy.props.BoolProperty(
        name="Center objects to target after scaling",
        description="Move scaled objects so their bounding box center aligns with the target's center",
        default=False
    )

    if rescaler_selection_tracker not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(rescaler_selection_tracker)

def unregister():
    if relay_updater:
        relay_updater.unregister()
    if rescaler_selection_tracker in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(rescaler_selection_tracker)

    del bpy.types.Scene.rescaler_target
    del bpy.types.Scene.rescaler_center_to_target

    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
