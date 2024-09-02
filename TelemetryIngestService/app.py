import os
from kafka import KafkaConsumer, KafkaProducer
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('telemetry-ingest-service')


KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
INPUT_KAFKA_TOPIC = os.getenv('INPUT_KAFKA_TOPIC', 'inbound-telemetry')
OUTPUT_KAFKA_TOPIC = os.getenv('OUTPUT_KAFKA_TOPIC', 'branch-energy')

consumer = KafkaConsumer(INPUT_KAFKA_TOPIC, bootstrap_servers=[KAFKA_BROKER])
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def parse_timestamp_datetime(timestamp_str):
    return datetime.fromisoformat(timestamp_str) if timestamp_str else None

def parse_telemetry(raw_payload):
    logger.info(f"raw_payload: {str(raw_payload)}")
    try:
        parsed_record = {
            'payload_timestamp': parse_timestamp_datetime(raw_payload.get('timestamp')).isoformat(),
            'energy_timestamp': parse_timestamp_datetime(raw_payload.get('payload').get('timestamp')).isoformat(),
            'repo': raw_payload.get('payload').get('repository'),
            'branch': raw_payload.get('payload').get('branch'),
            'workflow': raw_payload.get('payload').get('workflow'),
            'job_id': raw_payload.get('payload').get('job_id'),
            'energy': raw_payload.get('payload').get('energy')
        }
    except Exception as e:
        logger.info(f"Failed to parse telemetry message: {e}")
        parsed_record = {'error': f"Failed to parse telemetry message: {e}"}
    logger.info(f"parsed_record: {str(parsed_record)}")
    return parsed_record

for message in consumer:
    record = json.loads(message.value)
    result = parse_telemetry(record)
    producer.send(OUTPUT_KAFKA_TOPIC, result)
