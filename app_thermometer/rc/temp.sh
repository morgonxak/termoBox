#! /bin/bash
sudo modprobe w1-gpio
sudo modprobe w1-therm
roomtemp=$(cat /sys/bus/w1/devices/28-0417720ca4ff/w1_slave | grep  -E -o ".{0,0}t=.{0,5}" | cut -c 3-)
echo "$roomtemp"
