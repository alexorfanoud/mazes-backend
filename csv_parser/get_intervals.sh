#!/bin/bash

echo "package,start_time,end_time" > $(git rev-parse --show-toplevel)/csv_parser/package_intervals.csv
# kubectl logs -n thesis parsec | grep "Parsec_interval" | cut -d$'\t' -f2 >> $(git rev-parse --show-toplevel)/csv_parser/package_intervals.csv
docker logs $(docker ps -a | grep parsec | awk '{print $1}') | grep "Parsec_interval" | cut -d$'\t' -f2 >> $(git rev-parse --show-toplevel)/csv_parser/package_intervals.csv
