bl_info = {
    "name": "Context Switcher",
    "blender": (4, 2, 1),
    "category": "User Interface",
}

import bpy
import rna_keymap_ui
from bpy.types import Operator, AddonPreferences

# Global variables
addon_keymaps = []

class SCREEN_OT_context_switcher(Operator):
    bl_idname = "screen.context_switcher"
    bl_label = "Context Switcher"
    bl_description = "Open the context switcher at the mouse cursor location"
    bl_options = {'REGISTER', 'UNDO'}

    def switch_workspace(self, context, workspace_name):
        for ws in bpy.data.workspaces:
            if ws.name == workspace_name:
                context.window.workspace = ws
                return {'FINISHED'}
        return {'CANCELLED'}

    def draw(self, context):
        layout = self.layout
        
        area_types = {
            "General": [
                ('VIEW_3D', "3D Viewport", 'VIEW3D'),
                ('IMAGE_EDITOR', "Image Editor", 'IMAGE'),
                ('UV', "UV Editor", 'UV'),
                ('CompositorNodeTree', "Compositor", 'NODE_COMPOSITING'),
                ('TextureNodeTree', "Texture Node Editor", 'NODE_TEXTURE'),
                ('GeometryNodeTree', "Geometry Node Editor", 'NODETREE'),
                ('ShaderNodeTree', "Shader Editor", 'NODE_MATERIAL'),
                ('SEQUENCE_EDITOR', "Video Sequencer", 'SEQUENCE'),
                ('CLIP_EDITOR', "Movie Clip Editor", 'TRACKER'),
            ],
            "Animation": [
                ('DOPESHEET', "Dope Sheet", 'ACTION'),
                ('TIMELINE', "Timeline", 'TIME'),
                ('FCURVES', "Graph Editor", 'GRAPH'),
                ('DRIVERS', "Drivers", 'DRIVER'),
                ('NLA_EDITOR', "Nonlinear Animation", 'NLA'),
            ],
            "Scripting": [
                ('TEXT_EDITOR', "Text Editor", 'TEXT'),
                ('CONSOLE', "Python Console", 'CONSOLE'),
                ('INFO', "Info", 'INFO'),
            ],
            "Data": [
                ('OUTLINER', "Outliner", 'OUTLINER'),
                ('PROPERTIES', "Properties", 'PROPERTIES'),
                ('FILES', "File Browser", 'FILEBROWSER'),
                ('ASSETS', "Asset Browser", 'ASSET_MANAGER'),
                ('SPREADSHEET', "Spreadsheet", 'SPREADSHEET'),
                ('PREFERENCES', "Preferences", 'PREFERENCES'),
            ]
        }

        row = layout.row()
        
        # Add workspaces column first
        col = row.column()
        col.label(text="Workspaces")
        
        # Get current workspace and area type
        current_workspace = context.workspace.name
        current_area_type = context.area.ui_type
        
        # List all workspaces
        for ws in bpy.data.workspaces:
            op = col.operator("screen.context_switcher_workspace", 
                            text=ws.name, 
                            icon='WORKSPACE',
                            depress=(ws.name == current_workspace))
            op.workspace_name = ws.name
        
        # Add separator
        row.separator()
        
        # Add the rest of the area types
        for group, types in area_types.items():
            col = row.column()
            col.label(text=group)
            for identifier, name, icon in types:
                props = col.operator("wm.context_set_enum", 
                                   text=name, 
                                   icon=icon,
                                   depress=(identifier == current_area_type))
                props.data_path = "area.ui_type"
                props.value = identifier

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=700)

    def execute(self, context):
        return {'FINISHED'}

class SCREEN_OT_context_switcher_workspace(Operator):
    bl_idname = "screen.context_switcher_workspace"
    bl_label = "Switch Workspace"
    bl_description = "Switch to the selected workspace"
    bl_options = {'INTERNAL'}

    workspace_name: bpy.props.StringProperty()

    def execute(self, context):
        for ws in bpy.data.workspaces:
            if ws.name == self.workspace_name:
                context.window.workspace = ws
                break
        return {'FINISHED'}

