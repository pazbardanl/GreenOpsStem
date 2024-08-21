# GreenOpsStem
GreenOps service

# Docker Compose
`docker-compose up --build`
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
