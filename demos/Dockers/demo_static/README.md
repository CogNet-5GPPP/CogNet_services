[Dockerfile][] | [requirements.txt][] |[myapp.py][] | [Authors][] | [License][] 


This demo will read data from Kafka server that is running on Monasca machine and then it will push those data to "demo1" topic on Kafka machine. This way Policy Manager will listen for an event to met a given condition from Policy.

If this condition is met *Policy Manager* will trigger an action with fixed parameters.

# Warning

All ips shown in this example are not updated, they are example ones.
Each time CogNet infrastructure is deployed different servers get new dynamic ips. There is an automatically updated list of those ips/hosts combination in [hosts](https://github.com/CogNet-5GPPP/demos_public/blob/master/hosts) file from demos_public repository.

# Docker components
Following we are going to explain the content and working of the components of the Docker:

The components of this Docker will be 3 files:

  * Dockerfile
  * requirements.txt
  * myapp.py

# Dockerfile

Is the main configuration file from Dockers, there it will be all Docker configuration, in our case it will be:
    
```  
FROM python:2-onbuild
    
USER root
    
    
################################################
#Your python application to be launched
COPY myapp.py /src/myapp.py
#################################################
    
    
#Run our application at startup
CMD ["/usr/bin/python","/src/myapp.py"]
```    

This docker file will create a docker image based on python 2 and copy:

  * myapp.py


file to the Docker image.

In final part of this file we have set the starting comand to be launched when we run the Docker.

# requirements.txt

This file will contain python-pip dependencies. Here we can add all python dependencies that can be installed via *pip* that we want to use in our python application. We will run a kafka-python based aplication so content should be:
    
```
kafka-python
```    

# myapp.py

This file will be our python application and the place where our source code must be.

This application will execute the following steps

  1. Prepare python Kafka dependencies
  2. Connect to **metrics** topic from kafka server to read metrics
  3. Connect to Kafka server in producer mode to push procesed data
  4. Read policy from json file
  6. Send policy to "newpolicy" topic in order to create a new policy
  5. Read metrics from Kafka
  6. Process metrics
    1. Read received metrics
    2. Get kind of metric that had been received
    3. Check if that is the kind of data we need
    4. Set data value to the policy definition
  7. Send policy with new value to **newtopic** defined in policy to Kafka

```
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

# To consume latest messages from metrics topic
consumer = KafkaConsumer('metrics',bootstrap_servers=["monasca:9092"])

# To produce new messages to kafka
producer = KafkaProducer(bootstrap_servers=["kafka:9092"])


# Read newpolicy.json
with open('newpolicy.json') as json_data:
    json_policy = json.load(json_data)

#Read topicName from policy
topicName=json_policy['supa-policy']['supa-policy-target']['topicName']

#Push new policy to Kafka
future = producer.send('newpolicy',json.dumps(json_policy))


# Receive messages from kafka metrics topic
for message in consumer:
                # do something with received messages

        #load each message as json data
        data = json.loads(message.value)

        #get type of metric of the message
        value_name=data['metric']['name']

        #check that that metric is the metric we need
        if value_name == "cpu.user_perc":

          #get metric value
          value_data=data['metric']['value']

          #append that value to the previous defined policy
          json_policy['supa-policy']['supa-policy-statement']['event']['event-value']=value_data

          #Send that policy as new measure to the listening topicName topic
          future = producer.send(topicName,json.dump(json_policy))
        #else:
          #print("Not valid data")
```    

### Authors


- Angel Martin (amartin@vicomtech.org)
- Felipe Mogollon (fmogollon@vicomtech.org)

### License


Copyright 2016 Vicomtech.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

[Dockerfile]: #dockerfile
[requirements.txt]: #requirementstxt
[myapp.py]: #myapppy
[start.sh]: #startsh
[Authors]: #authors
[License]: #license
  
