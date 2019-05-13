#!/usr/bin/env python3

import logging
import sys
import argparse
import commands
import socket
from pathlib import Path
from subprocess import Popen,PIPE





REMOTE_SERVER = "www.github.com"

def setup_logging():
 logger = logging.getLogger()
 for h in logger.handlers:
     logger.removeHandler(h)
 h = logging.StreamHandler(sys.stdout)
 FORMAT = "[%(levelname)s %(asctime)s %(filename)s:%(lineno)s - %(funcName)21s() ] %(message)s"
 h.setFormatter(logging.Formatter(FORMAT))
 logger.addHandler(h)
 logger.setLevel(logging.INFO)
 return logger

def is_connected(REMOTE_SERVER):
 try:
     host = socket.gethostbyname(REMOTE_SERVER)
     s = socket.create_connection((host, 80), 2)
     print("Here is the ip address the server is running on {} ".format([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] \
     if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]))
     return True
 except:
     print("Not connected to the internet")
 return False


def setup_folder_structure():
    path = Path('backups')
    path.mkdir(exist_ok=True)



if __name__ == "__main__":
 logger = setup_logging() # sets up logging
 logger.info("Welcome to Open Source Development Platform!")
 is_connected(REMOTE_SERVER) # checks to see if connected to the internet
 setup_folder_structure()
 test = commands.OSDPBase()

 # sets up command line arguments
 parser = argparse.ArgumentParser(description='Open Source Development Platform')
 parser.add_argument("--init","-i", required=False, dest='init',action='store_true',help='Initialize new project folder')
 parser.add_argument("--new","-n", required=False, dest='new',action='store_true',help='Create new project from template file')
 parser.add_argument("--update","-u", required=False, dest='update',action='store_true',help='Update settings')
 parser.add_argument("--backup","-b", required=False,dest='backup',action='store',help='Sync project to backup device')
 parser.add_argument("--destroy","-e", required=False,dest='destroy',action='store',help='Delete project from folder')
 parser.add_argument("--start","-s", required=False,dest='start',action='store',help='Start services')
 parser.add_argument("--stop","-d", required=False,dest='stop',action='store',help='Stop services')
 parser.add_argument("--clean","-c", required=False,dest='clean',action='store_true',help='Generates clean config file')
 # run in server mode only
 parser.add_argument("--server","-p", required=False,dest='server',action='store_true',help='Start server mode')
 result = parser.parse_args()

 if result.init:
     logger.info("Pulling down yaml file so you can customize your environment!")
     test.init()
 elif result.new:
     test.new()
 elif result.update:
     test.update()
 elif result.backup:
     logger.info("We are backing up all your projects to S3!")
     test.backup()
 elif result.destroy:
     project = result.destroy
     logger.info("We are destroying your vagrant box now!")
     test.destroy(projectname=project)
 elif result.start:
     project = result.start
     logger.info("We are starting your development environment now!")
     test.start(projectname=project)
 elif result.stop:
     project = result.stop
     logger.info("We are stopping your vagrant box now!")
     test.stop(projectname=project)
 elif result.clean:
     Popen(["python3","configs.py"])
 elif result.server:
     Popen(["python3","apiserver.py"], stdout=PIPE)


