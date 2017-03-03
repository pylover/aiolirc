import re
import os
from setuptools import setup, find_packages

# reading pymlconf version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), 'aiolirc', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


dependencies = [
    'lirc'
]


setup(
    name='aiolirc',
    version=package_version,
    author="Vahid Mardani",
    author_email="vahid.mardani@gmail.com",
    url="http://aiolirc.dobisel.com",
    description="lirc async io python api",
    zip_safe=False,
    keywords="lirc asyncio api",
    long_description=open('README.rst', encoding='utf-8').read(),
    license="GPLv3",
    packages=find_packages(),
    install_requires=dependencies,
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Cython',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware',
    ]
)
