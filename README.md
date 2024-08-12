# GreenOpsStem
GreenOps service

# Building and Running services in docker containers individually
## InboundTelemetryService
### Docker build
`docker build -t gos-inbound-telemetry-service .`
### Docker run
`docker run -p 80:80 -e PYTHONUNBUFFERED=1 <image id>`
