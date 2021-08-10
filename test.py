# from bpy.app.handlers import persistent
# import bpy


# @persistent
# def tratata(dummy):
#     print('zalupaaaaaa')
#     os.popen('copy {} {}'.format(copy_from, copy_to))

# #bpy.app.handlers.render_write.remove(tratata)
# bpy.app.handlers.render_write.append(tratata)


# import os

# copy_from = '"D:\\Stomatidin.mp4"'
# copy_to = '"D:\\Prev\\Stomatidin.mp4"'


loc = 'D:\\Projects\\Stomatidin_2019_056'
serv = 'D:\\projects\\Pipiline\\server\\Stomatidin_2019_056'
rel_path = 'Work\\3D\\Render'

import os

print(os.path.join(loc, rel_path))

