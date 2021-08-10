from bpy.app.handlers import persistent
import bpy


@persistent
def tratata(dummy):
    print('zalupaaaaaa')
    os.popen('copy {} {}'.format(copy_from, copy_to))
    
#bpy.app.handlers.render_write.remove(tratata)
bpy.app.handlers.render_write.append(tratata)


import os

copy_from = '"D:\\Stomatidin.mp4"'
copy_to = '"D:\\Prev\\Stomatidin.mp4"'


