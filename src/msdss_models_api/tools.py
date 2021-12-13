from celery import Celery
from msdss_base_database import Database
from msdss_data_api import DataManager

from .defaults import *
from .handlers import *
from .managers import *

def create_models_bg_manager_func(
    models=[],
    folder=DEFAULT_MODELS_FOLDER,
    worker=Celery(broker=DEFAULT_BROKER_URL, backend=DEFAULT_BACKEND_URL),
    models_manager=None,
    bg_manager=None,
    *args,
    **kwargs
):
    """
    Create a function yielding a :class:`msdss_models_api.managers.ModelsBackgroundManager`.
    
    Parameters
    ----------
    models : list(:class:`msdss_models_api.models.Model`)
        List of available ``Model`` objects to use for creating and managing model instances.
        Ensure that the class names are unique, otherwise the last object takes priority.
    folder : str
        The folder path to store models in. The folder will be created if it does not exist.
    worker : :class:`celery:celery.Celery`
        A ``celery`` app object to manage background tasks.
    models_manager : :class:`msdss_models_api.managers.ModelsManager` or None
        A models manager object to manage models. If ``None``, a default manager will be created using parameters ``folder`` and ``models``.
    bg_manager : :class:`msdss_models_api.managers.ModelsBackgroundManager` or None
        A models background manager object to manage model tasks. If ``None``, a default manager will be created using all other parameters.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_models_api.managers.ModelsBackgroundManager`.

    Returns
    -------
    func
        A function yielding a preconfigured :class:`msdss_models_api.managers.ModelsBackgroundManager`.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        import tempfile
        from msdss_models_api.models import *
        from msdss_models_api.tools import *

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup models
            models = [Model]

            # Create a function yielding the models manager to use as a dependency
            get_bg_manager = create_models_bg_manager_func(models=models, folder=folder_path)
    """
    models_manager = models_manager if models_manager else ModelsManager(models=models, folder=folder)
    bg_manager = bg_manager if bg_manager else ModelsBackgroundManager(worker=worker, models_manager=models_manager, *args, **kwargs)
    def out():
        yield bg_manager
    return out

def create_models_db_bg_manager_func(
    models=[],
    database=Database(),
    folder=DEFAULT_MODELS_FOLDER,
    worker=Celery(broker=DEFAULT_BROKER_URL, backend=DEFAULT_BACKEND_URL),
    models_manager=None,
    bg_manager=None,
    *args,
    **kwargs
):
    """
    Create a function yielding a :class:`msdss_models_api.managers.ModelsDBBackgroundManager`.
    
    Parameters
    ----------
    models : list(:class:`msdss_models_api.models.Model`)
        List of available ``Model`` objects to use for creating and managing model instances.
        Ensure that the class names are unique, otherwise the last object takes priority.
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        A database object for using models with data from the database.
    folder : str
        The folder path to store models in. The folder will be created if it does not exist.
    worker : :class:`celery:celery.Celery`
        A ``celery`` app object to manage background tasks.
    models_manager : :class:`msdss_models_api.managers.ModelsManager` or None
        A models manager object to manage models. If ``None``, a default manager will be created using parameters ``folder`` and ``models``.
    bg_manager : :class:`msdss_models_api.managers.ModelsBackgroundManager` or None
        A models background manager object to manage model tasks. If ``None``, a default manager will be created using all other parameters.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_models_api.managers.ModelsBackgroundManager`.

    Returns
    -------
    func
        A function yielding a preconfigured :class:`msdss_models_api.managers.ModelsDBBackgroundManager`.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        import tempfile
        from msdss_base_database import Database
        from msdss_models_api.models import *
        from msdss_models_api.tools import *

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup models and db
            models = [Model]
            database = Database()

            # Create a function yielding the models manager to use as a dependency
            get_bg_manager = create_models_db_bg_manager_func(models=models, database=database, folder=folder_path)
    """
    data_manager = DataManager(database=database)
    models_manager = models_manager if models_manager else ModelsDBManager(models=models, data_manager=data_manager, folder=folder)
    bg_manager = bg_manager if bg_manager else ModelsDBBackgroundManager(worker=worker, models_manager=models_manager, *args, **kwargs)
    def out():
        yield bg_manager
    return out