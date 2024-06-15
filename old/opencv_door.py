import sys
import cv2
from cvzone import FaceDetectionModule
import paho.mqtt.client as mqtt
import time
import door_hcsr04

# --- MQTT Configuration ---
mqtt_server = "192.168.1.39"
mqtt_username = "hieu"
mqtt_password = "hieu"
mqtt_port = 1883
topic_door_state = "raspberrypi/door-state"
topic_face_presence = "raspberrypi/opencv-face"

# --- MQTT Setup ---
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)

# Callback for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")
        
client.on_connect = on_connect  
client.connect(mqtt_server, mqtt_port) 
client.loop_start()  

def run_face_detection():
    detector = FaceDetectionModule.FaceDetector()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 10)

    if not cap.isOpened():
        print("Error: Could not open USB camera")
        return

    start_time = time.time()
    while True: 
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame from USB camera")
            continue
        
        frame, faces = detector.findFaces(frame)
        if faces:
            print("Face Detected")
            client.publish(topic_face_presence, "yes")
            time.sleep(1)
            break
        else:
            client.publish(topic_face_presence, "no")

        time_counter = time.time() - start_time
        if time_counter >= 20:
            print("No face detected, turn off camera")
            break
        else: dynamic_print(f"{time_counter:.1f} seconds") 

        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    # Clean up resources
    cap.release()
    cv2.destroyAllWindows()

def dynamic_print(input):
    output_text = f"{input}    "
    sys.stdout.write("\r" + output_text) 
    sys.stdout.flush()

if __name__ == '__main__':
    try:
        door_state,_ = door_hcsr04.get_door_state_time()
        while True:
            new_door_state,_ = door_hcsr04.get_door_state_time()
            # Check if door state changed
            if new_door_state != door_state:
                door_state = new_door_state
                client.publish(topic_door_state, door_state)
                run_face_detection() 

            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopped by User")

    finally:
        door_hcsr04.release_echo_trig_line()
        client.loop_stop()
        client.disconnect()
