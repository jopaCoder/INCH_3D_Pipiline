import subprocess    


# path_to_notepad = "C:\\Program Files\\Krita (x64)\\bin\\krita.exe"
# path_to_file = "D:\\panoform_grid_basic.png"

# subprocess.call([path_to_notepad, path_to_file])

filename = "D:\\Projects\\Stomatidin_2019_056\\Work\\3D\\Project\\Maps\\Screen.png"

subprocess.run('cmd /c start "" "'+ filename +'"')