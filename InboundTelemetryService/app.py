from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

app = Flask(__name__)

# producer = KafkaProducer(bootstrap_servers='kafka:9092',
#                          value_serializer=lambda v: json.dumps(v).encode('utf-8'))

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    print('inbound telemetry message: ' + str(data))
    # result = process_data(data)
    # Send result to Kafka topic
    # producer.send('processed_data', result)
    return jsonify(data)

def process_data(data):
    return {"processed_data": data}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)