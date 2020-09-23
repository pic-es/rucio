#!/bin/bash

while :
do
    rucio-abacus-account --run-once >> /var/log/daemon_logs/abacus-account.log &
    rucio-abacus-rse --run-once >> /var/log/daemon_logs/abacus-rse.log &
    rucio-judge-evaluator --run-once >> /var/log/daemon_logs/evaluator.log &
    rucio-conveyor-submitter --run-once >> /var/log/daemon_logs/submitter.log &
    rucio-conveyor-poller --run-once --older-than 0 >> /var/log/daemon_logs/poller.log & 
    rucio-conveyor-finisher --run-once >> /var/log/daemon_logs/finisher.log &
    rucio-judge-cleaner --run-once >> /var/log/daemon_logs/judge-cleaner.log &
    rucio-judge-injector --run-once >> /var/log/daemon_logs/judge-injector.log &
    rucio-judge-repairer --run-once >> /var/log/daemon_logs/judge-repairer.log &
    for rse in $(eval "rucio list-rses")
    do
        rucio-reaper --greedy --rse $rse --run-once >> /var/log/daemon_logs/reaper.log & 
    done
    rucio-hermes --run-once >> /var/log/daemon_logs/hermes.log &
done
