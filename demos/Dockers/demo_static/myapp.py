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

                #get metric value
                value_data=data['metric']['value']

		#Machine learning algorithm

		data_post_machine_learning=my_machine_learning_operation(value_data)

		#push data
		json_policy['supa-policy']['supa-policy-statement']['event']['event-value']=data_post_machine_learning

               

                #Send that policy as new measure to the listening topicName topic
                future = producer.send(topicName,json.dumps(json_policy))
            #else:
                #print("Not valid data")
        except ValueError:
            print "No valid data"



