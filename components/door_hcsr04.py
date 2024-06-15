import gpiod
import time

class DoorStateHCSR04:
    def __init__(self, trig_pin, echo_pin, threshold_distance=4):
        self.chip = gpiod.Chip('gpiochip4')
        self.trig_line = self.chip.get_line(trig_pin)
        self.echo_line = self.chip.get_line(echo_pin)
        self.trig_line.request(consumer='hc-sr04-trig', type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
        self.echo_line.request(consumer='hc-sr04-echo', type=gpiod.LINE_REQ_DIR_IN)

        #Instance's global variables
        self.threshold_distance = threshold_distance
        self.previous_door_state = None
        self.last_change_time = None
        self.time_since_last_change = None

    def get_distance(self):
        # Set TRIG LOW
        self.trig_line.set_value(0)
        time.sleep(0.002)

        # Send 10us pulse to TRIG
        self.trig_line.set_value(1)
        time.sleep(0.00001)
        self.trig_line.set_value(0)

        # Start recording time
        pulse_start = time.time()
        pulse_end = pulse_start
        timeout = time.time() + 0.04

        try:
            while self.echo_line.get_value() == 0 and time.time() < timeout:
                pulse_start = time.time()

            while self.echo_line.get_value() == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            if pulse_duration <= 0:
                raise ValueError("Invalid pulse duration. Check connections.")

            distance = pulse_duration * 17150
            return round(distance, 2)

        except (OSError, ValueError) as error:
            print(f"HC-SR04: Error measuring distance. {error}")
            return None

    def get_door_state(self):
        current_distance = self.get_distance()

        # Handle error
        if current_distance is None:
            return self.previous_door_state
        
        # Door state has changed
        current_door_state = 'open' if current_distance <= self.threshold_distance else 'closed'
        return current_door_state

    def release_gpio(self):
        self.trig_line.release()
        self.echo_line.release()

    # Function deprecated: Not require for the project anymore
    def get_door_state_time(self, timeout):
        current_distance = self.get_distance()
        current_door_state = 'open' if current_distance <= self.threshold_distance else 'closed'

        # Door state has changed
        if current_door_state != self.previous_door_state:
            self.last_change_time = time.time()
            self.time_since_last_change = 0.0 # Reset the time counter when state changes
            self.previous_door_state = current_door_state
        elif self.last_change_time is not None:  # Only calculate if there was a previous change
            self.time_since_last_change = round(time.time() - self.last_change_time, 1)
            if self.time_since_last_change > timeout: # Stop tracking time after timeout
                self.time_since_last_change = None 

        return current_door_state, self.time_since_last_change

if __name__ == "__main__":
    sensor = DoorStateHCSR04(23, 24)
    try:
        while True:
            door_state = sensor.get_door_state()
            print(f"Door state: {door_state}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped by User")
    finally:
        sensor.release_gpio()
        print("GPIO released")
