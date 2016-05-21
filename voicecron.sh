#! /bin/bash

case "$(pgrep -f voicerec.py | wc -w)" in

0)  echo "Starting Voice Record"
    sudo python /home/pi/dev/voicerec.py
    ;;
*)  echo "Voice Rec  already running"
    ;;
esac


