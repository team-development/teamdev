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
- Please use develop branch and pull request

## TODO:
 - Create list of bind mount points for docker and use a try block to make sure the user is not asking for a mount point that isnt allowed by default
 - If project already exists consider forcing rename of the project during creation. We don't want to delete the project or change one that has been already uploaded in the API
 -

kill $(ps aux | grep apiserver.py | awk '{ print $2 }')
