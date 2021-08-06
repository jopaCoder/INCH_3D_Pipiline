import os
import types
import bpy
import shutil
import subprocess    

from bpy.types import ColorRampElement, Operator
from .properties import SyncCheckBox, ProjectListItem
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty, EnumProperty

from . import project_operations


class INCH_PIPILINE_OT_dummy(Operator):
    """Detailed descroption"""

    bl_label = "Dummy"
    bl_idname = "inch.dummy"

    message: StringProperty(default='Pish!')

    def execute(self, context):

        print(self.message)
        return {'FINISHED'}


#region catalog
class INCH_PIPILINE_OT_copy_folder_path(Operator):
    """Detailed descroption"""

    bl_label = "Copy folder path"
    bl_idname = "inch.copy_folder_path"

    def execute(self, context):
        path = bpy.context.scene.inch_current_folder.local_path

        command = 'echo ' + path.strip() + '| clip'
        os.system(command)

        return {'FINISHED'}


class INCH_PIPILINE_OT_open_folder(Operator):
    """Open local folder. Press CTRL to open server folder"""

    bl_label = "Open folder"
    bl_idname = "inch.open_folder"

    def execute(self, context):
        path = bpy.context.scene.inch_current_folder.local_path
        os.startfile(path)
        return {'FINISHED'}

    def invoke(self, context, event):
        if event.ctrl:
            path = bpy.context.scene.inch_current_folder.server_path
            os.startfile(path)
            return {'FINISHED'}
        return self.execute(context)


class INCH_PIPILINE_OT_generate_sub_catalog(Operator):
    """Detailed descroption"""

    bl_label = "Generate sub-catalog"
    bl_idname = "inch.generate_sub_catalog"

    lvl: IntProperty()

    def execute(self, context):

        project_operations.initialize_catalog()

        return {'FINISHED'}
#endregion

# region files

class INCH_PIPILINE_OT_open_file(Operator):
    """Press CTRL for alternative soft. Press ALT for import. Press SHIFT for link"""

    bl_label = "Open file"
    bl_idname = "inch.open_file"

    file_path: StringProperty()
    file_type: StringProperty()

    def execute(self, context):
       
        if self.file_type == 'Blender':
            bpy.ops.wm.open_mainfile(filepath=self.file_path)
        else:
            #project_operations.show_message_box('Wrong file')
            subprocess.run('cmd /c start "" "'+ self.file_path +'"')
        return {'FINISHED'}

    def invoke(self, context, event):
        if event.ctrl and self.file_type == 'Image':
            soft = project_operations.read_local_paths('g_editor')
            subprocess.Popen([soft, self.file_path])
            return {'FINISHED'}
        else:
            return self.execute(context)


class INCH_PIPILINE_OT_generate_files_list(Operator):
    """Press CTRL to open local folder. Press SHIFT to open server folder"""

    bl_label = "Get list of open folder"
    bl_idname = "inch.generate_files_list"

    local_path: StringProperty(default='')
    server_path: StringProperty(default='')
    name: StringProperty(default='')

    def execute(self, context):

        local_folder = self.local_path
        server_folder = self.server_path

        dict_of_items = project_operations.compare_lists(local_folder, server_folder)
        project_operations.build_list(dict_of_items)
        project_operations.redraw_ui()

        current_folder = bpy.context.scene.inch_current_folder
        current_folder.local_path = local_folder
        current_folder.server_path = server_folder
        current_folder.name = self.name

        return {'FINISHED'}

    def invoke(self, context, event):
        if event.ctrl:
            os.startfile(self.local_path)
            return {'FINISHED'}
        elif event.shift:
            try:
                os.startfile(self.server_path)
            except FileNotFoundError:
                project_operations.show_message_box('Включи VPN', 'Макс, не тупи!')
            return {'FINISHED'}
        else:
            return self.execute(context)


class INCH_PIPILINE_OT_copy_file(Operator):
    """Copy file to server or backward"""

    bl_label = "Copy file"
    bl_idname = "inch.copy_file"

    to_server: BoolProperty()

    def execute(self, context):
        index = bpy.context.scene.inch_list_index

        file_from = bpy.context.scene.inch_files_list[index].local_path
        file_to = bpy.context.scene.inch_files_list[index].server_path

        try:
            if self.to_server:
                shutil.copy2(file_from, file_to)
            else:
                shutil.copy2(file_to, file_from)
        except FileNotFoundError:
            project_operations.show_message_box('Включи VPN!', 'Макс, не тупи!')
        project_operations.refresh_files_list()

        return {'FINISHED'}


