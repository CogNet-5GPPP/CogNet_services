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
            if value_name == "test.user_perc":

                #get metric value
                value_data=data['metric']['value']



                #set that value to the previous defined policy
                for i in range (0, len(events)-1):

                	#Machine learning algorithm
                    #set random value for each event-value depending
                    eventtype=json_policy['supa-policy']['supa-policy-statement']['event'][i]['event-value-type']
                    if eventtype == "float":
                        value_data=random.uniform(8.0, 100.0)
                    elif eventtype == "int":
                        value_data=some_machine_learning_operation(json_policy['supa-policy']['supa-policy-statement']['event'][i]['value-data'])
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
