
import os
import bpy
import shutil
import subprocess
import shlex

from bpy.types import Operator
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty, EnumProperty

from .properties import SyncCheckBox, ProjectListItem
from . import project_operations as jopa
from . import project_system_paths


class INCH_PIPILINE_OT_dummy(Operator):
    """Detailed descroption"""

    bl_label = "Dummy"
    bl_idname = "inch.dummy"

    message: StringProperty(default='Pish!')

    def execute(self, context):

        print(self.message)
        return {'FINISHED'}


# region catalog
class INCH_PIPILINE_OT_copy_folder_path(Operator):
    """Copy folder path. Press CTRL for server path"""

    bl_label = "Copy folder path"
    bl_idname = "inch.copy_folder_path"

    path: StringProperty()

    def execute(self, context):
        
        command = 'echo {} | clip'.format(self.path.strip())
        os.system(command)

        return {'FINISHED'}

    def invoke(self, context, event):
        if event.ctrl:
            self.path = bpy.context.scene.inch_current_folder.server_path
        else:
            self.path = bpy.context.scene.inch_current_folder.local_path
        return self.execute(context)


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
            try:
                os.startfile(path)
            except FileNotFoundError:
                jopa.show_message_box(path, 'Нет доступа')
            return {'FINISHED'}
        return self.execute(context)


class INCH_PIPILINE_OT_generate_sub_catalog(Operator):
    """Detailed descroption"""

    bl_label = "Generate sub-catalog"
    bl_idname = "inch.generate_sub_catalog"

    lvl: IntProperty()

    def execute(self, context):

        jopa.initialize_catalog()

        return {'FINISHED'}
# endregion

# region files


class INCH_PIPILINE_OT_open_file(Operator):
    """Press CTRL for alternative soft. Press ALT for import. Press SHIFT for link"""

    bl_label = "Open file"
    bl_idname = "inch.open_file"

    file_path: StringProperty()
    file_type: StringProperty()

    def execute(self, context):

        if self.file_type == 'Blender':
            try:
                bpy.ops.wm.open_mainfile(filepath=self.file_path)
            except RuntimeError:
                jopa.show_message_box(
                    'Сперва скопируй файл!', 'Не стоит запускать файлы с сервака')
        else:
            cmd = 'cmd /c start "{}"'.format(self.file_path, '')
            args = shlex.split(cmd)
            subprocess.run(args, shell=True)
        return {'FINISHED'}

    def invoke(self, context, event):
        if event.shift and self.file_type == 'Image':
            bpy.ops.object.load_reference_image(filepath=self.file_path)
            return {'FINISHED'}
        if event.ctrl and self.file_type == 'Image':
            soft = jopa.read_paths_settings('g_editor')
            subprocess.Popen([soft, self.file_path])
            return {'FINISHED'}
        elif event.alt and self.file_type == 'Fbx':
            bpy.ops.import_scene.fbx(filepath=self.file_path)
            return {'FINISHED'}
        elif event.alt and self.file_type == 'Obj':
            bpy.ops.import_scene.obj(filepath=self.file_path)
            return {'FINISHED'}
        elif event.alt and self.file_type == 'Alembic':
            bpy.ops.wm.alembic_import(filepath=self.file_path)
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

        dict_of_items = jopa.compare_lists(local_folder, server_folder)
        jopa.build_list(dict_of_items)
        jopa.redraw_ui()

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
                jopa.show_message_box(self.server_path, 'Нет доступа')
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
            jopa.show_message_box(file_to, 'Файл не существует или к нему нет доступа')
        jopa.refresh_files_list()

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
        file_to_delete = eval(
            'bpy.context.scene.inch_files_list[{}].{}'.format(index, self.path))

        return file_to_delete

    def execute(self, context):
        file_to_delete = self.define_file()

        try:
            os.remove(file_to_delete)
        except FileNotFoundError:
            self.path = 'server_path'
            file_to_delete = self.define_file()
            os.remove(file_to_delete)

        jopa.refresh_files_list()

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

        jopa.refresh_files_list()

        return {'FINISHED'}
# endregion

# region project

class INCH_PIPILINE_OT_import_project(Operator):
    """Import project from global db"""

    bl_idname = 'wm.import_project'
    bl_label = 'Import Project'

    glob_projects: CollectionProperty(type=ProjectListItem)
    index: IntProperty(default=0)

    def execute(self, context):
        project = self.glob_projects[self.index]
        jopa.write_new_project(project.name, project.type,
                               project.local_path, project.server_path)
        jopa.create_catalogs(
            project.type, project.local_path, project.server_path)
        jopa.reload_projects_db()

        context.scene.inch_project_enum = project.name

        return {'FINISHED'}

    def invoke(self, context, event):
        if jopa.ping_server():       
            self.glob_projects.clear()
            for key, project_dict in jopa.read_global_projects():
                project_list_item = self.glob_projects.add()
                project_list_item.name = key
                project_list_item.type = project_dict[key]['type']
                project_list_item.local_path = project_dict[key]['local_path']
                
                local_root = jopa.read_paths_settings('local_root')
                if not (project_list_item.local_path).startswith(local_root):
                    project_folder = os.path.basename(project_list_item.local_path)
                    project_list_item.local_path = os.path.join(local_root, project_folder)

                project_list_item.server_path = project_dict[key]['server_path']

            return context.window_manager.invoke_props_dialog(self)
        else:
            jopa.show_message_box('VPN?', 'Сервер не отвечает')
            return {"FINISHED"}
    def draw(self, context):
        layout = self.layout

        layout.template_list('INCH_PIPILINE_UL_global_project_browser', '', self,
                             'glob_projects', self, 'index', rows=10)


