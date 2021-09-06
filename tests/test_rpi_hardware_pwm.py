from rpi_hardware_pwm import HardwarePWM, HardwarePWMException
import pytest

@pytest.fixture(scope="function", autouse=True)
def pwm0_path(tmp_path, mocker):
    # prepare something ahead of all tests
    pwm_path = tmp_path / "pwmchip0"
    pwm_path.mkdir(parents=True)

    pwm0_path = (pwm_path / "pwm0")
    pwm0_path.mkdir()
    (pwm0_path / "enable").touch()
    (pwm0_path / "period").touch()
    (pwm0_path / "duty_cycle").touch()

    mocker.patch(
        'rpi_hardware_pwm.HardwarePWM.is_overlay_loaded',
        new_callable=mocker.PropertyMock,
        return_value=lambda: True
    )

    mocker.patch(
        'rpi_hardware_pwm.HardwarePWM.is_export_writable',
        new_callable=mocker.PropertyMock,
        return_value=lambda: True
    )

    mocker.patch(
        'rpi_hardware_pwm.HardwarePWM.chippath',
        new_callable=mocker.PropertyMock,
        return_value=str(pwm_path)
    )

    return pwm0_path



def test_initialization(pwm0_path):
    hz = 5
    hw = HardwarePWM(0, hz)
    with open(pwm0_path / "period", 'r') as f:
        assert int(f.read().strip()) == 1 / hz * 1_000_000_000

    with open(pwm0_path / "duty_cycle", 'r') as f:
        assert int(f.read().strip()) == 0

    dc = 25
    hw.start(dc)

    with open(pwm0_path / "duty_cycle", 'r') as f:
        assert int(f.read().strip()) == (dc / 100) * 1 / hz * 1_000_000_000


def test_changing_dc(pwm0_path):
    hz = 5
    hw = HardwarePWM(0, hz)
    dc = 25
    hw.start(dc)

    with open(pwm0_path / "duty_cycle", 'r') as f:
        old_dc_written = int(f.read().strip())

    new_dc = 50
    hw.change_duty_cycle(new_dc)

    with open(pwm0_path / "duty_cycle", 'r') as f:
        new_dc_written = int(f.read().strip())

    assert new_dc_written == 2 * old_dc_written


def test_changing_hz(pwm0_path):
    hz = 25
    hw = HardwarePWM(0, hz)

    with open(pwm0_path / "period", 'r') as f:
        old_period_written = int(f.read().strip())

    new_hz = 50
    hw.change_frequency(new_hz)

    with open(pwm0_path / "period", 'r') as f:
        new_period_written = int(f.read().strip())

    assert new_period_written == old_period_written / 2


def test_stop(pwm0_path):
    hz = 25
    hw = HardwarePWM(0, hz)
    hw.start(10)

    with open(pwm0_path / "enable", 'r') as f:
        assert int(f.read().strip()) == 1

    hw.stop()

    with open(pwm0_path / "enable", 'r') as f:
        assert int(f.read().strip()) == 0


def test_invalid_freq(pwm0_path):
    with pytest.raises(HardwarePWMException):
            hw = HardwarePWM(0, 0.001)
