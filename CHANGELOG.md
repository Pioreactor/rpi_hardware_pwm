  ## [0.3.1] - 2026-02-09

  ### Fixed
  - Reduced intermittent first-use PWM initialization failures on Raspberry Pi (`PermissionError` when writing `/sys/class/pwm/.../
  period` or `.../duty_cycle`).
  - Hardened sysfs startup flow to wait until PWM control files are present and writable after export.
  - Added short retry/backoff for constructor-time initialization writes to tolerate transient udev/permission timing races.

  ### Notes
  - No API changes.
  - Backward compatible; behavior is only more robust during early PWM setup (especially right after boot / first PWM use).

