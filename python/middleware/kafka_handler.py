import sys
sys.path.append("..")
from confluent_kafka import Consumer, KafkaError
from model.DBconfig import package_collection
import json

conf = {
	"bootstrap.servers": "brokerKafka1:9092,brokerKafka2:9092",
	"group.id": "SDEK_group",
	"auto.offset.reset": "earliest"
}

consumer = Consumer(conf)

consumer.subscribe(["package_topic"])

try:
	while True:
		msg = consumer.poll(1.0)
		if msg is None:
			continue
		if msg.error():
			if msg.error().code() == KafkaError._PARTITION_EOF:
				continue
			else:
				print(msg.error())
				break
		data = json.loads(msg.value().decode("utf-8"))
		package_collection.insert_one(data)
		data["_id"] = str(data["_id"])
		print(f"Received user data: {data}")
except KeyboardInterrupt:
	pass

finally:
	consumer.close()