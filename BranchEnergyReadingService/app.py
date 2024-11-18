import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
import logging

SERVICE_IDENTIFIER = os.getenv('SERVICE_IDENTIFIER', 'unnamed-service')

# TODO - extract logger creation to a util func or a logger wrapper
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(SERVICE_IDENTIFIER)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017')
MONGO_DB= os.getenv('MONGO_DB', 'gos_mongo')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')

def parse_query_record(record):
    try:
        repo_name = record['repo_name']
        branch_name = record['branch_name']
        return repo_name, branch_name
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
        raise Exception(f'document does not contain energy field: {e}. document: {document}')


def get_branch_latest_energy(collection, repo_name, branch_name):
    result_document = fetch_repo_branch_energy_document(collection, repo_name, branch_name)
    energy = extract_energy_from_document(result_document)
    return energy


def build_response(repo_name, branch_name, energy):
    return {
        "repo_name": repo_name,
        "branch_name": branch_name,
        "energy": energy
    }


def validate_environment():
    # TODO - extract env var validation code into a util func
    if not MONGO_COLLECTION:
        error_message = "Environment variable MONGO_COLLECTION is required and cannot be empty."
        logger.error(error_message)
        raise ValueError(error_message)

app = Flask(__name__)
validate_environment()
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

@app.route('/branch/energy', methods=['POST'])
def query():
    record = request.json
    repo_name, branch_name = parse_query_record(record)
    energy = get_branch_latest_energy(collection, repo_name, branch_name)
    response = build_response(repo_name, branch_name, energy)
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
