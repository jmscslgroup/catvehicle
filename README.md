# Cognitive and Autonomous Test Vehicle (CAT Vehicle) Testbed
The CAT Vehicle is a ROS based simulator to facilitate the development of autonomous vehicle applications. This repository houses the files that utilize the Gazebo simulator, and additional interfaces to the physical CAT Vehicle Testbed available at the University of Arizona - Department of Electrical and Computer Engineering.

# Dependencies
* ROS
* obstaclestopper

# Citation
If you find this work useful please give credits to the authors by citing:
```
Rahul Bhadani, Jonathan Sprinkle, Matthew Bunting. "The CAT Vehicle Testbed: A Simulator with Hardware in the Loop for Autonomous Vehicle Applications". Proceedings 2nd International Workshop on Safe Control of Autonomous Vehicles (SCAV 2018), Porto, Portugal, 10th April 2018, Electronic Proceedings in Theoretical Computer Science 269, pp. 32–47. Download:  http://dx.doi.org/10.4204/EPTCS.269.4.
```

bibtex:
```
@article{bhadani2018cat,
  title={The CAT Vehicle Testbed: A Simulator with Hardware in the Loop for Autonomous Vehicle Applications},
    author={Bhadani, Rahul Kumar and Sprinkle, Jonathan and Bunting, Matthew},
      journal={Proceedings 2nd International Workshop on Safe Control of Autonomous Vehicles (SCAV 2018), Porto, Portugal, 10th April 2018, Electronic Proceedings in Theoretical Computer Science 269, pp. 32–47},
        year={2018}
}
```



# catkin workspace and build
In order to use the catvehicle ROS package, you should work within a catkin workspace. If you do not already have one:
```
cd ~
mkdir -p catvehicle_ws/src
cd catvehicle_ws/src
catkin_init_workspace
cd ..
catkin_make
```

At this point, you can extract this package into your src directory
```
cd catvehicle_ws/src
tar xzf catvehicle-x.y.z.tgz
cd ..
catkin_make
```

# Simple tutorial and examples
Follow the tutorials on the CAT Vehicle Testbed group on the CPS Virtual Organization to see how to use the testbed.

# Acknowledgements
## License
Copyright (c) 2013-2018 Arizona Board of Regents
All rights reserved

Permission is hereby granted, without written agreement and without 
license or royalty fees, to use, copy, modify, and distribute this
software and its documentation for any purpose, provided that the 
above copyright notice and the following two paragraphs appear in 
all copies of this software.
 
IN NO EVENT SHALL THE ARIZONA BOARD OF REGENTS BE LIABLE TO ANY PARTY 
FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES 
ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN 
IF THE ARIZONA BOARD OF REGENTS HAS BEEN ADVISED OF THE POSSIBILITY OF 
SUCH DAMAGE.

THE ARIZONA BOARD OF REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY 
AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER
IS ON AN "AS IS" BASIS, AND THE ARIZONA BOARD OF REGENTS HAS NO OBLIGATION
TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

## Authors and contributors
* Jonathan Sprinkle (sprinkjm@email.arizona.edu)
* Rahul Bhadani (rahulkumarbhadani@email.arizona.edu)
* Sam Taylor
* Kennon McKeever (kennondmckeever@email.arizona.edu)
* Alex Warren
* Swati Munjal (smunjal@email.arizona.edu)
* Ashley Kang (askang@email.arizona.edu)
* Matt Bunting (mosfet@email.arizona.edu)
* Sean Whitsitt

## Support
This work was supported by the National Science Foundation and AFOSR under awards 1521617, 1446435, 1262960 and 1253334. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.

