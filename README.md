# rpi_hardware_pwm

Access the hardware PWM of a RaspberryPi with Python. More lightweight than alternatives.

### Installation

Installation is a two step process:

1. On the Raspberry Pi, add `dtoverlay=pwm-2chan` to `/boot/config.txt`. **Reboot your Raspberry Pi**. This defaults to GPIO_18 as the pin for PWM0 and GPIO_19 as the pin for PWM1.
    - Alternatively, you can change GPIO_18 to GPIO_12 and GPIO_19 to GPIO_13 using `dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4`.
    - You can check everything is working on running `lsmod | grep pwm` and looking for `pwm_bcm2835`
2. Install this library: `sudo pip install rpi-hardware-pwm`



### Examples

```python
from rpi_hardware_pwm import HardwarePWM

pwm = HardwarePWM(0, hz=60)
pwm.start(100) # full duty cycle

pwm.change_duty_cycle(50)

pwm.stop()


```

### History

The original code is from [jdimpson/syspwm](https://github.com/jdimpson/syspwm), We've updated it to Python3 and
made it look like the `RPi.GPIO` library's API (but more Pythonic than that.), and we use it in [Pioreactor](https://pioreactor.com) bioreactor system.