class INCH_PIPILINE_OT_copy_file_path(Operator):
    """Press CTRL for server path"""

    bl_label = "Copy file path"
    bl_idname = "inch.copy_file_path"

    local_path: StringProperty()
    server_path: StringProperty()
    path: StringProperty()

    def execute(self, context):
        command = 'echo ' + self.path.strip() + '| clip'
        os.system(command)
        return {'FINISHED'}

    def invoke(self, context, event):
        if event.ctrl:
            self.path = self.server_path
        else:
            self.path = self.local_path
            
        return self.execute(context)


class INCH_PIPILINE_OT_delete_file(Operator):
    """Delete selected file on the local. Hold CTRL to delete on the server"""

    bl_label = "Delete file"
    bl_idname = "inch.delete_file"

    path: StringProperty(default='local_path')

    def define_file(self):
        index = bpy.context.scene.inch_list_index
        file_to_delete = eval('bpy.context.scene.inch_files_list[{}].{}'.format(index, self.path))
        
        return file_to_delete

    def execute(self, context):
        file_to_delete = self.define_file()

        try:
            os.remove(file_to_delete)
        except FileNotFoundError:
            self.path = 'server_path'
            file_to_delete = self.define_file()
            os.remove(file_to_delete)

        project_operations.refresh_files_list()

        return {'FINISHED'}

    def invoke(self, context, event):
        if event.ctrl:          
            self.path = 'server_path'
            print('pish')
        else:
            self.path = 'local_path'
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):        
        
        file_to_delete = self.define_file()
        layout = self.layout
        layout.label(text='Delete {}'.format(file_to_delete))


class INCH_PIPILINE_OT_refresh_files_list(Operator):
    """Nothing interesting"""

    bl_label = "Dummy"
    bl_idname = "inch.refresh"

    def execute(self, context):

        project_operations.refresh_files_list()

        return {'FINISHED'}
# endregion

#region project
class INCH_PIPILINE_OT_refresh_projects_list(Operator):
    """Nothing interesting"""

    bl_label = "Refresh projects list"
    bl_idname = "inch.refresh_projects_list"

    def execute(self, context):
        project_operations.reload_projects_db()
        return {'FINISHED'}


class INCH_PIPILINE_OT_creating_project_dialog(Operator):
    """Menu for creating new project"""

    bl_idname = 'wm.inch_create_project_dialog'
    bl_label = 'Create Project'

    project_name: StringProperty(name='Name')

    server_path: StringProperty(
        name='Server Path',
        default='D:\\projects\\Pipiline\\server\\Stomatidin_2019_056'
    )

    project_type: EnumProperty(
        name="Type",
        items=[
            ("VIDEO", "Video", "Макс, не тупи..."),
            ("PACKS", "Packs", "Лучше б вы мне в утреннюю кашу насрали!"),
            ("UNITY", "Unity", "Не знал, что у нас такие есть..."),
        ]
    )

    def execute(self, context):

        project_name = self.project_name
        project_type = self.project_type
        server_path = self.server_path

        server_path = project_operations.convert_mac_to_human(server_path)
        local_path = project_operations.compute_project_local_path(server_path)

        project_operations.write_new_project(
            project_name, project_type, local_path, server_path)
        project_operations.reload_projects_db()
        project_operations.create_catalogs(
            project_type, local_path, server_path)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
#endregion

