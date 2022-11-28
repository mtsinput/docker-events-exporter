# docker-events-exporter
Prometheus exporter for Docker events for SWARM cluster

# Summary
For deploy service you could use such compose file
```docker
version: '3.3'

volumes:
  events_log:

networks:
  monitor-net:

services:
  events_exporter:
    image: wdmaster/docker-events-exporter:1.0.7
    hostname: "monitoring"
    container_name: events_exporter
    ports:
      - 9990:9990
    networks:
      - monitor-net
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - events_log:/log-events
    environment:
      - LOG_TO_DISK="TRUE"
      - DAYS_TO_STORE="10"
```