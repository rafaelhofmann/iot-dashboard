# IOT Dashboard

## Sensors
### Philipps Hue

### Xiaomi Miflora

### Xiamoi Temperature and Humidity Monitor 2

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

### hue_status.py
Reads the data from Philipps Hue light system and publishes the light groups with their `name` and `state` (`on`/`off`) data as a JSON object to a message queue in the topic `sensor/hue`.
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

### weather_forecast
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

## Used Libraries
The following libraries were used for this project.
| Library | Use case |
| ------- | -------- |
|`pyowm`|Library to read weather information from OpenWeatherMap (OWM). Used to check for rain and get the weather forecast.|
|`phue`|Used to read the data from the Philipps Hue light system.|
|`miflora`|Used to read sensor data from the Xiaomi Miflora plant sensor.|
|`tensorflow`|AI library to run object recognition on a webcam image with the aim to detect if an umbrella is present or not.|
|`numpy`|Used to transform the image for `tensorflow`|
|`opencv`|Fetch the picture from the attached webcam| 
