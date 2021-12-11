from celery import Celery
from fastapi import FastAPI
from msdss_base_api import API
from multiprocessing import Process

from .env import *
from .managers import *
from .routers import *

class ModelsAPI(API):
    """
    Models API class for managing models.
    
    * Extends the :class:`msdss_base_api:msdss_base_api.core.API` class

    Parameters
    ----------
    users_api : :class:`msdss_users_api:msdss_users_api.core.UsersAPI` or None
        Users API object to enable user authentication for models routes.
        If ``None``, user authentication will not be used for models routes.
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        A database object for using models with data from the database.
    models : list(:class:`msdss_models_api.models.Model`)
        List of available ``Model`` objects to use for creating and managing model instances.
        Ensure that the class names are unique, otherwise the last object in the list takes priority.
    broker_url : str or None
        Link to connect to a `RabbitMQ <https://www.rabbitmq.com/>`_ broker. Env vars will take priority - see parameter ``env``.
    backend_url : str or None
        Link to connect to a `RabbitMQ <https://www.rabbitmq.com/>`_ backend. Env vars will take priority - see parameter ``env``.
    folder : str
        The folder path to store models in. The folder will be created if it does not exist. Env vars will take priority - see parameter ``env``.
    models_router_settings : dict
        Keyword arguments passed to :func:`msdss_models_api.routers.get_models_router` except ``bg_manager``.
    load_env : bool
        Whether to load variables from a file with environmental variables at ``env_file`` or not.
    env : :class:`msdss_users_api.env.ModelsDotEnv`
        An object to set environment variables related to users configuration.
        These environment variables will overwrite the parameters above if they exist.

        By default, the related parameters above are assigned to each of the environment variables seen below if ``load_env`` is ``True``:

        .. jupyter-execute::
            :hide-code:

            from msdss_models_api.defaults import DEFAULT_DOTENV_KWARGS
            defaults = {k:v for k, v in DEFAULT_DOTENV_KWARGS.items() if k not in ['defaults', 'env_file', 'key_path']}
            print('<parameter> = <environment variable>\\n')
            for k, v in defaults.items():
                print(k + ' = ' + v)

    api : :class:`fastapi:fastapi.FastAPI`
        API object for creating routes.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_base_api:msdss_base_api.core.API`.

    Attributes
    ----------
    users_api_database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object for users API.
    misc : dict
        Dictionary of miscellaneous values:

        * ``fastapi_users_objects`` (dict): dict of values returned from :func:`msdss_users_api.tools.create_fastapi_users_objects`

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    Create models api without users:

    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_models_api.models import Model
        from msdss_models_api import ModelsAPI

        # Create database object
        database = Database(
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss'
        )

        # Create models api without users
        app = ModelsAPI(
            models=[Model],
            database=database,
            broker_url='redis://localhost:6379/0',
            backend_url='redis://localhost:6379/0'
        )

        # Run the app with app.start()
        # Try API at http://localhost:8000/docs
        # app.start()

    Create Models API with users:

    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_models_api.models import Model
        from msdss_models_api import ModelsAPI
        from msdss_users_api import UsersAPI

        # Create database object
        database = Database(
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss'
        )

        # Create a users api
        # CHANGE SECRETS TO STRONG PHRASES
        users_api = UsersAPI(
            'cookie-secret',
            'jwt-secret',
            'reset-secret',
            'verification-secret',
            database=database
        )

        # Create a models api with users
        app = ModelsAPI(
            users_api,
            models=[Model],
            database=database,
            broker_url='redis://localhost:6379/0',
            backend_url='redis://localhost:6379/0'
        )

        # Run the app with app.start()
        # Try API at http://localhost:8000/docs
        # app.start()

    Create Models API with users and data management:

    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_models_api.models import Model
        from msdss_models_api import ModelsAPI
        from msdss_users_api import UsersAPI
        from msdss_data_api import DataAPI

        # Create database object
        database = Database(
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss'
        )

        # Create a users api
        # CHANGE SECRETS TO STRONG PHRASES
        users_api = UsersAPI(
            'cookie-secret',
            'jwt-secret',
            'reset-secret',
            'verification-secret',
            database=database
        )

        # Create a data api with users
        data_users_api = UsersAPI(
            'cookie-secret',
            'jwt-secret',
            'reset-secret',
            'verification-secret',
            database=database
        )
        data_api = DataAPI(data_users_api, database=database)

        # Create a models api with users and data management
        app = ModelsAPI(
            users_api,
            models=[Model],
            database=database,
            broker_url='redis://localhost:6379/0',
            backend_url='redis://localhost:6379/0'
        )
        app.add_app(data_api)

        # Run the app with app.start()
        # Try API at http://localhost:8000/docs
        # app.start()
    """
    def __init__(
        self,
        users_api=None,
        database=Database(),
        models=[],
        broker_url=DEFAULT_BROKER_URL,
        backend_url=DEFAULT_BACKEND_URL,
        folder=DEFAULT_MODELS_FOLDER,
        models_router_settings={},
        load_env=True,
        env=ModelsDotEnv(),
        api=FastAPI(
            title='MSDSS Models API',
            version='0.0.0'
        ),
        *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)

        # (UsersAPI_env) Set env vars
        if env.exists() and load_env:
            env.load()
            broker_url = env.get('broker_url', broker_url)
            backend_url = env.get('backend_url', backend_url)
            folder = env.get('folder', folder)

        # (ModelsAPI_bg) Create background manager for models
        models_manager = ModelsDBManager(models=models, database=database, folder=folder)
        worker = Celery(broker=broker_url, backend=backend_url)
        bg_manager = ModelsDBBackgroundManager(worker=worker, models_manager=models_manager)
        models_router_settings['bg_manager'] = bg_manager
        
        # (ModelsAPI_users) Add users app if specified
        if users_api:
            models_router_settings['users_api'] = users_api
            self.add_apps(users_api)

        # (ModelsAPI_router_models) Add models router
        models_router = get_models_router(**models_router_settings)
        self.add_router(models_router)

        # (ModelsAPI_router_attr) Set attributes
        self.misc = {}
        self.misc['bg_manager'] = bg_manager

    def start_worker(self):
        """
        Start the background worker to process background tasks.

        This should be run in a separate terminal instance from the app.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            from msdss_models_api.models import Model
            from msdss_models_api import ModelsAPI

            # Create models api without users
            app = ModelsAPI(
                models=[Model],
                broker_url='redis://localhost:6379/0',
                backend_url='redis://localhost:6379/0'
            )

            # Run the background worker in a separate terminal
            app.start_worker()
        """
        self.misc['bg_manager'].start()