class INCH_PIPILINE_OT_refresh_projects_list(Operator):
    """Nothing interesting"""

    bl_label = "Refresh projects list"
    bl_idname = "inch.refresh_projects_list"

    def execute(self, context):
        jopa.reload_projects_db()
        return {'FINISHED'}


class INCH_PIPILINE_OT_creating_project_dialog(Operator):
    """Menu for creating new project"""

    bl_idname = 'wm.inch_create_project_dialog'
    bl_label = 'Create Project'

    project_name: StringProperty(name='Name')

    server_path: StringProperty(
        name='Server Path',
        default=''
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

        server_path = jopa.convert_mac_to_human(server_path)
        local_path = jopa.compute_project_local_path(server_path)

        jopa.write_new_project(
            project_name, project_type, local_path, server_path)
        jopa.reload_projects_db()
        jopa.create_catalogs(
            project_type, local_path, server_path)

        context.scene.inch_project_enum = project_name

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'project_name')
        layout.prop(self, 'server_path')
        path = self.server_path
        if path.endswith('\\') or path.endswith('/'): path = path[:-1]
        self.project_name = os.path.basename(path)
        
        return self.execute(context)
# endregion


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
                files_list = jopa.compare_lists(check.local_path, server_path)

                for file in files_list:
                    if files_list[file]['state'] == 'local':
                        if not os.path.exists(server_path):
                            shutil.copytree(local_path, server_path)
                        #shutil.copy2(files_list[file]['local_path'], files_list[file]['server_path'])
                        os.popen('copy "{}" "{}"'.format(files_list[file]['local_path'],
                                                         files_list[file]['server_path']))
                    elif files_list[file]['state'] == 'server':
                        if not os.path.exists(local_path):
                            shutil.copytree(server_path, local_path)
                        #shutil.copy2(files_list[file]['server_path'], files_list[file]['local_path'])
                        os.popen('copy "{}" "{}"'.format(files_list[file]['server_path'],
                                                         files_list[file]['local_path']))
                    elif files_list[file]['state'] == 'synced':
                        print('{} need to compare'.format(file))

        jopa.refresh_files_list()

        return {'FINISHED'}

    def invoke(self, context, event):

        if jopa.ping_server():
            project_local_path = context.scene.inch_current_project.local_path
            project_server_path = context.scene.inch_current_project.server_path

            curr_folder = context.scene.inch_current_folder.name

            dir_local_path = context.scene.inch_current_project.local_path
            checkbox = self.checkboxes
            checkbox.clear()

            if len(checkbox) == 0:
                # prefix components:
                space = '           '
                branch = '      │   '
                # pointers:
                tee = '      ├── '
                last = '      └── '

                def scan_dirs(local_path):
                    server_path = local_path.replace(
                        project_local_path, project_server_path)

                    dir_contents = {}
                    local_contents = {}
                    server_contents = {}

                    def scan_dir(path):
                        try:
                            with os.scandir(path) as it:
                                for entry in it:
                                    if entry.is_dir():
                                        yield entry.name, entry.path
                        except FileNotFoundError:
                            return ''

                    for name, path in scan_dir(local_path):
                        local_contents[name] = path
                    for name, path in scan_dir(server_path):
                        server_contents[name] = path

                    only_local = set(list(local_contents.keys())) - \
                        set(list(server_contents.keys()))
                    only_server = set(list(server_contents.keys())) - \
                        set(list(local_contents.keys()))
                    synced = set(list(local_contents.keys())) - only_local

                    for key in only_local:
                        dir_contents[key] = {'local_path': local_contents[key],
                                             'server_path': local_contents[key].replace(local_path, server_path)}
                    for key in only_server:
                        dir_contents[key+'***'] = {'local_path': server_contents[key].replace(server_path, local_path),
                                                   'server_path': server_contents[key]}
                    for key in synced:
                        dir_contents[key] = {'local_path': local_contents[key],
                                             'server_path': server_contents[key]}

                    return dir_contents

                def tree(path, prefix: str = ''):

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
                    if str(name).endswith(curr_folder):
                        item.checkbox = True

            return context.window_manager.invoke_props_dialog(self)
        else:
            jopa.show_message_box('Включи VPN')
            return {'FINISHED'}

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

        jopa.set_render_path(full_path)

        bpy.ops.wm.save_as_mainfile(filepath=full_path)

        jopa.refresh_files_list()


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

        local_root = bpy.context.scene.inch_current_project.local_path
        server_root = bpy.context.scene.inch_current_project.server_path
        relative_folder = 'Work\\3D\\Project\\Blend_Files\\Versions'

        old_local_mainfile_path = bpy.data.filepath
        old_mainfile_name = os.path.basename(old_local_mainfile_path)
        old_server_mainfile_path = os.path.join(server_root, relative_folder[:-9], old_mainfile_name)

        itered_mainfile_name = iterate_name(old_local_mainfile_path)

        dst_old_local_mainfile = os.path.join(local_root, relative_folder, old_mainfile_name)
        dst_old_server_mainfile = os.path.join(server_root, relative_folder, old_mainfile_name)
        
        
        try:
            jopa.set_render_path(itered_mainfile_name)
            bpy.ops.wm.save_as_mainfile(filepath=itered_mainfile_name)

            shutil.move(old_local_mainfile_path, dst_old_local_mainfile)
            try:
                shutil.move(old_server_mainfile_path, dst_old_server_mainfile)
            except FileNotFoundError:
                print('Nothing to move on server')
        except TypeError:
            jopa.show_message_box('Save the file first!')
            return {'FINISHED'}

        jopa.refresh_files_list()

        return {'FINISHED'}


