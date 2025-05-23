# rpi hardware pwm
![CI status](https://github.com/pioreactor/rpi_hardware_pwm/actions/workflows/ci.yaml/badge.svg)
[![PyPI version](https://badge.fury.io/py/rpi-hardware-pwm.svg)](https://badge.fury.io/py/rpi-hardware-pwm)

Access the hardware PWM of a Raspberry Pi with Python. More lightweight than alternatives.

### Installation

1. On the Raspberry Pi, add `dtoverlay=pwm-2chan` to `/boot/firmware/config.txt`. This defaults to `GPIO_18` as the pin for `PWM0` and `GPIO_19` as the pin for `PWM1`.
    - Alternatively, you can change `GPIO_18` to `GPIO_12` and `GPIO_19` to `GPIO_13` using `dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4`.
    - On the Pi 5, use channels 0 and 1 to control GPIO_12 and GPIO13, respectively; use channels 2 and 3 to control GPIO_18 and GPIO_19, respectively
    - On all other models, use channels 0 and 1 to control GPIO-18 and GPIO_19, respectively
2. **Reboot your Raspberry Pi**.
    - You can check everything is working on running `lsmod | grep pwm` and looking for `pwm_bcm2835`
3. Install this library: `sudo pip3 install rpi-hardware-pwm`



### Examples


```python
from rpi_hardware_pwm import HardwarePWM

pwm = HardwarePWM(pwm_channel=0, hz=60, chip=0)
pwm.start(100) # full duty cycle

pwm.change_duty_cycle(50)
pwm.change_frequency(25_000)

pwm.stop()


```

### History

The original code is from [jdimpson/syspwm](https://github.com/jdimpson/syspwm), We've updated it to Python3 and
made it look like the `RPi.GPIO` library's API (but more Pythonic than that.), and we use it in [Pioreactor](https://pioreactor.com) bioreactor system.

