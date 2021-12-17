from bluepy.btle import Peripheral

TEMPERATURE_PREC = 2


class MiTempMonitor2Poller:
    """
    Inspired by https://github.com/erdose/xiaomi-mi-lywsd03mmc and refactored to work with our use case
    """

    def __init__(self, mac):
        self._mac = mac
        self.peripheral = Peripheral(self._mac)

        # enable notifications of Temperature, Humidity and Battery voltage
        self.peripheral.writeCharacteristic(0x0038, b"\x01\x00", True)
        self.peripheral.writeCharacteristic(0x0046, b"\xf4\x01\x00", True)

        self.peripheral.withDelegate(self)

    def fetch_values(self):
        """
        Returns a dict with two keys: temperature and humidity
        """
        self.peripheral.waitForNotifications(10.0)
        return self._data

    def handleNotification(self, handle, raw_data):
        """
        Handles the bluetooth data from the sensor.
        This method gets called when waitForNotifications is called
        """
        temperature = round(int.from_bytes(raw_data[0:2], byteorder="little", signed=True) / 100, TEMPERATURE_PREC)
        humidity = int.from_bytes(raw_data[2:3], byteorder="little")
        self._data = {"temperature": temperature, "humidity": humidity}
