import network
import time
import dht
import machine
import socket

WIFI_SSID = "YOUR-WIFI-SSID"
WIFI_PASSWORD = "YOUR-WIFI-PASSWORD"

HOST = "YOUR-AZURE-APP-NAME.azurewebsites.net"
PATH = "/api/YOUR_FUNCTION_NAME"

sensor = dht.DHT22(machine.Pin(4))

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi network...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Connection established! IP Address:", wlan.ifconfig()[0])

def read_sensor():
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print(f"Data read - Temperature: {temp}°C | Humidity: {hum}%")
        return temp, hum
    except Exception as e:
        print("Sensor error:", e)
        return None, None

def send_data_azure(temp, hum):
    try:
        query_path = f"{PATH}?temp={temp}&hum={hum}"
        print("Connecting to server via TCP...")
        addr_info = socket.getaddrinfo(HOST, 80)[0]
        addr = addr_info[-1]
        s = socket.socket()
        s.settimeout(10)
        s.connect(addr)
        request = f"GET {query_path} HTTP/1.1\r\nHost: {HOST}\r\nConnection: close\r\n\r\n"
        s.send(request.encode('utf-8'))
        response = s.read()
        print("Response received from Azure:", response)
        s.close()
    except Exception as e:
        print("Transmission error:", e)

connect_wifi()

while True:
    temp, hum = read_sensor()
    if temp is not None and hum is not None:
        send_data_azure(temp, hum)
    time.sleep(600)  # once every 10 minutes