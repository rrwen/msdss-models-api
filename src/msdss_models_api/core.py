from celery import Celery
from fastapi import FastAPI
from msdss_base_api import API
from msdss_base_database import Database
from msdss_data_api.managers import DataManager

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
    database : :class:`msdss_base_database:msdss_base_database.core.Database` or None
        A database object for using models with data from the database. If ``None``, a default database object will be created.
    models : list(:class:`msdss_models_api.models.Model`) or dict(:class:`msdss_models_api.models.Model`)
        List or dict of available ``Model`` objects to use for creating and managing model instances.
        If ``list``, ensure that the class names are unique, otherwise the last object in the list takes priority.
    worker : :class:`celery:celery.Celery` or None
        Celery worker for background processes. If ``None``, a default worker will be created using parameters ``broker_url`` and ``backend_url``.
    broker_url : str or None
        Link to connect to a `Redis <https://redis.io/>`_ broker. Env vars will take priority - see parameter ``env``.
        If parameter ``worker`` is set, this will not be applied.
    backend_url : str or None
        Link to connect to a `Redis <https://redis.io/>`_ backend. Env vars will take priority - see parameter ``env``.
        If parameter ``worker`` is set, this will not be applied.
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
    models_api_database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object for users API.
    models_api_worker : :class:`celery:celery.Celery`
        Same as parameter ``worker``.

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

        # Add users routes
        app.add_app(users_api)

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
        data_api = DataAPI(users_api, database=database)

        # Create a models api with users and data management
        app = ModelsAPI(
            users_api,
            models=[Model],
            database=database,
            broker_url='redis://localhost:6379/0',
            backend_url='redis://localhost:6379/0'
        )

        # Add users and data routes
        app.add_apps(users_api, data_api)

        # Run the app with app.start()
        # Try API at http://localhost:8000/docs
        # app.start()
    """
    def __init__(
        self,
        users_api=None,
        database=None,
        models=[],
        worker=None,
        broker_url=DEFAULT_BROKER_URL,
        backend_url=DEFAULT_BACKEND_URL,
        folder=DEFAULT_MODELS_FOLDER,
        models_router_settings={},
        load_env=True,
        env=ModelsDotEnv(),
        api=FastAPI(
            title='MSDSS Models API',
            version='0.0.7'
        ),
        *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)

        # (ModelsAPI_env) Set env vars
        if env.exists() and load_env:
            env.load()
            broker_url = env.get('broker_url', broker_url)
            backend_url = env.get('backend_url', backend_url)
            folder = env.get('folder', folder)

        # (ModelsAPI_folder) Create folder if not exists
        if not os.path.isdir(folder):
            os.makedirs(folder)

        # (ModelsAPI_bg) Create background manager for models
        database = database if database else Database()
        data_manager = DataManager(database=database)
        models_manager = ModelsDBManager(models=models, data_manager=data_manager, folder=folder)
        worker = worker if worker else Celery(broker=broker_url, backend=backend_url)
        metadata_manager = ModelsMetadataManager(data_manager, models_manager)
        bg_manager = ModelsDBBackgroundManager(worker=worker, models_manager=models_manager, metadata_manager=metadata_manager)
        models_router_settings['bg_manager'] = bg_manager
        
        # (ModelsAPI_users) Add users app if specified
        if users_api:
            models_router_settings['users_api'] = users_api

        # (ModelsAPI_router_models) Add models router
        models_router = get_models_router(**models_router_settings)
        self.add_router(models_router)

        # (ModelsAPI_router_attr) Set attributes
        self.models_api_worker = worker
        self.misc = {}
        self.misc['bg_manager'] = bg_manager

        # (ModelsAPI_startup) Setup app startup
        @self.event('startup')
        async def startup():
            self.logger.info('Waiting for base models metadata to be loaded into database.')
            metadata_manager.load_base_models()
            self.logger.info('Base models metadata loading complete.')

    def get_worker(self):
        """
        Get the background worker to process background tasks.

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
            worker = app.get_worker()
        """
        out = self.models_api_worker
        return out
