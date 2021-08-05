import json
import os
import glob

import bpy

from . import project_system_paths
from . import templates

# region Project


def compute_project_local_path(server_path):
    project_folder = os.path.basename(server_path)
    local_root = read_local_paths('local_root')
    project_local_path = os.path.join(local_root, project_folder)

    return project_local_path


def write_new_project(project_name, project_type, local_path, server_path):

    projects_dict = {}
    local_json_path = project_system_paths.LOCAL_JSON_PATH
    server_json_path = project_system_paths.SERVER_JSON_PATH

    def insert_project(json_path):
        projects_dict[project_name] = {
            'type': project_type, 'local_path': local_path, 'server_path': server_path}
        # Я не умею создавать папки! думай что-то или создай папку для сервер_дб вручную
        with open(json_path, 'w') as projects_db:
            json.dump(projects_dict, projects_db, indent=2)

    # Проверяем существование файлов бд
    if not os.path.exists(local_json_path):
        insert_project(local_json_path)
    else:
        try:  # проверяем, не пустой ли файл. Нужно, так как открываем дб и дополняем
            with open(local_json_path, 'r') as local_projects_db:
                projects_dict = json.load(local_projects_db)

        except json.decoder.JSONDecodeError:
            insert_project(local_json_path)

        else:
            insert_project(local_json_path)

    # Да бля, просто копирую код...
    if not os.path.exists(server_json_path):
        insert_project(server_json_path)
    else:
        try:  # а что делать? Я тупой!
            with open(server_json_path, 'r') as local_projects_db:
                projects_dict = json.load(local_projects_db)

        except json.decoder.JSONDecodeError:
            insert_project(server_json_path)

        else:
            insert_project(server_json_path)


def reload_projects_db():

    if os.path.exists(project_system_paths.LOCAL_JSON_PATH):
        with open(project_system_paths.LOCAL_JSON_PATH, 'r') as projects_db:
            local_projects_dict = json.load(projects_db)

        projects_collection = bpy.context.scene.inch_projects_collection
        projects_collection.clear()

        for project_key in local_projects_dict.keys():
            collection_item = projects_collection.add()
            collection_item.name = project_key
            collection_item.type = local_projects_dict[project_key]['type']
            collection_item.local_path = local_projects_dict[project_key]['local_path']
            collection_item.server_path = local_projects_dict[project_key]['server_path']


def assing_project(self, context):

    try:
        startup_script = bpy.data.texts['INCH_pipiline_startup_settings.py']
    except KeyError:
        startup_script = bpy.data.texts.new(
            'INCH_pipiline_startup_settings.py')
    else:
        startup_script = bpy.data.texts['INCH_pipiline_startup_settings.py']

    current_project_key = bpy.context.scene.inch_project_enum
    current_project_hodler = bpy.context.scene.inch_current_project
    projects_col = bpy.context.scene.inch_projects_collection

    startup_script.use_module = True
    startup_script.clear()
    startup_script.write(
        'import bpy \n \nbpy.context.scene.inch_project_enum = "{}"'.format(current_project_key))

    current_project_hodler.name = projects_col[current_project_key]['name']
    current_project_hodler.type = projects_col[current_project_key]['type']
    current_project_hodler.local_path = projects_col[current_project_key]['local_path']
    current_project_hodler.server_path = projects_col[current_project_key]['server_path']

    initialize_catalog()


def generate_projects_list(self, context):

    col_items = []

    for project_item in bpy.context.scene.inch_projects_collection:

        project_key = project_item.name

        item = (project_key, project_key, project_key)

        col_items.append(item)

    return col_items

# endregion

# region List


def build_list(dict_of_stats):

    property_group = bpy.context.scene.inch_files_list
    property_group.clear()

    list_of_items = dict_of_stats.keys()
    list_of_items = sorted(list_of_items)

    for item in list_of_items:
        file_type = check_file_type(item)

        handle = property_group.add()
        handle.name = item
        handle.state = dict_of_stats[item]['state']
        handle.state_icon = dict_of_stats[item]['state_icon']
        handle.alert = dict_of_stats[item]['alert']
        handle.local_path = dict_of_stats[item]['local_path']
        handle.server_path = dict_of_stats[item]['server_path']
        handle.main_icon = dict_of_stats[item]['main_icon']
        handle.file_type = file_type


def refresh_files_list():

    current_folder = bpy.context.scene.inch_current_folder

    dict_of_items = compare_lists(
        current_folder.local_path, current_folder.server_path)
    build_list(dict_of_items)
    redraw_ui()


def split_path(listOfFiles):
    splittedList = []
    for f in listOfFiles:
        splittedList.append(os.path.basename(f))
    return splittedList


def compare_lists(local_dir, server_dir):

    folder_stats = check_folder_type(os.path.basename(local_dir))
    main_icon = folder_stats['icon']
    mask = folder_stats['mask']

    local_files = glob.glob(os.path.join(local_dir, mask))
    server_files = glob.glob(os.path.join(server_dir, mask))

    local_files = split_path(local_files)
    server_files = split_path(server_files)

    # find unique words
    only_local_files = set(local_files) - set(server_files)
    only_server_files = set(server_files) - set(local_files)
    # find duplicates with converting to list for sorting
    duply_local = set(local_files) - set(only_local_files)

    file_stats = {}

    list_of_lists = (only_local_files, only_server_files, duply_local)

    keys = ('only_local_files', 'only_server_files', 'duply_local')

    state = {'only_local_files': 'local',
             'only_server_files': 'server',
             'duply_local': 'synced'}

    state_icon = {'only_local_files': 'NODETREE',
                  'only_server_files': 'URL',
                  'duply_local': 'DOT'}

    alert = {'only_local_files': False,
             'only_server_files': True,
             'duply_local': False}

    for index in range(3):
        for item in list_of_lists[index]:
            file_stats[item] = {'state': state[keys[index]],
                                'state_icon': state_icon[keys[index]],
                                'alert': alert[keys[index]],
                                'main_icon': main_icon,
                                'local_path': os.path.join(local_dir, item),
                                'server_path': os.path.join(server_dir, item)
                                }
    return file_stats

