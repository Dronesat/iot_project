import sys
import time
import door_mpu6050
import door_hcsr04
import door_face_detection

def dynamic_print2(line1, line2):
    sys.stdout.write("\r" + line1)
    sys.stdout.write("\n" + line2)
    sys.stdout.flush()

def dynamic_print(input):
    output_text = f"{input}    "
    sys.stdout.write("\r" + output_text) 
    sys.stdout.flush()

def debug():
    timeout = 20
    door_motion, last_change_motion = door_mpu6050.get_door_motion_time(timeout)
    door_state, last_change_state = door_hcsr04.get_door_state_time(timeout)
    dynamic_print(f"Door Motion: {door_motion}, Time Since Last Change: {last_change_motion} seconds",
                  f"Door State: {door_state}, Time Since Last Change: {last_change_state} seconds")

previous_door_state = None

while True:
    door_motion = door_mpu6050.get_door_motion()
    door_state = door_hcsr04.get_door_state()

    # Check if the door state changed from open to closed
    if (previous_door_state == 'open' and door_state == 'closed'):
        time.sleep(0.5)  
        if door_motion == 'moving':
            face_result = door_face_detection.run_face_detection() 
            if face_result is not None:
                print(f"\nFinal result: Face detected: {face_result}") 
                if face_result == 'yes':
                    print("Door closed and face detected")
                elif face_result == 'no':
                    print("Door closed but face not detected")
                
    # Check if the door state changed from closed to open
    elif (previous_door_state == 'closed' and door_state == 'open'):
        time.sleep(0.5)
        if door_motion == 'moving': 
            face_result = door_face_detection.run_face_detection() 
            if face_result is not None:
                print(f"\nFinal result: Face detected: {face_result}") 
                if face_result == 'yes':
                    print("Door opened and face detected")
                elif face_result == 'no':
                    print("Door opened but face not detected")

    previous_door_state = door_state 