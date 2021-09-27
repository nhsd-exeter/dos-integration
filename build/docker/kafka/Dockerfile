FROM openjdk
RUN cd opt && curl -OL https://dlcdn.apache.org/kafka/3.0.0/kafka_2.13-3.0.0.tgz && tar -zxvf kafka_2.13-3.0.0.tgz && rm kafka_2.13-3.0.0.tgz
WORKDIR /opt/kafka_2.13-3.0.0
COPY start.sh /opt/kafka_2.13-3.0.0
CMD ["./start.sh"]
