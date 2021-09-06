from setuptools import setup, find_packages
import os


# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

setup(
    name="rpi_hardware_pwm",
    packages=find_packages('.'),
    version='0.1.3',
    license='OSI Approved :: GNU General Public License v3 (GPLv3)',
    description='Control Hardware PWM on the Raspberry Pi',
    long_description = long_description,
    long_description_content_type='text/markdown',
    author='Cam Davidson-Pilon',
    author_email='cam@pioreactor.com',
    url='https://github.com/Pioreactor/rpi_hardware_pwm',
    keywords=["raspberry pi", "pwm", "hardware"],
    package_data={"rpi_hardware_pwm": ["py.typed"]},
    install_requires=[],
    python_requires='>=3.5',
    # https://pypi.org/classifiers/
    classifiers=["Development Status :: 4 - Beta", "Topic :: System :: Hardware", ]
)