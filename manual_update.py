import os
import shutil

update_folder = '\\\\fileserver.inch\\public\\exchange\\01 Aleksey Vykhristyuk\\Global_Projects_DB\\GOAWAY\\IWILLKILLYOU\\GERRARAHERE\\update'

files_folder = 'D:\\projects\\INCH_3D_Pipiline\\INCH_3D_Pipiline'

with os.scandir(files_folder) as folder:
    for entry in folder:
        if not entry.is_dir() and not entry.name.endswith('.txt'):
            trgt_path = os.path.join(update_folder, entry.name)
            shutil.copy2(entry.path, trgt_path)
