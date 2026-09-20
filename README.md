# Smart-Water-Monitoring-System
IoT-based Smart Water Monitoring System using ESP32, Wokwi and ThingSpeak.

## 2. Problem Statement

Traditional water tank monitoring systems often require manual checking of water levels and may not provide continuous information about environmental conditions or water quality. Manual monitoring can lead to water overflow, insufficient water availability, and delayed detection of poor water conditions.

The Smart Water Monitoring System is designed to monitor water level, temperature, humidity, and simulated water quality using an ESP32-based IoT system. The system automatically controls a water pump according to the water level and safety conditions. It also provides an alarm when the simulated water quality falls below the defined safe threshold.

The system sends the monitored data to the ThingSpeak cloud platform, allowing the data to be viewed remotely through graphs and providing a cloud-based pump control command.

## 3. Objectives

- To monitor the water level of a tank using an HC-SR04 ultrasonic sensor.
- To monitor temperature and humidity using a DHT22 sensor.
- To simulate water-quality monitoring using a potentiometer as an analog sensor.
- To automatically control a water pump using a relay based on the water level.
- To provide an alarm when the simulated water quality falls below the defined threshold.
- To indicate the system status using green and red LEDs.
- To send sensor data and system status to the ThingSpeak cloud platform.
- To receive a pump-control command from ThingSpeak for remote control.
- To implement safety conditions that prevent the pump from operating when water quality is poor or the tank level is too high.
- To visualize the monitored data through ThingSpeak graphs.

- ## 4. Components and Software Used

### Hardware Components

- ESP32 Development Board
- HC-SR04 Ultrasonic Sensor
- DHT22 Temperature and Humidity Sensor
- Potentiometer (used to simulate a water-quality sensor)
- Relay Module
- Green LED
- Red LED
- Buzzer
- 220Ω Resistors
- Connecting Wires

### Software and Platforms

- Wokwi — for circuit design and ESP32 simulation
- MicroPython — for programming the ESP32
- ThingSpeak — for IoT cloud data monitoring and remote pump-control commands
- GitHub — for storing and documenting the project

- ## 5. Circuit Diagram

The circuit is designed using an ESP32 and the required sensors and output devices. The ESP32 acts as the main controller and communicates with the sensors, relay, LEDs, buzzer, and ThingSpeak cloud platform.

The main connections are:

| Component | ESP32 GPIO |
|---|---:|
| DHT22 Data | GPIO 15 |
| HC-SR04 Trigger | GPIO 5 |
| HC-SR04 Echo | GPIO 18 |
| Potentiometer Signal | GPIO 34 |
| Relay IN | GPIO 23 |
| Green LED | GPIO 26 |
| Red LED | GPIO 25 |
| Buzzer | GPIO 27 |

The DHT22 and potentiometer are powered from 3.3V, while the HC-SR04 and relay module are powered from 5V. All components share a common ground with the ESP32.


## 6. Working Principle

The Smart Water Monitoring System uses an ESP32 as the main controller. The system continuously collects data from the connected sensors and uses the measured values to monitor the condition of the water tank.

The HC-SR04 ultrasonic sensor measures the distance between the sensor and the water surface. This distance is used to calculate the water level percentage based on the assumed tank height of 100 cm.

The DHT22 sensor measures the temperature and humidity of the surrounding environment. The potentiometer is used as a simulated water-quality sensor. Its analog reading is converted into a percentage value representing the simulated water quality.

The ESP32 controls the water pump through a relay. In automatic mode, the pump is switched ON when the water level falls below 20% and switched OFF when the water level rises above 80%. Between these levels, the previous pump state is retained.

If the simulated water quality falls below 40%, the system activates the red LED and buzzer, switches the pump OFF, and generates an alarm condition. This safety condition takes priority over the pump command received from the cloud.

The system communicates with the ThingSpeak cloud platform through Wi-Fi. Sensor readings and system status are uploaded to ThingSpeak, while the pump-control command is read from Field 8. Field 8 supports three commands: automatic mode, force pump OFF, and request pump ON. High water level and poor water quality safety conditions can override a pump ON request.

