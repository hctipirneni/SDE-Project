import time
import ujson
import urequests
from machine import I2C, Pin
from bme680 import Adafruit_BME680
from wlan_config import WLAN_SSID, WLAN_PASSWORD
import network
import usocket as socket

# ThingSpeak API key and channel ID
THINGSPEAK_API_KEY = 'QWXQFREQ5YEWHFKR'
THINGSPEAK_CHANNEL_ID = '2343445'

# Observer interface
class Observer:
    def update(self, data):
        pass

# Observable (Subject) interface
class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, data):
        for observer in self._observers:
            observer.update(data)

# Concrete implementation of Observer (Sensor)
class BME680_I2C(Adafruit_BME680):
    def __init__(self, i2c, address=0x77, debug=False, *, refresh_rate=10):
        self._i2c = i2c
        self._address = address
        self._debug = debug
        super().__init__(refresh_rate=refresh_rate)

    def _read(self, register, length):
        result = bytearray(length)
        self._i2c.readfrom_mem_into(self._address, register, result)
        if self._debug:
            print("\t${:x} read ".format(register), " ".join(["{:02x}".format(i) for i in result]))
        return result

    def _write(self, register, values):
        if self._debug:
            print("\t${:x} write".format(register), " ".join(["{:02x}".format(i) for i in values]))
        for value in values:
            self._i2c.writeto_mem(self._address, register, bytearray([value]))
            register += 1

    def read_sensor_data(self):
        self._perform_reading()  # Perform reading before accessing sensor values
        temperature = self.temperature
        pressure = self.pressure
        humidity = self.humidity
        gas_resistance = self.gas
        return {
            "temperature": temperature,
            "pressure": pressure,
            "humidity": humidity,
            "gas_resistance": gas_resistance,
        }

# Concrete implementation of Observable (Server)
class SensorServer(Observable):
    def __init__(self, i2c1, i2c2):
        super().__init__()
        self.sensor1 = BME680_I2C(i2c1)
        self.sensor2 = BME680_I2C(i2c2)

    def send_data(self):
        data1 = self.sensor1.read_sensor_data()
        data2 = self.sensor2.read_sensor_data()
        print(f"Sending data to observers: Sensor 1 - {data1}, Sensor 2 - {data2}")
        self.notify_observers({"sensor1": data1, "sensor2": data2})

    def send_data_thingspeak(self, data):
        url = f'https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}&field1={data["sensor1"]["temperature"]}&field2={data["sensor1"]["pressure"]}&field3={data["sensor1"]["humidity"]}&field4={data["sensor1"]["gas_resistance"]}&field5={data["sensor2"]["temperature"]}&field6={data["sensor2"]["pressure"]}&field7={data["sensor2"]["humidity"]}&field8={data["sensor2"]["gas_resistance"]}'
        response = urequests.get(url)
        print('Sending data to ThingSpeak:', response.text)

# Set up I2C and create the server
i2c1 = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
i2c2 = I2C(1, scl=Pin(3), sda=Pin(2), freq=100000)
server = SensorServer(i2c1, i2c2)

# Connect to WLAN using credentials from the separate file
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WLAN_SSID, WLAN_PASSWORD)
while not wlan.isconnected():
    time.sleep(1)

# Server address
ip = wlan.ifconfig()[0]
server_address = (ip, 8042)

# Socket connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(1)
print('Server listening on', server_address)

while True:
    print('Waiting for a connection...')
    client_socket, client_address = server_socket.accept()
    print('Accepted connection from', client_address)

    # Receive the request data
    request_data = client_socket.recv(1024).decode('utf-8')
    print('Received request:\n', request_data)

    # Extract the requested path from the request
    path = request_data.split(' ')[1]

    if path == '/':
        with open("index.html", "r") as file:
            html_content = file.read()
        # Construct the HTTP response
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html_content}"
        client_socket.sendall(response.encode('utf-8'))

    # Handle the "/sensor_data" route
    elif path == '/sensor_data':
        server.send_data()  # Send sensor data to observers

        # Send data to ThingSpeak
        server.send_data_thingspeak({
            "sensor1": server.sensor1.read_sensor_data(),
            "sensor2": server.sensor2.read_sensor_data(),
        })

        # Construct the JSON response with sensor data
        response_data = {
            "sensor1": server.sensor1.read_sensor_data(),
            "sensor2": server.sensor2.read_sensor_data(),
        }
        response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + ujson.dumps(response_data)
        client_socket.sendall(response.encode('utf-8'))

    # Close the client socket
    client_socket.close()

# Close the server socket when the script exits
server_socket.close()

