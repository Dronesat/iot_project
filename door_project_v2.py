import sys
import time
import json
import paho.mqtt.client as mqtt
from components import door_mpu6050, face_detection
from components.oled_display import OLEDDisplay
from components.door_hcsr04 import DoorStateHCSR04

class SmartDoorSystem:
    def __init__(self, mqtt_server, mqtt_port, mqtt_username, mqtt_password):
        # MQTT Broker Configuration
        self.mqtt_server = mqtt_server
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.topic_door_events = "raspberrypi/door_events"
        self.topic_occupancy_status = "raspberrypi/occupancy_status"
        
        # Global Variables
        self.previous_door_state = None
        self.occupancy_changed = False
        self.occupancy_status = "no"  # Default occupancy status
        self.face_status = "no"
        self.face_confidence = 0

        # Initialise components
        self.display = OLEDDisplay()
        self.door_state_sensor = DoorStateHCSR04(23, 24)

        # Initialize MQTT client
        self.client = mqtt.Client()
        self.client.username_pw_set(mqtt_username, mqtt_password)
        self.client.on_connect = self.on_connect 
        self.client.on_message = self.on_message
        self.client.connect(mqtt_server, mqtt_port)  
        self.client.loop_start()
        self.display.update_display(f"Smart Door System", f"System Running....", f"")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.topic_occupancy_status)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        if msg.topic == self.topic_occupancy_status:
            self.occupancy_status = msg.payload.decode()
            self.update_display()

    def publish_door_event(self, event_type, face_status, confidence, occupancy_changed):
        payload = json.dumps({
            "event_type": event_type,
            "face_status": face_status,
            "confidence": confidence,
            "occupancy_changed": occupancy_changed,
            "timestamp": time.time()  
        })
        self.client.publish(self.topic_door_events, payload)

    def update_display(self):
        door_state = "open" if self.previous_door_state == 'open' else "closed"
        face_display = f"Face: {self.face_status.capitalize()} ({self.face_confidence:.1f}%)"
        self.display.update_display(f"Occupancy: {self.occupancy_status.capitalize()}", f"Door: {door_state.capitalize()}", face_display)
        print(f"Display updated: Occupancy: {self.occupancy_status.capitalize()}, Door: {door_state.capitalize()}, {face_display}")
    
    def handle_door_event(self, previous_state, current_state):
        time.sleep(0.08)
        if door_mpu6050.get_door_motion() != 'moving':
            return # Return if door is not in motion

        face_result, confidence = face_detection.run_face_detection(95)
        if face_result is None:  
            return # Return if face detection failed

        event_type = "opened" if current_state == 'open' else "closed"
        self.face_status = "yes" if face_result == 'yes' else "no"
        self.face_confidence = confidence

        self.occupancy_changed = self.face_status == "yes"

        print(f"\nDoor: {event_type}, Face: {self.face_status} (Confidence: {confidence}%)")
        self.publish_door_event(event_type, self.face_status, confidence, self.occupancy_changed)
        self.previous_door_state = current_state
        #time.sleep(1.0)
        self.update_display()  # Update the display after handling the door event

    def run(self):
        while True:
            door_motion = door_mpu6050.get_door_motion()
            door_state = self.door_state_sensor.get_door_state()

            # Check if door state changed AND occupancy changed
            if self.previous_door_state != door_state and self.occupancy_changed:
                print(f"\nOccupancy status has likely changed!")
                self.occupancy_changed = False  # Reset

            if self.previous_door_state != door_state:
                self.handle_door_event(self.previous_door_state, door_state)

            self.previous_door_state = door_state

    def system_shutdown(self):
        self.door_state_sensor.release_gpio()
        self.display.update_display(f"Smart Door System",f"System Shutdown",f"GPIO Released")

if __name__ == "__main__":
    smart_door_system = SmartDoorSystem(
        mqtt_server="192.168.1.39", 
        mqtt_port=1883, 
        mqtt_username="hieu", 
        mqtt_password="hieu")
    try:
        while True:
            smart_door_system.run()
    except KeyboardInterrupt:
        print("Stopped by User")
    finally:
        smart_door_system.system_shutdown()