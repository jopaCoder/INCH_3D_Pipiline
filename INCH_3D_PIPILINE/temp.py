import os

video = ( 'Preview',
            'Preview\\Video',
            'Preview\\Image',
            'Work',
            'Work\\3D',
            'Work\\3D\\Export',
            'Work\\3D\\Render',
            'Work\\3D\\Project',
            'Work\\3D\\Project\\Maps',
            'Work\\3D\\Project\\Maps\\HDRI',
            'Work\\3D\\Project\\Temp',                     
            'Work\\3D\\Project\\Sound',
            'Work\\3D\\Project\\Blend_Files',
            'Work\\3D\\Project\\Blend_Files\\Versions',
            'Work\\3D\\Project\\Blend_Files\\Characters',
            'Work\\3D\\Project\\Blend_Files\\Characters\\Versions',
            'Work\\3D\\Project\\Other_Apps',
            'Work\\3D\\Project\\References',
            'Work\\3D\\Project\\Scripts',
            'Work\\3D\\Project\\Preprodaction',
            'Work\\3D\\Project\\Preprodaction\\Storyboard',
            'Work\\3D\\Project\\Preprodaction\\Cinematic',
            'Work\\3D\\Project\\Cache'
)

parts = video[9].split('\\')
print(parts)