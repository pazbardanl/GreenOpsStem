import os
from datetime import datetime
from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
OUTPUT_KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'inbound-telemetry')

app = Flask(__name__)

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))


@app.route('/process', methods=['POST'])
def process():
    inbound_datetime = datetime.now()
    data = request.get_json()
    print('inbound telemetry message: ' + str(data))
    result = process_data(inbound_datetime, data)
    producer.send(OUTPUT_KAFKA_TOPIC, result)
    return jsonify(data)


def process_data(timestamp, data):
    return {"timestamp": timestamp.isoformat(), "payload": data}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)