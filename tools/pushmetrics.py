from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError
from random import randint
import random
import json
import time
import string


mytopicname="metrics"
somerandomnumber=randint(0,10000)

# To produce new messages to kafka
producer = KafkaProducer(bootstrap_servers=["kafka:9092"])

message='{"metric": {"timestamp": 1505977750180.926, "value_meta": null, "name": "cpu.user_perc", "value": 38.3, "dimensions": {"hostname": "monasca", "service": "monitoring"}}, "meta": {"region": "useast", "tenantId": "a7c4a1ade7d040ccb1fb0d9ef4228d9e"}, "creation_time": 1505977753}'
messageJson=json.loads(message);

while True:
	# Setting timestamp
	timestamp=int(time.time())
	messageJson['metric']['timestamp']=timestamp
	messageJson['metric']['creation_time']=timestamp

	#Indicate that is not valid data
	messageJson['metric']['dimensions']['hostname']="fake"
	messageJson['metric']['dimensions']['service']="debugmonitoring"

	#Generate low random value
	messageJson['metric']['value']=randint(0,2)

	#Send message
	producer.send(mytopicname,json.dumps(messageJson))

	time.sleep(2)

	print "pushed data"
