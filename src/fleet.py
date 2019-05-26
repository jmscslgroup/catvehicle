#!/usr/bin/env python
#
# Author: Rahul Bhadani
# Copyright (c) 2019 Rahul Bhadani, Arizona Board of Regents
# All rights reserved.

""" This script helps launch a fleet of n cars along x-axis. """

import roslaunch
import rospy, rosbag
import sys, math, time
import signal
import subprocess, shlex
from subprocess import call
import sys
import signal
import psutil
import numpy as np


class catlaunch:
    def __init__(self, num_of_vehicles):
        call(["pkill", "ros"])
        call(["pkill", "gzserver"])
        call(["pkill", "gzclient"])
        time.sleep(2)
        self.num_of_vehicles = num_of_vehicles

        #Car's length, value reported here is the length of bounding box along the longitudinal direction of the car
        self.car_to_bumper = 4.4324092962
        """Generate coordinate on x-axis to place `num_of_vehicles`"""

        X = []
        self.car_spacing = 20.0
        pos = 0.0
        for x in range(0, num_of_vehicles):
            X.append(pos)
            pos = (x+1)*(self.car_to_bumper + self.car_spacing)

        self.X = X

        self.name = []
        for s in range(0, num_of_vehicles):
            self.name.append(s)


    def spawn(self):

        """Start roscore"""
        self.roscore = subprocess.Popen('roscore', stdout=subprocess.PIPE, shell=True)
        self.roscore_pid = self.roscore.pid
        time.sleep(5)
        rospy.init_node('twentytwo', anonymous=True)

        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(uuid)

        #Object to launch empty world
        launch = roslaunch.parent.ROSLaunchParent(uuid,["/home/ivory/VersionControl/catvehicle_ws/src/catvehicle/launch/catvehicle_empty.launch"])

        #Object to spawn catvehicle in the empty world

        cli_args = []
        spawn_args = []
        spawn_file = []
        self.launchspawn = []
        launchfile = ['/home/ivory/VersionControl/catvehicle_ws/src/catvehicle/launch/humancar_spawn.launch']
        humanlaunchfile = ['/home/ivory/VersionControl/catvehicle_ws/src/catvehicle/launch/humancar_spawn.launch']
        for n in range(0, 3):
            print(n)
            cli_args.append(['X:='+ str(self.X[n]), 'robot:='+ str(self.name[n])])
            print(cli_args[n][0:])
            spawn_file.append([(roslaunch.rlutil.resolve_launch_arguments(launchfile)[0], cli_args[n])])
            self.launchspawn.append(roslaunch.parent.ROSLaunchParent(uuid, spawn_file[n]))

        for n in range(3, self.num_of_vehicles):
            print(n)
            cli_args.append(['X:='+ str(self.X[n]), 'robot:='+ str(self.name[n])])
            print(cli_args[n][0:])
            spawn_file.append([(roslaunch.rlutil.resolve_launch_arguments(humanlaunchfile)[0], cli_args[n])])
            self.launchspawn.append(roslaunch.parent.ROSLaunchParent(uuid, spawn_file[n]))

        launch.start()
        print('Empty world launched.')
        time.sleep(3)

        for n in range(0, self.num_of_vehicles):
            print('Vehicle' + str(n) + ' spawning')
            self.launchspawn[n].start()
            time.sleep(20)


    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C!')
        print('############################################')

        print('Terminating spawn launches')
        for n in range(0, self.num_of_vehicles):
            self.launchspawn[n].shutdown()

        print('Now killing roscore')
        #kill the child process of roscore
        try:
            parent = psutil.Process(self.roscore_pid)
            print(parent)
        except psutil.NoSuchProcess:
            print("Parent process doesn't exist.")
            return
        children = parent.children(recursive=True)
        print(children)
        for process in children:
            print("Attempted to kill child: " + str(process))
            process.send_signal(signal.SIGTERM)

        #kill the roscore
        self.roscore.terminate()
        #Wait to prevent the creation of zombie processes.
        self.roscore.wait()

        call(["pkill", "ros"])
        call(["pkill", "gzserver"])
        call(["pkill", "gzclient"])

        sys.exit(0)


def main(argv):
    cl = catlaunch(22)
    print(cl.X)

    cl.spawn()

    signal.signal(signal.SIGINT, cl.signal_handler)
    print('Press Ctrl+C')
    signal.pause()

if __name__ == '__main__':
    main(sys.argv[1:])