def draw_menu(self, context):
    self.layout.operator(SCREEN_OT_context_switcher.bl_idname)

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    keymap_type: bpy.props.StringProperty(default="NONE")
    keymap_value: bpy.props.StringProperty(default="PRESS")
    keymap_ctrl: bpy.props.BoolProperty(default=False)
    keymap_alt: bpy.props.BoolProperty(default=False)
    keymap_shift: bpy.props.BoolProperty(default=False)

    def clear_keymap_settings(self):
        self.keymap_type = "NONE"
        self.keymap_value = "PRESS"
        self.keymap_ctrl = False
        self.keymap_alt = False
        self.keymap_shift = False

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.label(text="Keymap List:", icon="KEYINGSET")

        wm = context.window_manager
        kc = wm.keyconfigs.addon
        if not kc:
            col.label(text="No addon keyconfig available", icon='ERROR')
            return

        keymap_exists = False
        if addon_keymaps:
            km, kmi = addon_keymaps[0]
            if km and kmi and kmi.idname == SCREEN_OT_context_switcher.bl_idname:
                keymap_exists = True
                col.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
                
                self.keymap_type = kmi.type
                self.keymap_value = kmi.value
                self.keymap_ctrl = kmi.ctrl
                self.keymap_alt = kmi.alt
                self.keymap_shift = kmi.shift

        if not keymap_exists:
            self.clear_keymap_settings()
            row = col.row()
            row.operator(SCREEN_OT_context_switcher_add_keymap.bl_idname, 
                        text="Add Keyboard Shortcut", 
                        icon='ADD')

class SCREEN_OT_context_switcher_add_keymap(Operator):
    bl_idname = "screen.context_switcher_add_keymap"
    bl_label = "Add Context Switcher Keymap"
    bl_description = "Add keyboard shortcut for Context Switcher"
    bl_options = {'REGISTER', 'INTERNAL'}

    def add_hotkey(self):
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if kc:
            km = kc.keymaps.new(name='Window', space_type='EMPTY')
            kmi = km.keymap_items.new(
                SCREEN_OT_context_switcher.bl_idname,
                type='NONE',
                value='PRESS'
            )
            addon_keymaps.append((km, kmi))
            return kmi
        return None

    def execute(self, context):
        addon_keymaps.clear()
        self.add_hotkey()
        return {'FINISHED'}

def draw_menu(self, context):
    self.layout.operator(SCREEN_OT_context_switcher.bl_idname)

def register():
    bpy.utils.register_class(SCREEN_OT_context_switcher_workspace)
    bpy.utils.register_class(SCREEN_OT_context_switcher)
    bpy.utils.register_class(SCREEN_OT_context_switcher_add_keymap)
    bpy.utils.register_class(AddonPreferences)
    
    # Add to View menu
    bpy.types.VIEW3D_MT_view.append(draw_menu)
    
    # Add initial hotkey if preferences exist
    prefs = bpy.context.preferences.addons[__name__].preferences
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc and prefs.keymap_type != "NONE":
        km = kc.keymaps.new(name='Window', space_type='EMPTY')
        kmi = km.keymap_items.new(
            SCREEN_OT_context_switcher.bl_idname,
            type=prefs.keymap_type,
            value=prefs.keymap_value
        )
        kmi.ctrl = prefs.keymap_ctrl
        kmi.alt = prefs.keymap_alt
        kmi.shift = prefs.keymap_shift
        addon_keymaps.append((km, kmi))

def unregister():
    # Remove keymaps
    for km, kmi in addon_keymaps:
        if hasattr(km, 'keymap_items'):
            try:
                km.keymap_items.remove(kmi)
            except (ReferenceError, RuntimeError):
                pass
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_view.remove(draw_menu)
    bpy.utils.unregister_class(SCREEN_OT_context_switcher_workspace)
    bpy.utils.unregister_class(SCREEN_OT_context_switcher)
    bpy.utils.unregister_class(SCREEN_OT_context_switcher_add_keymap)
    bpy.utils.unregister_class(AddonPreferences)

if __name__ == "__main__":
    register()