FROM python

WORKDIR /usr/src/benchmark

RUN pip install requests

COPY ./ ./

ENTRYPOINT ["./entrypoint.sh"]
