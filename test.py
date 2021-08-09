from bpy.app.handlers import persistent
import bpy


@persistent
def tratata(dummy):
    print('zalupaaaaaa')

#bpy.app.handlers.render_write.remove(tratata)
bpy.app.handlers.render_write.append(tratata)