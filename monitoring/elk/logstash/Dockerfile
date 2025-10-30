FROM docker.elastic.co/logstash/logstash:8.11.0

COPY pipeline /usr/share/logstash/pipeline

EXPOSE 5000 5044 8080

CMD ["logstash"]
