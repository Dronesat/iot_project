  #include <WiFi.h>
  #include <PubSubClient.h>
  #include <ESP32Servo.h> 
  #include <LiquidCrystal.h>
  #include <OneWire.h>
  #include <DallasTemperature.h>

  // LCD1602 Pin Configuration
  LiquidCrystal lcd(19,23,18,17,16,15);
  const int lcdColumns = 16;
  const int lcdRows = 2;

  // Wi-Fi Credentials
  const char* ssid = "TALKTALK27B641-2-4Ghz";
  const char* password = "NXQ9DKXQ";

  // MQTT Broker Details
  const char* mqtt_server = "192.168.1.39";
  const char* mqtt_username = "hieu"; 
  const char* mqtt_password = "hieu";

  // Servo onject 
  Servo radiator_servo; 

  //DS18B20 Configuration
  const int oneWireBus = 22;     
  OneWire oneWire(oneWireBus);
  DallasTemperature DS18B20_sensors(&oneWire);

  // MQTT Client
  WiFiClient espClient;
  PubSubClient client(espClient);

  // Flags to track sensor status
  bool tempWorking = true; 
  float temperatureGlobal;

  int radiator_valve = 0;

  void setup() {
    Serial.begin(115200);
    radiator_servo.attach(27);

    // Start the DS18B20 sensor
    DS18B20_sensors.begin();

    // Setup Wi-Fi and MQTT
    setup_wifi(); 
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);

    //Initialise LCD
    lcd.begin(lcdColumns, lcdRows);
    lcd.clear();
    lcd.print("Initialising...");
    delay(1000); 
  }

  void setup_wifi() {
    delay(10);
    // Start by connecting to a WiFi network
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    lcd.print("Connecting...");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  }

  void callback(char* topic, byte* message, unsigned int length) {
    Serial.print("Message arrived on topic: ");
    Serial.print(topic);
    Serial.print(". Message: ");
    String messageTemp;
  
    for (int i = 0; i < length; i++) {
      Serial.print((char)message[i]);
      messageTemp += (char)message[i];
      }
    Serial.println();

    // Control Servo
    if (String(topic) == "esp32/radiator_servo") {
      Serial.print("Radiator valve servo position: ");
      radiator_valve = messageTemp.toInt(); 
      int pos = map(radiator_valve, 0, 5, 0, 180);
      Serial.println(pos);
      radiator_servo.write(pos);
      //delay(15);
      }
  }

  void reconnect() {
    while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("ESP32-Client", mqtt_username, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("esp32/radiator_servo");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
      }
    }
  }

  void tempSensor() {
    // Sensor Readings
    DS18B20_sensors.requestTemperatures(); 
    float temperatureC = DS18B20_sensors.getTempCByIndex(0);
    temperatureGlobal = temperatureC;

    if (!isnan(temperatureC)) {
    // Publish temp readings to MQTT topics
    Serial.print(F("Temperature: "));
    Serial.println(temperatureGlobal);
    client.publish("esp32/ds18b20/temperatureC", String(temperatureC).c_str());
    } else {
    Serial.println(F("Failed to read from temperature sensor!"));
    }

    if (isnan(temperatureC) || temperatureC == -127.00) {
          tempWorking = false;
      } else {
          tempWorking = true;
      }
  }

  void lcdDisplayStatus() {
    // Update LCD display
    lcd.clear();

    // Display Wi-Fi status
    if (WiFi.status() == WL_CONNECTED) {
        lcd.print("WiFi: Connected");
    } else {
        lcd.print("WiFi: Reconnecting");
    }

    // Display sensor status on second line
    lcd.setCursor(0, 1); // Move cursor to the second line
    if (tempWorking) {
          //lcd.print("Temp:"); // Added "Temp:" label
          lcd.print(temperatureGlobal, 1); // Display temperature with 1 decimal place
          lcd.print("C ");
          lcd.print(" Valve: ");
          lcd.print(radiator_valve);
    } else {
      lcd.print("Temp error");
    }
  }

  void loop() {
    if (!client.connected()) {
      reconnect();
    }
    client.loop(); 
    tempSensor();
    lcdDisplayStatus();

    //delay(1000);
  }