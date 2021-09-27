import time
import random
from kafka import KafkaProducer
from kafka.errors import KafkaError

# give broker IP from docker
producer = KafkaProducer(bootstrap_servers="localhost:29092")

# continuous loop
#var = 1
#while var == 1:

num = random.randint(0, 10)
num_bytes = bytes(str(num), encoding="utf-8")
print ("Try sending message")
try:
    result = producer.send("demoPing", value=num_bytes, key=num_bytes)
    print("{0}".format(result))
except Exception as e:
    print("Error: {0}".format(e))
#pass

    # wait 1 second
    #time.sleep(1)
