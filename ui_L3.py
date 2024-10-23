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

def Print(*args):
    if False:
        print(*args)

def Unit_M(length=4):
    return [[1 if i == j else 0 for j in range(length)] for i in range(length)]

def get_col(begin=0):
    # Print(f'get_col:{begin}')
    obj = bpy.context.object
    if not obj:
        return None
    NG=bpy.data.node_groups["Transform"]
    input=NG.nodes["Input Matrix"].inputs
    switch = NG.nodes["Switch"].inputs[0]
    if switch.default_value:
        newV = [None] * 4
        for i in range(len(newV)):
            newV[i] = bpy.data.node_groups["Transform"].nodes["Input Matrix"].inputs[i+begin*4].default_value
        return newV
    else:
        newV = [ i[begin] for i in obj.matrix_world ]
        # for i in range(len(newV)):
        #     input[i+begin*4].default_value = newV[i]   # update only 4
        return newV

def set_col(self,newV,begin=0):
    Print(f'set_col:{begin}')
    NG=bpy.data.node_groups["Transform"]
    input=NG.nodes["Input Matrix"].inputs
    switch = NG.nodes["Switch"].inputs[0]
    if self.shear:
        for i in range(len(newV)):
            input[i+begin*4].default_value = newV[i]   # update only 4
    else:
        self.shear = True


def update_matrix(input):
    Print('update_matrix')
    obj = bpy.context.object
    if not obj:
        return
    NG=bpy.data.node_groups["Transform"]
    switch = NG.nodes["Switch"].inputs[0]
    if switch.default_value:
        matrix = obj.matrix_world.copy()
        Print(f'switch:{switch.default_value}\nmatrix=\n{matrix}\n{obj.matrix_world}\n')
        obj.matrix_world = Unit_M()    # 复原
        Print(f'switch:{switch.default_value}\nmatrix2:\n{matrix}\n{obj.matrix_world}\n')
        for i in range(len(input)):
            input[i].default_value = matrix[i%4][i//4]
        
    else:
        matrix = Unit_M()
        # 找回
        for i in range(len(input)):
            matrix[i//4][i%4] = input[i].default_value
        obj.matrix_world = matrix.copy()
        Print(f'switch:{switch.default_value}\nmatrix:\n{matrix}\n')

def update_switch(self, context):
    Print('update_switch')
    NG=bpy.data.node_groups["Transform"]
    input=NG.nodes["Input Matrix"].inputs
    switch = NG.nodes["Switch"].inputs[0]

    switch.default_value = self.shear
    update_matrix(input)
    
    obj = bpy.context.object
    # 检测当前有没有几何节点修改器，没有则添加
    if not obj.modifiers:
        modifier = obj.modifiers.new(type='NODES', name='GN')
        # 设置几何节点修改器的节点树为 'Transform'
        modifier.node_group = bpy.data.node_groups.get('Transform')
    

class Get:
    def c1(self):
        return get_col(0)
    def c2(self):
        return get_col(1)
    def c3(self):
        return get_col(2)
    def c4(self):
        return get_col(3)
    
class Set:
    def c1(self, value):
        set_col(self,value,0)
    def c2(self, value):
        set_col(self,value,1)
    def c3(self, value):
        set_col(self,value,2)
    def c4(self, value):
        set_col(self,value,3)


class PropsGroup_games101(bpy.types.PropertyGroup):
    shear: bpy.props.BoolProperty(
        name='Shear',
        default=True,
        description='Enable Shear. 开启剪切变换',
        update=update_switch
    )
    c1: bpy.props.FloatVectorProperty(
        name='Column 1',
        size=4,
        default=[1.,0.,0.,0.],
        get=Get.c1,
        set=Set.c1,
        description='',
    )
    c2: bpy.props.FloatVectorProperty(
        name='Column 2',
        size=4,
        default=[0.,1.,0.,0.],
        get=Get.c2,
        set=Set.c2,
        description='',
    )
    c3: bpy.props.FloatVectorProperty(
        name='Column 3',
        size=4,
        default=[0.,0.,1.,0.],
        get=Get.c3,
        set=Set.c3,
        description='',
    )
    c4: bpy.props.FloatVectorProperty(
        name='Column 4',
        size=4,
        default=[0.,0.,0.,1.],
        get=Get.c4,
        set=Set.c4,
        description='',
    )


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

        row = layout.row()
        row.operator(ReloadScriptOperator.bl_idname,
                        text="", icon='FILE_REFRESH',emboss=False)
        row.operator(UnregScriptOperator.bl_idname,
                        text="", icon='X',emboss=False)
        
        # lock icon button
        row.prop(props, "shear", text="", icon='MOD_LATTICE')

        col = layout.column(align=True)
        row = col.row(align=True)
        col_ = row.column(align=True)
        col_.prop(props, 'c1')
        col_ = row.column(align=True)
        col_.prop(props, 'c2')
        col_ = row.column(align=True)
        col_.prop(props, 'c3')
        col_ = row.column(align=True)
        col_.prop(props, 'c4')


class UnregScriptOperator(bpy.types.Operator):
    bl_idname = 'object.unreg_script'
    bl_label = 'Unregister'
    bl_options = {'REGISTER'}
    bl_description = 'Unregister Script. 移除面板，可以再次运行来重新加载脚本'
    
    def execute(self, context):
        unregister()
        return {'FINISHED'}


class ReloadScriptOperator(bpy.types.Operator):
    bl_idname = 'object.reload_script'
    bl_label = 'Reload'
    bl_options = {'REGISTER'}
    bl_description = 'Reload Script. 重载脚本'

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
    UnregScriptOperator,
)


def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.games101 = bpy.props.PointerProperty(
        type=PropsGroup_games101)


def unregister():
    del bpy.types.Scene.games101
    for i in classes:
        bpy.utils.unregister_class(i)


if __name__ == "__main__":
    register()
