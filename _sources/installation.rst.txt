Installation
---------------

catvehicle can be used with ROS Melodic or ROS Noetic. For this installation in particular we will be using ROS Noetic. 


Virtual Machine Installation 
+++++++++++++++++++++++++++++++++

This is the installation of virtual software to host Ubuntu 20.04. 
There are several virtualization softwares. We recommend using VMWare which is provided through The University of Arizona software licensing. 
If you are running windows, you may also use dual boot. 
In this section we will go over how to install VMWare on your machine. 

.. note:: 
    If you have an Ubuntu running system, you do not need to install a virtual machine software. 
    This tutorial does not go over how to install VirtualBox or Dual boot, though those are options. 

VMware
^^^^^^^^^
For this section you may use the `software license <https://e5.onthehub.com/WebStore/ProductsByMajorVersionList.aspx?cmi_cs=1&cmi_mnuMain=16a020b5-ed3c-df11-b4ab-0030487d8897&ws=c6fcd2a5-a432-de11-9d57-0030485a8df0&vsro=8>`_ through The University of Arizona.
If you do not have an account, you may use the `Free VMware for  Windows or Linux. <https://my.vmware.com/en/web/vmware/free#desktop_end_user_computing/vmware_work station_player/15_0>`_ 
For Mac you need the `Free Fushion VMware License. <https://my.vmware.com/en/web/vmware/free#desktop_end_user_computing/vmware_work station_player/15_0>`_

.. caution::
    Make sure to choose VMware Workstation 16.x Pro for a Windows or Linux computer 
    and VMware Fushion 12 Pro for Mac. 

For Mac:
----------
Once you have downloaded VMware Fusion 12 Pro, open the disk image file and double click to install. 
You will get a pop up saying "VMware Fusion is an app downloaded from the internet", go ahead and open it. 
Then you need to authenticate and allow the application to run.
After the initialization screen, allow the system extension to proceed through the system preference. 
To do this you need to click on the open system preference, and allow for the system extension. 
Agree to the Lincense. 

.. note:: 
    If you were able to download VMWare through The University of Arizona, go ahead and enter the license number. 
    If you got it through the website for free, go ahead and select the option to try VMware for 30 days. 

Click Done after the installation has been completed. 

For Windows: 
--------------
Once you have downloaded VMware Workstation 16x Pro, open the disk image file right click on it and run as an administrator. 
Click next on all the windows, if you obtained the license through The University of Arizona, you may enter the license number. 
If not you may do select the 30 day trial. 

VirtualBox
^^^^^^^^^^^^
You may download `VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_ from its website. 
Select your computer's operating system. Once downloaded, you may install it. 

Dual Boot
^^^^^^^^^^^^^
This option works well with Windows already installed. You will need an empty USB drive.


Ubuntu Desktop Download 
++++++++++++++++++++++++
This section will help with installing Ubuntu 20.04 LTS.

.. note:: 
   If you already have Ubuntu 20.04 LTS as your running system you may skip to the next section where we install ROS. 

Before Installing 
^^^^^^^^^^^^^^^^^^^^^^
Before we continue, please make sure to have your virtual software up and running.
The installation works with VMWare or VirtualBox.

Istallation Steps for VMware: 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Download Ubuntu Desktop from the `Ubuntu Download Page <https://ubuntu.com/download/desktop>`_
2. Make sure it is Ubuntu 20.04.2.0 LTS.
3. Open VMware and select **Create a new virtual machine**. 
4. In the *New Virtual Wizard* select **I will instal the operating system later.** 
5. Next, select the operating system **Linux** with **Ubuntu 64-bit** as the version. 
6. Click **Next**, you may choose to rename your system, and chose a path for the virtual machine. 
7. Select your **Maximum disk size (GB)** to be at least **100** and **Split virtual disk into multiple files**
8. Click *Next*, then click on **customize hardware** and change the *Memory* from 2GB to **8GB**. 
9. Scroll down to the **New CD/DVD (SATA)** option and select **Use ISO inage file:** find Ubuntu image you had previously downloaded. 
10. Click on **close** then **finish**.
11.  Your newly instlaled virtual machine should be displayed on the left side panel. Click on **Play Virtual Machine**. 
12. Once the Welcome screen appears, select the language and **Install Ubuntu**.
13. In the *Updates and Other Software screen* make sure to select **Normal installation** and click continue. 
14. In the *Installation type* screen select **Erase disk and install Ubutu**. 
15. Click **Install now** and then **continue**. 
16. Select your region and then complete the user information screen. 
17. Click on complete installation, and wait until the installation to complete. 
18. Once the installation is complete click on **restart now** and wait for the system to restart. 

Now you should have a login screen and ready to move on to the next step of the installation. 


ROS-noetic Installation 
+++++++++++++++++++++++++

If you got this far, you should have Ubuntu 20.04.2.0 LTS running. 

In this section we will be installing and making sure that ROS is running. 
You may visit the official site at `Ubuntu install of ROS Noetic <http://wiki.ros.org/noetic/Installation/Ubuntu>`_

.. caution:: 
   Make sure to choose Noetic for Ubuntu.

.. raw::html
    <iframe width="560" height="315" src="https://www.youtube.com/embed/ZNqekNFKDuc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
 
.. video::Ros-noetic-installation.mov   

Set up your source list, to make sure your software accepts ROS packages: 
:: 
   sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'  

Set your keys:
::
   sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

Make sure your Debian package index is up to date: 
::
   sudo apt update
   
Install ROS-Full-Desktop: 
::
   sudo apt install ros-noetic-desktop-full

Set up your environment (you must source this script in every bash terminal you use ROS in):
::
   source /opt/ros/noetic/setup.bash

Install Tool for building packages: 
:: 
   sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential

Install and initialize rosdep to use many ROS tools: 

Install: 
::
   sudo apt install python3-rosdep

Initialize: 
::
   sudo rosdep init


Now that you have ROS install, you may test it by running: 
::
   roscore

This will run ROS and get something like: 

.. image:: roscore-output.jpg


Installing the CATvehicle Simulator
++++++++++++++++++++++++++++++++++++

.. note::
    You can find the instructions on the github repository at: https://github.com/jmscslgroup/catvehicle/tree/noetic_gazebo-11
    
    Make sure that you are using the **Noetic-gazebo-11 branch**, this is cruicial for a successful installation. 

.. raw::html
    <iframe width="560" height="315" src="https://www.youtube.com/embed/CsjsgmYSqYs" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>    

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

Video tutorials
================
1. Installations and Quick Start
------------------------------------

This tutorial video demonstrates how to install :code:`Ros-noetic`.

..  youtube:: ZNqekNFKDuc
    :aspect: 16:9


This tutorial video demonstrates how to install :code:`CATvehicle Simulator`.

..  youtube:: CsjsgmYSqYs
   :aspect: 16:9
