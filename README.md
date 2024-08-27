# GreenOpsStem
GreenOps system backend

# Docker Compose
### UP
`docker-compose up --build`
###DOWN
`docker-compose down`

# Building and Running services in docker containers individually

## InboundTelemetryService

### Docker build
```
cd InboundTelemetryService/
docker build -t gos-inbound-telemetry-service .
```

### Docker run

`docker run -p 80:80 -e PYTHONUNBUFFERED=1 <image id>`

### Kafka consumer to listen on the service's output topic:

`winpty docker exec -it greenopsstem-kafka-1 kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic inbound-telemetry --from-beginning`