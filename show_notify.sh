#!/bin/bash 
# show_notify
usr_name=rabbit
source /home/$usr_name/.bashrc
pid=$(pgrep -u $usr_name gnome-sess | head -n 1)
dbus=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$pid/environ | sed 's/DBUS_SESSION_BUS_ADDRESS=//' )
export DBUS_SESSION_BUS_ADDRESS=$dbus
export HOME=/home/$usr_name
export DISPLAY=:0
/usr/bin/notify-send  $1 $2 $3 $4 