import re
import os
from setuptools import setup, find_packages, Extension

from Cython.Build import cythonize


# reading pymlconf version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), 'aiolirc', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


dependencies = [
    'cython',
]

libraries = [
    'lirc_client',
]

extensions = [
    Extension('aiolirc.client', ['aiolirc/client.pyx'], libraries=libraries),
    Extension('aiolirc.config', ['aiolirc/config.pyx'], libraries=libraries),
]


setup(
    name='aiolirc',
    version=package_version,
    install_requires=dependencies,
    packages=find_packages(),
    ext_modules=cythonize(extensions),
    classifiers=[
        'Programming Language :: Python :: 3.5'
    ]
)
