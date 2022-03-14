FROM python

WORKDIR /usr/src/benchmark

RUN pip install requests prometheus_client
# RUN mkdir -p /metrics/benchmark

COPY ./ ./

ENTRYPOINT ["./entrypoint.sh"]
