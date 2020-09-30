import requests
import os
import errno
import json
import hashlib
import sys

# print help info
def plsgethelp():
    print("usage: python client.py host_os <address> <port>")
    print("\n         host_os == name of the operating system the server is on [win/linux]")

if "help" in sys.argv:
    plsgethelp()
    sys.exit(1)

# set operating system of server in command line argumet
if len(sys.argv) > 1:
    if sys.argv[1].upper() == 'linux'.upper():
        operating_system = 'linux'
    elif sys.argv[1].upper() == 'win'.upper() or sys.argv[1].upper() == 'windows'.upper():
        operating_system = 'win'
else:
    plsgethelp()
    sys.exit(1)

# set remote address/url
if len(sys.argv) > 2:
    address = sys.argv[2]
else:
    address = input('server address: [do not need to add "https://"]')


# set remote port
if len(sys.argv) > 3:
    try:
        port = int(sys.argv)
    except:
        print('invalid port')
else:
    # default port
    port = 42068


# os specific arguments
# IMPORTANT: this is for the server and not the client
if operating_system == 'linux':
    root = '/'
    listdir = 'ls'
    slash = '/'

elif operating_system == 'win':
    root = 'c:\\'
    listdir = 'dir'
    slash = '\\'

# more default variables
## set the default start location for the shell
cwd = root
## url of the server
url = f"http://{address}:{port}/"

# derive the password to the server
password = input('password: ')
# send hashed password bc the connection in encryptionless
m = hashlib.sha256()
m.update(password.encode('utf-8'))
hashed_password = m.hexdigest()



# create downloads folder
if not os.path.exists('./downloads'):
    os.makedirs('downloads')

def cd(command, cwd):
    #append new stuff to path
    command_split = command.split()

    # cd by itslef should go back to document root
    if len(command_split) == 1:
        return root

    change = ' '.join(command.split(' ')[1:]) # remove the 'cd' from the command
    back_count = change.count('..') # ppl can go back more than one

    # if there is at least one .. then removve that many fromt he file path
    if back_count > 0:
        cwd_split = cwd.strip(slash)
        cwd_split = cwd_split.split(slash)
        change = slash.join(cwd_split[0:-back_count])
        cwd = slash + change + slash

    else:
        cwd += change + slash

    # cwd is the new path
    return cwd

# print current path
def print_path(command, cwd):
    command_split = command.split(' ')
    if command_split[0].upper() == ":path".upper():
        print(cwd)


def handle_errors(text):
    if "No such file or directory" in text:
        print ("No such file or directory" )
    elif "Permission denied" in text:
        print ("Permission denied")

    else:
        print("other error")

        with open('crash_report', 'w+')as report:
            report.write(text)
        print('crash report written')





# this function is used by both download and fdownload functions and is not callable directly by the main loop
# downloads a single file in path variable
def download_file(path):
        dest_path = './downloads/' + path.strip(root).replace('/..', '').replace('\\', '/') # strip root to avoid / or c: directories, replace .. to avoid path traversal and replace \ bc windows weird

        data = {
                "pass": str(hashed_password),
                "path": path
                }

        res = requests.post(url+'download', json=data)

        if len(res.text) < 100:
            print(res.text)

        # write file and make parent directories
        if not os.path.exists(os.path.dirname(dest_path)):
            try:
                os.makedirs(os.path.dirname(dest_path))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(dest_path, 'wb+')as outfile:
            outfile.write(res.content)



# prepares download of single file for download_file
def download(command):
    command_split = command.split(' ')
    if command_split[0].upper() == ':down'.upper():
        path = ' '.join(command_split[1:])
        download_file(path)


# downloads a folder of files one by one
def fdownload(dirpath):
    command_split = command.split(' ')
    if command_split[0].upper() == ':fdown'.upper():
        path = ' '.join(command_split[1:])
        data = {
                "pass": str(hashed_password),
                "path": path
                }

        res = requests.post(url+'list', json=data)
        files = json.loads(res.text)
        print(files)# returns list of files (not yet recursive)

        for element in files:
            try:
                download_file(element)
                print(f'{element} [succ]')
            except:
                print(f'{element} [fail]')




command = ''
while True:
    command_prev = command
    command = input(' >>> ')
    path = None

    # lets not send anything empty
    if len(command) == 0:
        continue

    # internal commands
    if command[0] == ':':
        # the functions determine weather its meant for them in order to not clutter up the main loop
        # this is a quick and dirty way of adding new functionality as well
        download(command)
        fdownload(command)
        print_path(command, cwd)
        continue

    #
    elif command.split(' ')[0] == 'cd':
        cwd = cd(command, cwd)
        print(cwd)
        command = listdir



    data = {
            "pass": str(hashed_password),
            "cwd": cwd,
            "com": command
            }

    res = requests.post(url+'send', json=data)

    try:
        out = json.loads(res.text)
        if out['returncode'] == "0":
            print(out['stdout'])
        else:
            print("stdout", out['stdout'])
            print("returncode:", out['returncode'])
            print("stderr:", out['stderr'])
    except:
        handle_errors(res.text)

