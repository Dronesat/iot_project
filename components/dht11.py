import sys
import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt

# MQTT Broker Configuration
mqtt_server = "192.168.1.39"
mqtt_username = "hieu"
mqtt_password = "hieu"
mqtt_port = 1883
topic_temperature = "rpi/dht11/temperature"
topic_humidity = "rpi/dht11/humidity"

# DHT11 Sensor Setup
sensor = adafruit_dht.DHT11(board.D14, use_pulseio=True)

# MQTT Functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

# MQTT client setup
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.on_connect = on_connect 
client.connect(mqtt_server, mqtt_port)  

# Start client loop
client.loop_start() 

def dynamic_print(input):
    output_text = f"{input}    "
    sys.stdout.write("\r" + output_text) 
    sys.stdout.flush()

def publish_sensor_data(temp, humidity):
    client.publish(topic_temperature, temp)
    client.publish(topic_humidity, humidity)

while True:
    try:
        temperature_c = sensor.temperature
        humidity = sensor.humidity
        dynamic_print(f"\rTemp: {temperature_c} C, Humidity: {humidity} % ")
        publish_sensor_data(temperature_c, humidity)
    except RuntimeError:
        continue  # Ignore errors
    except Exception as error:
        sensor.exit()  
        client.loop_stop() 
        client.disconnect()
        raise error

    time.sleep(2.0) 
