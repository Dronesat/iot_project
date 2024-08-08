# Smart Radiator System with Hand Gesture Control

This project demonstrates an IoT smart radiator control system that use hand gesture recognition to optimise thermal management in residential household.

<img src="https://github.com/user-attachments/assets/0f112c8d-345c-4347-ae7f-1a93e3a3c52b" width="650">

## Features

* **Automated Radiator Valve Control:**  Use a servo motor mounted on the radiator valve to automate the temperature control process.
* **Hand Gesture Recognition:** Incorporates a hand-free control method using hand gestures, provides convenience and encourages energy-saving.
* **Remote Monitoring and Control:** A dashboard interface allows users to monitor real-time temperature data and control the system remotely.
* **IoT Integration:** The system uses MQTT for communication between devices, showcasing the potential of IoT in smart home applications.

## Hardware Components

* Raspberry Pi 5: Serves as the central controller, hosting the Node-RED software, MQTT broker, and hand gesture recognition software.
* ESP32 Microcontroller: Acts as a remote sensor and actuator node, collecting temperature data and controlling the radiator valve.
* Temperature Sensors (DHT11, DS18B20): Monitor room temperature and provide data for the control system.
* Servo Motor (SG90): Controls the radiator valve to regulate the flow of hot water.
* Ultrasonic Sensor (HC-SR04) and Gyroscope Sensor (MPU6050):  Detect door events (opening/closing) to trigger hand gesture recognition.
* Camera (Logitech C525): Captures hand gestures for interpretation and control.
* OLED Display and LCD Display: Provide visual feedback on system status and sensor readings.

## Software Components

* Node-RED:  Implements the logic, handling sensor data, gesture recognition results, and control commands.
* Mosquitto MQTT Broker: Data exchange between the Raspberry Pi and ESP32.
* MediaPipe:  Enables hand gesture recognition using machine learning models.
* OpenCV:  Processes images from the camera for gesture detection.
* Python:  Implements the smart door system and gesture recognition functionality.
* Arduino IDE and C++:  Used for ESP32 development.

## Setup and Installation

1. Clone this repository to your Raspberry Pi.
2. Install the required libraries and dependencies (refer to the `requirements.txt` file).
3. Configure the MQTT broker and connect the ESP32 to your Wi-Fi network.
4. Calibrate the sensors for accurate door event detection.
5. Load the hand gesture recognition model.
6. Run the Python script for the smart door system and the Node-RED flow.
7. Access the Node-RED dashboard to monitor and control the system.

## Future Enhancements

* Integrate with a mobile robotic platform for enhanced environmental monitoring and user interaction.
* Improve hand gesture recognition accuracy in dark lighting conditions.
* Implement a dedicated door sensor to simplify installation process.

## Contributing

Contributions are welcome! Feel free to submit bug reports, feature requests, or pull requests.

## License

This project is licensed under the MIT License.

## Acknowledgments

* The authors would like to acknowledge the contributions of the open-source communities behind MediaPipe, OpenCV, Mosquitto MQTT, and Node-RED.
