from os import path
import types
import bpy

from . import project_operations

from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup


class CatalogListItem(PropertyGroup):

    name: StringProperty(
        name="Name",
        description="A name for this item",
        default="Zalupa")

    local_path: StringProperty(
        name="Path",
        description="A name for this item",
        default="local_path")

    server_path: StringProperty(
        name="Path",
        description="A name for this item",
        default="server_path")


class CatalogListHandler(PropertyGroup):

    col: CollectionProperty(type=CatalogListItem)
    index: IntProperty(update=project_operations.generate_subcatalog)
    self_lvl: IntProperty()
    trgt_lvl: IntProperty()


class ProjectListItem(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="A name for this item",
        default="Zalupa")

    type: StringProperty(
        name="Type",
        description="Type of the project",
        default="Zalupa")

    local_path: StringProperty(
        name="Local Path",
        description="Local path of the project",
        default="Zalupa")

    server_path: StringProperty(
        name="Server Path",
        description="Server path of the project",
        default="Zalupa")


class FileListItem(PropertyGroup):

    name: StringProperty(
        name="Name",
        description="A name for this item",
        default="Zalupa"
        )

    file_type: StringProperty(
            name="Name",
            description="",
            default="Zalupa"
            )

    local_path: StringProperty(
        name="Path"
        )

    server_path: StringProperty(
        name="Path"
        )

    state: StringProperty(
        name="",
        default='local'
        )

    state_icon: StringProperty(
        name="",
        default='X'
        )

    main_icon: StringProperty(
        name="",
        default='BLENDER'
        )

    alert: BoolProperty(
        default=False
        )


class SyncCheckBox(PropertyGroup):
    name: StringProperty()
    checkbox: BoolProperty()
    local_path: StringProperty()
    server_path: StringProperty()


class CopyJobState(PropertyGroup):
    command: StringProperty(default='Run copy job')
    state: BoolProperty(default=False)


def register():
    bpy.utils.register_class(FileListItem)
    bpy.utils.register_class(ProjectListItem)
    bpy.utils.register_class(CatalogListItem)
    bpy.utils.register_class(CatalogListHandler)
    bpy.utils.register_class(SyncCheckBox)
    bpy.utils.register_class(CopyJobState)

    bpy.types.Scene.inch_inch_copy_job_state = PointerProperty(type=CopyJobState)

    bpy.types.Scene.inch_catalogs = CollectionProperty(type=CatalogListHandler)

    # список файлов
    bpy.types.Scene.inch_files_list = CollectionProperty(type=FileListItem)
    bpy.types.Scene.inch_list_index = IntProperty(
        name="Index for my_list", default=0)

    # список проектов
    bpy.types.Scene.inch_projects_collection = CollectionProperty(
        type=ProjectListItem)
    bpy.types.Scene.inch_project_enum = EnumProperty(
        items=project_operations.generate_projects_list, update=project_operations.assing_project)

    bpy.types.Scene.inch_current_project = PointerProperty(
        type=ProjectListItem)
    bpy.types.Scene.inch_current_folder = PointerProperty(
        type=ProjectListItem)

def unregister():
    bpy.utils.unregister_class(FileListItem)
    bpy.utils.unregister_class(ProjectListItem)
    bpy.utils.unregister_class(CatalogListItem)
    bpy.utils.unregister_class(CatalogListHandler)
    bpy.utils.unregister_class(SyncCheckBox)
    bpy.utils.unregister_class(CopyJobState)

    del bpy.types.Scene.inch_inch_copy_job_state
    del bpy.types.Scene.inch_catalogs
    del bpy.types.Scene.inch_files_list
    del bpy.types.Scene.inch_list_index
    del bpy.types.Scene.inch_projects_collection
    del bpy.types.Scene.inch_project_enum
    del bpy.types.Scene.inch_current_project
    del bpy.types.Scene.inch_current_folder
