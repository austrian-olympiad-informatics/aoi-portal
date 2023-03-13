from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt")) as requirements_txt:
    REQUIRES = requirements_txt.read().splitlines()

setup(
    name='aoiportal',
    packages=['aoiportal'],
    include_package_data=True,
    install_requires=REQUIRES,
    entry_points={
        'console_scripts': [
            'aoiportal=aoiportal.cli:cli'
        ],
    },
)
