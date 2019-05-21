## Features
- Manages mutiple vagrant environments
- YAML config file. 
- Library of working Vagrantfiles
- Automatic project backup to S3
- Manages Docker environments
- Server only mode with REST API

## Requirements
- virtualbox 5.x
- vagrant >1.8.4
- Python 3.x
- Install requirements_osdp.txt
- amazon aws account (For S3 backups) 
- sudo apt-get install python3-distutils for docker to work. (if not on Ubuntu 19.04)


## How to use
- download latest version (Clone or Download Zip) 
- Install requirements_osdp.txt
- python3 osdpv2.py --init (Downloads template.yml file to get started)
- Edit the file osdp/template.yml and add your company name, project name, version of linux. Currently (ubuntu, xenial, docker, amazon, dcos_vagrant)
- The server mode needs to be enabled by using --server in order to work for local mode
- For Team mode a server in the cloud or wherever has to be running for team mode
- python3 osdpv2.py --new (This downloads the vagrantfile for you from this repo)
- python3 osdpv2.py --start company (company works well for me but can be any name or project you put under project in yaml file) At the end it spits out port number.
- Connect with your favorite ssh client or navigate to project/company/vagrant and do a vagrant ssh
- When your done with the project or no longer want the vagrant environment just do osdpv3.py --destroy


## Developers
- Please use developer branch and pull request

## TODO:

- Move start stop and destroy to one method.
- Add custom exceptions and assert. Basic testing.
- Add Dropbox sync
- clean up all os file system checks
- General refactor of all code to make pretty and perform better.
- Add state machine so that the application always knows what has been started.
- Make plugin system so users can add Vagrantfiles or profiles.
- Make it so the application can automatically pull from ansible-galaxy
- Create a mode that creates an environment in the background like virtualenv but at a vagrant scale.

kill $(ps aux | grep teamdev.py | awk '{ print $2 }')
