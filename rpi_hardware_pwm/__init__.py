#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import perf_counter
from time import sleep
import os.path

class HardwarePWMException(Exception):
    pass



class HardwarePWM:
    """
    Control the hardware PWM on the Raspberry Pi. Need to first add `dtoverlay=pwm-2chan` to `/boot/config.txt`.

    pwm0 is GPIO pin 18 is physical pin 12 (dtoverlay can be deployed to use GPIO 12 (physical pin 32) instead)
    pwm1 is GPIO pin 19 is physical pin 35 (dtoverlay can be deployed to use GPIO 13 (physical pin 33) instead)

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
     - For Rpi 1,2,3,4, use chip=0; For Rpi 5, use chip=2. Update: As of linux kernel 6.12, chip=0 is used for all models.
     - For Rpi 1,2,3,4 only channels 0 and 1 are available
     - If you get "write error: Invalid argument" - you have to set duty_cycle to 0 before changing period
     - /sys/ pwm interface described here: https://web.archive.org/web/20200722035349/https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html

    """

    _duty_cycle: float
    _hz: float
    chippath: str = ""

    def __init__(self, pwm_channel: int, hz: float, chip: int = 0) -> None:

        if pwm_channel not in {0, 1, 2, 3}:
            raise HardwarePWMException("Only channel 0 and 1 and 2 and 3 are available on the Rpi.")

        if hz < 0.1:
            raise HardwarePWMException("Frequency can't be lower than 0.1 on the Rpi.")

        self.chippath: str = f"/sys/class/pwm/pwmchip{chip}"
        self.pwm_channel = pwm_channel
        self.pwm_dir = f"{self.chippath}/pwm{self.pwm_channel}"
        self._duty_cycle = 0
        self._hz = hz

        if not self.is_overlay_loaded():
            raise HardwarePWMException(
                "Need to add 'dtoverlay=pwm-2chan' to /boot/config.txt and reboot"
            )
        if not self.is_export_writable():
            raise HardwarePWMException(f"Need write access to files in '{self.chippath}'")
        if not self.does_pwmX_exists():
            self.create_pwmX()
        else:
            self.wait_for_pwmX_ready()

        # On first export, sysfs control files can exist before write permissions
        # are fully applied. Retry briefly to avoid flaky startup failures.
        self._retry_on_permission_error(lambda: self.__init_frequency(self._hz)) # set this first before DC
        self._retry_on_permission_error(lambda: self.__init_dc(self._duty_cycle))


    def is_overlay_loaded(self) -> bool:
        return os.path.isdir(self.chippath)

    def is_export_writable(self) -> bool:
        return os.access(os.path.join(self.chippath, "export"), os.W_OK)

    def is_pwmdir_writable(self) -> bool:
        return os.access(self.pwm_dir, os.W_OK)

    def is_control_writable(self, control_file: str) -> bool:
        control_path = os.path.join(self.pwm_dir, control_file)
        return os.path.exists(control_path) and os.access(control_path, os.W_OK)

    def does_pwmX_exists(self) -> bool:
        return os.path.isdir(self.pwm_dir)

    def echo(self, message: int, file: str) -> None:
        with open(file, "w") as f:
            f.write(f"{message}\n")

    def create_pwmX(self, timeout=10.0) -> None:
        self.echo(self.pwm_channel, os.path.join(self.chippath, "export"))
        self.wait_for_pwmX_ready(timeout=timeout)

    def wait_for_pwmX_ready(self, timeout=10.0) -> None:
        required_controls = ("period", "duty_cycle", "enable")
        start = perf_counter()
        while True:
            if self.does_pwmX_exists() and all(self.is_control_writable(c) for c in required_controls):
                return

            if perf_counter() - start > timeout:
                controls = ", ".join(required_controls)
                raise PermissionError(f"Unable to create/write to {self.pwm_dir} ({controls})")
            sleep(0.01)

    @staticmethod
    def _retry_on_permission_error(action, timeout=0.5) -> None:
        start = perf_counter()
        attempt = 0
        while True:
            try:
                action()
                return
            except PermissionError:
                if perf_counter() - start >= timeout:
                    raise

                attempt += 1
                sleep(min(0.05 * attempt, 0.2))

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
        self.change_duty_cycle(0)

        per = 1 / float(self._hz)
        per *= 1000  # now in milliseconds
        per *= 1_000_000  # now in nanoseconds
        self.echo(int(per), os.path.join(self.pwm_dir, "period"))

        self.change_duty_cycle(original_duty_cycle)

    def __init_frequency(self, hz: float) -> None:
        assert self._duty_cycle == 0

        per = 1 / float(hz)
        per *= 1000  # now in milliseconds
        per *= 1_000_000  # now in nanoseconds
        self.echo(int(per), os.path.join(self.pwm_dir, "period"))

    def __init_dc(self, dc: float) -> None:
        assert dc == 0
        self.echo(dc, os.path.join(self.pwm_dir, "duty_cycle"))


if __name__ == "__main__":
    pwm = HardwarePWM(pwm_channel=0, hz=60, chip=0)
    pwm.start(100) # full duty cycle
    sleep(2)
    pwm.change_duty_cycle(50)
    sleep(2)
    pwm.change_frequency(25_000)
    sleep(2)
    pwm.stop()
