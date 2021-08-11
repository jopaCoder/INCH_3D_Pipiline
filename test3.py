# import os

# hostname = "192.168.18.254" #example
# response = os.system("ping -n 1 " + hostname)

# #and then check the response...
# if response == 0:
#     print(hostname, 'is up!')
# else:
#     print(hostname, 'is down!')


import os

path = 'jopa\\nanaika\\pisun'
path, tail = os.path.split(path)

print(path)