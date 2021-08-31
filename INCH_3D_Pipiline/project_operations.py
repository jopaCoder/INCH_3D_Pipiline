import json
import os
import glob
import shutil
import subprocess
import shlex

import bpy

from . import project_system_paths
from . import templates

# region Project


def compute_project_local_path(server_path):
    project_folder = os.path.basename(server_path)
    local_root = read_paths_settings('local_root')
    project_local_path = os.path.join(local_root, project_folder)

    return project_local_path


def load_db(json_path):
    project_dict = {}
    try:
        with open(json_path, 'r') as projects_db:
            projects_dict = json.load(projects_db)
        return projects_dict
    except FileNotFoundError:
        return project_dict
    except json.decoder.JSONDecodeError:
        return project_dict


def write_db(json_path, projects_dict):
    with open(json_path, 'w') as projects_db:
        json.dump(projects_dict, projects_db, indent=2) 


def check_for_matches(db, key):
    for _key in db:
        if _key == key:
            return True
    return False    


def write_new_project(project_name, project_type, local_path, server_path):
    local_json_path = project_system_paths.LOCAL_PROJECT_DB_PATH
    server_json_path = project_system_paths.SERVER_PROJECT_DB_PATH        

    def append_project(json_path):
        projects_dict = load_db(json_path)
        if not check_for_matches(projects_dict, project_name):
            projects_dict[project_name] = {
                'type': project_type, 'local_path': local_path, 'server_path': server_path}
            write_db(json_path, projects_dict) 

    append_project(local_json_path)
    append_project(server_json_path)


def reload_projects_db():
    local_db_path = project_system_paths.LOCAL_PROJECT_DB_PATH
    archived_db_path = project_system_paths.ARCHIVED_PROJECT_DB_PATH
    local_db = load_db(local_db_path)
    archived_db = load_db(archived_db_path)

    projects_collection = bpy.context.scene.inch_projects_collection
    projects_collection.clear()

    for project_key in local_db.keys():
        if not project_key in archived_db:
            collection_item = projects_collection.add()
            collection_item.name = project_key
            collection_item.type = local_db[project_key]['type']
            collection_item.local_path = local_db[project_key]['local_path']
            collection_item.server_path = local_db[project_key]['server_path']


def assing_project(self, context):
    
    try:
        current_project_key = bpy.context.scene.inch_project_enum
        current_project_hodler = bpy.context.scene.inch_current_project
        projects_col = bpy.context.scene.inch_projects_collection

        current_project_hodler.name = projects_col[current_project_key]['name']
        current_project_hodler.type = projects_col[current_project_key]['type']
        current_project_hodler.local_path = projects_col[current_project_key]['local_path']
        current_project_hodler.server_path = projects_col[current_project_key]['server_path']

        initialize_catalog()

    except KeyError:
        print('KeyError from: {}'.format(self))


def generate_projects_list(self, context):

    col_items = []

    for project_item in bpy.context.scene.inch_projects_collection:

        project_key = project_item.name

        item = (project_key, project_key, project_key)

        col_items.append(item)

    return col_items


def read_global_projects():
    local_db_path = project_system_paths.LOCAL_PROJECT_DB_PATH
    server_db_path = project_system_paths.SERVER_PROJECT_DB_PATH  
    
    local_projects_dict = load_db(local_db_path)
    global_projects_dict = load_db(server_db_path)

    global_projects = set(list(global_projects_dict.keys())) - set(list(local_projects_dict.keys()))
        
    for key in global_projects:
        yield key, {key: {'local_path': global_projects_dict[key]['local_path'],
                            'server_path': global_projects_dict[key]['server_path'],
                            'type': global_projects_dict[key]['type']
        }}


def build_projects_manager_lists():
    local_db_path = project_system_paths.LOCAL_PROJECT_DB_PATH
    archived_db_path = project_system_paths.ARCHIVED_PROJECT_DB_PATH
    
    lived_db = load_db(local_db_path)
    archived_db = load_db(archived_db_path)

    colls = bpy.context.scene.inch_projects_manager_col
    colls.archived_projects.clear()
    colls.lived_projects.clear()
    for key in lived_db.keys():
        if key in archived_db.keys():
            item = colls.archived_projects.add()
        else:
            item = colls.lived_projects.add()
        
        item.name = key
        item.local_path = lived_db[key]['local_path']
        item.server_path = lived_db[key]['server_path']
        item.type = lived_db[key]['type']

