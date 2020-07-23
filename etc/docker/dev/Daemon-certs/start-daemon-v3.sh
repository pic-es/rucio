#!/bin/bash

while :
do
    rucio-judge-evaluator --run-once
    rucio-conveyor-submitter --run-once
    rucio-conveyor-poller --run-once --older-than 0
    rucio-conveyor-finisher --run-once
    rucio-hermes --run-once
    rucio-judge-cleaner --run-once 
    rucio-judge-injector --run-once 
    rucio-judge-repairer --run-once 
    for rse in $(eval "rucio list-rses")
    do
        rucio-reaper --greedy --rse $rse --run-once  
    done
done

