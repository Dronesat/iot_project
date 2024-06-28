import mpu6050
import time
import math

class DoorMotionMPU6050:
    def __init__(self, i2c_address=0x68, angular_velocity_threshold=4, dt=0.2, alpha=0.97, timeout=20):
        """
        Initialise the DoorMotionSensor with given parameters.
        
        :param i2c_address: I2C address of the MPU6050 sensor.
        :param movement_threshold: Threshold for detecting door movement (degrees per second).
        :param dt: Time interval for reading sensor data (seconds).
        :param alpha: Weight for the gyroscope data in the complementary filter.
        :param timeout: Timeout for motion state tracking (seconds).
        """
        self.mpu6050 = mpu6050.mpu6050(i2c_address)  # I2C Interface: Address 0x68
        self.angular_velocity_threshold = angular_velocity_threshold  # Degrees per second
        self.dt = dt  # Time interval for reading sensor data
        self.alpha = alpha  # Weight for the gyroscope in the complementary filter
        self.timeout = timeout  # Timeout for motion state tracking
        
        # Variables to track door state, angle, and angular velocity
        self.door_state = "stationary"
        self.angle = 0.0  # Initial angle
        self.gyro_offset = 0.0  # Store the initial gyro offset
        
        # Initial calibration
        _, gyro_data, _ = self.read_sensor_data()  # Read initial gyro data
        self.initial_gyro_x = gyro_data['x']  # Store the initial gyro reading for offset
        
        # Global Variables
        self.previous_door_motion = None  

    def read_sensor_data(self):
        try:
            accelerometer_data = self.mpu6050.get_accel_data()
            gyroscope_data = self.mpu6050.get_gyro_data()
            temperature = self.mpu6050.get_temp()
            return accelerometer_data, gyroscope_data, temperature

        except OSError as e:
            print(f"Error reading sensor data: {e}")
            return None, None, None 
        
    def get_door_motion(self):
        try:
            accel_data, gyro_data, _ = self.read_sensor_data()

            # Handle sensor reading error 
            if accel_data is None or gyro_data is None:
                return self.door_state

            # Correct the gyro reading
            angular_velocity_z = gyro_data['x'] - self.initial_gyro_x  

            # Determine door state based on angular velocity
            if abs(angular_velocity_z) > self.angular_velocity_threshold:
                self.door_state = "moving"
            else:
                self.door_state = "stationary"

            time.sleep(self.dt)
            return self.door_state

        except Exception as error:
            print(f"Error in get_door_motion: {error}")
            return self.door_state

    def run(self):
        while True:
            door_motion= self.get_door_motion()

            if door_motion != self.previous_door_motion:
                print(f"Door motion: {door_motion}")
                self.previous_door_motion = door_motion

            time.sleep(0.1)

if __name__ == "__main__":
    door_motion_sensor = DoorMotionMPU6050()
    door_motion_sensor.run()