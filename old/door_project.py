import sys
import time
import json
import paho.mqtt.client as mqtt
from components import door_mpu6050, face_detection
from components.oled_display import OLEDDisplay
from components.door_hcsr04 import DoorStateHCSR04

# MQTT Broker Configuration
mqtt_server = "192.168.1.39"
mqtt_username = "hieu"
mqtt_password = "hieu"
mqtt_port = 1883
topic_door_events = "raspberrypi/door_events"
topic_occupancy_status = "raspberrypi/occupancy_status"

# Global Variables
previous_door_state = None
occupancy_changed = False
occupancy_status = "no"  # Default occupancy status
face_status = "no"
face_confidence = 0

# Initialize 
display = OLEDDisplay()
door_state_sensor = DoorStateHCSR04(23, 24)

# MQTT Functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic_occupancy_status)
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    global occupancy_status
    if msg.topic == topic_occupancy_status:
        occupancy_status = msg.payload.decode()
        update_display()

def publish_door_event(event_type, face_status, confidence, occupancy_changed):
    payload = json.dumps({
        "event_type": event_type,
        "face_status": face_status,
        "confidence": confidence,
        "occupancy_changed": occupancy_changed,
        "timestamp": time.time()  
    })
    client.publish(topic_door_events, payload)

def update_display():
    global occupancy_status, face_status, face_confidence, previous_door_state
    door_state = "closed" if previous_door_state == 'open' else "open"
    face_display = f"Face: {face_status.capitalize()} ({face_confidence:.1f}%)"
    display.update_display(f"Occupancy: {occupancy_status.capitalize()}", f"Door: {door_state.capitalize()}", face_display)
    print(f"Display updated: Occupancy: {occupancy_status.capitalize()}, Door: {door_state.capitalize()}, {face_display}")
    print(f"Prev door state: {previous_door_state}")

# MQTT client setup and start
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.on_connect = on_connect 
client.on_message = on_message
client.connect(mqtt_server, mqtt_port)  
client.loop_start() 

def handle_door_event(previous_state, current_state):
    global occupancy_changed, face_status, face_confidence, previous_door_state
    time.sleep(0.08)  
    if door_mpu6050.get_door_motion() != 'moving':
        return  # Return if door is not in motion

    face_result, confidence = face_detection.run_face_detection(95)
    if face_result is None: # Return if face detection failed
        return

    event_type = "opened" if current_state == 'open' else "closed"
    face_status = "yes" if face_result == 'yes' else "no"
    face_confidence = confidence

    occupancy_changed = face_status == "yes"

    print(f"\nDoor: {event_type}, Face: {face_status} (Confidence: {confidence}%)")
    publish_door_event(event_type, face_status, confidence, occupancy_changed) 
    previous_door_state = current_state
    time.sleep(1.0)
    update_display()  # Update the display after handling the door event
    

while True:
    door_motion = door_mpu6050.get_door_motion()
    door_state = door_state_sensor.get_door_state()

    # Check if door state changed AND occupancy changed
    if previous_door_state != door_state and occupancy_changed:
        print(f"\nOccupancy status has likely changed!")
        occupancy_changed = False  # Reset

    if previous_door_state != door_state:
        handle_door_event(previous_door_state, door_state)

    previous_door_state = door_state 

def debug():
    def dynamic_print2(line1, line2):
        sys.stdout.write("\r" + line1)
        sys.stdout.write("\n" + line2)
        sys.stdout.flush()
    timeout = 20
    door_motion, last_change_motion = door_mpu6050.get_door_motion_time(timeout)
    door_state, last_change_state = door_hcsr04.get_door_state_time(timeout)
    dynamic_print2(f"Door Motion: {door_motion}, Time Since Last Change: {last_change_motion} seconds",
                  f"Door State: {door_state}, Time Since Last Change: {last_change_state} seconds")