class INCH_PIPILINE_OT_sync(Operator):
    """Sync project"""

    bl_idname = 'wm.sync'
    bl_label = 'Sync'
    
    checkboxes: CollectionProperty(type=SyncCheckBox)

    def execute(self, context):

        for check in self.checkboxes:
            if check.checkbox:
                local_path = check.local_path
                server_path = check.server_path
                files_list = project_operations.compare_lists(check.local_path, server_path)

                for file in files_list:
                    if files_list[file]['state'] == 'local':
                        if not os.path.exists(server_path): shutil.copytree(local_path, server_path)
                        shutil.copy2(files_list[file]['local_path'], files_list[file]['server_path'])
                    elif files_list[file]['state'] == 'server':
                        if not os.path.exists(local_path): shutil.copytree(server_path, local_path)
                        shutil.copy2(files_list[file]['server_path'], files_list[file]['local_path'])
                   
                    elif files_list[file]['state'] == 'synced':
                        print('{} need to compare'.format(file))

        project_operations.refresh_files_list()

        return {'FINISHED'}

    def invoke(self, context, event):
        
        project_local_path = context.scene.inch_current_project.local_path
        project_server_path = context.scene.inch_current_project.server_path    

        dir_local_path = context.scene.inch_current_project.local_path
        checkbox = self.checkboxes
        checkbox.clear()

        if len(checkbox) == 0:
        # prefix components:
            space =  '           '
            branch = '      │   '
            # pointers:
            tee =    '      ├── '
            last =   '      └── '

            def scan_dirs(local_path):     
                server_path = local_path.replace(project_local_path, project_server_path)
               
                dir_contents = {}
                local_contents = {}
                server_contents = {}

                
                def scan_dir(path):
                    try:
                        with os.scandir(path) as it:
                            for entry in it:
                                if  entry.is_dir():
                                    yield entry.name, entry.path
                    except FileNotFoundError:
                        return ''

                for name, path in scan_dir(local_path): local_contents[name] = path
                for name, path in scan_dir(server_path): server_contents[name] = path

                only_local = set(list(local_contents.keys())) - set(list(server_contents.keys()))
                only_server = set(list(server_contents.keys())) - set(list(local_contents.keys()))
                synced = set(list(local_contents.keys())) - only_local

                for key in only_local:
                    dir_contents[key] = {'local_path': local_contents[key], 
                                         'server_path': local_contents[key].replace(local_path, server_path)}
                for key in only_server:
                    dir_contents[key+'***'] = {'local_path': server_contents[key].replace(server_path,local_path), 
                                         'server_path': server_contents[key]}
                for key in synced:
                    dir_contents[key] = {'local_path': local_contents[key], 
                                         'server_path': server_contents[key]}


                return dir_contents

            def tree(path, prefix: str=''):

                contents = scan_dirs(path)
                pointers = [tee] * (len(contents) - 1) + [last]
                for pointer, name in zip(pointers, contents):
                    yield prefix + pointer + name, contents[name]['local_path'], contents[name]['server_path']

                    extension = branch if pointer == tee else space 
                    yield from tree(contents[name]['local_path'], prefix=prefix+extension)

            for name, dir_local_path, dir_server_path in tree(project_local_path):
                item = checkbox.add()
                item.name = name
                item.local_path = dir_local_path
                item.server_path = dir_server_path

        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        checkbox = self.checkboxes

        for item in checkbox:                      
            col.prop(item, 'checkbox', text=item.name)


class INCH_PIPILINE_OT_save_main_file_dialog(Operator):
    """Save current file to Blend files folder"""

    bl_idname = 'wm.inch_save_main_file'
    bl_label = 'Save main file'

    main_file_name: StringProperty(name='Name',
                                   description="Character_Zombie_Model \nCharacter_Zombie_Rig \nCharacter_Zombie_Animation_Running",
                                   default='Prefix_MainName_Sufix')

    def execute(self, context):

        main_file_name = self.main_file_name
        current_root = bpy.context.scene.inch_current_project.local_path
        relative_file_folder = 'Work\\3D\\Project\\Blend_Files'

        head_path = os.path.join(current_root, relative_file_folder)
        full_path = os.path.join(head_path, main_file_name+'_01.blend')

        bpy.ops.wm.save_as_mainfile(filepath=full_path)

        project_operations.refresh_files_list()

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        col_l = row.column(align=True)
        col_l.label(text="Character_Zombie_Model")
        col_l.label(text="Character_Zombie_Rig")
        col_l.label(text="Character_Zombie_Animation_Running")

        col_r = row.column(align=True)
        col_r.label(text="Scene_Lavina_Modeling")
        col_r.label(text="Scene_Lavina_Animation")
        col_r.label(text="Prop_Dildo_Modeling")

        layout.prop(self, 'main_file_name', text='')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)


