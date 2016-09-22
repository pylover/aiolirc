import re
import os
from setuptools import setup, find_packages


dependencies = [
    'python-lirc'
]


# reading pymlconf version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), 'aiolirc', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


setup(
    name='aiolirc',
    version=package_version,
    install_requires=dependencies,
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.5'
    ]
)
