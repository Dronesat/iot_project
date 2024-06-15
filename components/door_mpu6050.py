import mpu6050
import time
import math

def read_sensor_data():
    try:
        accelerometer_data = mpu6050.get_accel_data()
        gyroscope_data = mpu6050.get_gyro_data()
        temperature = mpu6050.get_temp()
        return accelerometer_data, gyroscope_data, temperature

    except OSError as e:
        print(f"Error reading sensor data: {e}")
        return None, None, None 

# Gyroscope Setup and Initial Calibration
mpu6050 = mpu6050.mpu6050(0x68) #I2C Interface: Address 0x68
_, _, _ = read_sensor_data()  # Discard initial readings
time.sleep(1)

# Variables to track door state, angle, and angular velocity
door_state = "stationary"
angle = 0.0  # Initial angle 
gyro_offset = 0.0 # Store the initial gyro offset

# Initial calibration
_, gyro_data, _ = read_sensor_data()  # Read initial gyro data
initial_gyro_x = gyro_data['x']  # Store the initial gyro reading for offset

# Threshold for angular velocity 
movement_threshold = 2.5  # Degrees per second
dt = 0.2

# Complementary Filter Parameters 
alpha = 0.97  # Weight for the gyroscope (0.95 - 0.99)

# Global Variables
previous_door_motion = None  
last_change_time = None
time_since_last_change = None

# Combine gyro and accelerometer data
def get_door_motion():
    global door_state, angle, gyro_offset  # Access global variables

    try: 
        accel_data, gyro_data, _ = read_sensor_data()

        # Handle sensor reading error 
        if accel_data is None or gyro_data is None:
            return door_state
        
        gyro_x = gyro_data['x'] - initial_gyro_x  # Correct the gyro reading

        # Estimate angle from accelerometer (door is vertical when closed)
        accel_angle = math.atan2(accel_data['y'], accel_data['z']) * 180 / math.pi

        # Calculate angle change from gyro
        gyro_angle = gyro_x * dt

        # Apply complementary filter to fuse the data
        angle = alpha * (angle + gyro_angle) + (1 - alpha) * accel_angle

        # Estimate angular velocity
        angular_velocity_z = gyro_x

        # Determine door state based on angular velocity
        if abs(angular_velocity_z) > movement_threshold:
            door_motion = "moving"
        else:
            door_motion = "stationary"

        #print(f"Angle (Filtered): {angle:.1f} degrees, Angular Velocity (Z): {angular_velocity_z:.1f} degrees/s, Door state: {door_state}")
        time.sleep(dt) 
        return door_motion
    
    except Exception as error:
        print(f"Error in get_door_motion: {error}")
        return door_state

def get_door_motion_time(timeout):
    global previous_door_motion, last_change_time, time_since_last_change
    current_door_motion = get_door_motion()

    # Door state has changed
    if current_door_motion != previous_door_motion:
        last_change_time = time.time()  
        time_since_last_change = 0.0  # Reset the time counter when state changes
        previous_door_motion = current_door_motion 

    elif last_change_time is not None:  # Only calculate if there was a previous change
        time_since_last_change = round(time.time() - last_change_time, 1) 
        if time_since_last_change > timeout:
            time_since_last_change = None  # Stop tracking time after timeout

    return current_door_motion, time_since_last_change 

if __name__ == "__main__":
    while True:
        door_motion, time_since_change = get_door_motion_time(20)
        
        if time_since_change is not None or door_motion != previous_door_motion:
            print(f"Door motion: {door_motion} (time since change: {time_since_change}s)")
            previous_door_motion = door_motion 

        time.sleep(0.1)  