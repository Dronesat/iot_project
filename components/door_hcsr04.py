import gpiod
import time

# --- GPIO Setup for Ultrasonic Sensor HC-SR04 ---
chip = gpiod.Chip('gpiochip4')  
trig_line = chip.get_line(23)
echo_line = chip.get_line(24)
trig_line.request(consumer='hc-sr04-trig', type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
echo_line.request(consumer='hc-sr04-echo', type=gpiod.LINE_REQ_DIR_IN)

# Global Variables
previous_door_state = None  
last_change_time = None
time_since_last_change = None

def get_distance():
    # Set TRIG LOW
    trig_line.set_value(0)
    time.sleep(0.002)

    # Send 10us pulse to TRIG
    trig_line.set_value(1)
    time.sleep(0.00001)
    trig_line.set_value(0)

    # Start recording time
    pulse_start = time.time()
    pulse_end = pulse_start  # Default value to prevent error
    timeout = time.time() + 0.04  # Timeout to avoid infinite loops

    try:
        while echo_line.get_value() == 0 and time.time() < timeout:
            pulse_start = time.time()

        while echo_line.get_value() == 1:
            pulse_end = time.time()

        # Check for unreasonable pulse durations
        pulse_duration = pulse_end - pulse_start
        if pulse_duration <= 0:
            raise ValueError("Invalid pulse duration. Check connections.")

        distance = pulse_duration * 17150
        distance = round(distance, 2)
        return distance

    except (OSError, ValueError) as error:
        print(f"HC-SR04: Error measuring distance. {error}")
        return None  
    
def get_door_state():
    current_distance = get_distance()
    
    # Handle error
    if current_distance is None:
        return previous_door_state
    
    current_door_state = 'open' if current_distance <= 4 else 'closed'
    return current_door_state

# Function deprecated, doesnt need anymore
def get_door_state_time(timeout):
    global previous_door_state, last_change_time, time_since_last_change

    current_distance = get_distance()
    current_door_state = 'open' if current_distance <= 4 else 'closed'

    # Door state has changed
    if current_door_state != previous_door_state:
        last_change_time = time.time()  
        time_since_last_change = 0.0  # Reset the time counter when state changes
        previous_door_state = current_door_state 
    elif last_change_time is not None:  # Only calculate if there was a previous change
        time_since_last_change = round(time.time() - last_change_time, 1) 

        if time_since_last_change > timeout:
            time_since_last_change = None  # Stop tracking time after 20 seconds

    return current_door_state, time_since_last_change 

def release_GPIO():
    trig_line.release()
    echo_line.release()

if __name__ == "__main__":
    try:
        while True:
            door_state = get_door_state()
            print(f"Door state: {door_state}")
            time.sleep(1)  
    except KeyboardInterrupt:
        print("Stopped by User")
    finally: 
        release_GPIO()
        print("GPIO released")