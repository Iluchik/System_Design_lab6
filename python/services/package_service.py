from fastapi import HTTPException, status
from model.DBconfig import Package_description, Package, package_collection
from bson import ObjectId
from confluent_kafka import Producer
import json

conf = {
	"bootstrap.servers": "brokerKafka1:9092,brokerKafka2:9092"
}

producer = Producer(**conf)

def delivery_report(err, msg):
	if err is not None:
		print(f"Message delivery failed: {err}")
	else:
		print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# ==== Package service ================================================================================================

class package_service():

	async def create_package(self, package_desc: Package_description, current_user: dict):
		if package_desc.recipient_id == current_user["user"].id:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't send a package to yourself")
		insert_obj = package_desc.__dict__
		insert_obj["sender_id"] = current_user["user"].id
		try:
			producer.produce(
				topic="package_topic",
				value=json.dumps(insert_obj),
				callback=delivery_report
			)
			producer.flush()
		except Exception as e:
			print(f"Error: {e}")
		return "Your message has been successfully sent for processing!"

	async def get_user_packages(self, current_user: dict):
		find_result = []
		for doc in package_collection.find({"$or": [{"sender_id": current_user["user"].id}, {"recipient_id": current_user["user"].id}]}):
			doc["_id"] = str(doc["_id"])
			find_result.append(doc)
		return find_result

	async def update_package(self, updated_package: dict, current_user: dict):
		package = package_collection.find_one({"_id": ObjectId(updated_package["_id"])})
		if package is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
		if (package["sender_id"] == current_user["user"].id) or (package["recipient_id"] == current_user["user"].id):
			package_collection.update_one({"_id": ObjectId(updated_package["_id"])}, {"$set": {"sender_id": updated_package["sender_id"], "recipient_id": updated_package["recipient_id"], "package_details": updated_package["package_details"]}})
			return updated_package
		else:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only change package related to the current account")

	async def delete_package(self, product_id: str, current_user: dict):
		package = package_collection.find_one({"_id": ObjectId(product_id)})
		if package is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
		if (package["sender_id"] == current_user["user"].id) or (package["recipient_id"] == current_user["user"].id):
			package_collection.delete_one({"_id": ObjectId(package["_id"])})
			package["_id"] = str(package["_id"])
			return package
		else:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only change package related to the current account")

# =====================================================================================================================