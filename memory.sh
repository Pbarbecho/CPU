l#!/bin/bash
time=30
x=0
n=0.5

now="$(date)"
echo "MEM Begin : $now"
$(rm /root/Documents/EV/statistics/cpu/*.*)

while [ $x -le $time ]
do
  $(free -m | grep -v Linux | grep -v Average: >> /root/Documents/EV/statistics/mem/$x.txt)
  x=$(( $x + 1 ))
  sleep $n
done
now="$(date)"
echo "MEM End : $now"
