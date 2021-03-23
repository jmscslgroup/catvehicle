Installing the CATvehicle Simulator
++++++++++++++++++++++++++++++++++++

.. note::
    You can find the instructions on the github repository at: https://github.com/jmscslgroup/catvehicle/tree/noetic_gazebo-11
    
    Make sure that you are using the **Noetic-gazebo-11 branch**, this is cruicial for a successful installation. 

First, let's make sure that all the necessary packages are installed for the simulator to run properly. 
::
    sudo apt-get update
    sudo apt-get install ros-noetic-controller-manager
    sudo apt-get install ros-noetic-ros-control ros-noetic-ros-controllers
    sudo apt-get install ros-noetic-gazebo-ros-control
    sudo apt-get install ros-noetic-velodyne

Let's create a working space: 
::
    cd ~
    mkdir -p catvehicle_ws/src
    cd catvehicle_ws/src
    catkin_init_workspace
    cd ..
    catkin_make

Now you may clone the Github repository and other dependent package into your src directory
::
    cd ~/catvehicle_ws/src
    git clone https://github.com/jmscslgroup/catvehicle
    git clone https://github.com/jmscslgroup/obstaclestopper
    git clone https://github.com/jmscslgroup/control_toolbox
    git clone https://github.com/jmscslgroup/sicktoolbox
    git clone https://github.com/jmscslgroup/sicktoolbox_wrapper
    git clone https://github.com/jmscslgroup/stepvel
    git clone https://github.com/jmscslgroup/cmdvel2gazebo
    cd catvehicle
    git checkout noetic_gazebo-11 
    cd ..
    cd ..
    catkin_make

Source workspace to the environment path
::
    echo "source ~/catvehicle_ws/devel/setup.bash" >> ~/.bashrc
    source ~/.bashrc
    source ./devel/setup.bash

Run the CATvehicle using ROS
::
    roslaunch catvehicle catvehicle_neighborhood.launch

Open a new Tab and check to see the Rostopic list 
::
    rostopic list

Source the workspace on the newly opened tab: 
::
    source devel/setup.bash

Finally launch Gagebo
:: 
    gzclient

Congratulations, now have a CATvehicle running simulator! 

Installations and Quick Start
------------------------------------
    
This tutorial video demonstrates how to install :code:`CATvehicle Simulator`.

..  youtube:: CsjsgmYSqYs
   :aspect: 16:9
