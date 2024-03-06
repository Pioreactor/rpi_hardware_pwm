#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path

class HardwarePWMException(Exception):
    pass



class HardwarePWM:
    """
    Control the hardware PWM on the Raspberry Pi. Need to first add `dtoverlay=pwm-2chan` to `/boot/config.txt`.

    pwm0 is GPIO pin 18 is physical pin 32 (dtoverlay can be deployed to use GPIO 12 instead)
    pwm1 is GPIO pin 19 is physical pin 33 (dtoverlay can be deployed to use GPIO 13 instead)

    Example
    ----------
    >pwm = HardwarePWM(0, hz=20)
    >pwm.start(100)
    >
    >pwm.change_duty_cycle(50)
    >pwm.change_frequency(50)
    >
    >pwm.stop()

    Notes
    --------
     - For Rpi 1,2,3,4, use chip=0; For Rpi 5, use chip=2
     - For Rpi 1,2,3,4 only channels 0 and 1 are available
     - If you get "write error: Invalid argument" - you have to set duty_cycle to 0 before changing period
     - /sys/ pwm interface described here: https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html

    """

    _duty_cycle: float
    _hz: float
    chippath: str = "/sys/class/pwm/pwmchip0" # mostly here for testing

    def __init__(self, pwm_channel: int, hz: float, chip: int = 0) -> None:

        if pwm_channel not in {0, 1, 2, 3}:
            raise HardwarePWMException("Only channel 0 and 1 and 2 and 3 are available on the Rpi.")

        self.chippath: str = f"/sys/class/pwm/pwmchip{chip}"
        self.pwm_channel = pwm_channel
        self.pwm_dir = f"{self.chippath}/pwm{self.pwm_channel}"
        self._duty_cycle = 0

        if not self.is_overlay_loaded():
            raise HardwarePWMException(
                "Need to add 'dtoverlay=pwm-2chan' to /boot/config.txt and reboot"
            )
        if not self.is_export_writable():
            raise HardwarePWMException(f"Need write access to files in '{self.chippath}'")
        if not self.does_pwmX_exists():
            self.create_pwmX()

        while True:
            try:
                self.change_frequency(hz)
                break
            except PermissionError:
                continue


    def is_overlay_loaded(self) -> bool:
        return os.path.isdir(self.chippath)

    def is_export_writable(self) -> bool:
        return os.access(os.path.join(self.chippath, "export"), os.W_OK)

    def does_pwmX_exists(self) -> bool:
        return os.path.isdir(self.pwm_dir)

    def echo(self, message: int, file: str) -> None:
        with open(file, "w") as f:
            f.write(f"{message}\n")

    def create_pwmX(self) -> None:
        self.echo(self.pwm_channel, os.path.join(self.chippath, "export"))

    def start(self, initial_duty_cycle: float) -> None:
        self.change_duty_cycle(initial_duty_cycle)
        self.echo(1, os.path.join(self.pwm_dir, "enable"))

    def stop(self) -> None:
        self.change_duty_cycle(0)
        self.echo(0, os.path.join(self.pwm_dir, "enable"))

    def change_duty_cycle(self, duty_cycle: float) -> None:
        """
        a value between 0 and 100
        0 represents always low.
        100 represents always high.
        """
        if not (0 <= duty_cycle <= 100):
            raise HardwarePWMException("Duty cycle must be between 0 and 100 (inclusive).")
        self._duty_cycle = duty_cycle
        per = 1 / float(self._hz)
        per *= 1000  # now in milliseconds
        per *= 1_000_000  # now in nanoseconds
        dc = int(per * duty_cycle / 100)
        self.echo(dc, os.path.join(self.pwm_dir, "duty_cycle"))

    def change_frequency(self, hz: float) -> None:
        if hz < 0.1:
            raise HardwarePWMException("Frequency can't be lower than 0.1 on the Rpi.")

        self._hz = hz

        # we first have to change duty cycle, since https://stackoverflow.com/a/23050835/1895939
        original_duty_cycle = self._duty_cycle
        if self._duty_cycle:
            self.change_duty_cycle(0)

        per = 1 / float(self._hz)
        per *= 1000  # now in milliseconds
        per *= 1_000_000  # now in nanoseconds
        self.echo(int(per), os.path.join(self.pwm_dir, "period"))

        self.change_duty_cycle(original_duty_cycle)
