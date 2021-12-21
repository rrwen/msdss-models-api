Install
=======

Without Users
-------------

1. Install `Anaconda 3 <https://www.anaconda.com/>`_ for Python
2. Install `PostgreSQL <https://www.postgresql.org/>`_ or your preferred database
3. Install `Redis <https://redis.io/>`_
4. Install ``msdss-models-api`` via pip or through a conda environment

.. code::

   conda create -n msdss-models-api python=3.8
   conda activate msdss-models-api
   pip install msdss-models-api[postgresql]

.. note::

   Optionally, you can also install other databases supported by ``sqlalchemy``:

   .. code::

      pip install msdss-models-api[mysql]
      pip install msdss-models-api[sqlite]

With Users
----------

This package can be installed with user authentication support:

1. Install `Anaconda 3 <https://www.anaconda.com/>`_ for Python
2. Install `PostgreSQL <https://www.postgresql.org/>`_ or your preferred database
3. Install `Redis <https://redis.io/>`_
4. Install ``msdss-models-api`` via pip or through a conda environment

.. code::

   conda create -n msdss-models-api python=3.8
   conda activate msdss-models-api
   pip install msdss-models-api[users-postgresql]

.. note::

   Optionally, you can also install other databases supported by ``sqlalchemy``:

   .. code::

      pip install msdss-models-api[users-mysql]
      pip install msdss-models-api[users-sqlite]