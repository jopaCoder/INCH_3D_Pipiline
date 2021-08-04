import os

path = 'D:\\projects\\Inch_360_2021_08'
# prefix components:
space =  '    '
branch = '│   '
# pointers:
tee =    '├── '
last =   '└── '

dir = ['Preview', 'Work', 'Materials']

def tree(dir_path: str='', prefix: str=''):
 
    contents = dir_path
    pointers = [tee] * (len(contents) - 1) + [last]

    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path
        
        extension = branch if pointer == tee else space 
        #yield from tree(path, prefix=prefix+extension)

for line in tree(dir):
    print(line)