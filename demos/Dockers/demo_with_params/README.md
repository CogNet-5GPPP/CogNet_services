This tutorial will describe the way to deploy a Docker that contains policy with multiple action params whose values are described by variables that will be filled from event data in execution time.

# Warning

All ips shown in this example are not updated, they are example ones.
Each time CogNet infrastructure is deployed different servers get new dynamic ips. There is an automatically updated list of those ips/hosts combination in [hosts](https://github.com/CogNet-5GPPP/demos_public/blob/master/hosts) file from demos_public repository.

# Content

There are several files whithin this tutorial:

* policy.json -> The policy that is going to be pushed
* push_policy.py -> A python script that will push the policy and will it with random measures
* Dockerfile -> The file that describes the Docker
* requirements.txt -> contains the python pip modules that will be installed in the Docker image
* ansible.yml -> The file that will describe the way the Docker will be deployed

# Github destination

For simplicity reasons we have opted to deploy all the content from this tutorial in the same github folder.


# Deploying a policy into *CogNet* infrastructure

The steps to deploy a policy into *CogNet* infrastructure will be:

1. [Create a policy ](#the-policy)
2. [Create an application that read that policy and pushes events to kafka](#the-pushing-python-application)
3. Upload content to github
4. Create a Docker
    1. [Create Docker file](#create-a-dockerfile)
    2. Create requeriments.txt
5. Upload Dockerfile and requeriments.txt to github    
6. [Create ansible file to deploy the docker](#ansibleyml-playbook-file)
7. Upload ansible.yml to github
8. [Create a Jenkins project](#create-jenkins-project)
9. Execute Jenkins project  


# The policy

First step will be to define a new policy, then you can see an example of a policy.json file:

```
{"supa-policy": {
                "supa-policy-validity-period": {
                        "start": "2016-12-20T08:42:57.527404Z"
                },
                "supa-policy-target": {
                        "domainName": "systemZ",
                        "subNetwork": "192.168.1.1",
                        "instanceName": ["devstack", "devstack2"],
                        "topicName": "developmentvicomtech"

                },
                "supa-policy-statement": {
                        "event": {
                                "event-name": "test_event",
                                "event-value-type": "float",
                                "event-value": "0.0",
                                "instanceName": [""]
                        },
                        "condition": {
                                "condition-name": "test_event.multipolicy1",
                                "condition-operator": ">",
                                "condition-threshold": "0"
                        },
                        "action": {
                                "action-name": "reroute_vnf",
                                "action-host": "http://192.168.10.9:8080",
                                "action-type": "test-action",
                                "action-param":[ {
                                        "param-type": "topology",
                                        "param-value": "10",
                                        "instanceName": ["1","2"]
                                 },{
                                        "param-type": "topology2",
                                        "param-value": "$event-value",
                                        "instanceName": ["$instanceName"]
                                 }]
                        }
                }
        }
}
```

The policy contains several elements, but the main ones are:

* event
* condition
* action

## event

This policy contains only one event. The structure of an event is:

* event-name -> a string
* event-value-type -> a string containing the type of the value: supported types are: int, float, char (for strings)
* event-value -> a string containing the value of the event. This string will be treated by Policy Manager as defined on *event-value-type*
* instanceName -> an array of strings containing the elements that had produced the event

## condition

Is the condition that must be met by the event to execute the action. It is composed by:

* condition-name -> an explanatory string that contains the name of the event that is going to be evaluated
* condition-operator -> a string containing on of the following valid operators (>,<,==,!=)
* condition-threshold -> the threshold that will be evaluated against the corresponding *event-value*

## action

The action that will be performed if the event meets the condition.

* action-name: A descriptive string with the name of the action
* action-host: A string containing the host where *action-params* will be pushed through a **POST** request. If blank the action params will be pushed to kafka *topicName*
* action-type: a string containing the type of action
* action-param: an array containing the different params that will be pushed

*action-param* structure is:

* param-type: the type of used param
* param-value: The value of the pushed param. Can be a variable
* instance-name: An array containing the instances that will be affected by the action. Can be a variable. If it is a variable it must be also an array of an unique variable, if not, system wont work.


### action-param variables

Action param variables will search for the field from the event to be read in order to fill the param variable value, for example:

*$event-value*

will be substituted by *Policy Manager* by the value of *event-value* from the event each time a new policy event is being pushed to *topicName*



## Some notes about policy creation

If a multiple events policy is created, when pushed, it must be multiple events policy, otherwise system wont work.

# The pushing python application

As we don't have yet any *real* values to be pushed into the policy we have modified our pushing example python script to push random generated values to get some kind of valid data into the policy engine. This operation will be performed by *push_policy.py* script.

Working:

1. Read policy.json and push it to *newpolicy* topic
2. Listen for kafka events. When a new event is comming generate a random value.
3. Create a new policy with that generated values.
4. Push new policy to *topicName* from *policy.json* 
5. Goto 2

```
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time

# Read newpolicy.json
with open('policy.json') as json_data:
    json_policy = json.load(json_data)

#Read topicName and conditionName from policy
topicName=json_policy['supa-policy']['supa-policy-target']['topicName']
conditionName=json_policy['supa-policy']['supa-policy-statement']['condition']['condition-name']
print(topicName)
print(conditionName)
# To consume latest messages from metrics topic
groupId="%s%s"%(topicName,conditionName)
consumer = KafkaConsumer('metrics',bootstrap_servers=["kafka:9092"],group_id=groupId)

# To produce new messages to kafka
producer = KafkaProducer(bootstrap_servers=["kafka:9092"])


#Push new policy to Kafka
future = producer.send('policy',json.dumps(json_policy))
# Receive messages from kafka metrics topic
for message in consumer:
                # do something with received messages
        #load each message as json data
        try:
            data = json.loads(message.value)

            #get type of metric of the message
            value_name=data['metric']['name']

            #check that that metric is the metric we need
            if value_name == "cpu.system_perc":

                #generate random values to fill our policy, we don't have any measure to fill this right now
                
                value_data=data['metric']['value']

                #set that value to the previous defined policy
                print(value_data)
                #print(event-value)
                json_policy['supa-policy']['supa-policy-statement']['event']['event-value']=value_data

                #Send that policy as new measure to the listening topicName topic
                future = producer.send(topicName,json.dumps(json_policy))
                time.sleep(1)
            #else:
                #print("Not valid data")
        except ValueError:
            print "No valid data"
```

# Creating a Docker

This part of the tutorial will cover the way to deploy the pushing policy into *CogNet* infrastructure. To execute this task we will have to create a Docker from the code and deploy it into infrastructure.

First step will be creating a Dockerfile.

## Create a Dockerfile

This file will control the files that will be deployed on the Docker and the way to start the Docker.

```
FROM python:2-onbuild

USER root


COPY push_policy.py /src/push_policy.py
COPY policy.json /src/policy.json
CMD ["python","/src/push_policy.py"]

```
This Dockerfile indicates we are going to use a *python:2-onbuild* based Ubuntu distribution, that means that we will use an Ubuntu based distribution with the default python-2 installation.

The Dockerfile will copy the pushing script and the policy description file.

Final line indicates that the command that will be launched when Docker starts will be the pushing script.

## ansible.yml playbook file

Once the Dockerfile has been created next step will be creating an *Ansible* file to deploy that Docker into *CogNet* infrastructure.

This creates and runs a new Docker instance containing our ML code. It can be divided into 3 parts:

1. Download Docker repository
2. Building the Docker image
3. Launching Docker image

Current names for this demo will be:

* image name: tutorial_params
* image tag: policydemo
* container name: docker_params

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
        force: yes

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
        name=tutorial_params
        tag=policydemo
        path=/home/cognet/repo/demos/Dockers/tutorial_with_param
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
      docker_container: >
        name=docker_params
        image="tutorial_params:policydemo"
        state=absent
        api_version=1.18
    - name: Create Container
      docker_container: >
        name=docker_multiple_events
        image="tutorial_params:policydemo"
        state=started
        etc_hosts="{{ hosts_ip }}"
        api_version=1.18
```

For more information, please refer to [ansible helloworld description](https://github.com/CogNet-5GPPP/Apis_public/tree/master/helloworlds/ansible)


## Uploading ansible file to github

## Create Jenkins project

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

