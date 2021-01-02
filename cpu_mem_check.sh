#!/bin/bash
time=120000
x=0
n=9

now="$(date)"
echo "CPU Begin : $now"
$(rm /root/PycharmProjects/cpu_usage/statistics/cpu/*.*)


while [ $x -le $time ]
do
  $(sar -P ALL 1 1 | grep -v Linux | grep -v Average: >> /root/PycharmProjects/cpu_usage/statistics/cpu/$x.txt)
  x=$(( $x + 1 ))
  sleep $n
done
now="$(date)"
echo "CPU End : $now"