The green LED indicates normal operation, while the red LED and buzzer indicate a poor water-quality alarm.


## 7. Program Explanation

The ESP32 program is written in MicroPython and is divided into several functional sections.

### a] Library and Hardware Initialization

The program imports the required MicroPython libraries for Wi-Fi communication, timing, DHT22 sensing, HTTP requests, GPIO control, ADC input, PWM output, and ultrasonic pulse measurement.
The ESP32 GPIO pins are configured for the DHT22, HC-SR04, potentiometer, relay, LEDs, and buzzer.

### b] Wi-Fi Connection

The ESP32 connects to the Wokwi-GUEST Wi-Fi network. A successful connection is required for communication with ThingSpeak.

### c] Water Level Measurement

The HC-SR04 ultrasonic sensor sends an ultrasonic pulse and measures the return time. The measured distance is converted into water level percentage using the following calculation:
Water Level (%) = ((Tank Height - Distance) / Tank Height) × 100
The assumed tank height in the project is 100 cm. The calculated value is limited to a range of 0% to 100%.

### d] Temperature and Humidity Measurement

The DHT22 sensor measures temperature in degrees Celsius and relative humidity in percentage.

### e] Simulated Water-Quality Measurement

The potentiometer is connected to the ESP32 analog input at GPIO 34. Its ADC value ranges from 0 to 4095 and is converted into a percentage to represent simulated water quality.
The water-quality condition is classified using the following threshold:
- Below 40% — Poor Water Quality
- 40% to below 70% — Moderate Water Quality
- 70% and above — Good Water Quality

### f] Pump Control and Safety Logic

The relay connected to GPIO 23 controls the pump state.
In automatic mode:
- If the water level is below 20%, the pump is turned ON.
- If the water level is above 80%, the pump is turned OFF.
- Between 20% and 80%, the previous pump state is retained.
If the simulated water quality falls below 40%, the pump is always switched OFF and the alarm is activated.

### g] ThingSpeak Cloud Control

The ESP32 uploads water level, temperature, water quality, pump status, alarm status, humidity, and water distance to ThingSpeak.
The program reads the pump-control command from ThingSpeak Field 8:
- 0 — Automatic mode
- 1 — Force Pump OFF
- 2 — Request Pump ON
The cloud command cannot override the safety conditions for poor water quality or excessively high water level.

### h] LED and Buzzer Indication

The green LED indicates normal operation. When poor water quality is detected, the red LED turns ON and the buzzer is activated.

### i] Continuous Monitoring

After processing the sensor readings and updating ThingSpeak, the program waits for 20 seconds and repeats the process. This allows the system to continuously monitor the water tank and update the cloud platform.


## 8. Output

The Smart Water Monitoring System was successfully simulated and tested in Wokwi. The system responded correctly to different water-level, water-quality, and cloud-control conditions.
The following outputs were observed during testing:

### Automatic Mode

When ThingSpeak Field 8 was set to `0` (Automatic Mode) and the water level was below 20%, the ESP32 turned the pump ON through the relay.

- Water Level: Approximately 2.7%
- Water Quality: Above 40%
- Pump Status: ON
- Alarm Status: OFF
- Mode: Automatic

### Cloud Force OFF

When ThingSpeak Field 8 was set to `1`, the system switched the pump OFF.

- Pump Status: OFF
- Alarm Status: OFF
- Mode: Cloud Force OFF

### Cloud Request ON

When ThingSpeak Field 8 was set to `2` and the water level was suitable for pumping, the ESP32 turned the pump ON.

- Pump Status: ON
- Alarm Status: OFF
- Mode: Cloud Request ON

### Poor Water-Quality Safety Test

When the simulated water quality was reduced below 40%, the safety condition was activated.

- Water Quality: Approximately 15%
- Pump Status: OFF
- Alarm Status: ON
- Red LED: ON
- Buzzer: ON
- Relay: OFF

The poor water-quality safety condition overrides a pump ON request from ThingSpeak.

### ThingSpeak Output