class INCH_PIPILINE_OT_define_local_path_dialog(Operator):
    """Choose your local root projects folder """

    bl_idname = 'wm.setup_local_path_dialog'
    bl_label = 'Setup Path'

    local_root: StringProperty(name='Local root'
                               )
    g_editor: StringProperty(name='Graphical editor'
                             )

    def execute(self, context):

        jopa.write_local_root('local_root', self.local_root)
        jopa.write_local_root('g_editor', self.g_editor)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.local_root = jopa.read_paths_settings('local_root')
        self.g_editor = jopa.read_paths_settings('g_editor')
        return context.window_manager.invoke_props_dialog(self)


class INCH_PIPILINE_OT_copy_render_job(Operator):
    """Copy every render to server"""

    bl_idname = 'inch.render_job'
    bl_label = 'Render job'

    def execute(self, context):
        job_state = context.scene.inch_inch_copy_job_state

        if job_state.state == False:
            job_state.state = True
        else:
            job_state.state = False

        if job_state.command == 'Run copy job':
            job_state.command = 'Stop copy job'
        else:
            job_state.command = 'Run copy job'
        
        def copy_job(dummy):
            local_root = bpy.context.scene.inch_current_project.local_path
            server_root = bpy.context.scene.inch_current_project.server_path
            
            local_path, tail = os.path.split(bpy.context.scene.render.filepath)
            server_path = local_path.replace(local_root, server_root)

            if not os.path.exists(server_path): shutil.copytree(local_path, server_path)

            files = jopa.compare_lists(local_path, server_path)

            for file in files:
                if files[file]['state'] == 'local':
                    os.popen('copy "{}" "{}"'.format(files[file]['local_path'], files[file]['server_path']))

        
        handler = bpy.app.handlers.render_write

        if not len(handler) == 0:
            for h in handler:
                handler.clear()
        else:
            handler.append(copy_job)
        
        return {'FINISHED'}


class INCH_PIPILINE_OT_update(Operator):
    """Update"""

    bl_idname = 'inch.update'
    bl_label = 'Update'

    def execute(self, context):

        update_folder = project_system_paths.UPDATE_FOLDER
        abs_path = project_system_paths.ABS_PATH
        
        with os.scandir(update_folder) as it:
            for entry in it:
                src_file = entry.path
                trgt_file = os.path.join(abs_path, entry.name)
                shutil.copy2(src_file, trgt_file)

        jopa.show_message_box('Все файлы обновления скопированы', 'Обновление прошло успешно, а хотя - хуй его знает')

        return {'FINISHED'}


classes = (INCH_PIPILINE_OT_dummy,
           INCH_PIPILINE_OT_iter_main_file,
           INCH_PIPILINE_OT_save_main_file_dialog,
           INCH_PIPILINE_OT_generate_files_list,
           INCH_PIPILINE_OT_generate_sub_catalog,
           INCH_PIPILINE_OT_copy_file_path,
           INCH_PIPILINE_OT_refresh_files_list,
           INCH_PIPILINE_OT_creating_project_dialog,
           INCH_PIPILINE_OT_define_local_path_dialog,
           INCH_PIPILINE_OT_refresh_projects_list,
           INCH_PIPILINE_OT_open_folder,
           INCH_PIPILINE_OT_copy_folder_path,
           INCH_PIPILINE_OT_delete_file,
           INCH_PIPILINE_OT_copy_file,
           INCH_PIPILINE_OT_open_file,
           INCH_PIPILINE_OT_sync,
           INCH_PIPILINE_OT_import_project,
           INCH_PIPILINE_OT_copy_render_job,
           INCH_PIPILINE_OT_update)


def register():
    for cl in classes:
        bpy.utils.register_class(cl)


def unregister():
    for cl in classes:
        bpy.utils.unregister_class(cl)