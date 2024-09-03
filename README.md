# GreenOpsStem
GreenOps system backend

# Docker Compose
### UP
`docker-compose up --build`
###DOWN
`docker-compose down`

# Services (as individual docker containers)

## InboundTelemetryService
A rest API that accepts raw telemetry messages relays them to a kafka topic.
* **Input**: REST endpoint `http://localhost:80/process`
* **Output**: Kafka topic `inbound-telemetry`

#### Docker build
```
cd InboundTelemetryService/
docker build -t gos-inbound-telemetry-service .
```

#### Docker run

`docker run -p 80:80 -e PYTHONUNBUFFERED=1 <image id>`

#### curl command for testing:

```
curl --location 'http://localhost:80/process' \
--header 'Content-Type: application/json' \
--data '{
    "query":"sanity"
}'
```

#### Kafka consumer to listen on the service's output topic:

`winpty docker exec -it greenopsstem-kafka-1 kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic inbound-telemetry --from-beginning`

#### view logs:

`docker-compose logs -f inbound-telemetry-service`

## _TelemetryWritingService_ (DataWritingService)
* **Input**: Kafka topic(s): `inbound-telemetry`
* **Output** Mongo collection: (DB:collection) `gos_mongo`:`inbound_telemetry`

#### Docker build
```
cd DataWritingService/
docker build -t gos-telemetry-writing-service .
```

#### Docker run
`docker run -e PYTHONUNBUFFERED=1 <image id>`

_(this will probably fail to run outside docker compose since no kafka broker nor mongo db are available when running this service standalone)_

#### Querying output Mongo collection of the service's output
Get all entries: 

`docker exec greenopsstem-mongo-1 mongosh --eval 'db.getSiblingDB("gos_mongo").inbound_telemetry.find().pretty()'`

Get all entries sorted descending by timestamp:

`docker exec greenopsstem-mongo-1 mongosh --eval 'db.getSiblingDB("gos_mongo").inbound_telemetry.find().sort({"timestamp": -1}).pretty()'`
#### view logs:

`docker-compose logs -f telemetry-writing-service`

## TelemetryIngestService
Read raw telemetry messages from a kafka topic, parses them and pushes the result into another kafka topic 
* **Input**: Kafka topic `inbound-telemetry`
* **Output**: Kafka topic `branch-energy`

#### Docker build
```
cd InboundTelemetryService/
docker build -t gos-telemetry-ingest-service .
```

#### Docker run

`docker run -p 80:80 -e PYTHONUNBUFFERED=1 <image id>`

#### Kafka consumer to listen on the service's output topic:

`winpty docker exec -it greenopsstem-kafka-1 kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic branch-energy --from-beginning`

#### view logs:

`docker-compose logs -f telemetry-ingest-service`

## _BranchEnergyWritingService_ (DataWritingService)
* **Input**: Kafka topic(s): `branch-energy`
* **Output** Mongo collection: (DB:collection) `gos_mongo`:`branch_energy`

#### Docker build
```
cd DataWritingService/
docker build -t gos-branch-energy-writing-service .
```

#### Docker run
`docker run -e PYTHONUNBUFFERED=1 <image id>`

_(this will probably fail to run outside docker compose since no kafka broker nor mongo db are available when running this service standalone)_

#### Querying output Mongo collection of the service's output
Get all entries: 

`docker exec greenopsstem-mongo-1 mongosh --eval 'db.getSiblingDB("gos_mongo").branch_energy.find().pretty()'`

Get all entries sorted descending by payload_timestamp:

`docker exec greenopsstem-mongo-1 mongosh --eval 'db.getSiblingDB("gos_mongo").branch_energy.find().sort({"payload_timestamp": -1}).pretty()'`

Get all entries sorted descending by energy_timestamp:

`docker exec greenopsstem-mongo-1 mongosh --eval 'db.getSiblingDB("gos_mongo").branch_energy.find().sort({"energy_timestamp": -1}).pretty()'`


#### view logs:

`docker-compose logs -f branch-energy-writing-service`
