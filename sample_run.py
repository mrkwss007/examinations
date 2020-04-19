#!/usr/bin/env python3

import pathlib
import platform
import sys
import subprocess
import os
import json

GIT_CMD = "git"

class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = pathlib.Path(newPath).expanduser().resolve()

    def __enter__(self):
        self.savedPath = pathlib.Path.cwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def updateGit(url, branch, root):
    dirStart = url.rfind("/")
    dirname = url[dirStart + 1:-4]

    with cd(root):
        p = pathlib.Path(dirname)
        if (branch):
            bs = " --branch " + branch
        else:
            bs = ""
        if not p.is_dir():
            print("cloning {0} from url {1} root {2}".format(dirname, url, root), 'git command', GIT_CMD)

            cmd = GIT_CMD + " clone " + bs + " " + url + " " + dirname
            os.system(cmd)
        else:
            print("git directory exists")

        with cd(dirname):
            print("Executing git pull")
            o = None
            try:
                o = subprocess.check_output(GIT_CMD + " pull", shell=True)
            except subprocess.CalledProcessError:
                pass
            if (o):
                print('git pull:' + o.decode('utf-8'))


f = pathlib.Path(__file__)
d = f.parent.resolve()

COURSE, EXAMTYPE, UNIVERSITY, YEAR = d.name.split(' - ')

HOME = pathlib.Path.home()

EXAMTITLE = " - ".join([COURSE, EXAMTYPE, UNIVERSITY, YEAR])

# EXAMDIR = pathlib.Path("/usr/local/") / "examinations"
EXAMDIR = pathlib.Path(".") / "examinations"
ROOTDIR = pathlib.Path(".")
updateGit("http://www.github.com/mrkwss007/examinations.git", "master", EXAMDIR.parent )

TEMPLATE = EXAMDIR / 'Templates'
CODEDIR = ROOTDIR / 'Code'

print('EXAMDIR', EXAMDIR, 'EXAMTITLE', EXAMTITLE, 'TEMPLATE', TEMPLATE)

PARENT = pathlib.Path("..")

values = {
    'university': UNIVERSITY,
    'coursetitle': COURSE,
    'examtype': EXAMTYPE,
    'examiners': "包傑奇",  # "Jacky Baltes",
    'date': "Monday, 6th January 2020",
    'time': "9:30 - 12:30",
    'room': "NTNU TA412",
    'note': """
Attempt all questions.<br>
Show your work to receive full marks.<br>
This is an <b>open book/open internet</b> examination. You are allowed to use any printed material, your computer, and the Internet.<br>
You are <b>not</b> allowed to use any form of communication including talking to your class mates, mobile phones, Facebook, email, instant messenger, and similar systems.<br>
Use of communication in any form will lead to <b>immediate</b> disqualification.<br>
Some of the questions may not be solvable, that is it may be impossible to calculate the requested information. In this case, say so in your answer and explain why.<br>
"""
}

cmd = [sys.executable,
       str(EXAMDIR / 'create_exam.py'),
       '-v',
       '-v',
       str(EXAMTITLE) + '.py',
       '--template_dir', str(TEMPLATE),
       '--resource_dir', str(ROOTDIR / 'Code'),
       '--resource_dir', str(PARENT / 'Code'),
       '--resource_dir', str(ROOTDIR / 'Questions'),
       '--resource_dir', str(PARENT / 'Questions'),
       '--styles', str(TEMPLATE / 'exam_template.css'),
       '--values', json.dumps(values)
       ]

print('Executing command', cmd)
subprocess.call(cmd)
