FROM python

WORKDIR /usr/src/benchmark

RUN pip install requests
RUN mkdir -p /metrics/benchmark

COPY ./ ./

ENTRYPOINT ["./entrypoint.sh"]
