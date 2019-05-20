#!/usr/bin/env python3

from ruamel.yaml import YAML
import sys
import os

current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r"osdp/configuration")




inp = """\
                # Open Source Development Platform
                osdp:
                  # details
                  linux: amazon   # So we can develop AWS Lambda with same python version
                  username: james-knott
                  password: mypassword
                  project: company
                  configs: https://github.com/james-knott/configuration.git
                  platform: docker # Currently supported docker and vagrant
                  runtime: python3.6
                  dockerhubusername: buildmystartup
                  dockerhubpassword: mypassword
                  imagename: buildmystartup/ghettolabs
                  pushto: ghettolabs/python
                  dockerdeveloperimage: buildmystartup/ghettolabs:python3.6
                  dockerhome: /home
                """
def create_configs(inp):
    yaml = YAML()
    code = yaml.load(inp)
    yaml.dump(code, sys.stdout)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    with open('osdp/configuration/settings.yml', "w") as f:
        yaml.dump(code, f)

create_configs(inp)