# endregion

# region Root


def write_local_root(key, path):

    paths_dict = {}

    try:
        with open(project_system_paths.LOCAL_PATH_SETTINGS, 'r') as local_path_setting:
            paths_dict = json.load(local_path_setting)
    except json.decoder.JSONDecodeError:
        pass
    finally:
        paths_dict[key] = path

        with open(project_system_paths.LOCAL_PATH_SETTINGS, 'w') as local_path_setting:
            json.dump(paths_dict, local_path_setting, indent=2)


def read_local_paths(key):
    project_system_paths.LOCAL_PATH_SETTINGS

    if os.path.exists(project_system_paths.LOCAL_PATH_SETTINGS):
        with open(project_system_paths.LOCAL_PATH_SETTINGS, 'r') as local_path_setting:
            return json.load(local_path_setting)[key]
    else:
        return 'Произошла какая - то хуйня. Зовите Лешу!'

# endregion

# region Catalog


def clear_subcatalog(trgt_lvl, self_lvl):
    for lvl in range(6 - self_lvl):
        to_clear = eval('bpy.context.scene.inch_catalogs[{}].col'.format(lvl + trgt_lvl))
        to_clear.clear()


def generate_subcatalog(self, context):

    trgt_lvl = self.trgt_lvl
    self_lvl = self.self_lvl

    if self_lvl < 4:
        col = eval('bpy.context.scene.inch_catalogs[{}].col'.format(trgt_lvl))
        index = eval('bpy.context.scene.inch_catalogs[{}].index'.format(self_lvl))
        local_path = eval(
            'bpy.context.scene.inch_catalogs[{}].col[{}].local_path'.format(self_lvl, index))
        server_path = eval(
            'bpy.context.scene.inch_catalogs[{}].col[{}].server_path'.format(self_lvl, index))

        col.clear()

        clear_subcatalog(trgt_lvl, self_lvl)

        with os.scandir(local_path) as it:
            for entry in it:
                if entry.is_dir():
                    item = col.add()
                    item.name = entry.name
                    item.local_path = os.path.join(local_path, entry.name)
                    item.server_path = os.path.join(server_path, entry.name)


def initialize_catalog():

    catalog = bpy.context.scene.inch_catalogs
    local_path = bpy.context.scene.inch_current_project.local_path
    server_path = bpy.context.scene.inch_current_project.server_path

    if len(catalog) == 0:
        for lvl in range(7):
            item = catalog.add()
            item.self_lvl = lvl
            item.trgt_lvl = lvl+1

    col = bpy.context.scene.inch_catalogs[0].col
    col.clear()

    try:
        with os.scandir(local_path) as it:
            for entry in it:
                if entry.is_dir:
                    item = col.add()
                    item.name = entry.name
                    item.local_path = os.path.join(local_path, entry.name)
                    item.server_path = os.path.join(server_path, entry.name)
    except FileNotFoundError:
        show_message_box(message="Someone deleted project folder",
                         title="Макс, не тупи!", icon='ERROR')

    clear_subcatalog(1, 2)


def create_catalogs(project_type, local_path, server_path):

    project_struct = ()

    if project_type == "VIDEO":
        project_struct = templates.VIDEO
    elif project_type == "PACKS":
        project_struct = templates.PACKS
    elif project_type == "UNITY":
        project_struct = templates.UNITY

    try:
        os.mkdir(local_path)
    except FileExistsError:
        print('{} is alreary exsists'.format(local_path))

    try:
        os.mkdir(server_path)
    except FileExistsError:
        print('{} is alreary exsists'.format(server_path))

    for path in project_struct:

        try:
            os.mkdir(os.path.join(local_path, path))
            os.mkdir(os.path.join(server_path, path))
        except FileExistsError:
            print('{} is alreary exsists'.format(path))


# endregion

def convert_mac_to_human(path):
    if path.startswith("smb"):
        path = path.replace("/", "\\")
        path = path.replace("smb:", "")
        path = path.replace("-", "")
        return path
    else:
        path = path.replace("-", "")
        return path


def show_message_box(message="", title="Message Box", icon='INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def check_folder_type(folder):
    dict = {}
    mask = ''
    icon = ''

    if folder == 'Blend_Files':
        mask = '*.blend'
        icon = 'BLENDER'
    elif folder == 'Maps' or folder == 'References' or folder == 'Preview' or folder == 'Render':
        mask = '*.*'
        icon = 'IMAGE_DATA'
    else:
        mask = '*.*'
        icon = 'FILE'

    dict = {'mask': mask, 'icon': icon}
    return dict

def check_file_type(file):
    filename, ext = os.path.splitext(file)
    #fbx obj alembic 
    if ext == '.blend':
        return 'Blender'
    elif ext == '.tif' or ext == '.tiff' or ext == '.jpg' or ext == '.jpeg' or ext == '.png':
        return 'Image'
    elif ext == '.obj' or ext == '.fbx' or ext == '.abc':
        return 'Mesh'
    elif ext == '.wav' or ext == '.mp3':
        return 'Sound'
    else:
        return 'Other'

def redraw_ui():
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "UI":
                    region.tag_redraw()
