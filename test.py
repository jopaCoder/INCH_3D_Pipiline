
from json import load
import os

from bpy.types import TOPBAR_MT_file_context_menu

print('......................................................................................')
path = 'D:\\projects\\Inch_360_2021_08'
local_root = 'D:\\projects'


for root, dir, filename in os.walk(path):
    parts, names = os.path.split(root)
    
    dots = []
    spaces = []
    to_print = ''

    parts = parts.split('\\')

    for part in parts:
        part = '.'*len(part)
        dots.append(part)
       
        part = ' '*len(part)
        spaces.append(part)

    for dot in dots:
        to_print = to_print + dot

    print(to_print + names)