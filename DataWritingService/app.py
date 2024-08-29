import os
from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# KAFKA_BROKER = 'kafka:9092'
# KAFKA_TOPIC = 'inbound-telemetry'
# MONGO_URI = 'mongodb://mongo:27017'

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'inbound-telemetry')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017')

consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=[KAFKA_BROKER])
client = MongoClient(MONGO_URI)
db = client.gos_mongo
collection = db.inbound_telemetry

for message in consumer:
    record = json.loads(message.value)
    collection.insert_one(record)
