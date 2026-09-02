# ESP32 Climate Monitor with Azure & Tuya Integration

This project is an end-to-end IoT solution that collects environmental data via an ESP32 microcontroller and autonomously triggers a smart Tuya air conditioning unit through a Microsoft Azure backend.

## System Architecture

🔹 **Edge Hardware**
* An `ESP32` microcontroller paired with a `DHT22` temperature and humidity sensor, programmed in `MicroPython`.

🔹 **Cloud Backend**
* A serverless `Azure Function` (Python v2 model) that ingests telemetry data via HTTP triggers.

🔹 **Smart Home Integration**
* `Tuya IoT Platform OpenAPI` for remote device execution.

## Core Automation Logic

The ESP32 continuously monitors local climate conditions and transmits telemetry directly to the Azure Function using native TCP socket connections. The serverless backend evaluates this data against predefined environmental thresholds:

🔹 **Cooling Trigger**
* If the temperature reaches `27.0°C` or higher, the AC activates on `Cool` mode at `24°C`.

🔹 **Dehumidification Trigger**
* If humidity reaches `60.0%` or higher (in optimal temperatures), the AC activates on `Wet` (Dehumidify) mode.

Upon meeting a threshold, the Azure Function authenticates securely with the Tuya Cloud API and dispatches the precise control payload to the physical smart AC unit, fully automating the climate control process.
