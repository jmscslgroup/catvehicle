#!/usr/bin/env python


# Author : Rahul Bhadani
# Initial Date: Nov 15, 2020
# License: MIT License

#   Permission is hereby granted, free of charge, to any person obtaining
#   a copy of this software and associated documentation files
#   (the "Software"), to deal in the Software without restriction, including
#   without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to
#   permit persons to whom the Software is furnished to do so, subject
#   to the following conditions:

#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.

import rospy
import sys, getopt
import tensorflow as tf
print("Loaded Tensorflow version {}".format(tf.__version__))
import os, sys
import pandas as pd
import numpy as np
import pickle


from std_msgs.msg import String, Header, Float64
from geometry_msgs.msg  import Twist, Pose, PoseStamped
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import Point

from catvehicle import safe_accel

class rlpredict():
    """
    Python class for rlprediction

    Parameters
    ----------

    ns: `str`
        Nampespace of the robot model (i.e., AV)

    policy_model: `tf.keras.Sequential`
        RL-trained policy model

    vf_model: `tf.keras.Sequenctial`
        RL-trained value function model

    ego_cmdvel_topic: `str`
        What's the topic on which commanded velocity of ego vehicle is to be published

    leadvel_topic: `str`
        What's the topic on which leader's velocity is being published

    relvel_topic: `str`
        What's the topic on which relative velocity is being broadcasted

    leaddist_topic: `str`
        What's the topic on which leader's relative distance is being published

    egovel_topic: `str`
        What's the topic on which ego's velocity is being published


    Attributes
    -----------

    ns: `str`
        Nampespace of the robot model (i.e., AV)

    policy_model: `tf.keras.Sequential`
        RL-trained policy model

    vf_model: `tf.keras.Sequenctial`
        RL-trained value function model

    ego_cmdvel_topic: `str`
        What's the topic on which commanded velocity of ego vehicle is to be published

    leadvel_topic: `str`
        What's the topic on which leader's velocity is being published

    relvel_topic: `str`
        What's the topic on which relative velocity is being broadcasted

    leaddist_topic: `str`
        What's the topic on which leader's relative distance is being published

    egovel_topic: `str`
        What's the topic on which ego's velocity is being published


    """

    def __init__(self, ns, policy_model, vf_model, ego_cmdvel_topic = None, leadvel_topic = None, relvel_topic = None, leaddist_topic = None, egovel_topic = None, headway_scale = 1000, speed_scale = 50):

        # variables for holding data
        self.leaddist = None
        self.egovel = None
        self.relvel = None
        self.leadervel = None
        self.leaderaccel = None
        self.egoaccel = None
        self.total_dist = 0

        self.old_leaddist = None
        self.old_egovel = None
        self.old_leadervel = None
        self.old_leaderaccel = None
        self.old_egoaccel = None

        self.old_cmdvel = 0

        # last and current time
        self.last_leadveltime = None
        self.last_egoveltime = None
        self.last_disttime = None
        self.current_leadveltime = None
        self.current_egoveltime = None
        self.current_disttime = None

        self.last_pubtime = None
        self.current_pubtime = None

        # new message flag
        self.newlead_msg = False
        self.newego_msg = False
        self.newdist_msg = False
        self.newrelvel_msg = False

        self.first = False


        self.policy_model = None
        self.vf_model = None

        if os.path.exists(policy_model):
            self.policy_model = tf.keras.models.load_model(policy_model)
        else:
            rospy.logerror("Error reading filepath {} for policy model.")

        if os.path.exists(vf_model):
            self.vf_model = tf.keras.models.load_model(vf_model)
        else:
            rospy.logerror("Error reading filepath {} for value-function model.")

        self.headway_scale = headway_scale
        self.speed_scale = speed_scale

        self.leadvel_topic = leadvel_topic
        self.relvel_topic = relvel_topic

        if ego_cmdvel_topic is not None:
            self.ego_cmdvel_topic = ego_cmdvel_topic
        else:
            self.ego_cmdvel_topic = 'cmd_vel'

        self.ego_cmdaccel_topic = 'accel'

        if leaddist_topic is not None:
            self.leaddist_topic = leaddist_topic
        else:
            self.leaddist_topic = 'distanceEstimatorSteeringBased/dist'

        if egovel_topic is not None:
            self.egovel_topic = egovel_topic
        else:
            self.egovel_topic = 'vel'


        self.ns = ns
        rospy.init_node("rl_predict", anonymous=True)

        # publishers
        self.egocmdvel_pub = rospy.Publisher(self.ego_cmdvel_topic, Twist, queue_size = 1)
        self.egocmdaccel_pub = rospy.Publisher(self.ego_cmdaccel_topic, Twist, queue_size = 1)

        # subscribers

        # if leadvel topic is None, we will estimate leader's velocity from leaddist and ego velocity
        if self.leadvel_topic is not None:
            self.leadvel_sub = rospy.Subscriber(self.leadvel_topic, Twist, self.leadvel_cb )

        # if relative vel topic is None, we will estimate relative velocity from leaddist
        if self.relvel_topic is not None:
            self.relvel_sub = rospy.Subscriber(self.relvel_topic, Twist, self.relvel_cb )

        self.distance_sub = rospy.Subscriber(self.leaddist_topic, Float64, self.leaddist_cb)
        self.egovel_sub = rospy.Subscriber(self.egovel_topic, Twist, self.egovel_cb)

    def leadvel_cb(self, data):
        """
        Call back function for leader's velocity subscriber

        """
        self.old_leadervel = self.leadervel

        self.leadervel = data.linear.x

        # Assign current velocity time to the last velocity time before getting a new time
        self.last_leadveltime = self.current_leadveltime

        self.current_leadveltime = rospy.Time.now()

        if (self.last_leadveltime is not None) and (self.current_leadveltime is not None):
            duration = self.current_leadveltime - self.last_leadveltime
            deltaT = duration.to_sec()
            self.total_dist = self.total_dist + self.leadervel*deltaT
            #self.total_dist = self.total_dist%50.0
            if deltaT == 0.0:
                self.newlead_msg = False
                return

            # Calculate instantaneous acceleration
            self.leaderaccel = (self.leadervel -self.old_leadervel)/deltaT

        self.newlead_msg = True

    def egovel_cb(self, data):
        """
        Call back function for ego's velocity subscriber

        """
        self.old_egovel = self.egovel
        self.egovel = data.linear.x

        # Assign current velocity time to the last velocity time before getting a new time
        self.last_egoveltime = self.current_egoveltime

        self.current_egoveltime = rospy.Time.now()

        if (self.last_egoveltime is not None) and (self.current_egoveltime is not None):
            duration = self.current_egoveltime - self.last_egoveltime
            deltaT = duration.to_sec()

            if deltaT == 0.0:
                self.newego_msg = False
                return

            # Calculate instantaneous acceleration
            self.egoaccel = (self.egovel -self.old_egovel)/deltaT

        self.newego_msg = True

    def relvel_cb(self, data):
        """
        Call back function for relative velocity subscriber

        """
        self.relvel = data.linear.x
        self.newrelvel_msg = True

    
    def leaddist_cb(self, data):
        """
        Call back function for relative distance subscriber

        """
        self.leaddist = data.data
        if self.relvel_topic is None:
            self.old_leaddist = self.leaddist
            # Assign current distance time to the last distance time before getting a new time
            self.last_disttime = self.current_disttime
            self.current_disttime = rospy.Time.now()
            if (self.last_disttime is not None) and (self.current_disttime is not None):
                duration = self.current_disttime - self.last_disttime
                deltaT = duration.to_sec()
                if deltaT == 0.0:
                    self.newdist_msg = False
                    return
                # Calculate instantaneous acceleration
                self.relvel = (self.leaddist -self.old_leaddist)/deltaT

        self.newdist_msg = True

    def publish(self):
        """
        Publish function for rlpredict class

        """
        new_vel = 0

        if self.leadvel_topic is None:
            self.leadervel = self.leaddist + self.egovel

        if np.any([self.newdist_msg, self.newego_msg, self.newlead_msg, self.newrelvel_msg]):
            
            rospy.loginfo("Input ego velocity: {}".format(self.egovel))
            rospy.loginfo("Input leader velocity: {}".format(self.leadervel))
            rospy.loginfo("Input lead distance: {}".format(self.leaddist))
            rospy.loginfo("Total distance covered modulo 50 by ego: {}".format(self.total_dist))
            state = np.array([[self.egovel/self.speed_scale, self.leaddist/self.headway_scale, self.leadervel/self.speed_scale, 0, (self.total_dist/50.0)%50]])

            rospy.loginfo("Input state is {}".format(state))
            policy_prediction = self.policy_model.predict(state)
            value_prediction = self.vf_model.predict(state)

            rospy.loginfo("Reward for current prediction is {}".format(value_prediction[0][0]))

            rospy.loginfo("Mean acceleration from current prediction is {}".format(policy_prediction[0][0]))

            rospy.loginfo("Log of standard deviation of acceleration from current prediction is {}".format(policy_prediction[0][1]))

            new_accel = policy_prediction[0][0]

           


            self.last_pubtime = self.current_pubtime
            self.current_pubtime = rospy.Time.now()
            if (self.last_pubtime is not None) and (self.current_pubtime is not None):
                duration = self.current_disttime - self.last_disttime
                deltaT = duration.to_sec()
                if deltaT == 0.0:
                    return
                
                if not self.first:
                    if new_accel < 0.0:
                        new_accel = 0.1
                    self.first = True 

                modified_accel = safe_accel(new_accel, self.egovel, self.leadervel, self.leaddist, deltaT)

                #new_vel = self.old_cmdvel + new_accel*deltaT
                
                new_vel = self.old_cmdvel + modified_accel*deltaT
                
                if new_vel < 0.0001:
                    new_vel = 0
                new_vel_msg = Twist()
                rospy.loginfo("Predicted velocity for the ego is {}".format(new_vel))
                new_vel_msg.linear.x = new_vel
                new_vel_msg.linear.y = 0.0
                new_vel_msg.linear.z = 0.0
                new_vel_msg.angular.x = 0.0
                new_vel_msg.angular.y = 0.0
                new_vel_msg.angular.z = 0.0
                self.egocmdvel_pub.publish(new_vel_msg)

                new_accell_msg = Twist()
                rospy.loginfo("Predicted velocity for the ego is {}".format(new_vel))
                new_accell_msg.linear.x = modified_accel
                new_accell_msg.linear.y = new_accel
                new_accell_msg.linear.z = 0.0
                new_accell_msg.angular.x = 0.0
                new_accell_msg.angular.y = 0.0
                new_accell_msg.angular.z = 0.0

                self.egocmdaccel_pub.publish(new_accell_msg)

            self.newdist_msg = False
            self.newego_msg = False
            self.newlead_msg = False
            self.newrelvel_msg = False
            self.old_cmdvel = new_vel
            
            

def main(argv):
    ns = rospy.get_namespace() # Retrieve namespace this way appends '/' at the end as well
    ns = ns[0:-1]

    argv = argv[:-2]

    policy_model = argv[0]
    print("Policy model is {}".format(policy_model))
    vf_model = argv[1]
    print("VF model is {}".format(vf_model))
    
    if len(argv) > 2:
        distance_topic = argv[2]
        print("distance_topic model is {}".format(distance_topic))
    else:
        distance_topic = None

    if len(argv) > 3:
        leadvel_topic = argv[3]
        print("leadvel_topic model is {}".format(leadvel_topic))
    else:
        leadvel_topic = None

    if len(argv) > 4:
        relvel_topic = argv[4]
        print("relvel_topic model is {}".format(relvel_topic))
    else:
        relvel_topic = None

    node = rlpredict(ns, policy_model=policy_model, vf_model=vf_model, leadvel_topic=leadvel_topic, relvel_topic=relvel_topic, leaddist_topic = distance_topic)

    rate= rospy.Rate(20)

    while not rospy.is_shutdown():
        if rospy.get_param("/execute", False):
            node.publish()
            rate.sleep()

if __name__ == '__main__':
    main(sys.argv[1:])
