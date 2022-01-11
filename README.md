# IOT Dashboard
## Problem to solve
With the COVID-19 pandemic, we were all forced to work from home. This brought a whole new set of new hobbies and problems with it, that we try to address with this IoT project.

## Devices
### Philipps Hue
Philipps Hue is a system that consists of LED lamps, sensors, and switches. The system can be controlled manually using a Smartphone or can be automated, for example using Apple HomeKit.

### Xiaomi Miflora
The Miflora is a wireless bluetooth sensor platform that allows to monitor the condition of plants. It monitors the moisture, ambient light, and temperature.

### Xiamoi Temperature and Humidity Monitor 2
The Temperature and Humidity Monitor 2 is a small bluetooth device with an integrated display. It can display the room temperature and humidity.

## Files
In the following sections all files and their use are described.

### configuration.yaml
An example configuration file `example.configuration.yaml` is provided.

### configuration.py
Abstraction layer for the `configuration.yaml` file that contains all the config items for this project.
This file handles loading and accessing the configuration file.

### flower_status.py
Reads the data from one Xiaomi Miflora plant sensor and publishes the `temperature`, `moisture`, and `light` data as a JSON object to a message queue in the topic `sensor/flower`.
JSON format:
```json
{
  "temperature": 12,
  "moisture": 35.7,
  "light": 150
}
```

### room_monitor.py
Reads the data from one Xiaomi Temperature and Humidity monitor 2 and publishes the `temperature` and `humidity` data as a JSON object to a message queue in the topic `sensor/room`.
JSON format:
```json
{
  "temperature": 26.2,
  "humidity": 42,
}
```

### hue_light_status.py
Reads the data from Philips Hue light system and publishes the light groups with their `name` and `state` (`on`/`off`) data as a JSON object to a message queue in the topic `sensor/hue/light`.
JSON format:
```json
[
  {
    "name": "Living Room",
    "state": true
  },
  {
    "name": "Hallway",
    "state": false
  }
]
```

### hue_light_control.py
This script can turn Philips Hue lights on and off depending on their current light status.
The script expects a json object as string as the first parameter where the group name is saved in the `name` property of the json object.
The group name has to be converted to the interal Hue id to control the lights of the group.

### hue_motion_sensor.py
Reads the motion sensor data from the Philipps Hue bridge and publishes the sensor information to MQTT with the information `presence_detected` to the topic `sensor/hue/motion`.
**The event will only be published when presence is detected. Otherwhise nothing will be sent.**
```json
{
    "presence_detected": true
}
```

### node_red_flow.json
This file contains the node-red flows that are used to build the dashboard and read the data.

### rain_check.py
Reads the weather data from `pyowm` and checks the next hours for rain. The output will be written to `stdout` for further processing in node-red.
JSON format:
```json
{
  "will_rain": true
}
```

### umbrella_detection.py
Fetches one image from the attached webcam and executes an object recognition search using `tensorflow`. The result will be written to `stdout` for further processing in node-red.
JSON format:
```json
{
  "umbrella_detected": true
}
```

### weather_forecast.py
Reads the weather data from `pyowm` and gets the forecast for the next 5 days. The output will be written to `stdout` for further processing in node-red.
JSON format:
```json
[
  {
    "date_unix": "12345",
    "date_formatted": "17.12",
    "min_temperature": 0,
    "max_temperature": 10,
    "status": "cloudy",
    "detailed_status": "cloudy overcast"
  },
  {
    "date_unix": "12345",
    "date_formatted": "18.12",
    "min_temperature": 0,
    "max_temperature": 12,
    "status": "cloudy",
    "detailed_status": "cloudy overcast"
  }
]
```

### send_umbrella_reminder.py
This file is responsible for sending a whatsapp message to the configured number with the reminder that the umbrella was forgotten.

## Used Libraries
The following libraries were used for this project.
| Library | Version | Use case |
| ------- | ------- | -------- |
|`bluepy`|1.3.0|Python library to interface with the bluetooth system on Linux.|
|`btlewrap`|0.0.10|Bluetooth wrapper library for different bluetooth backends.|
|`pyowm`|3.2.0|Library to read weather information from OpenWeatherMap (OWM). Used to check for rain and get the weather forecast.|
|`phue`|1.1|Used to read the data from the Philipps Hue light system.|
|`miflora`|0.7.1|Used to read sensor data from the Xiaomi Miflora plant sensor.|
|`tflite_runtime`|2.5.0.post1|AI library to run object recognition on a webcam image with the aim to detect if an umbrella is present or not. Runtime/Light version of `tensorflow`|
|`numpy`|1.16.2|Used to transform the image for `tensorflow`.|
|`opencv`|4.1.0.25|Fetch the picture from the attached webcam.| 
|`paho_mqtt`|1.6.1|MQTT library for Python|
|`requests`|2.21.0|Library to execute HTTP requests|
|`twilio`|7.4.0|Library to send whatsapp or sms|