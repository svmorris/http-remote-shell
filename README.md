# simple python remote shell
This is a python implementation of a server that offers a shell and a way to download files

### why?
Have you ever created a one-line reverse shell and ended up relying on it for 2 years, but don't want to install ssh because the sysadmins might find it suspicious. Probably not, but i had this problem so i built this shell.

### what it's not for:
This is not meant to replace ssh in any way, it's just a small improvement for longer operations or shells that want to be less obvious than ssh, telnet, or anything else.

### implementation
TL;DR: flask web server, with a python requests based client to interface with it

###### server
flask based web server
the webserver has 2 main functions:
- command
    - executes a command on the server
    - post method
    - arguments
        - password (hashed of course)
        - command (a command to execute)
        - path (where to execute command) 

- download
    - downloads a file from the server
    - post method
    - arguments:
        - password (hashed of course)
        - path (path to file)


###### client
uses python requests to communicate to the server




### features:
- a shell that works on both windows and linux hosts
- downloading folders and files
- connectionless [ no worries about losing connection and having to reconnect ]
- a (potentially)false feeling of security

### problems:
- no encryption [yet, dont worry passwords are passed hashed so password stealing **should** not be an issue]
- time constraints caused bugs and potential security issues [ feel free to pull request bugs ]
- connectionless [ yes you have to reconnect each time ]
- DEPENDENCIES (lots of them):
    - server: python >3.6, python3-flask, python3-bcrypt
    - client: python >3.6, python3-requests, python3-hashlib


## usage:
### client
###### launching
```
python client.py host_os <address> <port>
```
* host\_os: operating system of the server
    - this is needed for things like `/ vs c:\`

* address(optional): address of the server
    - if you don't give one here it will ask you later

* port: what port it should connect on
    - default (if blank) is `42068`

###### commands
commands are prefixed with `:`
* :down  -- download one file
* :fdown -- download one folder
    - both downloads **need a full path to the file**
    - both downloads will save to the downloads(w+) folder

* :path -- prints your current path
    - here to assist with downloading files


###### other things to keep in mind
* cd
    - is handled by the client so might be a bit different then normal
    - when cd is sent with no arguments it will go back to root
    - when cd-ing into an invalid path you have to `cd ..` -- sorry

* command output or errors will only be shown after the process has terminated
    - all the fun of http/1

* commands that hang wont work
these include programs like: 
    - vim ( or any other text editor )
    - [h]top
    - ssh


