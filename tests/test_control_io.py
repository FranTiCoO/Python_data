import importlib
import sys
import types
import unittest
from pathlib import Path


class FakePWM:
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.started = False
        self.duty_cycles = []
        self.stopped = False

    def start(self, value):
        self.started = True
        self.start_value = value

    def ChangeDutyCycle(self, value):
        self.duty_cycles.append(value)

    def stop(self):
        self.stopped = True


class FakeGPIO:
    BCM = 1
    OUT = 2
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.mode = None
        self.outputs = {}
        self.setups = {}
        self.pwm_objects = []

    def setmode(self, mode):
        self.mode = mode

    def getmode(self):
        return self.mode

    def setup(self, pin, mode):
        self.setups[pin] = mode

    def output(self, pin, value):
        self.outputs[pin] = value

    def PWM(self, pin, frequency):
        pwm = FakePWM(pin, frequency)
        self.pwm_objects.append(pwm)
        return pwm


class ControlIOPWMTests(unittest.TestCase):
    def setUp(self):
        self.fake_gpio = FakeGPIO()
        self.fake_gpio_module = types.ModuleType("RPi.GPIO")
        self.fake_gpio_module.BCM = FakeGPIO.BCM
        self.fake_gpio_module.OUT = FakeGPIO.OUT
        self.fake_gpio_module.HIGH = FakeGPIO.HIGH
        self.fake_gpio_module.LOW = FakeGPIO.LOW
        self.fake_gpio_module.setmode = self.fake_gpio.setmode
        self.fake_gpio_module.getmode = self.fake_gpio.getmode
        self.fake_gpio_module.setup = self.fake_gpio.setup
        self.fake_gpio_module.output = self.fake_gpio.output
        self.fake_gpio_module.PWM = self.fake_gpio.PWM

        self.fake_rpi_module = types.ModuleType("RPi")
        self.fake_rpi_module.GPIO = self.fake_gpio_module

        sys.modules["RPi"] = self.fake_rpi_module
        sys.modules["RPi.GPIO"] = self.fake_gpio_module

        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        sys.modules.pop("control_io", None)

        self.control_io_module = importlib.import_module("control_io")
        self.control_io = self.control_io_module.ControlIO(gpio_module=self.fake_gpio_module, logger_instance=types.SimpleNamespace(debug=lambda *args, **kwargs: None))

    def test_output_pwm_reuses_the_same_pwm_instance(self):
        self.control_io.output_pwm(25)
        self.control_io.output_pwm(75)

        self.assertEqual(len(self.fake_gpio.pwm_objects), 1)
        self.assertEqual(self.fake_gpio.pwm_objects[0].duty_cycles, [25.0, 75.0])

    def test_cleanup_stops_pwm_and_releases_gpio(self):
        self.control_io.output_pwm(50)
        self.control_io.cleanup()

        self.assertTrue(self.fake_gpio.pwm_objects[0].stopped)
        self.assertEqual(self.fake_gpio.outputs[self.control_io.pin_pump_toggle], self.fake_gpio.LOW)
        self.assertEqual(self.fake_gpio.outputs[self.control_io.pin_light_toggle], self.fake_gpio.LOW)
        self.assertEqual(self.fake_gpio.outputs[self.control_io.pin_light_mode], self.fake_gpio.LOW)


if __name__ == "__main__":
    unittest.main()
