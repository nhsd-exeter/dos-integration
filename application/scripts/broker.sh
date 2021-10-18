#!/bin/bash

#bootstrap server
if [ $# -gt 0 -a $1 -lt 4 ]; then
  KAFKA_OPTS="-javaagent:/opt/kafka/prometheus/jmx_prometheus_javaagent-0.3.0.jar=7071:/opt/kafka/prometheus/kafka-0-8-2.yml" $KAFKA_HOME/bin/kafka-server-start.sh -daemon /vagrant/config/server$1.properties
# $KAFKA_HOME/bin/kafka-server-start.sh -daemon /vagrant/config/server$1.properties
else
    echo "Usage: "$(basename $0)" <broker_id>"
fi
