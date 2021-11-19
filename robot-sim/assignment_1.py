from __future__ import print_function
import time
from sr.robot import *

a_th = 3.0
""" float: Threshold for the control of the orientation"""

d_th = 0.4
""" float: Threshold for the control of the linear distance"""

R = Robot()
""" instance of the class Robot"""

def drive(speed , seconds):
    """
    Function for setting a linear velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed , seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def find_silver_token():
    """
    Function to find the closest silver token where is located in front of the robot

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist = 100
    for token in R.see():
        if token.dist < 3.5*d_th and -90 < token.rot_y < 90 and token.info.marker_type == MARKER_TOKEN_SILVER:
            dist = token.dist
            rot_y = token.rot_y
    if dist==100:
    	return -1, -1
    else:
   	    return dist, rot_y

def find_golden_token():
    """
    Function to find golden tokens in front, right side and left side of the robot and the closest of them in mentioned directions

    Returns:
    front_obstacles (dict): distance and angle of golden tokens where is located in front of the robot
    right_obstacles (dict): distance and angle of golden tokens where is located in right side of the robot
    left_obstacles (dict): distance and angle of golden tokens where is located in left side of the robot
	front_obstacle_dist (float): distance of the closest golden token where is located in front of the robot (100 if no golden token is detected)
	right_obstacle_dist (float): distance of the closest golden token where is located in right side of the robot (100 if no golden token is detected)
    left_obstacle_dist (float): distance of the closest golden token where is located in left side of the robot (100 if no golden token is detected)
    """
    front_obstacles = dict()
    right_obstacles = dict()
    left_obstacles = dict()

    front_obstacle_dist = 100
    right_obstacle_dist = 100
    left_obstacle_dist = 100
    
    for token in R.see():
        if token.dist < 3.5*d_th and token.info.marker_type == MARKER_TOKEN_GOLD:
            if -45 <= token.rot_y <= 45: # Select golden tokens in front of the robot
                front_obstacles[token.rot_y] = token.dist
            elif 45 < token.rot_y <= 135: # Select golden tokens in right side of the robot
                right_obstacles[token.rot_y] = token.dist
            elif -135 <= token.rot_y < -45: # Select golden tokens in left side of the robot
                left_obstacles[token.rot_y] = token.dist
    
    if len(front_obstacles) != 0: # Select the closest golden token in front of the robot
        front_obstacle_dist = min(front_obstacles.values())
    if len(right_obstacles) != 0: # Select the closest golden token in right side of the robot
        right_obstacle_dist = min(right_obstacles.values())
    if len(left_obstacles) != 0: # Select the closest golden token in left side of the robot
        left_obstacle_dist = min(left_obstacles.values())
       
    return front_obstacles , right_obstacles , left_obstacles , front_obstacle_dist , right_obstacle_dist , left_obstacle_dist

# Main Code
while True:
    [front_obs_gold , right_obs_gold , left_obs_gold , front_obs_dist_gold , right_obs_dist_gold , left_obs_dist_gold] = find_golden_token() # Call find_golden_token() function
    [dist_silver , rot_y_silver] = find_silver_token() # Call find_silver_token() function
    if dist_silver == -1: # If the robot couldn't see any silver token
        if front_obs_dist_gold > 0.75: # If the closest golden token in front of the robot isn't near 
            print("[ROBOT]: Going Forward")
            drive(60,0.25)
        else: # If the closest golden token in front of the robot is near then the robot should decide to turn right or left
            if len(right_obs_gold.values()) < len(left_obs_gold.values()):
                print("[ROBOT]: Turning Right")
                turn(4,0.5)
            elif len(right_obs_gold.values()) > len(left_obs_gold.values()):
                print("[ROBOT]: Turning Left")
                turn(-4,0.5)  
            else:
                while front_obs_dist_gold <= 0.75:
                    [front_obs_gold , right_obs_gold , left_obs_gold , front_obs_dist_gold , right_obs_dist_gold , left_obs_dist_gold] = find_golden_token() # Call find_golden_token() function   
                    if right_obs_dist_gold > left_obs_dist_gold:
                        print("[ROBOT]: Turning Right")
                        turn(4,0.5)
                    elif right_obs_dist_gold <= left_obs_dist_gold:
                        print("[ROBOT]: Turning Left")
                        turn(-4,0.5)
    else: # If the robot could see any silver token
        if front_obs_dist_gold > 0.75: # If the closest golden token in front of the robot isn't near 
            if rot_y_silver > a_th: # Fixing misalignment
                print("[ROBOT]: Turning Right")
                turn(2,0.5)
            elif rot_y_silver < -a_th:
                print("[ROBOT]: Turning Left")
                turn(-2,0.5)
            else:
                if dist_silver > d_th: # Going forward after fixing misalignment
                    print("[ROBOT]: Going Forward")
                    drive(30,0.25)
                else: # Grabbing the specified silver token
                    print("[ROBOT]: Getting The Silver Token") 
                    R.grab() 
                    print("[ROBOT]: Turning Right")
                    turn(30,2)
                    print("[ROBOT]: Releasing The Silver Token") 
                    R.release()
                    print("[ROBOT]: Going Backward")
                    drive(-20,1)
                    print("[ROBOT]: Turning Left")
                    turn(-30,2)
        else: # If the closest golden token in front of the robot is near then the robot should decide to turn right or left
            if len(right_obs_gold.values()) < len(left_obs_gold.values()):
                print("[ROBOT]: Turning Right")
                turn(4,0.5)
            elif len(right_obs_gold.values()) > len(left_obs_gold.values()):
                print("[ROBOT]: Turning Left")
                turn(-4,0.5)  
            else:            
                while front_obs_dist_gold <= 0.75:
                    [front_obs_gold , right_obs_gold , left_obs_gold , front_obs_dist_gold , right_obs_dist_gold , left_obs_dist_gold] = find_golden_token() # Call find_golden_token() function    
                    if right_obs_dist_gold > left_obs_dist_gold:
                        print("[ROBOT]: Turning Right")
                        turn(4,0.5)
                    elif right_obs_dist_gold <= left_obs_dist_gold:
                        print("[ROBOT]: Turning Left")
                        turn(-4,0.5)