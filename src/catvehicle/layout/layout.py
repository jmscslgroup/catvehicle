#!/usr/bin/env python
# Initial Date: November 2020
# Author: Rahul Bhadani
# Copyright (c)  Rahul Bhadani, Arizona Board of Regents
# All rights reserved.

""" This script helps launch a fleet of n cars. """

__author__ = 'Rahul Bhadani'
__email__  = 'rahulbhadani@email.arizona.edu'

from datetime import timedelta
import logging
_LOGGER= logging.getLogger(__name__)

import sys, time, subprocess, os, datetime, glob, psutil, signal
from subprocess import call

import rospkg, rostopic, roslaunch, rospy
from gazebo_msgs.srv import GetPhysicsProperties
from gazebo_msgs.srv import SetPhysicsProperties

from ..launch import launch
class layout:
    """
     
     `layout`: Base class for Simulation for Connected-and-Inteligent-Vehicle CPS. 
    Creates simulation layout for simulating vehicles and control.

    Parameters
    -------------
    X: `list`, `double`
        x-coordinate of vehicles's position in the world frame of reference
    
    Y: `list`, `double`
        y-coordinate of vehicles's position in the world frame of reference
    
    Yaw: `list`, `double`
        yaw of all the vehicles in the world frame of reference
    
    n_vehicles: `integer`
        Number of vehicles to spawn in the simulation
    
    max_update_rate: `double`
        Maximum Update Rate for Physics Engine (e.g. Gazebo) Simulator

        Default Value: 100 Hz

    time_step: `double`
        Time Step size taken by time-step solver during simulation
        
        Default Value: 0.01 seconds

    update_rate: `double`
        Update Rate to publish new state information by decoupled vehicle model
        
        Default Value: 20 Hz

    record_time: `double`
        Amount of time in seconds to capture data while running the simulation
        
        Default Value: 60.0 seconds

    description: `string`
        A descriptive text about the current simulation run
        Default Value: "Sparkle simulation"

    Attributes
    -----------
    X: `list`, `double`
        x-coordinate of vehicles's position in the world frame of reference

    Y: `list`, `double`
        y-coordinate of vehicles's position in the world frame of reference
    
    Yaw: `list`, `double`
    
    n_vehicles: `double`
        Number of vehicles to spawn in the simulation
    
    max_update_rate: `double`
        Maximum Update Rate for Physics Engine (e.g. Gazebo) Simulator. 
        Default Value: 100 Hz
    
    time_step: `double`
        Time Step size taken by time-step solver during simulation
        Default Value: 0.01 seconds
    
    record_time: `double`
        Amount of time in seconds to capture data while running the simulation
        Default Value: 60.0 seconds
    
    description: `string`
        A descriptive text about the current simulation run
        Default Value: "Sparkle simulation"
    
    callflag:`dictionary`
        Dictionary to keep track of executation sequence of different class function
    
    uuid:
        A universally unique identifier (UUID)  for roslaunch
    
    bagdir: `string`
        Path where ROSBags is saved

    gzstatsfile: `string`
        Filepath of simulation statistics file.    
        
    bagfile: `string`
        Filepath of the rosbag saved at the end of the simulation.
        
    """
    def __init__(self, n_vehicles=1, X=0, Y=0, Yaw=0.0, **kwargs) -> None:

        # Kill any existing ROS and gzserver and gzclient
        call(["pkill", "ros"])
        call(["pkill", "gzserver"])
        call(["pkill", "gzclient"])
        call(["pkill", "rosbag"])
        call(["pkill", "record"])
        time.sleep(1)

        
        _LOGGER.info("Creating simulation layout")
        # Define attributes for layout class
        self.package_name = "catvehicle"
        self.n_vehicles = n_vehicles
        self.X = X # X-Coordinates of all the vehicles.
        self.Y = Y # Y-Coordinates of all the vehicles.
        self.Yaw = Yaw #Yaw of all the vehicles.
        self.max_update_rate = kwargs.get("max_update_rate", 100)
        self.time_step = kwargs.get("time_step", 0.01)
        self.record_time = kwargs.get("record_time", 60.0)
        self.description = kwargs.get("description", "CAT Vehicle simulation with {0} cars.".format(self.n_vehicles))
        self.bagdir = kwargs.get("bagdir", "./")
        self.gzstatsfile = None
        self.bagfile = None

        # get an instance of RosPack with the default search paths
        rospack = rospkg.RosPack()
        self.package_path = ''
        try:
            self.package_path = rospack.get_path(self.package_name)
        except rospkg.ResourceNotFound as s:
            print("Package "+ str(s.args[0])+ " Not Found")
            raise

        self.callflag = {
            "bagrecord": False,
            "roscore": False,
            "physics_engine": False,
            "rviz": False,
            "control": False, 
        }
        self.rviz_process = None
        self.gzstats = None
        self.gzclient = None

        self.rosbag_cmd = None
        self.roscore_pid = None
        self.rosbag_pid = None
        self.rviz_pid = None
        self.gzclient_pid = None

        self.launchcontrol_obj = []


    def checkroscore(self, uri = "localhost", port = 11311):
        """
         Checks if roscore is running

        Parameters
        -------------
        uri: `string`
            Specifies ROS_MASTER_URI
            A valid IP address string or resolvable hostname
        port: `integer` [0-65535]
            port number where roscore will start
            A valid port ranges from 0 to 65535 but note that not all port numbers are allowed.

        Returns
        ---------
        `boolean`
            Returns `True` if roscore is running otherwise returns false

        """
        os.environ["ROS_MASTER_URI"] = "http://"+uri+":"+str(port)
        roscore_status = False
        try:
            rostopic.get_topic_class('/rosout')
            roscore_status = True
        except rostopic.ROSTopicIOException as e:
            roscore_status = False
            pass
        return roscore_status

    def roscore(self, uri = "localhost", port = 11311):
        """
        layout.roscore(uri="localhost", port=11311)
        Starts the roscore.

        Sets the `layout.callflag["roscore"]` to `True` only if the roscore is started locally by this particular simulation call.

        Parameters
        -------------
        uri: `string`
            Specifies ROS_MASTER_URI
            A valid IP address string or resolvable hostname
        port: `integer` [0-65535]
            port number where roscore will start
            A valid port ranges from 0 to 65535 but note that not all port numbers are allowed.

        """
        os.environ["ROS_MASTER_URI"] = "http://"+uri+":"+str(port)
        if self.checkroscore(uri, port):
            return
        self.roscore = subprocess.Popen('roscore -p ' + str(port), stdout=subprocess.PIPE, shell=True)
        self.roscore_pid = self.roscore.pid

        self.callflag["roscore"] = True
        time.sleep(5)



    def bagrecord(self, prefix = "catvehicle", **kwargs):
        """
        Performs rosbag record

        The function starts rosbag record in a subprocess and saved PID identifier.
        It also start logging gz stat metrics for post-analysis of simulation.

        Parameters
        -------------
        bagdir: `string`
            Path/Directory where ROS Bag will be saved

        prefix: `string`
            A descriptive string to be prefixed at the beginning of bag file name.


        """
        self.bagdir = kwargs.get("bagdir", "./")
        self.record_time = kwargs.get("record_time", 60.0)
        # if logdir path doesn't exist, then create
        if not os.path.exists(self.bagdir):
            os.mkdir(self.bagdir)

        # specify rosbag record command with different flags, etc.
        command = ["rosbag "+ " record "+ "-a "+ " -o " + self.bagdir + "/" + prefix + "_n_" + str( self.n_vehicles) +  '_max_update_rate_' + str(self.max_update_rate) + '_time_step_' + str(self.time_step) + '_recordtime_' + str(self.record_time) + ' --duration=' + str(self.record_time) +  ' __name:=bagrecorder']

        _LOGGER.info("Starting rosbag record with the command: {}".format(command))
        self.rosbag_cmd = subprocess.Popen(command, shell=True, executable='/bin/bash')
        self.rosbag_pid = self.rosbag_cmd.pid
        time.sleep(5)

        # Write Gazebo stats
        dt_object = datetime.datetime.fromtimestamp(time.time())
        dt = dt_object.strftime('%Y-%m-%d-%H-%M-%S-%f')
        self.gzstatsfile = self.bagdir + "/gzstats_" + dt  + ".txt"
        self.gzstats = subprocess.Popen(["gz stats > " + self.gzstatsfile ], shell=True)
        
        self.callflag["bagrecord"] = True

        # sleep for 10 seconds plus 0.5 seconds for each vehicles
        time.sleep(10 + self.n_vehicles/2)

    def stoprecord(self):
        """
        Stop the recording of rosbag file.
        
        The function gracefully terminates the `rosbag record` command and waits until the bag file writing is complete.
        The function also reindexes the bag file in case the rosbag record terminates prematurely.

        """
        if not self.callflag["bagrecord"]:
            return
        
        _LOGGER.info("Stopping rosbag record")
        self.rosbag_cmd.send_signal(subprocess.signal.SIGINT)
        bagkiller = subprocess.Popen(["rosnode kill /bagrecorder"], shell=True)

        ## Check of .bag.active is still being written
        print("Retrieving the latest bag file")
        current_path = os.getcwd()
        os.chdir(self.bagdir)
        list_of_files1 = glob.glob('*.bag')
        list_of_files2 = glob.glob('*.bag.active')
        list_of_files = list_of_files1 + list_of_files2
        bagconverted = False
        if len(list_of_files) != 0:
            latest_file = max(list_of_files, key=os.path.getctime)
            if "bag.active" in latest_file[-10:]:
                    try:
                        filesize = os.path.getsize(latest_file)
                    except OSError as err:
                        _LOGGER.info("OS error: {0}".format(err))
                        sys.exit()
                    counter = 0
                    while True:
                        try:
                            time.sleep(2)
                            newfilesize = os.path.getsize(latest_file)
                            byteswritten = newfilesize - filesize
                            if byteswritten == 0.0:
                                counter = counter + 1
                            
                            print("Bag file is still being written. Bytes written: {}".format(byteswritten))
                            
                            if counter > 10:
                                print("Something went wrong while saving the bag file, exiting. Please restart the simulation.")
                                self.killroscore()
                                sys.exit()
                        except OSError as err:
                            print('.active bag file is gone.')
                            list_of_files1 = glob.glob('*.bag')
                            list_of_files2 = glob.glob('*.bag.active')
                            list_of_files = list_of_files1 + list_of_files2
                            latest_file_written = max(list_of_files, key=os.path.getctime)
                            if (latest_file_written[:-4] == latest_file[:-11]):
                                _LOGGER.info("Bag file {} successfully written".format(latest_file_written))
                            else:
                                _LOGGER.info("Something went wrong while finising the  writing of {}.".format(latest_file))
                            bagconverted = True
                            break
                        if byteswritten == 0:
                            break
                        else:
                            filesize = newfilesize

        _LOGGER.info("Bag file {} saved successfully.")
        stdout = bagkiller.communicate()
        _LOGGER.info('rosnode kill: {}'.format(stdout))
        time.sleep(5+self.n_vehicles)
        
         #check if bag file has been killed:
        psaef = subprocess.Popen(["ps -aef | grep bagrecorder"], shell=True)
        stdout = psaef.communicate()
        _LOGGER.info('ps -aef  STDOUT:{}'.format(stdout))
        call(["pkill", "rosbag"])
        call(["pkill", "record"])
        self.gzstats.terminate()
        os.chdir(current_path)

    def killroscore(self):
        """
        Terminates roscore

        """
        if not self.callflag["roscore"]:
            return
        
        _LOGGER.info("Killing roscore.")
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
        # Unconditionally trying to Kill ROS, useful in a situation where ros master was started by someone else.
        call(["pkill", "ros"])

    def physicsengine(self, **kwargs):
        """
        Starts physics engine simulator
        Currently, only Gazebo is supported

        Sets the `layout.callflag["physics_engine"]` to `True`.

        """
        initial_world = kwargs.get("initial_world", self.package_path + "/launch/catvehicle_empty.launch")
        initial_launch = launch(launchfile=initial_world)
        initial_launch.start()
        _LOGGER.info("Physics world created.")
        self.callflag["physics_engine"] = True
        time.sleep(5)

    def rviz(self):
        """
        starts the ros-rviz for visualizing vehicle's path, point cloud, etc.

        Sets the `layout.callflag["rviz"]` to `True`.

        """
        _LOGGER.info("Starting RVIZ.")
        self.rviz_process = subprocess.Popen(["sleep 3; rosrun rviz rviz -d {}".format(self.package_path + "/config/api.rviz")], stdout=subprocess.PIPE, shell=True)
        self.rviz_pid = self.rviz_process.pid
        self.callflag["rviz"] = True
        
    def create(self, uri="localhost", port=11311):
        """
        layout.create(uri="localhost", port=11311)
        
        Class method `create()` creates the simulation environment. If roscore has not started, then this function starts roscore as well by calling `layout.roscore()`.  If there is an already running roscore for given uri and port, it doesn't start the roscore.

        It also checks if a physics world (e.g. Gazebo world) is present or not, if not, it also calls `layout.phsyicsengine()` to create a simulated physics world. 
        
        Finally `create` sets desired physics   properties such as max step size and max update rate.
        
        Parameters
        -------------
        uri: `string`
            Specifies ROS_MASTER_URI
            A valid IP address string or resolvable hostname
        port: `integer` [0-65535]
            port number where roscore will start
            A valid port ranges from 0 to 65535 but note that not all port numbers are allowed.

        """
        # If roscore has not started yet, then start the roscore
        if not self.callflag["roscore"]:
            self.roscore(uri, port)
        
        self.uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        # Create a new ROS Node
        rospy.init_node('catvehicle_layout', anonymous=True)
        roslaunch.configure_logging(self.uuid)

        if not self.callflag["physics_engine"]:
            self.physicsengine()
        
        self.gzclient = subprocess.Popen(["gzclient"], stdout=subprocess.PIPE, shell=True)
        self.gzclient_pid = self.gzclient.pid

        rospy.wait_for_service('gazebo/get_physics_properties')
        rospy.wait_for_service('gazebo/set_physics_properties')

        get_physics_properties_prox = rospy.ServiceProxy('gazebo/get_physics_properties', GetPhysicsProperties)
        physics_properties = get_physics_properties_prox()

        physics_properties.max_update_rate = self.max_update_rate
        physics_properties.time_step = self.time_step

        set_physics_properties_prox = rospy.ServiceProxy('gazebo/set_physics_properties', SetPhysicsProperties)
        set_physics_properties_prox(physics_properties.time_step,
                                    physics_properties.max_update_rate,
                                    physics_properties.gravity,
                                    physics_properties.ode_config)
        time.sleep(4)

        get_physics_properties_prox = rospy.ServiceProxy('gazebo/get_physics_properties', GetPhysicsProperties)
        physics_properties = get_physics_properties_prox()
        print("Current  max_update_rate is {}".format( physics_properties.max_update_rate))

        if physics_properties.max_update_rate != self.max_update_rate:
            print("Max Update Rate was not set properly, terminating simulation. Please restart the simulation.")
            sys.exit()

    def spawn(self, include_laser = None):
        '''
        `layout.spawn()` spawns the simulated vehicles in the physics world.

        Parameters
        -------------
        include_laser: Union["all", "lead", None, `list`]
            specifies whether to include laser in each car.
            ALL means include laser in every car
            Lead means include laser only in first car
            None means do not include laser in any car
            `list` specifies indices for which to include laser

        '''
        # #Object to spawn catvehicle in the empty world

        laser_flag = [False]*self.n_vehicles
        if include_laser.lower() == "all":
            laser_flag = [True]*self.n_vehicles
        elif  include_laser.lower() == "lead":
            laser_flag[0] = True
        elif isinstance(include_laser, list):
            for n in range(0, self.n_vehicles):
                if n in include_laser:
                    laser_flag[n] = True

        self.launch_obj = []
        for n in range(0, self.n_vehicles):
            launch_itr = launch(launchfile=self.package_path + '/launch/catvehicle_spawn.launch', X  = self.X[n], Y=self.Y[n], yaw = self.Yaw[n], robot = "catvehicle_{:03d}".format(n), laser_sensor =laser_flag[n])
            self.launch_obj.append(launch_itr)
        
        for n in range(0, self.n_vehicles):
            self.launch_obj[n].start()

    def destroy(self, sig = signal.SIGINT):
        '''
        Class method `destroy` terminates the simulation in the stack order of the various states of simulation were created.

        Parameters
        --------------
        sig: `signal`
            Pressing CTRL-C or SIGINT invokes destroy function.
        '''
        time.sleep(5)
        _LOGGER.info('SIGINT: Destroying the physics world and terminating the simulation.')
        _LOGGER.info('Terminating spawn launches')
        for n in range(0, self.n_vehicles):
            if self.callflag["control"]:
                self.launchcontrol_obj[n].shutdown()
                rospy.loginfo("Control for vehicle %s terminated", self.name[n])
            self.launch_obj[n].shutdown()

        
        if self.callflag["rviz"]:
            _LOGGER.info("Destroying ros-rviz")
            self.rviz_process.terminate()
            call(["pkill", "rviz"])
        
        _LOGGER.info('Destroying physics world')
        #kill the roscore
        self.gzclient.terminate()
        #Wait to prevent the creation of zombie processes.
        self.gzclient.wait()
        call(["pkill", "gzserver"])
        call(["pkill", "gzclient"])

        self.stoprecord()
        self.latesbag()
        self.killroscore()
        _LOGGER.info("##### Simulation Terminated #####")

    def latesbag(self):
        '''
        Class method `latestbag` returns the latest bag file that saved ROS messages

        Returns
        ----------
        string:
            Path of the bag file.
        '''
        _LOGGER.info("Retrieving latest bag file")
        if self.callflag["bagrecord"]:
            list_of_files1 = glob.glob('*.bag')
            list_of_files2 = glob.glob('*.bag.active')
            list_of_files = list_of_files1 + list_of_files2
            
            if len(list_of_files) != 0:
                latest_file = max(list_of_files, key=os.path.getctime)

                # if bag  file didn't terminate properly then we need to reindex it.
                if "bag.active" in latest_file[-10:]:
                    reindex = subprocess.Popen(["rosbag reindex " +  latest_file],   stdout=subprocess.PIPE, shell=True)
                    stdout = reindex.communicate()[0]
                    _LOGGER.info('reindex STDOUT:{}'.format(stdout))

                    bagfix = subprocess.Popen(["rosbag fix " +  latest_file + " " + latest_file[:-7]],   stdout=subprocess.PIPE, shell=True)
                    stdout = bagfix.communicate()[0]
                    _LOGGER.info('bagfix STDOUT:{}'.format(stdout))
                    latest_file = latest_file[:-7]

                if "bag"not  in latest_file[-3:]:
                    _LOGGER.info("Bag file recording unsuccessful in this sesssion")
                    sys.exit()

                _LOGGER.info("Bag File Recorded Is: " + latest_file)


                self.bagfile = latest_file

                filename = self.bagfile[0:-4]
                create_dir = subprocess.Popen(["mkdir -v " +  filename],   stdout=subprocess.PIPE, shell=True)
                stdout = create_dir.communicate()
                print('mkdir STDOUT:{}'.format(stdout))
                print("Renaming GZStat log file [{}] to retain bag file information".format(self.gzstatsfile))
                move_cmd = subprocess.Popen(["mv -v  " + self.gzstatsfile + " "+  filename+"/" + filename + "_gzStats.txt"],   stdout=subprocess.PIPE, shell=True)
                stdout = move_cmd.communicate()
                print('mv STDOUT:{}'.format(stdout))
                self.gzstatsfile = filename+"/" +filename + "_gzstats.txt"
                return self.bagdir + "/" + latest_file
            else:
                print("No compatible bag file was found.")
                return None

        else:
            print("No bag was recorded in the immediate run.")
            return None

    def control(self, **kwargs):
        """
        Class methods specifies control algorithm for imparting velocity to the car.
        The Control Algorithm can be either uniform, OVFTL (Optimal-Velocity Follow-The-Leader) Model, FollowerStopper, IDM, or anything else.

        
        control_method: `str`

            Control method for each vehicle. It can be list with different control method for each car. If provided, list, the list size must be same as the number of cars

            First vehicle can't have a car-following model such as IDM, OVFTL, Followerstopper, RL. If provided uniform velocity, then leader velocity will be used for imparting velocities to all vehicles.

        leader_vel: `float`

        str_angle: `float`

        initial_distance: Union[`double`, list]
            When providing linear route, make sure, initial distance is 0

        route: Union["circular", "linear"]

        """

        leader_vel = kwargs.get("leader_vel", 3.0)
        str_angle = kwargs.get("str_angle", 0.0)
        control_method = kwargs.get("control_method", "uniform")
        route = kwargs.get("route", "linear")
        rlpolicy_model = kwargs.get("rlpolicy_model")
        rlvf_model = kwargs.get("rlvf_model")
        

        if route not in ["linear", "circular"]:
            _LOGGER.error("Two types of routes are supported: circular and linear")

        # control_method is a single string to denote types
        # convert single string to a list to apply to all vehicles
        # this I won't need to write separate for loops with if-else
        if isinstance(control_method, str):
            control_method = [control_method]*self.n_vehicles
        
        initial_distance = kwargs.get("initial_distance", 20.0)

        if isinstance(initial_distance, float):
            initial_distance = [initial_distance]*self.n_vehicles

        available_control_method = ["uniform", "ovftl", "idm", "injector", "rl"]

        if not all(item in available_control_method for item in control_method):
            _LOGGER.error("Unsupported vehicle control method specified. Exiting the simulation")


        injection_files = kwargs.get("injection_files", None)
        inj_timecols = kwargs.get("time_col", "Time")
        inj_velcols = kwargs.get("vel_control", "Message")

        if len(control_method) < self.n_vehicles:
            _LOGGER.error("For list type control methods, number of methods should be at least same as number of vehicles spawned.")
        

        if control_method[0].lower() == "injector":
            injection_file = injection_files[0]
            inj_timecol = inj_timecols[0]
            inj_velcol = inj_velcols[0]
            launchobj =launch(launchfile=self.package_path + '/launch/velinjector.launch', csvfile = injection_file, time_col = inj_timecol, vel_col = inj_velcol, robot = "catvehicle_{:03d}".format(i), str_angle = str_angle)
            self.launchcontrol_obj.append(launchobj)

        elif control_method[0].lower() == "uniform":
            launchobj = launch(launchfile=self.package_path+'/launch/stepvel.launch',
            constVel = 0.0, strAng = str_angle, robot ="catvehicle_{:03d}".format(i))
            self.launchcontrol_obj.append(launchobj)

        else:
            if route == "linear":
                _LOGGER.error("With linear route, control method for leader vehicle in the platoon only works with uniform and injector control method. ")

            else:
                if control_method[0].lower() == "idm":
                    launchobj = launch(launchfile=self.package_path+'/launch/idm.launch',
                        robot ="catvehicle_{:03d}".format(0),
                        leader_name = "catvehicle_{:03d}".format(self.n_vehicles-1),
                        str_angle = str_angle,
                        initial_distance = initial_distance[0],
                        leader_x_init = self.X[-1],
                        leader_y_init = self.Y[-1],
                        ego_x_init = self.X[0],
                        ego_y_init = self.Y[0]
                        )
                    
                    self.launchcontrol_obj.append(launchobj)
                
                elif control_method[0].lower() == "followerstopper":
                    launchobj = launch(launchfile=self.package_path+'/launch/followerstopper.launch',
                        robot ="catvehicle_{:03d}".format(0),
                        leader_name = "catvehicle_{:03d}".format(self.n_vehicles-1),
                        str_angle = str_angle,
                        initial_distance = initial_distance[0],
                        leader_x_init = self.X[-1],
                        leader_y_init = self.Y[-1],
                        ego_x_init = self.X[0],
                        ego_y_init = self.Y[0]
                        )
                    self.launchcontrol_obj.append(launchobj)
                
                elif control_method[0].lower() == "rl":
                    launchobj = launch(launchfile=self.package_path+'/launch/rlpredict.launch',
                        robot="catvehicle_{:03d}".format(0),
                        leader = "catvehicle_{:03d}".format(self.n_vehicles-1),
                        policy_model = rlpolicy_model,
                        vf_model = rlvf_model
                        )
                    self.launchcontrol_obj.append(launchobj)

        # for vehicles other than lead vehicles
        for i in range(1, self.n_vehicles):
            if control_method[i].lower() == "injector":
                injection_file = injection_files[i]
                inj_timecol = inj_timecols[i]
                inj_velcol = inj_velcols[i]
                launchobj =launch(launchfile=self.package_path + '/launch/velinjector.launch', csvfile = injection_file, time_col = inj_timecol, vel_col = inj_velcol, robot = "catvehicle_{:03d}".format(i), str_angle = str_angle)
                self.launchcontrol_obj.append(launchobj)

            elif control_method[i].lower() == "uniform":
                launchobj = launch(launchfile=self.package_path+'/launch/stepvel.launch',
                constVel = 0.0, strAng = str_angle, robot ="catvehicle_{:03d}".format(i))
                self.launchcontrol_obj.append(launchobj)

            elif control_method[i].lower() == "idm":
                launchobj = launch(launchfile=self.package_path+'/launch/idm.launch',
                    robot ="catvehicle_{:03d}".format(i),
                    leader_name = "catvehicle_{:03d}".format(i-1),
                    str_angle = str_angle,
                    initial_distance = initial_distance[i],
                    leader_x_init = self.X[i-1],
                    leader_y_init = self.Y[i-1],
                    ego_x_init = self.X[i],
                    ego_y_init = self.Y[i]
                    )
                
                self.launchcontrol_obj.append(launchobj)
            
            elif control_method[i].lower() == "followerstopper":
                launchobj = launch(launchfile=self.package_path+'/launch/followerstopper.launch',
                    robot ="catvehicle_{:03d}".format(i),
                    leader_name = "catvehicle_{:03d}".format(i-1),
                    str_angle = str_angle,
                    initial_distance = initial_distance[i],
                    leader_x_init = self.X[i-1],
                    leader_y_init = self.Y[i-1],
                    ego_x_init = self.X[i],
                    ego_y_init = self.Y[i]
                    )
                self.launchcontrol_obj.append(launchobj)
            
            elif control_method[i].lower() == "rl":
                launchobj = launch(launchfile=self.package_path+'/launch/rlpredict.launch',
                    robot="catvehicle_{:03d}".format(i),
                    leader = "catvehicle_{:03d}".format(i-1),
                    policy_model = rlpolicy_model,
                    vf_model = rlvf_model
                    )
                self.launchcontrol_obj.append(launchobj)
            

        
        for n in range(1, self.n_vehicles):
            _LOGGER.info("Control node with index {} started".format(n))
            self.launchcontrol_obj[n].start()
        
        _LOGGER.info("Control node with index {} started".format(0))
        self.launchcontrol_obj[0].start()
        
        
        for n in range(0, self.n_vehicles):
            if control_method[0] == "uniforn":
                rosparamset = subprocess.Popen(["rosparam set /" +"catvehicle_{:03d}".format(n)+"/constVel " + str(leader_vel)  ],   stdout=subprocess.PIPE, shell=True)

        
        call(["rosparam", "set", "/execute", "true"])
        self.callflag["control"] = True




    
        
        
