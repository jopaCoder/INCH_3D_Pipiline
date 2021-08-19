from .project_operations import check_update
import bpy
from bpy.types import Panel, UIList
import os

class INCH_PIPILINE_UL_global_project_browser(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.label(text=item.name)
        row.label(text=item.type)


class INCH_PIPILINE_UL_catalog_browser(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        self.use_filter_show = False
        row = layout.row(align=True)
        folder = row.operator("inch.generate_files_list",
                              text='', icon='FILE_FOLDER', emboss=False)
        folder.local_path = item.local_path
        folder.server_path = item.server_path
        folder.name = item.name
        row.label(text=item.name)


class INCH_PIPILINE_UL_files_list(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        icon = item.main_icon
        open_file_ot = row.operator('inch.open_file', text='', icon=icon, emboss=False)
        open_file_ot.file_path=item.local_path
        open_file_ot.file_type=item.file_type
        
        split = row.split(factor=0.4)
        split.label(text=item.name)
        split.alert = item.alert

        row2 = split.row()
        copy_file_path_ot = row2.operator("inch.copy_file_path", 
                                                text='', 
                                                icon=item.state_icon, 
                                                emboss=False)
        copy_file_path_ot.local_path = item.local_path
        copy_file_path_ot.server_path = item.server_path
        
        row2.label(text=item.state)
        state = item.state

        if 'server' in state:
            item_path = item.server_path
        else:
            item_path = item.local_path

        try:
            filesize = round(os.stat(item_path).st_size/(1024*1024),2)            
        except FileNotFoundError:
            filesize = 'error'
        row2.label(text='{}mb'.format(filesize))

class INCH_PIPILINE_PT_MainUI(Panel):

    bl_label = "INCH 3D Pipiline"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Pipeline'

    def draw(self, context):
        scene = context.scene

# region header
        layout = self.layout
        main_col = layout.column()
        first_row = main_col.row()
        first_row.prop(scene, 'inch_project_enum', text='Project')

        second_row = main_col.row()
        second_row.scale_y = 1.5
       # second_row.operator("inch.generate_sub_catalog", text='Change Catalog').lvl = 0
        second_row.operator("wm.sync", text='Sync')
# endregion

# region list catalog
        second_sub_row = main_col.row(align=True)
        second_sub_row.template_list('INCH_PIPILINE_UL_catalog_browser',
                                     '', scene.inch_catalogs[0],
                                     'col',
                                     scene.inch_catalogs[0],
                                     'index', rows=11)

        second_sub_row.template_list('INCH_PIPILINE_UL_catalog_browser',
                                     '', scene.inch_catalogs[1],
                                     'col',
                                     scene.inch_catalogs[1],
                                     'index', rows=11)

        second_sub_row.template_list('INCH_PIPILINE_UL_catalog_browser',
                                     '', scene.inch_catalogs[2],
                                     'col',
                                     scene.inch_catalogs[2],
                                     'index', rows=11)

        second_sub_row.template_list('INCH_PIPILINE_UL_catalog_browser',
                                     '', scene.inch_catalogs[3],
                                     'col',
                                     scene.inch_catalogs[3],
                                     'index', rows=11)

        second_sub_row.template_list('INCH_PIPILINE_UL_catalog_browser',
                                     '', scene.inch_catalogs[4],
                                     'col',
                                     scene.inch_catalogs[4],
                                     'index', rows=11)
# endregion

# region files list
        third_row = main_col.row()
        box = third_row.box()
        box.label(text='{}:'.format(
            bpy.context.scene.inch_current_folder.local_path))
        box_row = box.row()
        box_row.template_list('INCH_PIPILINE_UL_files_list', '', scene,
                              'inch_files_list', scene, 'inch_list_index', rows=10)
# endregion

# region rigth column
        right_col = box_row.column()
        right_col.scale_y = 1.5
        right_col.scale_x = 1
        right_col.operator("inch.refresh", text='', icon='FILE_REFRESH')
        right_col.operator("inch.open_folder", text='', icon='FILE_FOLDER')
        right_col.operator("inch.copy_folder_path", text='', icon='DUPLICATE')

        right_col.separator(factor=5)

        right_col.operator("inch.copy_file", text='', icon='EXPORT').to_server=True
        right_col.operator("inch.copy_file", text='', icon='IMPORT').to_server=False
# endregion

# region footer
        foutrh_row = main_col.row()
        foutrh_row.ui_units_y = 2
        foutrh_row.scale_y = 2
        foutrh_row.scale_x = 2
        foutrh_row.operator("wm.call_menu", text='',
                            icon='PREFERENCES').name = "OBJECT_MT_simple_custom_menu"
        
        foutrh_row.label(text=check_update())
        foutrh_row.separator(factor=100.0)
        foutrh_row.operator("wm.inch_save_main_file", text='', icon='BLENDER')
        foutrh_row.operator("inch.iter_main_file", text='', icon='ADD')
        foutrh_row.operator("inch.delete_file", text='', icon='TRASH')
# endregion


class SettingsMenu(bpy.types.Menu):
    bl_label = "God mode"
    bl_idname = "OBJECT_MT_simple_custom_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"

        layout.operator_menu_enum

        layout.operator("wm.inch_create_project_dialog", text='New Project')
        layout.operator("wm.import_project", text='Import Project')
        layout.operator("inch.dummy", text='Manage projects')
       
        sepparator = '-'*30
        layout.label(text=sepparator)
        
        layout.operator("wm.setup_local_path_dialog", text='Local Path')
        layout.operator("inch.update", text='Update')

        layout.label(text=sepparator)

        job_state = context.scene.inch_inch_copy_job_state
        alert_row = layout.row()
        alert_row.alert = job_state.state
        alert_row.operator('inch.render_job', text=job_state.command, emboss=False, icon='ARMATURE_DATA')


def register():
    bpy.utils.register_class(INCH_PIPILINE_UL_catalog_browser)
    bpy.utils.register_class(INCH_PIPILINE_UL_files_list)
    bpy.utils.register_class(INCH_PIPILINE_PT_MainUI)
    bpy.utils.register_class(SettingsMenu)
    bpy.utils.register_class(INCH_PIPILINE_UL_global_project_browser)


def unregister():
    bpy.utils.unregister_class(INCH_PIPILINE_UL_catalog_browser)
    bpy.utils.unregister_class(INCH_PIPILINE_UL_files_list)
    bpy.utils.unregister_class(INCH_PIPILINE_PT_MainUI)
    bpy.utils.unregister_class(SettingsMenu)
    bpy.utils.unregister_class(INCH_PIPILINE_UL_global_project_browser)