#!/bin/bash

NS=/$1

if [ $# -eq 1 ]; then
  NS=/azcar_sim
fi


echo 'Car'  $NS ' should move forward for a few seconds'
rostopic pub -r 10 -f forward.bagy $NS/cmd_vel geometry_msgs/Twist
echo 'Car should move in reverse for a few seconds'
rostopic pub -r 10 -f reverse.bagy $NS/cmd_vel geometry_msgs/Twist   
echo 'Car should stop'
