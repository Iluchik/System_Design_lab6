from pymongo import MongoClient
from confluent_kafka import Consumer, KafkaError
import json
import os

DATABASE_URL_MONGO = os.getenv("MONGO_URL", "mongodb://mongoDB:27017/")
client = MongoClient(DATABASE_URL_MONGO)
archdb = client["arch"]
package_collection = archdb["packages"]

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