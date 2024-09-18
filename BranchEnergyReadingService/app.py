import os
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient
import json
import logging

SERVICE_IDENTIFIER = os.getenv('SERVICE_IDENTIFIER', 'unnamed-service')

# TODO - extract logger creation to a util func or a logger wrapper
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(SERVICE_IDENTIFIER)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
QUERY_KAFKA_TOPIC = os.getenv('QUERY_KAFKA_TOPIC')
RESPONSE_KAFKA_TOPIC = os.getenv('RESPONSE_KAFKA_TOPIC')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017')
MONGO_DB= os.getenv('MONGO_DB', 'gos_mongo')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')


def parse_query_record(record):
    try:
        query_id = record['query_id']
        repo_name = record['repo_name']
        branch_name = record['branch_name']
        return query_id, repo_name, branch_name
    except Exception as e:
        logger.error(f'failed to parse query field: {e}')


def fetch_repo_branch_energy_document(collection, repo_name, branch_name):
    result_document = collection.find_one(
        {'repo': repo_name, 'branch': branch_name},
        sort=[('energy_timestamp', -1)],
        projection={'energy': 1, '_id': 0}
    )
    if result_document is None:
        raise Exception(f'document for repo={repo_name}, branch = {branch_name} not found')
    return result_document


def extract_energy_from_document(document):
    if 'energy' in document:
        return document['energy']
    else:
        raise Exception(f'document for repo={repo_name}, branch = {branch_name} does not contain energy field: {e}')


def get_branch_latest_energy(collection, repo_name, branch_name):
    result_document = fetch_repo_branch_energy_document(collection, repo_name, branch_name)
    energy = extract_energy_from_document(result_document)
    return energy


def build_response(query_id, repo_name, branch_name, energy):
    return {
        "query_id": query_id,
        "repo_name": repo_name,
        "branch_name": branch_name,
        "energy": energy
    }


def validate_environment():
    # TODO - extract env var validation code into a util func
    if not QUERY_KAFKA_TOPIC:
        error_message = "Environment variable QUERY_KAFKA_TOPIC is required and cannot be empty."
        logger.error(error_message)
        raise ValueError(error_message)
    if not RESPONSE_KAFKA_TOPIC:
        error_message = "Environment variable RESPONSE_KAFKA_TOPIC is required and cannot be empty."
        logger.error(error_message)
        raise ValueError(error_message)
    if not MONGO_COLLECTION:
        error_message = "Environment variable MONGO_COLLECTION is required and cannot be empty."
        logger.error(error_message)
        raise ValueError(error_message)

logger.info(f'STARTED -- listening for queries on kafka broker:topic ({KAFKA_BROKER}:{QUERY_KAFKA_TOPIC}), responding on broker:topic ({KAFKA_BROKER}:{RESPONSE_KAFKA_TOPIC}), reading from mongo connection:db:collection ({MONGO_URI}:{MONGO_DB}:{MONGO_COLLECTION})')
consumer = KafkaConsumer(QUERY_KAFKA_TOPIC, bootstrap_servers=[KAFKA_BROKER])
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

for message in consumer:
    try:
        record = json.loads(message.value)
        logger.info(f'inbound query: {str(record)}')
        query_id ,repo_name, branch_name = parse_query_record(record)
        energy = get_branch_latest_energy(collection, repo_name, branch_name)
        response = build_response(query_id, repo_name, branch_name, energy)
        producer.send(RESPONSE_KAFKA_TOPIC, response)
        logger.info(f'outbound response sent: {str(response)}')
    except Exception as e:
        logger.error(f'{e}')



