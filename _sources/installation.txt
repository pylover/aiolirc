Installation
============

Prerequisites
-------------

Debian
^^^^^^

.. code-block:: console

  $ apt-get install build-essential python3.5-dev


.. code-block:: console

  $ pip install cython


From PyPI
---------

pip:

.. code-block:: console

  $ pip install aiolirc


From Source
-----------

.. code-block:: console

  $ cd path/to/source/directory
  $ pip install .

or:

.. code-block:: console

  $ python setup.py install

You may use the source folder in-place as a python library in `sys.path`, so you have to
build the C extensions before using the library:

.. code-block:: console

  $ cd path/to/source/directory
  $ python setup.py build_ext --inplace


Development, editable:

.. code-block:: console

  $ cd path/to/source/directory
  $ python setup.py build_ext --inplace
  $ nosetests
  $ pip install -e .


From Github
-----------
Latest development code:

.. code-block:: console

  $ pip install git+https://github.com/pylover/aiolirc.git