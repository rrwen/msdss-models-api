Quick Start
===========

Without Users
-------------

After installing the package, setup the models folder and ``redis`` broker/backend urls for background tasks using ``msdss-dotenv`` in a command line terminal:

.. code::

    msdss-dotenv init --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_MODELS_FOLDER ./models --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_MODELS_BROKER_URL redis://localhost:6379/0 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_MODELS_BACKEND_URL redis://localhost:6379/0 --key_path <KEY_PATH>

.. note::

    Set the ``<KEY_PATH>`` to a secure location (preferable outside of the project directory) as you will need this to unlock your created ``.env`` file

Next, set up database environment variables:

.. code::

    msdss-dotenv set MSDSS_DATABASE_DRIVER postgresql --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_USER msdss --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_PASSWORD msdss123 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_HOST localhost --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_PORT 5432 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_NAME msdss --key_path <KEY_PATH>

After setting up environment variables, create a python file called ``app.py`` and use the package via :class:`msdss_models_api.core.ModelsAPI`:

.. code-block:: python
    :caption: app.py

    from msdss_models_api import ModelsAPI

    # Create app using env vars
    app = ModelsAPI()

    # Get the redis background worker to run using celery
    worker = app.get_worker()

    # Run the app with app.start()
    # API is hosted at http://localhost:8000
    # Try API at http://localhost:8000/docs
    # app.start()

In one terminal, run the background worker for ``app.py`` using ``celery``:

.. code::

    celery -A app.worker worker

In another terminal, run the Models API using ``uvicorn``:

.. code::

    uvicorn app.api

With Users
----------

After installing the package, setup the models folder and ``redis`` broker/backend urls for background tasks using ``msdss-dotenv`` in a command line terminal:

.. code::

    msdss-dotenv init --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_MODELS_FOLDER ./models --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_MODELS_BROKER_URL redis://localhost:6379/0 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_MODELS_BACKEND_URL redis://localhost:6379/0 --key_path <KEY_PATH>

.. note::

    Set the ``<KEY_PATH>`` to a secure location (preferable outside of the project directory) as you will need this to unlock your created ``.env`` file

Then, set up database environment variables:

.. code::

    msdss-dotenv set MSDSS_DATABASE_DRIVER postgresql --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_USER msdss --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_PASSWORD msdss123 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_HOST localhost --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_PORT 5432 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_NAME msdss --key_path <KEY_PATH>

Next, set up user environment variables:

.. code::
   
    msdss-dotenv set MSDSS_USERS_COOKIE_SECRET cookie-secret --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_USERS_JWT_SECRET jwt-secret --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET reset-phrase --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_USERS_VERIFICATION_TOKEN_SECRET verification-phrase --key_path <KEY_PATH>

.. note::

    The variables above (e.g. ``cookie-secret``, ``jwt-secret``, etc) should be a strong passphrase - you can generate strong phrases with:
    
    .. code::

        openssl rand -hex 32

Finally, create a ``superuser`` with the ``msdss-users`` command line interface:

.. code::

    msdss-users register --superuser

After setting up environment variables, create a python file called ``app.py`` and use the package via :class:`msdss_models_api.core.ModelsAPI`:

.. code-block:: python
    :caption: app.py

    from msdss_models_api import ModelsAPI
    from msdss_users_api import UsersAPI

    # Create users app
    users_app = UsersAPI()

    # Create app using env vars
    app = ModelsAPI()

    # Add users app to models app
    app.add_app(users_app)

    # Get the redis background worker to run using celery
    worker = app.get_worker()

    # Run the app with app.start()
    # API is hosted at http://localhost:8000
    # Try API at http://localhost:8000/docs
    # app.start()

In one terminal, run the background worker for ``app.py`` using ``celery``:

.. code::

    celery -A app.worker worker

In another terminal, run the Models API using ``uvicorn``:

.. code::

    uvicorn app.api
