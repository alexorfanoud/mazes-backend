FROM python

WORKDIR /usr/src/benchmark

RUN pip install requests prometheus_client

COPY ./ ./

ENTRYPOINT ["./entrypoint.sh"]
