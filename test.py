
print('......................................................................................')
path = 'D:\\projects\\Inch_360_2021_08'

from pathlib import Path
import os

# prefix components:
space =  '    '
branch = '│   '
# pointers:
tee =    '├── '
last =   '└── '

def scan_dir(path):
    dir_contents = {}
    with os.scandir(path) as it:
        for entry in it:
            if  entry.is_dir():
                dir_contents[entry.name] = entry.path
    return dir_contents

def tree(path, prefix: str=''):

    contents = scan_dir(path)
    pointers = [tee] * (len(contents) - 1) + [last]

    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path

        extension = branch if pointer == tee else space 
        yield from tree(contents[path], prefix=prefix+extension)

for line in tree(path):
   print('{}'.format(line))
