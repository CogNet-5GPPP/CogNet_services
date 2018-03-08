from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError
from random import randint
import json


mytopicname="metrics"
somerandomnumber=randint(0,10000)
# To consume latest messages from metrics topic
consumer = KafkaConsumer(mytopicname,bootstrap_servers=["kafka:9092"],group_id=somerandomnumber)

for message in consumer:
    try:
        json.loads(message.value)
    except ValueError:
        print(message.value)
