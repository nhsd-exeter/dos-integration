# SEE: https://diagrams.mingrammer.com/

import sys

from diagrams import Cluster, Diagram
from diagrams.onprem.analytics import Spark
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.aggregator import Fluentd
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Nginx
from diagrams.onprem.queue import Kafka


if len(sys.argv) > 1:
    file = str(sys.argv[1])
else:
    file = "diagram"

with Diagram("Advanced Web Service with On-Premise", filename=file, show=False):
    ingress = Nginx("ingress")

    metrics = Prometheus("metric")
    metrics << Grafana("monitoring")

    with Cluster("Service Cluster"):
        grpcsvc = [Server("grpc1"), Server("grpc2"), Server("grpc3")]

    with Cluster("Sessions HA"):
        master = Redis("session")
        master - Redis("replica") << metrics
        grpcsvc >> master

    with Cluster("Database HA"):
        master = PostgreSQL("users")
        master - PostgreSQL("slave") << metrics
        grpcsvc >> master

    aggregator = Fluentd("logging")
    aggregator >> Kafka("stream") >> Spark("analytics")

    ingress >> grpcsvc >> aggregator
