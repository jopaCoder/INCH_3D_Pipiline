# import subprocess    


# path_to_notepad = "C:\\Program Files\\Krita (x64)\\bin\\krita.exe"
# path_to_file = "D:\\panoform_grid_basic.png"

# subprocess.call([path_to_notepad, path_to_file])




dict1 = {'apelsin': 'jopa',
        'jopa': 'zalupa',
        'zalupa': 'krokodil',
        'pelmen': 'hvoropa',
        'avokato': 'tratata'}

list_for_sort = dict1.keys()

for item in list_for_sort:
    print(item)

print('\n')
list_for_sort = sorted(list_for_sort)

for item in list_for_sort:
    print(item)