# Warning

All ips shown in this example are not updated, they are example ones.
Each time CogNet infrastructure is deployed different servers get new dynamic ips. There is an automatically updated list of those ips/hosts combination in [hosts](https://github.com/CogNet-5GPPP/demos_public/blob/master/hosts) file from demos_public repository.


## Navigation

[Hello World Docker][] | [Create docker folder][] | [Create python app][] | [Create policy][] | [Create a Docker that holds app and policy][] | [Create Docker file][] | [Create requitements file][] | [Upload project to github][] |
[Deploy on infrastructure][] | [Create ansible playbook file][] | [Create Jenkins project][] | [Prerequisites][] | [Build a Docker][] | [Run a Docker image][] | [Authors][] | [License][]

This folder will contain the Docker demos that can be deployed on CogNet infrastructure.

Each Docker files will be hold in different subfolders.

## Contents

This folder contains 4 examples of supported demos that could run into CogNet infrastructure:

* [demo_static](demo_static)
* [demo_with_params](demo_with_params)
* [demo_multiple_events_with_param_variables](demo_multiple_events_with_param_variables)

* [demo_complete](demo_complete)

### demo_static

This demo reads data from the input and executes an identity function as Machine Learning algorithm which triggers an event including each incoming value. The policy engine executes a predefined action when the condition is satisfied by the event value. Action parameters are static and declared at the definition stage.

### demo_with_params

This demo reads data from the input and executes an identity function as Machine Learning algorithm which triggers an event including each incoming value. The policy engine executes a predefined action when the condition is satisfied by the event value. Action parameters are variables declared at the definition stage. Those parameters are filled from metadata values of the fired event.

### demo_multiple_events_with_param_variables

This demo reads data from the input and executes an identity function as Machine Learning algorithm which triggers an event including each incoming value. This event is merged with other events. The policy engine executes a predefined action when the condition is satisfied by the value of the target event. Action parameters are variables declared at the definition stage. Those parameters are filled from metadata values of the different events.

### demo_complete

This demo includes all the necessary steps to test and evaluate data automatically for a specific time period.

---

***All these samples make the integration of the Machine Learning with the Kafka input and the Policy Engine output by means of creating a Docker and Asnsible playbooks with let automate the deployment of new systems on the Common Infrastructure from a code encapsulated in Github and deployed by a Jenkins platform.***

# Hello world Docker

Just following CogNet documentation:


Get demo example from [GitHub](demo_static)

**Please notice that file names are case sensitive**.



## Create docker folder

```
$ mkdir docker
```



## Create python app:

myapp.py:


```
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

# Read newpolicy.json
with open('newpolicy.json') as json_data:
    json_policy = json.load(json_data)

#Read topicName and conditionName from policy
topicName=json_policy['supa-policy']['supa-policy-target']['topicName']
conditionName=json_policy['supa-policy']['supa-policy-statement']['condition']['condition-name']

# To consume latest messages from metrics topic
groupId="%s%s"%(topicName,conditionName)
consumer = KafkaConsumer('metrics',bootstrap_servers=["kafka:9092"],group_id=groupId)

# To produce new messages to kafka
producer = KafkaProducer(bootstrap_servers=["kafka:9092"])


#Push new policy to Kafka
future = producer.send('newpolicy',json.dumps(json_policy))
print("coming")
# Receive messages from kafka metrics topic
for message in consumer:
                # do something with received messages
        #load each message as json data
        print("message")
        try:
            data = json.loads(message.value)

            #get type of metric of the message
            value_name=data['metric']['name']

            #check that that metric is the metric we need
            if value_name == "cpu.system_perc":

                #get metric value
                print("value")
                value_data=data['metric']['value']

                #set that value to the previous defined policy
                json_policy['supa-policy']['supa-policy-statement']['event']['event-value']=value_data

                #Send that policy as new measure to the listening topicName topic
                future = producer.send(topicName,json.dumps(json_policy))
            #else:
                #print("Not valid data")
        except ValueError:
            print "No valid data"
```

## Create policy

newpolicy.json:

```
{"supa-policy": {
                "supa-policy-validity-period": {
                        "start": "2016-12-20T08:42:57.527404Z"
                },
                "supa-policy-target": {
                        "domainName": "systemZ",
                        "subNetwork": "192.168.1.1",
                        "instanceName": ["devstack", "devstack2"],
                        "topicName": "demo1"
                },
                "supa-policy-statement": {
                        "event": {
                                "event-name": "cpu.user_perc",
                                "event-value-type": "float",
                                "event-value": "10.1",
                                "instanceName": ["compute1", "compute2"]

                        },
                        "condition": {
                                "condition-name": "cpu.user_perc_high",
                                "condition-operator": ">",
                                "condition-threshold": "20.1"
                        },
                        "action": {
                                "action-name": "cpu_performance",
                                "action-host": "http://host.com/",
                                "action-type": "deploy-topology",
                                "action-param":[ {
                                        "param-type": "topology",
                                        "param-value": "ring",
                                        "instanceName": ["compute1", "compute2"]
                                },{
                                        "param-type": "size",
                                        "param-value": "10",
                                        "instanceName": ["compute1", "compute2"]
                                }]
                        }
                }
        }
}

```

## Create a Docker that holds app and policy

There will be some intermediate steps

### Create Docker file

Dockerfile:


```
FROM python:2-onbuild

USER root


COPY myapp.py /src/myapp.py
CMD ["python","/src/myapp.py"]
```


### Create requirements file

requirements.txt:

```
kafka-python
```

## Upload project to github

Upload to [https://github.com/CogNet-5GPPP/demos_public/](https://github.com/CogNet-5GPPP/demos_public/) repository.

Upload to **demos/Dockers/** folder.


## Deploy on infrastructure


### Create ansible.yml playbook file

```
- name: clone and update github repository
  hosts: docker
  remote_user: "{{ansible_user}}"
  become: yes
  tasks:

    - name: clone github repository
      git:
        repo: git@github.com:CogNet-5GPPP/demos_public.git
        dest: /home/cognet/repo
        accept_hostkey: yes
        key_file: /home/cognet/rsa
        update: yes

- name: Build an image with the docker_image module
  hosts: docker
  remote_user: "{{ansible_user}}"
  become: yes
  tasks:

    - name: python dependencies
      pip: name={{item}} version=1.9.0
      with_items:

      - docker-py

    - name: build the image
      docker_image: >
        name=mydemo
        tag=ontheedge
        path=/home/cognet/repo/demos/Dockers/demo
        state=present
        api_version=1.18
        force=true
- name: Create a data container
  hosts: docker
  remote_user: "{{ansible_user}}"
  become: yes
  vars:
    hosts_ip: "{ \"spark_master\":\"{{ hostvars.spark_master.ansible_ssh_host }}\",\"spark_slaves1\":\"{{ hostvars.spark_slaves1.ansible_ssh_host }}\", \"spark_slaves2\":\"{{ hostvars.spark_slaves2.ansible_ssh_host }}\", \"oscon\":\"{{ hostvars.oscon.ansible_ssh_host }}\",\"odl\":\"{{ hostvars.odl.ansible_ssh_host }}\",\"monasca\":\"{{ hostvars.monasca.ansible_ssh_host }}\",\"docker\":\"{{ hostvars.docker.ansible_ssh_host }}\",\"kafka\":\"{{ hostvars.kafka.ansible_ssh_host }}\",\"policy\":\"{{ hostvars.policy.ansible_ssh_host }}\"}"
  tasks:
    - name: Remove container
      docker_container:
        name: mydocker
        image: "mydemo:ontheedge"
        state: absent
    - name: Create Container
      docker_container:
        name: mydocker
        image: "mydemo:ontheedge"
        state: started
        etc_hosts: "{{ hosts_ip }}"
```

_**Please use lowercase for all the strings modified for your specific demo, including docker_image name and tag, docker_container name and image. In the examples "mydemo", "ontheedge", "mydocker" and consequently "mydemo:ontheedge"**_

### Upload ansible file to github

### Create Jenkins project


* Go to your Jenkins installation
* New Item (Freestyle project)
* Select Git as *Source code Management*
* Add Git repository (https://github.com/CogNet-5GPPP/demos_public/)
* Set GitHub Project credentials
* Select build steps and add Invoke Ansible Playbook
* Set relative playbook file (ansible.yml) path from github
* Add **/var/lib/jenkins/workspace/CogNet_RackSpace_Infrastructure_Deploy/scripts/setup/ansible/inventory** as *Inventory File* 
* Save

### Run Jenkins Project



# Environment

We are going to create the Docker in our development machine and the deploy that Docker on the *docker* virtual machine that belongs to *Cognet* architecture.

## Prerequisites

The prerequisites to build a Docker in our development machine (we supose that we are running a Ubuntu 16.04) are well explained on [Install Docker on Ubuntu](https://docs.docker.com/engine/installation/linux/ubuntulinux/) but we will have a small summary on this document:

Install dependencies and certificates
    
``` 
$ sudo apt-get update
$ sudo apt-get install apt-transport-https ca-certificates
```    

Add GPG key
    
```    
$ sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
```
    

Add *docker.io* repository
    
```    
$ echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
```    

Update repositories
    
```    
$ sudo apt-get update
```    

Install recomended packages
    
```    
$ sudo apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual
```    

Install docker

```    
$ sudo apt-get install docker-engine
```    

Start docker daemon
    
```    
$ sudo service docker start
```    

To check if docker is correctly working we could do
    
```    
$ sudo docker run hello-world
```    


# Build a Docker

We have to enter in the Docker folder that we want to build and execute:

```  
$sudo docker build -t mydocker:mytag .
```    

It will take some minutes to end. After this we can launch our docker and check if it is working ok.

# Run a Docker image
    
```    
$ sudo docker run -it --add-host kafka:162.13.119.237 monasca:162.13.119.239 mydocker:mytag
```    

The --add-host parameter will let us to add a dupla "ip hostname" to our Docker image at init time. We have to fill this command with kafka and monasca ip addresses.

If we have those elements on our development machine "/etc/hosts" file we can launch our Docker image in a different way that will let us to read those data automatically and add it automatically to our Docker image:
    
```    
sudo docker run -i --add-host kafka:`cat /etc/hosts | grep kafka | awk '{print $1}'` monasca:`cat /etc/hosts | grep monasca | awk '{print $1}'` mydocker:mytag
```

### Authors


- Angel Martin (amartin@vicomtech.org)
- Felipe Mogollon (fmogollon@vicomtech.org)

### License


Copyright 2016 Vicomtech.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.


[Hello World Docker]: #hello-world-docker
[Create docker folder]: #create-docker-folder
[Create python app]: #create-python-app
[Create policy]: #create-policy
[Create a Docker that holds app and policy]: #create-a-docker-that-holds-app-and-policy
[Create Docker file]: #create-docker-file
[Create requitements file]: #create-requirements-file
[Upload project to github]: #upload-project-to-github
[Deploy on infrastructure]: #deploy-on-infrastructure
[Create ansible playbook file]: #create-ansibleyml-playbook-file
[Create Jenkins project]: #create-jenkins-project
[Prerequisites]: #prerequisites
[Build a Docker]: #goals
[Run a Docker image]: #run-a-docker-image
[Authors]: #authors
[License]: #license
