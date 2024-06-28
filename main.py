import time
import json
import paho.mqtt.client as mqtt
from components.oled_display import OLEDDisplay
from components.door_hcsr04 import DoorStateHCSR04
from components.door_mpu6050 import DoorMotionMPU6050
from gesture.gesture_recognition import HandGestureRecognition

class SmartDoorSystem:
    def __init__(self, mqtt_server, mqtt_port, mqtt_username, mqtt_password):
        # MQTT Broker Configuration
        self.mqtt_server = mqtt_server
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.topic_occupancy_status = "smart_door_system/occupancy_status"
        self.topic_hand_gesture = "smart_door_system/hand_gesture"
        
        # Global Variables
        self.previous_door_state = None
        self.hand_gesture = None
        self.hand_score = None

        # Initialise components
        self.display = OLEDDisplay()
        self.door_state_sensor = DoorStateHCSR04(trig_pin=23, echo_pin=24, threshold_distance=4)
        self.door_motion_sensor = DoorMotionMPU6050(i2c_address=0x68, angular_velocity_threshold=3, dt=0.2, alpha=0.97, timeout=20)
        self.model_path = '/home/hieu/project/gesture/hand_gesture_model.task'

        # Initialise MQTT client
        self.client = mqtt.Client()
        self.client.username_pw_set(mqtt_username, mqtt_password)
        self.client.on_connect = self.on_connect 
        self.client.on_message = self.on_message
        self.client.connect(mqtt_server, mqtt_port)  
        self.client.loop_start()
        self.display.update_display(f"Smart Door System", f"System Initialised", f"Running...")

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback function for MQTT connection.
        """
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.topic_occupancy_status)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        """
        Callback function for receiving MQTT messages.
        """
        if msg.topic == self.topic_occupancy_status:
            self.occupancy_status = msg.payload.decode()
            self.update_display()

    def publish_hand_gesture(self, event_type, hand_gesture, score):
        """
        Publish door event to the MQTT broker.
        """
        payload = json.dumps({
            "event_type": event_type,
            "hand_gesture": hand_gesture,
            "score": score,
            "timestamp": time.time()  
        })
        self.client.publish(self.topic_hand_gesture, payload)

    def update_display(self):
        """
        Update the OLED display with current status.
        """
        str_score = str(self.hand_score)  # Ensure hand_score is converted to string
        self.display.update_display(f"Door: {self.previous_door_state}", f"Hand: {self.hand_gesture}", f"Score: {str_score}")
    
    def handle_door_event(self, current_state):
        """
        Handle door events including motion detection and face detection.
        """
        time.sleep(0.08)
        door_motion = self.door_motion_sensor.get_door_motion()
        if door_motion != 'moving':
            return # Return if door is not in motion
        
        hand_gesture = HandGestureRecognition(model=self.model_path, stop_on_gesture=True)
        result = hand_gesture.run()
        self.hand_gesture = result.hand_gesture_name
        self.hand_score = result.score
        self.previous_door_state = current_state
        print(f"Door: {current_state}")
        print(f'Result: {result.hand_gesture_name} ({result.score})')
        self.update_display()  # Update the display after handling the door event
        self.publish_hand_gesture(current_state,self.hand_gesture,self.hand_score)
        
    def run(self):
        """
        Main loop to continuously monitor door state and handle events.
        """
        try:
            while True:
                door_state = self.door_state_sensor.get_door_state()

                if self.previous_door_state != door_state:
                    self.handle_door_event(door_state)

                self.previous_door_state = door_state

        except KeyboardInterrupt:
            print("Stopped by User")
        finally:
            self.system_shutdown()

    def system_shutdown(self):
        self.door_state_sensor.release_gpio()
        self.display.update_display(f"Smart Door System",f"System Shutdown",f"GPIO Released")

if __name__ == "__main__":
    smart_door_system = SmartDoorSystem(
        mqtt_server="192.168.1.39", 
        mqtt_port=1883, 
        mqtt_username="hieu", 
        mqtt_password="hieu")
    smart_door_system.run()