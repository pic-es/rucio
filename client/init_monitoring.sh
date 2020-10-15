#!/bin/bash
#
# init_monitoring.sh


while true
do
  rm -f /core*
  python3 ./Rucio-monitoring.py
  rm -f /core*
  sleep 10

done

