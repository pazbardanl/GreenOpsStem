import os
from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import logging

SERVICE_IDENTIFIER = os.getenv('SERVICE_IDENTIFIER', 'unnamed-service')

# TODO - extract logger creation to a util func or a logger wrapper
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(SERVICE_IDENTIFIER)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
INPUT_KAFKA_TOPIC = os.getenv('INPUT_KAFKA_TOPIC')
OUTPUT_MONGO_URI = os.getenv('OUTPUT_MONGO_URI', 'mongodb://mongo:27017')
OUTPUT_MONGO_DB= os.getenv('OUTPUT_MONGO_DB', 'gos_mongo')
OUTPUT_MONGO_COLLECTION = os.getenv('OUTPUT_MONGO_COLLECTION')

# TODO - extract env var validation code into a util func
if not INPUT_KAFKA_TOPIC:
    error_message = "Environment variable INPUT_KAFKA_TOPIC is required and cannot be empty."
    logger.error(error_message)
    raise ValueError(error_message)
if not OUTPUT_MONGO_COLLECTION:
    error_message = "Environment variable OUTPUT_MONGO_COLLECTION is required and cannot be empty."
    logger.error(error_message)
    raise ValueError(error_message)

logger.info(f'STARTED -- listening on kafka broker:topic {KAFKA_BROKER}:{INPUT_KAFKA_TOPIC}, writing to mongo connection:db:collection {OUTPUT_MONGO_URI}:{OUTPUT_MONGO_DB}:{OUTPUT_MONGO_COLLECTION}')

consumer = KafkaConsumer(INPUT_KAFKA_TOPIC, bootstrap_servers=[KAFKA_BROKER])
client = MongoClient(OUTPUT_MONGO_URI)
db = client[OUTPUT_MONGO_DB]
collection = db[OUTPUT_MONGO_COLLECTION]

for message in consumer:
    record = json.loads(message.value)
    collection.insert_one(record)
    logger.info(f'record written: {str(record)}')
