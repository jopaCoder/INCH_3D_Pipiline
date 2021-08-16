import os

file1 = 'D:\\xata.blend'
file2 = "D:\Stomatidin.mp4"

date1 = os.stat(file1).st_mtime
date2 = os.stat(file2).st_mtime

if date1 > date2:
    print("xata in newr")