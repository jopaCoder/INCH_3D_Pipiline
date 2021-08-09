# from bpy.app.handlers import persistent
# import bpy


# @persistent
# def tratata(dummy):
#     print('zalupaaaaaa')

# #bpy.app.handlers.render_write.remove(tratata)
# bpy.app.handlers.render_write.append(tratata)


import os

file1 = '"D:\\Stomatidin.mp4"'
file2 = '"D:\\Prev\\Stomatidin.mp4"'

os.popen('copy {} {}'.format(file1, file2))