# endregion

# region List

def load_custom_icons():

    preview_collections = {}

    import bpy.utils.previews
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pcoll = bpy.utils.previews.new()

    with os.scandir(my_icons_dir) as it:
        for entry in it:
            pcoll.load(entry.name[:-4], entry.path, 'IMAGE')
            preview_collections["state"] = pcoll

    return preview_collections


def build_list(dict_of_stats):

    list_object = bpy.context.scene.inch_files_list
    list_object.clear()

    for key in sorted(dict_of_stats.keys()):
        file_type = check_file_type(key)

        handle = list_object.add()
        handle.name = key

        handle.state = dict_of_stats[key]['state']
        handle.state_icon = dict_of_stats[key]['state_icon']
        handle.alert = dict_of_stats[key]['alert']
        handle.local_path = dict_of_stats[key]['local_path']
        handle.server_path = dict_of_stats[key]['server_path']
        handle.main_icon = dict_of_stats[key]['main_icon']
        handle.file_size = dict_of_stats[key]['file_size']
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

    state_icon = {'only_local_files': 'icon_local',
                'only_server_files': 'icon_server',
                'duply_local': 'icon_synced'}

    alert = {'only_local_files': False,
            'only_server_files': True,
            'duply_local': False}

    for index in range(3):
        for item in list_of_lists[index]:

            local_path = os.path.join(local_dir, item)
            server_path = os.path.join(server_dir, item)
            file_state = state[keys[index]]

            if file_state == 'server':
                item_path = server_path
            else:
                item_path = local_path

            try:
                filesize = str('{}mb'.format(round(os.stat(item_path).st_size/(1024*1024),2)))
            except FileNotFoundError:
                filesize = 'error'

            if index == 2:
                local_mtime = os.stat(local_path).st_mtime
                server_mtime = os.stat(server_path).st_mtime
                
                if local_mtime > server_mtime:
                    relevance = 'icon_old'
                    rel_state = 'чем пахнет?'
                elif local_mtime < server_mtime:
                    relevance = 'icon_new'
                    rel_state = 'огурчик!'
                else:
                    relevance = 'icon_synced'
                    rel_state = file_state
            else:
                relevance = state_icon[keys[index]]
                rel_state = file_state

            file_stats[item] = {'state': rel_state,
                                'state_icon': relevance,
                                'alert': alert[keys[index]],
                                'main_icon': main_icon,
                                'local_path': local_path,
                                'server_path': server_path,
                                'file_size': filesize
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


def read_paths_settings(key):
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

    context = bpy.context
    catalog = context.scene.inch_catalogs

    if len(catalog) == 0:
        for lvl in range(7):
            item = catalog.add()
            item.self_lvl = lvl
            item.trgt_lvl = lvl+1
            item.name = '{}'.format(lvl)

    col = bpy.context.scene.inch_catalogs[0].col
    col.clear()

    if context.scene.inch_current_project.name == 'Zalupa': 
        assing_project(None, context)
    else:
        local_path = context.scene.inch_current_project.local_path
        server_path = context.scene.inch_current_project.server_path

        try:
            with os.scandir(local_path) as it:
                for entry in it:
                    if entry.is_dir:
                        item = col.add()
                        item.name = entry.name
                        item.local_path = os.path.join(local_path, entry.name)
                        item.server_path = os.path.join(server_path, entry.name)
        except FileNotFoundError:
            show_message_box(local_path,
                            'initialize_catalog: Папка не найдена', icon='ERROR')
        
        #потом заменим на rebuild
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
    except FileNotFoundError:
        show_message_box('Указанный в настройках путь, не существует!\n{}'.format(local_path), 'Корневой локальный каталог')

    try:
        os.mkdir(server_path)
    except FileExistsError:
        print('{} is alreary exsists'.format(server_path))
    except FileNotFoundError:
        show_message_box('Серверный путь, не существует!\n{}'.format(server_path), 'Корневой серверный каталог')

    for path in project_struct:

        try:
            os.mkdir(os.path.join(local_path, path))
            os.mkdir(os.path.join(server_path, path))
        except FileExistsError:
            print('{} is alreary exsists'.format(path))
        except FileNotFoundError:
            if not ping_server(): show_message_box('Включи VPN, сука!', 'Макс, не тупи!')


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

    if folder == 'Blend_Files' or folder == 'Versions':
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
    if ext == '.blend':
        return 'Blender'
    elif ext == '.tif' or ext == '.tiff' or ext == '.jpg' or ext == '.jpeg' or ext == '.png':
        return 'Image'
    elif ext == '.obj':
        return 'Obj'
    elif ext == '.fbx':
        return 'Fbx'
    elif ext == '.abc':
        return 'Alembic'
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


def run_vpn():
    if os.getlogin().lower == 'root':
        config = 'm.kekin'
    else:
        config = os.getlogin()

    cmd = 'start /b cmd /c "C:\\Program Files\\OpenVPN\\bin\\openvpn-gui.exe" --connect {}.ovpn'.format(config)
    args = shlex.split(cmd)
    x = subprocess.Popen(args, shell=True)


def ping_server():
    # hostname = "192.168.18.254"
    # response = os.system("ping -n 1 " + hostname)

    # if response == 0:
    #     return True
    # else:
    #     return False
    return True


def set_render_path(path):

    root_path = bpy.context.scene.inch_current_project.local_path
    rel_render_path = 'Work\\3D\\Render'
    filename = os.path.basename(path)
    filename = filename.replace('.blend', '')
    bpy.context.scene.render.filepath = os.path.join(root_path, rel_render_path, filename, filename + '_')


def check_startup_conditions():
    local_root = read_paths_settings('local_root')

    current_project = bpy.context.scene.inch_current_project
    current_folder = bpy.context.scene.inch_current_folder
    folder_local_path = current_folder.local_path

    if not folder_local_path == 'Zalupa':
        if not str(folder_local_path).startswith(local_root):
            index = folder_local_path.find(os.path.basename(current_project.local_path))
            wrong_root = folder_local_path[:index]
            actual_local_path = folder_local_path.replace(wrong_root, local_root)
            current_folder.local_path = actual_local_path


def check_update():
    update_folder = project_system_paths.UPDATE_FOLDER
    abs_path = project_system_paths.ABS_PATH
    try:
        with os.scandir(update_folder) as it:
            for entry in it:
                if not entry.is_dir():
                    src_file = entry.path
                    trgt_file = os.path.join(abs_path, entry.name)
                    src_file_size = os.stat(src_file).st_size
                    try:
                        trgt_file_size = os.stat(trgt_file).st_size
                    except FileNotFoundError:
                        return "Вышло новое обновление!"

                    if src_file_size != trgt_file_size:
                        return "Вышло новое обновление!"
        return '8==э'
    except FileNotFoundError:
        return 'VPN'


def copy_file(file_from, file_to):

    def copy():
        try:
            shutil.copy2(file_from, file_to)
        except FileNotFoundError:
            show_message_box(file_to, 'Файл не существует или к нему нет доступа')

    src_path, s_filename = os.path.split(file_from)
    dst_path, d_filename = os.path.split(file_to)
    
    if not os.path.exists(dst_path):
        shutil.copytree(src_path, dst_path)

    if os.path.isfile(file_to):
        src_mtime = os.stat(file_from).st_mtime
        dst_mtime = os.stat(file_to).st_mtime
        copy()

        if src_mtime < dst_mtime:          
            show_message_box('На более старый, дебил...', 'Файл заменен')
        elif src_mtime > dst_mtime:
            show_message_box('На более новый', 'Файл заменен')
        else:
            show_message_box('Ты ничего не потерял, но и не приобрел', 'Файл заменен')
    else:
        copy()
    