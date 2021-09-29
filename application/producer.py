import time
import random
import json
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers="kafka:9092")

while True:
    num = random.randint(0, 10)
    num_bytes = bytes(str(num), encoding="utf-8")
    producer.send("TestTopic", json.dumps(['foo', {'bar': ('baz', None, 1.0, 2),}]).encode('utf-8'))
    time.sleep(1)