The ESP32 successfully uploaded the monitored data to the ThingSpeak channel. The following fields were used:

1. Water Level
2. Temperature
3. Water Quality
4. Pump Status
5. Alarm Status
6. Humidity
7. Water Distance
8. Pump Control

The ThingSpeak graphs displayed the sensor readings and system status received from the ESP32.


## 9. Applications

The Smart Water Monitoring System demonstrates how IoT technology can be used for water management, monitoring, automation, and remote control.

The system can be applied in the following areas:

- **Household Water Tank Management:** The system can monitor the water level of overhead or underground storage tanks and automatically control the water pump.

- **Small Building Water Management:** The system can be adapted for apartments, offices, educational institutions, or small commercial buildings where regular monitoring of water storage is required.

- **Remote Water Monitoring:** Sensor readings can be transmitted to ThingSpeak, allowing users to view water-level, temperature, humidity, water-quality, and pump-status data remotely.

- **Water-Quality Alert Systems:** With an appropriate real water-quality sensor replacing the potentiometer used in this prototype, the system could provide alerts when water-quality measurements fall below a defined threshold.

- **IoT and Automation Education:** The project can be used as an educational model for learning ESP32 programming, sensor interfacing, relay control, cloud communication, data visualization, and IoT-based automation.


## 10. Limitations

The Smart Water Monitoring System has the following limitations:

- The project is developed and tested in the Wokwi simulation environment and has not been tested as a physical hardware installation.

- The potentiometer is used as a simulated water-quality sensor. Therefore, the current prototype does not perform actual measurement of parameters such as turbidity, pH, or dissolved substances.

- The water-level calculation assumes a tank height of 100 cm. A real installation would require calibration according to the actual tank dimensions and sensor position.

- The HC-SR04 ultrasonic sensor may require appropriate electrical interfacing and protection when connected to a real ESP32 hardware setup.

- The ThingSpeak cloud connection depends on network availability. If the ESP32 cannot connect to the network, cloud data transmission and remote pump-control commands will not be available.

- The prototype uses predefined thresholds for water level and simulated water quality. These thresholds may need to be adjusted for different tanks, environments, or applications.

- The simulated relay controls the pump logic in Wokwi, but the project does not represent the complete electrical and safety requirements of controlling a real water pump.


## 11. Future Scope

The Smart Water Monitoring System can be further improved and extended in the following ways:

- **Real Water-Quality Sensor:** The potentiometer used in the prototype can be replaced with a suitable calibrated water-quality or turbidity sensor for real-world measurements.

- **Mobile Application:** A mobile application could be developed to display sensor readings, pump status, alarms, and notifications in a more user-friendly manner.

- **Multiple Water Tanks:** The system could be extended to monitor multiple tanks and control their pumps using additional sensors and relay channels.

- **Advanced Notifications:** Email, mobile, or other notification services could be integrated to alert users about low water level, high water level, poor water quality, or system failures.

- **Improved Sensor Calibration:** Real hardware implementation could include calibration procedures to improve the accuracy of water-level and water-quality measurements.

- **Data Analysis:** Historical ThingSpeak data could be analyzed to identify water usage patterns and support better water-management decisions.

- **Solar-Powered Operation:** A suitable solar power system and battery could be added for applications where continuous operation with reduced dependence on conventional power is required.

- **Physical Hardware Implementation:** The Wokwi prototype can be converted into a physical ESP32-based system with appropriate electrical protection and a properly rated pump-control circuit.


Team Member's Details
1. Manya V - U03ZW24S0126 5th semester BCA B
2. Chanadana R - U03ZW24S0012 5th semester BCA B


## 13. Wokwi Project Link

The final Smart Water Monitoring System was designed, programmed, and tested using Wokwi.

[Open the Wokwi Project](https://wokwi.com/projects/475514499103966209)


## 14. ThingSpeak Channel Link

The Smart Water Monitoring System sends sensor readings and system status to the ThingSpeak cloud platform.

[Open the ThingSpeak Channel](https://thingspeak.com/channels/3498720)


