#!/bin/bash

# monitor.sh ---

# Usage:

# monitor.sh

usage="Usage:\n$0 JOB_ID"
[ -z "$1" ] && { echo -e "$usage"; exit 1; }
job_id=$1
i=30
# out=../monitor.sh.out.$job_id
out=$PWD/job_resources_monitor.$job_id

echo "[$(date)] *** Starting monitor for $job_id" | tee -a $out

while :; do
    qstat | grep -q "$job_id"
    [[ $? -eq 0 ]] || break
    qstat | grep -q -E "$job_id.+$USER r"
    if [[ $? -eq 0 ]]; then
        echo -n "[$(date)] " | tee -a $out
        qstat -j $job_id | grep '^usage' | tee -a $out
        # i=10
    else
        echo "[$(date)] Waiting for job $job_id ..." >&2
    fi
    sleep $i
done

echo "Done"
