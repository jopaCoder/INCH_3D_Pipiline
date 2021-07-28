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
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Interface"
}

import bpy
from bpy.app.handlers import persistent

from . import ui
from . import properties
from . import operators
from . import project_operations

@persistent
def load_handler(dummy):
    project_operations.reload_projects_db()
    project_operations.initialize_catalog()

def register():
    ui.register()
    properties.register()
    operators.register()

    bpy.app.handlers.load_post.append(load_handler)
    

def unregister():
    pass

if '__NAME__' == '__MAIN__':
    register()
