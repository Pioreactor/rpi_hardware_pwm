# rpi_hardware_pwm

Access the hardware PWM of a RaspberryPi with Python. More lightweight than alternatives.

### Examples

```python
from rpi_hardware_pwm import HardwarePWM

pwm = HardwarePWM(0, hz=60)
pwm.start(100) # full duty cycle

pwm.change_duty_cycle(50)

pwm.stop()


```


### History

The original code is from [jdimpson/syspwm](https://github.com/jdimpson/syspwm), I've updated it to Python3 and
made it look like the `RPi.GPIO` library's API (but more Pythonic than that.)

