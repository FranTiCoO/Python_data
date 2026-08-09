# OrchideenPi Overview

This application controls and monitors an orchid setup.

## Functionalities

- Reads temperature and humidity from a DHT22 sensor.
- Reads light intensity from a TSL2561 sensor.
- Controls actuators through GPIO outputs.
- Regulates temperature using PID-based PWM control.
- Runs timed behavior for sensors, pump, and light mode.
- Writes measurement data to a database.
- Applies runtime configuration updates through an RPC interface.
- Uses central logging for runtime events and error tracking.

## Main Runtime Components

- `main.py`: starts the runtime loop.
- `timer.py`: controls scheduled actions.
- `control_io.py`: handles GPIO outputs and PWM.
- `dht22.py`: sensor read handling for DHT22.
- `tsl2561.py`: sensor read handling for TSL2561.
- `pid_controller.py`: temperature control behavior.
- `writeDB.py`: data output to storage.
- `server.py`: receives configuration update requests.
- `config.py`: runtime configuration values.
- `logger_setup.py`: logging setup.
