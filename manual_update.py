import os
import shutil

update_folder = '\\\\fileserver.inch\\public\\exchange\\01 Aleksey Vykhristyuk\\Global_Projects_DB\\GOAWAY\\IWILLKILLYOU\\GERRARAHERE\\update'

files_folder = 'D:\\projects\\INCH_3D_Pipiline\\INCH_3D_Pipiline'


def upload(path, copypath):
    with os.scandir(path) as folder:
        for entry in folder:
            if entry.is_dir() and entry.name != '__pycache__':
                newpath = os.path.join(copypath, entry.name)
                try:
                    os.makedirs(newpath)
                except FileExistsError:
                    print('{} is exists'.format(entry.name))
                upload(entry.path, newpath)
            elif  not entry.is_dir() and not entry.name.endswith('.txt'):
                trgt_path = os.path.join(copypath, entry.name)
                shutil.copy2(entry.path, trgt_path)



upload(files_folder, update_folder)
print('Update files is uploading')
