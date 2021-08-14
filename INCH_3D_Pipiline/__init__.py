# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "INCH_3D_PIPILINE",
    "author" : "Jopa",
    "description" : "",
    "blender" : (2, 93, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "warning" : "",
    "category" : "Interface"
}

import bpy
import os

from bpy.app.handlers import persistent

from . import properties
from . import operators
from . import ui
from . import project_operations as jopa

@persistent
def load_handler(dummy):
    jopa.reload_projects_db()
    try:
        bpy.context.scene.inch_project_enum = bpy.context.scene.inch_current_project.name
    except TypeError:
        pass
    jopa.check_startup_conditions()
    jopa.initialize_catalog()
    
    if not bpy.context.scene.inch_current_folder.name == 'Zalupa': 
        jopa.refresh_files_list()
    if not os.path.exists(jopa.read_paths_settings('local_root')): 
        jopa.show_message_box('Залезь в настройки и укажи путь к папке с проектами', 'Макс, не тупи!')
    if not jopa.ping_server(): jopa.show_message_box('А ты точно включил VPN?', 'Сервер не отвечает!')

def register():
    properties.register()
    operators.register()
    ui.register()

    bpy.app.handlers.load_post.append(load_handler)
    

def unregister():
    properties.unregister()
    operators.unregister()
    ui.unregister()

if __name__ == "__main__":
    register()
