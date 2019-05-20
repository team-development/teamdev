from git import RemoteProgress
import os
from pathlib import Path
import teamdev
import vagrant
import backups
import git
from git import Repo
from git import RemoteProgress
from ruamel.yaml import YAML
import requests
import sys
from subprocess import check_output, PIPE, Popen
import subprocess
import docker
import dockerpty
import messages

class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "Downloading....")



class OSDPBase(object):

    def __init__(self):
        self.current_directory = os.getcwd()
        self.final_directory = os.path.join(self.current_directory, r"osdp/configuration")
        self.directory = 'osdp'
        self.secret_code = ''
        self.encoded_key = ''
        self.linux = ['ubuntu', 'centos', 'debian', 'amazon', 'dcos-vagrant', 'xenial', 'docker', 'amazonlinux', 'docker-lambda']
        self.logger = teamdev.setup_logging()
        self.REMOTE_SERVER = "www.github.com"
        self.introbanner = ""
        self.OSDPAPI = "http://127.0.0.1:8080"
        self.intro()
    def init(self):
        self.intro()
        if teamdev.is_connected(self.REMOTE_SERVER):
            try:
                if not os.path.exists(self.final_directory):
                    os.makedirs(self.final_directory)
                Repo.clone_from('https://github.com/james-knott/configuration.git', self.final_directory , branch="master", progress=MyProgressPrinter())
                self.logger.info("Downloaded the settings.yml file. Go to osdp/configuration/settings.yml to customize your environment!")
            except git.exc.GitCommandError as e:
                self.logger.info("Could not clone the repo. Folder may exist.!")
                if os.path.isfile('osdp/configuration/settings.yml'):
                    self.logger.info("Found the settings.yml file. It has already been downloaded!")
                    self.logger.info("Run with the --clean command to get original configs or remove osdp/configuration/settings.yml and re- --init")
                else:
                    self.logger.info("Could not connect to Github to download the settings.yml file. Creating Dynamically!")
                    inp = """\
                    # Open Source Development Platform
                    osdp:
                      # details
                      linux: amazon   # So we can develop AWS Lambda with same python version
                      username: jknott
                      project: company
                      configs: https://github.com/james-knott/configuration.git
                      platform: docker # Currently supported docker and vagrant
                      runtime: python3.6
                      dockerhubusername: buildmystartup
                      dockerhubpassword: mypassword
                      imagename: buildmystartup/ghettolabs
                      pushto: ghettolabs/python
                      dockerdeveloperimage: buildmystartup/ghettolabs:python3.6
                    """
                    yaml = YAML()
                    code = yaml.load(inp)
                    #yaml.dump(code, sys.stdout) test what they dynamic file looks like
                    self.logger("Your new project name is", code['osdp']['project'])
                    if not os.path.exists(self.final_directory):
                        os.makedirs(self.final_directory)
                    with open('osdp/configuration/settings.yml', "w") as f:
                        yaml.dump(code, f)
        else:
            print("Network connection is down")


    def new(self):
        try:
            if not os.path.isfile('osdp/configuration/settings.yml'):
                print("You ran new before init so let me grab the files for you")
                self.init()
                sys.exit(1)
        except:
            pass

        dataMap = self.get_settings()
        current_directory = os.getcwd()
        data_folder = Path("osdp")
        if dataMap['osdp']['platform'] == 'vagrant':
            file_to_open = data_folder / "projects" / dataMap['osdp']['project'] / "vagrant"
            final_directory = os.path.join(current_directory, file_to_open)
        elif dataMap['osdp']['platform'] == 'docker':
            file_to_open = data_folder / "projects" / dataMap['osdp']['project'] / "docker"
            final_directory = os.path.join(current_directory, file_to_open)
        if os.path.exists(final_directory):
            self.logger.info("A project with that name already exists!")
            try:
                self.get_project_from_db(dataMap['osdp']['project'])
            except:
                self.logger.info("This settings file has not been pushed to the api yet")
            #self.backups.backup()
            try:
                shutil.rmtree(final_directory, onerror=onerror)
                self.logger.info("The folder has been removed.!")
            except:
                self.logger.info("The folder could  not be removed.!")
        else:
            os.makedirs(final_directory)
        if dataMap['osdp']['linux'] not in self.linux:
            self.logger.info("The linux distro you selected is not supported yet!")
            self.logger.info("Go back into the settings.yml file and assign the linux key: ubuntu, centos, amazon, debian, dcos-vagrant !")
            sys.exit(1)
        url = "https://github.com/james-knott/" + dataMap['osdp']['linux'] + ".git"
        self.logger.info("Downloading project files!")
        try:
            Repo.clone_from(url, final_directory , branch="master")
        except:
            self.logger.info("The folder already exists with that project name. Try python3 osdpv2 --start projectname")
            sys.exit(1)
        try:
            print(dataMap)
            self.save_to_db(dataMap)
        except:
            self.logger.info("Could not save to db through api")
        self.get_project_from_db(dataMap['osdp']['project'])
        if dataMap['osdp']['platform'] == 'docker':
            IMG_SRC = dataMap['osdp']['dockerdeveloperimage']
            client = docker.Client()
            client.login(username=dataMap['osdp']['dockerhubusername'], password=dataMap['osdp']['dockerhubpassword'], registry="https://index.docker.io/v1/")
            client.pull(IMG_SRC)
            client.tag(image=dataMap['osdp']['dockerdeveloperimage'], repository=dataMap['osdp']['pushto'],tag=dataMap['osdp']['runtime'])
        messages.send_message(dataMap['osdp']['username'] + " " +  "Just created a new" + " " + dataMap['osdp']['platform'] + " " +  "Development Environment")

    def zipfolder(self):
        dt = datetime.datetime.now()
        datestring = dt.strftime('%m/%d/%Y')
        foldername = "osdpbackup"
        target_dir = os.getcwd()
        zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
        rootlen = len(target_dir) + 1
        for base, dirs, files in os.walk(target_dir):
            for file in files:
                fn = os.path.join(base, file)
                zipobj.write(fn, fn[rootlen:])


    def start(self, projectname):
        dataMap = self.get_settings()
        current_directory = os.getcwd()
        data_folder = Path("osdp")
        file_to_open = data_folder / "projects" / dataMap['osdp']['project'] / dataMap['osdp']['platform']
        final_directory = os.path.join(current_directory, file_to_open)
        if not os.path.exists(final_directory):
            print("This should have already been created")
            exit()
        if dataMap['osdp']['platform'] == 'vagrant':
            messages.send_message(dataMap['osdp']['username'] + " " + "Just started a vagrant box for Python Development")
            vagrant_folder = Path(final_directory)
            v = vagrant.Vagrant(vagrant_folder, quiet_stdout=False)
            try:
                v.up()
            except Exception as e:
                pass
            os.chdir(vagrant_folder)
            cmdCommand = "vagrant port"
            process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(output)
            subprocess.run(["vagrant","ssh"])
        elif dataMap['osdp']['platform'] == 'docker':
            print("Ths platform is docker and we will connect to the image")
            os.chdir(final_directory)
            retval = os.getcwd()
            IMG_SRC = dataMap['osdp']['dockerdeveloperimage']
            client = docker.Client()
            # Uncomment if working with a private image
            #client.login(username=dataMap['osdp']['dockerhubusername'], password=dataMap['osdp']['dockerhubpassword'], registry="https://index.docker.io/v1/")
            client.pull(IMG_SRC)
            #client.tag(image=dataMap['osdp']['dockerdeveloperimage'], repository=dataMap['osdp']['pushto'],tag=dataMap['osdp']['runtime'])
            #response = [line for line in client.push(dataMap['osdp']['pushto'] + ":" + dataMap['osdp']['runtime'], stream=True)]
            container_id = client.create_container(dataMap['osdp']['imagename'],stdin_open=True,tty=True,command='/bin/bash', volumes=dataMap['osdp']['dockerhome'],host_config=client.create_host_config \
            # Need to adjust this for mac users - change /Users to /home
            (binds=['/Users:/home',]))
            dockerpty.start(client, container_id)

    def stop(self, projectname):
        dataMap = self.get_settings()
        current_directory = os.getcwd()
        data_folder = Path("osdp")
        file_to_open = data_folder / "projects" / projectname / "vagrant"
        final_directory = os.path.join(current_directory, file_to_open)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
        vagrant_folder = Path(final_directory)
        v = vagrant.Vagrant(vagrant_folder, quiet_stdout=False)
        v.halt()

    def update(self):
        self.new()


    def destroy(self, projectname):
        dataMap = self.get_settings()
        current_directory = os.getcwd()
        data_folder = Path("osdp")
        file_to_open = data_folder / "projects" / projectname / "vagrant"
        final_directory = os.path.join(current_directory, file_to_open)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
        vagrant_folder = Path(final_directory)
        v = vagrant.Vagrant(vagrant_folder, quiet_stdout=False)
        v.destroy()

    def get_settings(self):
        yaml = YAML()
        if os.path.isfile('osdp/configuration/settings.yml'):
            with open(r"osdp/configuration/settings.yml") as f:
                dataMap = yaml.load(f)
                #self.save_to_db(dataMap)
                return dataMap
        else:
            self.logger.info("Could not find settings file. Downloading new copy. Please edit then run osdp --new again!")
            self.init()

    def save_to_db(self, settings):
        payload = {
        "platform": settings['osdp']['platform'],
        "linux": settings['osdp']['linux'],
        "username": settings['osdp']['username'],
        "password": settings['osdp']['password'],
        "project": settings['osdp']['project'],
        "github": "https://github.com/" + settings['osdp']['username'] + "/" + settings['osdp']['linux'] + ".git",
        "dockerhubusername": settings['osdp']['dockerhubusername'],
        "dockerhubpassword": settings['osdp']['dockerhubpassword'],
        "imagename": settings['osdp']['imagename'],
        "dockerhome": settings['osdp']['dockerhome'],
        "configs": settings['osdp']['configs']
        }
        ENDPOINT = self.OSDPAPI + "/project/" + settings['osdp']['project']
        response = requests.post(ENDPOINT, json=payload)
        print(response)
        self.logger.info("Saved to API")

    def get_project_from_db(self, project):
        ENDPOINT = self.OSDPAPI + "/project/" + project
        response = requests.get(ENDPOINT)
        oneproject = response.json()
        print("Dumping API project to screen so you can verify the contents")
        print("\n\n\n\n")
        print(oneproject)
        print("\n\n\n\n")
        print("Now you can start your project by typing" + "./teamdev.py --start " + oneproject['project']['name'])

    def intro(self):
        self.introbanner = """


 .----------------.  .----------------.  .----------------.  .----------------.
| .--------------. || .--------------. || .--------------. || .--------------. |
| |     ____     | || |    _______   | || |  ________    | || |   ______     | |
| |   .'    `.   | || |   /  ___  |  | || | |_   ___ `.  | || |  |_   __ \   | |
| |  /  .--.  \  | || |  |  (__ \_|  | || |   | |   `. \ | || |    | |__) |  | |
| |  | |    | |  | || |   '.___`-.   | || |   | |    | | | || |    |  ___/   | |
| |  \  `--'  /  | || |  |`\____) |  | || |  _| |___.' / | || |   _| |_      | |
| |   `.____.'   | || |  |_______.'  | || | |________.'  | || |  |_____|     | |
| |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'

For local usage you must start the server first. python3 teamdev.py --server
For team usage your server is already running but you must edit the OSDPAPI server URL so that your team can connect.
Go into messages.py and set your slack bot token if you want slack notifications.

1. Type python3 teamdev.py --init to bring down config file. Then edit config file to your needs.
2. Type python3 teamdev.py --new to use the new config file and pull down the artifacts.
3. Type python3 teamdev.py --start "projectname" to bring up the virtualbox or docker environment.

"""
        print(self.introbanner)

    def list(self):
        ENDPOINT = self.OSDPAPI + "/projects"
        response = requests.get(ENDPOINT)
        allprojects = response.json()
        for k, v in allprojects.items():
            for index in range(0, len(v)):
                print(k,v[index])
                print("\n\n\n\n")
    def add(self, project):
        try:
            if not os.path.isfile('osdp/configuration/settings.yml'):
                self.init()
        except:
            pass

        inp = """\
                # Open Source Development Platform
                osdp:
                  # details
                  linux: amazon   # So we can develop AWS Lambda with same python version
                  username: james-knott
                  password: mypassword
                  project: company
                  platform: docker # Currently supported docker and vagrant
                  runtime: python3.6
                  configs: https://github.com/james-knott/configuration.git
                  dockerhubusername: buildmystartup
                  dockerhubpassword: mypassword
                  imagename: buildmystartup/ghettolabs
                  pushto: ghettolabs/python
                  dockerdeveloperimage: buildmystartup/ghettolabs:python3.6
                  dockerhome: /home
                """
        ENDPOINT = self.OSDPAPI + "/project/" + project
        response = requests.get(ENDPOINT)
        oneproject = response.json()
        name = oneproject['project']['name']
        platform = oneproject['project']['platform']
        linux = oneproject['project']['linux']
        username = oneproject['project']['username']
        configs = oneproject['project']['configs']
        password = oneproject['project']['password']
        project = oneproject['project']['project']
        github = oneproject['project']['github']
        dockerhubusername = oneproject['project']['dockerhubusername']
        dockerhubpassword = oneproject['project']['dockerhubpassword']
        imagename = oneproject['project']['imagename']
        dockerhome = oneproject['project']['dockerhome']
        yaml = YAML()
        dataMap = yaml.load(inp)
        dataMap['osdp']['name'] = name
        dataMap['osdp']['linux'] = linux
        dataMap['osdp']['username'] = username
        dataMap['osdp']['password'] = password
        dataMap['osdp']['project'] = project
        dataMap['osdp']['configs'] = configs
        dataMap['osdp']['platform'] = platform
        dataMap['osdp']['dockerhubusername'] = dockerhubusername
        dataMap['osdp']['dockerhubpassword'] = dockerhubpassword
        dataMap['osdp']['github'] = github
        dataMap['osdp']['imagename'] = imagename
        dataMap['osdp']['dockerhome'] = dockerhome
        with open('osdp/configuration/settings.yml', "w") as f:
            yaml.dump(dataMap, f)

