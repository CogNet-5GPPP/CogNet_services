This tutorial will describe the way to deploy a *policy* into *CogNet* infrastructure. That policy will contain multiple events and multiple action params whose values are described by variables hat will be filled from events in execution time.

*Policy manager* will listen for certain event in order to check if a condition is met with values from that event.

If that condition is met, *Policy Manager* will execute an action with certain parameters. Those parameters get their values from variables that are read from events values at action execution time.

# Warning

All ips shown in this example are not updated, they are example ones.
Each time CogNet infrastructure is deployed different servers get new dynamic ips. There is an automatically updated list of those ips/hosts combination in [hosts](https://github.com/CogNet-5GPPP/CogNet_services/blob/master/hosts) file from CogNet_services repository.

# Content

There are several files whithin this tutorial:

* policy.json -> The policy that is going to be pushed
* push_policy_multiple_events_params.py -> A python script that will push the policy and will it with random measures
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

```json
{"supa-policy": {
  "supa-policy-validity-period": {
    "start": "2017-05-16T08:42:57.527404Z"
  },
  "supa-policy-target": {
    "domainName": "systemOpNFV",
    "subNetwork": "192.168.1.1",
    "instanceName": ["wit"],
    "topicName": "dse"
  },
  "supa-policy-statement": {
    "event": [{
      "event-name": "threat.flow",
      "event-value-type": "float",
      "event-value": "9.5",
      "instanceName": ["wit:vnf0"]
    }, {
      "event-name": "threat.ip",
      "event-value-type": "char",
      "event-value": "192.168.1.1",
      "instanceName": ["wit:vnf1"]
    }, {
      "event-name": "threat.port",
      "event-value-type": "int",
      "event-value": "884",
      "instanceName": ["wit:vnf2"]
    },
   {
      "event-name": "threat.protocol",
      "event-value-type": "char",
      "event-value": "UDP",
      "instanceName": ["wit:vnf3"]
    }],
    "condition": {
      "condition-name": "threat.flow_high",
      "condition-operator": ">",
      "condition-threshold": "8.0"
    },
    "action": {
      "action-name": "firewall_vnf",
      "action-host": "http://192.168.10.9:8080/",
      "action-type": " firewall_vnf",
        "action-param":[ 
          {
          "param-type": "duration",
          "param-value":"$event-value$threat.flow",
          "instanceName": ["$instanceName$threat.flow"]
        },{
          "param-type": "ip",
          "param-value": "$event-value$threat.ip",
          "instanceName": ["$instanceName$threat.ip"]
        }, {
          "param-type": "port",
          "param-value": "30",
          "instanceName": ["$instanceName$threat.port"]
        }, {
          "param-type": "protocol",
          "param-value": "$event-value$threat.protocol",
          "instanceName": ["$instanceName$threat.protocol"]
        }]
}}}}
```

The policy contains several elements, but the main ones are:

* events
* condition
* action

## events

This policy contains multiple events. Those events will be held on an array of events. The structure of an event is:

* event-name -> a string
* event-value-type -> a string containing the type of the value: supported types are: int, float, char (for strings)
* event-value -> a string containing the value of the event. This string will be treated by Policy Manager as defined on *event-value-type*
* instanceName -> an array of strings containing the elements that had produced the event

## condition

Is the condition that must be met by the events to execute the action. It is composed by:

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

Action param variables will be composed of two elements indicated by **$** character

* field to be read
* event to be read

for example:

*$event-value$threat.protocol*

will be substituted by *Policy Manager* by the value of *event-value* from the *thread.protocol* event each time a new policy event is being pushed to *topicName*



## Some notes about policy creation

If a multiple events policy is created, when pushed, it must be multiple events policy, otherwise system wont work.

# The pushing python application

As we don't have yet any *real* values to be pushed into the policy we have modified our pushing example python script to push random generated values to get some kind of valid data into the policy engine. This operation will be performed by *push_policy_multiple_events_params.py* script.

Working:

1. Read policy.json and push it to *newpolicy* topic
2. Listen for kafka events. When a new event is comming generate a random value depending on the data type.
3. Create a new policy with those generated values.
4. Push new policy to *topicName* from *policy.json* 
5. Goto 2

```python
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import random
import string
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
future = producer.send('newpolicy',json.dumps(json_policy))
# Receive messages from kafka metrics topic
# 
# 

events=json_policy['supa-policy']['supa-policy-statement']['event']


for message in consumer:
                # do something with received messages
        #load each message as json data
        try:
            data = json.loads(message.value)

            #get type of metric of the message
            value_name=data['metric']['name']

            #check that that metric is the metric we need
            if value_name == "cpu.system_perc":

                #get metric value
                value_data=data['metric']['value']

                #set that value to the previous defined policy
                for i in range (0, len(events)-1):
                    value_data=""
                    #set random value for each event-value depending
                    eventtype=json_policy['supa-policy']['supa-policy-statement']['event'][i]['event-value-type']
                    if eventtype == "float":
                        value_data=random.uniform(8.0, 100.0)
                    elif eventtype == "int":
                        value_data=random.randrange(0, 100)
                    elif eventtype == "char":
                        arrayString=["192.168.10.1","192.168.10.2","192.168.10.3","192.168.10.4","192.168.10.5","192.168.10.6","192.168.10.7"]
                        value_data=random.choice(arrayString)

                    #print (eventtype)
                    #print "Random value is %s " %value_data
                    json_policy['supa-policy']['supa-policy-statement']['event'][i]['event-value']=value_data

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

## Create a requirements.txt

*requirements.txt* file will hold the *pip* *python* modules that are neccessary as dependencies for the the pushing python application. The file will contain their names in each new line.

In our case only have *kafka-python* as pip dependency,so:

```
kafka-python
```

will be the only content for us.

# ansible.yml playbook file

Once the Dockerfile has been created next step will be creating an *Ansible* file to deploy that Docker into *CogNet* infrastructure.

This creates and runs a new Docker instance containing our ML code. It can be divided into 3 parts:

1. Download Docker repository
2. Building the Docker image (target will be the path where this code resides */home/cognet/repo/demos/Dockers/tutorial_multiple_events_with_param_variables* )
3. Launching Docker image


Current names for this demo will be:

* image name: tutorial_multiple_events
* image tag: policydemo
* container name: docker_multiple_events

```
- name: clone and update github repository
  hosts: docker
  remote_user: "{{ansible_user}}"
  become: yes
  tasks:

    - name: clone github repository
      git:
        repo: git@github.com:CogNet-5GPPP/CogNet_services.git
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
        name=tutorial_multiple_events
        tag=policydemo
        path=/home/cognet/repo/demos/Dockers/tutorial_multiple_events_with_param_variables
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
        name=docker_multiple_events
        image="tutorial_multiple_events:policydemo"
        state=absent
        api_version=1.18
    - name: Create Container
      docker_container: >
        name=docker_multiple_events
        image="tutorial_multiple_events:policydemo"
        state=started
        etc_hosts="{{ hosts_ip }}"
        api_version=1.18
```

For more information, please refer to [ansible helloworld description](https://github.com/CogNet-5GPPP/CogNet_Apis/tree/master/helloworlds/ansible)

# Create Jenkins project

* Go to [Jenkins](http://yourJenkinsIp:8080/)
* New Item (Freestyle project)
* Select Git as *Source code Management*
* Add Git repository [https://github.com/CogNet-5GPPP/CogNet_services](https://github.com/CogNet-5GPPP/CogNet_services)
* Set GitHub Project credentials
* Select build steps and add Invoke Ansible Playbook
* Set relative playbook file (ansible.yml) path from github
* Add **/var/lib/jenkins/workspace/CogNet_RackSpace_Infrastructure_Deploy/scripts/setup/ansible/inventory** as *Inventory File* 
* Save

## Run Jenkins Project


# References

[Docker](http://docker.io/)
[Ansible](http://ansible.com/)
[Policy helloworld](https://github.com/CogNet-5GPPP/CogNet_Apis/tree/master/helloworlds/policy)

