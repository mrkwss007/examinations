#!/usr/bin/env python

import subprocess
import pathlib
import os
import sys
import platform
import argparse
import re

GIT_CMD="git"

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = pathlib.Path(newPath).expanduser().resolve()

    def __enter__(self):
        self.savedPath = pathlib.Path.cwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def updateGit( url, branch,  root ):
    dirStart = url.rfind("/")    
    dirname=url[dirStart+1:-4]

    with cd( root ):
        p = pathlib.Path( dirname )
        if ( branch ):
            bs = " --branch " + branch
        else:
            bs = ""
        if not p.is_dir():
            print("cloning {0} from url {1} root {2}".format( dirname, url, root ), 'git command', GIT_CMD)
                
            cmd = GIT_CMD + " clone " + bs + " " + url + " " + dirname 
            os.system( cmd )
        else:
            print("git directory exists")

        with cd( dirname ):
            print("Executing git pull")
            o = None
            try:
                o = subprocess.check_output(GIT_CMD + " pull", shell=True)
            except subprocess.CalledProcessError:
                pass
            if ( o ):
                print( 'git pull:' + o.decode('utf-8') )

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Clone or pull a directory from github")
    parser.add_argument( "url", type=str, help="url of the repository")
    parser.add_argument("--branch", default="master", type=str, help="branch [master]" )
    parser.add_argument( "--root", default=".", type=str, help="root of the filesystem" )
    args = parser.parse_args()
    updateGit(args.url, args.branch, args.root)