class INCH_PIPILINE_OT_iter_main_file(Operator):
    """Iter current file for +1 and move old version to folder Versions """

    bl_idname = 'inch.iter_main_file'
    bl_label = 'Iter main file'

    def execute(self, context):

        def iterate_name(name):
            
            try:
                name_iterator_01 = int(name[len(name)-7])
            except ValueError:
                return {'CANCELED'}

            name_iterator_10 = int(name[len(name)-8])

            iter_to_replace = '{}{}.blend'.format(
                name_iterator_10, name_iterator_01)

            if name_iterator_01 == 9:
                name_iterator_10 += 1
                name_iterator_01 = 0
            else:
                name_iterator_01 += 1

            new_iter = '{}{}.blend'.format(name_iterator_10, name_iterator_01)
            itered_name = name.replace(iter_to_replace, new_iter)

            return itered_name

        bpy.ops.wm.save_mainfile()

        current_root = bpy.context.scene.inch_current_project.local_path
        relative_folder = 'Work\\3D\\Project\\Blend_Files\\Versions'

        old_mainfile_path = bpy.data.filepath
        old_mainfile_name = os.path.basename(old_mainfile_path)

        itered_mainfile_name = iterate_name(old_mainfile_path)

        head_path = os.path.join(current_root, relative_folder)
        destination_old_mainfile = os.path.join(head_path, old_mainfile_name)
        try:
            bpy.ops.wm.save_as_mainfile(filepath=itered_mainfile_name)
        except TypeError:
            project_operations.show_message_box('Save the file first!')
            return {'FINISHED'}
        shutil.move(old_mainfile_path, destination_old_mainfile)
        
        project_operations.refresh_files_list()

        return {'FINISHED'}


class INCH_PIPILINE_OT_define_local_path_dialog(Operator):
    """Choose your local root projects folder """

    bl_idname = 'wm.setup_local_path_dialog'
    bl_label = 'Setup Path'

    local_root: StringProperty(name='Local root',
                                default=project_operations.read_local_paths('local_root')
                                )
    g_editor: StringProperty(name='Graphical editor',
                                default=project_operations.read_local_paths('g_editor')
                                )

    def execute(self, context):

        project_operations.write_local_root('local_root', self.local_root)
        project_operations.write_local_root('g_editor', self.g_editor)

        return {'FINISHED'}

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


class INCH_PIPILINE_OT_import_project(Operator):
    """Import project from global db"""

    bl_idname = 'wm.import_project'
    bl_label = 'Import Project'

    glob_projects: CollectionProperty(type=ProjectListItem)
    index: IntProperty(default=0)

    def execute(self, context):
        project = self.glob_projects[self.index]
        project_operations.write_new_project(project.name, project.type, project.local_path, project.server_path)
        return {'FINISHED'}

    def invoke(self, context, event):
        
        for key, project_dict in project_operations.read_global_projects():
            project_list_item = self.glob_projects.add()
            project_list_item.name = key
            project_list_item.type = project_dict[key]['type']
            project_list_item.local_path = project_dict[key]['local_path']
            project_list_item.server_path = project_dict[key]['server_path']


        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout

        layout.template_list('INCH_PIPILINE_UL_global_project_browser', '', self,
                              'glob_projects', self, 'index', rows=10)



def register():
    bpy.utils.register_class(INCH_PIPILINE_OT_dummy)
    bpy.utils.register_class(INCH_PIPILINE_OT_iter_main_file)
    bpy.utils.register_class(INCH_PIPILINE_OT_save_main_file_dialog)
    bpy.utils.register_class(INCH_PIPILINE_OT_generate_files_list)
    bpy.utils.register_class(INCH_PIPILINE_OT_generate_sub_catalog)
    bpy.utils.register_class(INCH_PIPILINE_OT_copy_file_path)
    bpy.utils.register_class(INCH_PIPILINE_OT_refresh_files_list)
    bpy.utils.register_class(INCH_PIPILINE_OT_creating_project_dialog)
    bpy.utils.register_class(INCH_PIPILINE_OT_define_local_path_dialog)
    bpy.utils.register_class(INCH_PIPILINE_OT_refresh_projects_list)
    bpy.utils.register_class(INCH_PIPILINE_OT_open_folder)
    bpy.utils.register_class(INCH_PIPILINE_OT_copy_folder_path)
    bpy.utils.register_class(INCH_PIPILINE_OT_delete_file)
    bpy.utils.register_class(INCH_PIPILINE_OT_copy_file)
    bpy.utils.register_class(INCH_PIPILINE_OT_open_file)
    bpy.utils.register_class(INCH_PIPILINE_OT_sync)
    bpy.utils.register_class(INCH_PIPILINE_OT_import_project)