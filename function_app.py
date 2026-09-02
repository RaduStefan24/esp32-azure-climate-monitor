import os
import logging
import azure.functions as func
from tuya_connector import TuyaOpenAPI

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="climate_trigger")
def climate_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP request received from ESP32.')

    # 1. Extract parameters from the URL
    temp_str = req.params.get('temp')
    hum_str = req.params.get('hum')

    if not temp_str or not hum_str:
        return func.HttpResponse("Error: Missing data. Add '?temp=value&hum=value'.", status_code=400)

    try:
        temperature = float(temp_str)
        humidity = float(hum_str)
    except ValueError:
        return func.HttpResponse("Error: Parameters must be numbers.", status_code=400)

    # 2. Set decision thresholds
    TEMP_THRESHOLD = 27.0
    HUMIDITY_THRESHOLD = 60.0

    # 3. Determine the commands to send to Tuya
    tuya_commands = []
    success_message = ""

    if temperature >= TEMP_THRESHOLD:
        # Priority 1: If it's hot, turn on Cooling at 24 degrees
        # temp_set has scale=1 on this device => 24°C is sent as 240
        tuya_commands = [
            {'code': 'switch', 'value': True},
            {'code': 'mode', 'value': 'cold'},
            {'code': 'temp_set', 'value': 240}
        ]
        success_message = f"It is {temperature}°C. Turned on the AC to Cool at 24°C."

    elif humidity >= HUMIDITY_THRESHOLD:
        # Priority 2: If the temperature is below the threshold, but it's humid, turn on dehumidification
        # the device doesn't have 'dry', the equivalent is 'wet'
        tuya_commands = [
            {'code': 'switch', 'value': True},
            {'code': 'mode', 'value': 'wet'}
        ]
        success_message = f"Humidity is {humidity}%. Turned on the AC to Dehumidify (Wet)."

    else:
        return func.HttpResponse(f"Temp: {temperature}°C, Humidity: {humidity}%. Optimal conditions. AC remains off.", status_code=200)

    # 4. Authenticate and send command
    ACCESS_ID = os.environ.get("TUYA_CLIENT_ID")
    ACCESS_KEY = os.environ.get("TUYA_CLIENT_SECRET")
    DEVICE_ID = os.environ.get("TUYA_DEVICE_ID")
    ENDPOINT = "https://openapi.tuyaeu.com"

    try:
        openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.connect()

        final_command = {'commands': tuya_commands}
        result = openapi.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', final_command)

        logging.info(f"Tuya response: {result}")

        if not result.get('success'):
            return func.HttpResponse(
                f"Tuya rejected the command: {result}",
                status_code=500
            )

        return func.HttpResponse(success_message, status_code=200)

    except Exception as e:
        logging.error(f"Tuya API Error: {e}")
        return func.HttpResponse(f"Internal error communicating with the device: {e}", status_code=500)
