#!/bin/bash

echo "downloading kafka...$KAFKA_VERSION"

#download kafka binaries if not present
if [ ! -f  $KAFKA_TARGET/$KAFKA_NAME.tgz ]; then
   mkdir -p $KAFKA_TARGET
   su -c "yum -y install wget"
   wget -O "$KAFKA_TARGET/$KAFKA_NAME.tgz" https://archive.apache.org/dist/kafka/"$KAFKA_VERSION/$KAFKA_NAME.tgz"
fi

echo "installing JDK and Kafka..."

su -c "yum -y install java-1.8.0-openjdk-devel"

#disabling iptables
/etc/init.d/iptables stop

if [ ! -d $KAFKA_NAME ]; then 
   tar -zxvf $KAFKA_TARGET/$KAFKA_NAME.tgz
fi

chown vagrant:vagrant -R $KAFKA_NAME

echo "done installing JDK and Kafka..."

# chmod scripts
chmod u+x /vagrant/scripts/*.sh

# installing prometheus JMX agent on all the servers
sudo mkdir -p /opt/kafka/prometheus/
sudo wget -P /opt/kafka/prometheus/ https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.3.0/jmx_prometheus_javaagent-0.3.0.jar
sudo wget -P /opt/kafka/prometheus/ https://raw.githubusercontent.com/prometheus/jmx_exporter/master/example_configs/kafka-0-8-2.yml
sudo wget -P /opt/kafka/prometheus/ https://raw.githubusercontent.com/prometheus/jmx_exporter/master/example_configs/zookeeper.yaml
