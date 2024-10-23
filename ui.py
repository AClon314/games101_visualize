# type: ignore
import bpy
import math
bl_info = {
    "name": "Games101 Visualization",
    "author": "AClon",
    "description": "Games101教程可视化",
    "blender": (2, 80, 0),
    "version": (0, 0, 2),
    "location": "View3D > Sidebar > Item",
    "warning": "",
    "category": "Item"
}


def update_a(self, value):
    obj = bpy.context.object
    a11 = self.a11
    a12 = self.a12
    a21 = self.a21
    a22 = self.a22
    obj.rotation_euler[2] = math.atan2(a21, a11)


class PropsGroup_games101(bpy.types.PropertyGroup):
    obj = bpy.context.object
    zero: bpy.props.FloatProperty(name='0', default=0, get= lambda s: 0, description='常数0')
    one: bpy.props.FloatProperty(name='1', default=1, get= lambda s: 1, description='常数1,用于齐次坐标。\n点为1，向量为0（平移不变性）')
    a11: bpy.props.FloatProperty(name='sx*cos', default=1.0, description='sx*cos +hx*sx*sin',
                                 get=lambda s: obj.scale[0]*math.cos(obj.rotation_euler[2])
                                 )
    a12: bpy.props.FloatProperty(name='-sy*sin', default=0.0, description='-sy*sin +hx*sy*cos')
    a21: bpy.props.FloatProperty(name='sx*sin', default=0.0, description='sx*sin +hy*sx*cos')
    a22: bpy.props.FloatProperty(name='sy*cos', default=1.0, description='sy*cos -hy*sy*sin')
    

class Panel_games101(bpy.types.Panel):
    bl_label = 'GAMES101🎮:矩阵SRT'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.games101
        obj = context.object

        layout.operator(ReloadScriptOperator.bl_idname, text="重载脚本",icon='FILE_REFRESH')

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(props, "a11", text=f'{obj.scale[0]:.1f}*{math.cos(obj.rotation_euler[2]):.1f}=')
        row.prop(props, "a12", text=f'{obj.scale[1]:.1f}*{-math.sin(obj.rotation_euler[2]):.1f}=')
        row.prop(obj, "location", index=0, text="tx")

        row = col.row(align=True)
        row.prop(props, "a21", text=f'{obj.scale[0]:.1f}*{math.sin(obj.rotation_euler[2]):.1f}=')
        row.prop(props, "a22", text=f'{obj.scale[1]:.1f}*{math.cos(obj.rotation_euler[2]):.1f}=')
        row.prop(obj, "location", index=1, text="ty")

        row = col.row(align=True)
        row.prop(props,"zero")
        row.prop(props,"zero")
        row.prop(props,"one")


class ReloadScriptOperator(bpy.types.Operator):
    bl_idname = 'object.reload_script'
    bl_label = 'Reload Script'
    bl_options = {'REGISTER'}
    # bl_description = ''

    def execute(self, context):
        # 获取当前文本编辑器
        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                with bpy.context.temp_override(area=area):
                    bpy.ops.text.resolve_conflict(resolution='RELOAD')
                    bpy.ops.text.run_script()
                break
        else:
            self.report({'ERROR'}, "没有找到文本编辑器")
            return {'CANCELLED'}

        return {'FINISHED'}


classes = (
    Panel_games101,
    PropsGroup_games101,
    ReloadScriptOperator,
)


def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.games101 = bpy.props.PointerProperty(
        type=PropsGroup_games101)


def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.games101


if __name__ == "__main__":
    register()
