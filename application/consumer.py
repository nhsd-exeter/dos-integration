import json
from kafka import KafkaConsumer

consumer = KafkaConsumer('TestTopic', bootstrap_servers="kafka:9092")
for message in consumer:
    print (json.loads(message.value))
