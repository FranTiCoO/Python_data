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

## PID Self-Optimization

`simple_pid` does not provide automatic gain tuning. This project implements relay-feedback tuning around the configured temperature set point. The `PIDController` remains alive for the lifetime of the `DHT22` object, so its normal PID history and tuning measurements persist across sensor reads.

### How It Works

1. When `PID_SELF_OPTIMIZATION` is enabled, normal `simple_pid` output is disabled and tuning begins when the temperature controller is created.
2. At or below `SET_POINT`, the controller uses `PID_AUTOTUNE_OUTPUT_HIGH`. Above `SET_POINT`, it uses `PID_AUTOTUNE_OUTPUT_LOW`. This assumes higher PWM raises the temperature.
3. Each temperature crossing records the previous temperature extremum and its timestamp. The controller collects two extrema for each configured tuning cycle.
4. It averages the temperature oscillation amplitude $a$ and the period $P$, then calculates the relay's ultimate gain $K_u$ and Ziegler-Nichols PID gains:

$$
K_u = \frac{4d}{\pi a}, \qquad
K_p = 0.6K_u, \qquad
K_i = \frac{1.2K_u}{P}, \qquad
K_d = 0.075K_uP
$$

Here, $d$ is half the difference between the configured high and low PWM outputs.

5. The calculated gains are assigned to `config.KP`, `config.KI`, and `config.KD`, saved to `config.py`, installed in the active `simple_pid` instance, and normal PID control resumes.

### Enable Tuning

Configure the mode in `config.py` before starting the application:

```python
SET_POINT = 28.0

PID_SELF_OPTIMIZATION = True
PID_AUTOTUNE_OUTPUT_LOW = 0.0
PID_AUTOTUNE_OUTPUT_HIGH = 100.0
PID_AUTOTUNE_CYCLES = 3
```

`PID_AUTOTUNE_OUTPUT_LOW` must be less than `PID_AUTOTUNE_OUTPUT_HIGH`, both values must be within $0$ to $100$, and at least three cycles are required. The default $0$/$100$ range drives the actuator at full output during tuning; select narrower, safe limits for the connected heater or cooler and supervise the process.

After a successful tune, the calculated gains are saved automatically to `config.py` and therefore remain available after a restart. Set `PID_SELF_OPTIMIZATION = False` again once tuning is complete to avoid tuning on the next application start.

### Start Tuning While Running

The authenticated RPC server can start tuning on the live controller without restarting the application. After completing the normal TLS connection and `handshake`, call:

```python
print(connection.root.start_autotune())
```

The response is `PID self-optimization started` when the sensor controller is available. The next temperature measurement begins the relay-feedback cycle.

To wait for the completion signal and receive the saved gains, keep the connection open and call:

```python
result = connection.root.wait_for_autotune()
print(result)
```

On success, the result contains `{"state": "completed", "KP": ..., "KI": ..., "KD": ...}`. Pass a timeout in seconds to return early with `{"state": "running"}` when tuning has not finished yet:

```python
result = connection.root.wait_for_autotune(300)
```

To cancel an active tuning run, call:

```python
print(connection.root.cancel_autotune())
```

Cancellation restores normal PID control on the next temperature measurement. Any client waiting with `wait_for_autotune()` receives `{"state": "cancelled"}`.

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
