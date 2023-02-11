bl_info = {
    "name": "Fan blades",
    "author": "Gabriel Shaar",
    "version": (1, 0, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Add > Mesh > Fan blades",
    "description": "Add fan blades",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
    "email": "blendofishi@pm.me",
}

import bpy
from math import pi

def add_mesh(name, vertices, faces, edges=None, colllection_name="Collection"):    
    if edges is None:
        edges = []
    context = bpy.context
    
    scene = bpy.context.scene
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(mesh.name, mesh)
    object.location=context.scene.cursor.location
    scene.collection.objects.link(object)
    mesh.from_pydata(vertices, edges, faces)
    return object

class FanBladeGenerator(bpy.types.Operator):

    bl_idname = "object.fan_blade_generator"
    bl_label = "Fan blades"
    bl_options = {'REGISTER', 'UNDO'}

    count: bpy.props.IntProperty(name="Blades", default=5, min=2, max=50)
    deform: bpy.props.FloatProperty(name="Deform angle", default=35, min=2, max=100)
    thickness: bpy.props.FloatProperty(name="Thickness", default=0.15, min=0.001, max=1)
    form_smooth: bpy.props.IntProperty(name="Form smooth", default=4, min=1, max=10)
    edge_smooth_enabled: bpy.props.BoolProperty(name="Edge smooth", default=True)
    edge_smooth: bpy.props.IntProperty(name="Edge smooth", default=2, min=1, max=10)

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        scene = context.scene
        cursor = scene.cursor.location
        
        vertices = [
         (0.83, 0.0, -0.79), # 0
         (6.75, 0.0, -1.04), # 1
         (0.83, -0.0, 0.79), # 2
         (5.71, -0.0, 0.85), # 3
         (0.83, 0.0, -0.46), # 4
         (6.53, 0.0, 0.03)   # 5
        ]
        faces = [
            [2, 3, 5, 4], 
            [4, 5, 1, 0]
        ]
        object = add_mesh("Fan", vertices, faces)
        
        bpy.context.view_layer.objects.active = object
        fan_name = object.name
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        bpy.ops.object.empty_add(rotation=(0, 0, pi * (360 / self.count) / 180))
        blade_rotation_axis = context.object
        blade_rotation_axis.name = fan_name + '.Fan_blade_rotation'
        
        bpy.ops.object.empty_add()
        blade_deform_axis = context.object
        blade_deform_axis.empty_display_type = 'SPHERE'        
        blade_deform_axis.name = fan_name + '.Fan_blade_deform'
        
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(True)
        
        object.modifiers.new('Fan Form Smooth', 'SUBSURF')
        modifier_smooth = object.modifiers["Fan Form Smooth"]
        modifier_smooth.levels = self.form_smooth
        modifier_smooth.render_levels = self.form_smooth
        modifier_smooth.show_expanded = False
        
        object.modifiers.new('Fan Solidify', 'SOLIDIFY')
        modifier_solidify = object.modifiers["Fan Solidify"]
        modifier_solidify.thickness = self.thickness
        modifier_solidify.offset = 1.0
        modifier_solidify.show_expanded = False

        object.modifiers.new('Fan Deform', 'SIMPLE_DEFORM')
        modifier_deform = object.modifiers["Fan Deform"]
        modifier_deform.deform_axis = 'Z'
        modifier_deform.angle = pi * self.deform / 180
        modifier_deform.origin = blade_deform_axis
        modifier_deform.show_expanded = False

        object.modifiers.new('Fan Array', 'ARRAY')
        modifier_array = object.modifiers["Fan Array"]
        modifier_array.use_relative_offset = False
        modifier_array.use_object_offset = True
        modifier_array.count = self.count
        modifier_array.offset_object = blade_rotation_axis
        modifier_array.show_expanded = False
        
        if self.edge_smooth_enabled:
            object.modifiers.new('Fan Edge Smooth', 'SUBSURF')
            modifier_smooth = object.modifiers["Fan Edge Smooth"]
            modifier_smooth.levels = self.edge_smooth
            modifier_smooth.render_levels = self.edge_smooth
            modifier_smooth.show_expanded = False
            
        bpy.ops.object.select_all(action='DESELECT')
        blade_deform_axis.select_set(True)
        blade_rotation_axis.select_set(True)
        object.select_set(True)
        bpy.context.view_layer.objects.active = object
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        
        bpy.ops.object.select_all(action='DESELECT')
        object.select_set(True)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(FanBladeGenerator.bl_idname)


def register():
    bpy.utils.register_class(FanBladeGenerator)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(FanBladeGenerator)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()