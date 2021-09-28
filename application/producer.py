import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers="kafka:9092")

while True:
    num = random.randint(0, 10)
    num_bytes = bytes(str(num), encoding="utf-8")
    producer.send("TestTopic", value=num_bytes, key=num_bytes)
    time.sleep(1)
