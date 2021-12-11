from datetime import datetime
import os
import pickle
import shutil

from msdss_base_database import Database
from msdss_data_api.managers import DataManager
from shlex import split

from .defaults import *
from .handlers import *

class ModelsManager:
    """
    Class to manage :class:`msdss_models_api.models.Model` objects.
    
    Parameters
    ----------
    models : list(:class:`msdss_models_api.models.Model`)
        List of available ``Model`` objects to use for creating and managing model instances.
        Ensure that the class names are unique, otherwise the last object takes priority.
    folder : str
        The folder path to store models in. The folder will be created if it does not exist.
    handler : :class:`msdss_models_api.handlers.ModelsHandler`
        Handler object to manage model operations.
    suffix : str
        Suffix for pickled model object files. These files contain the model objects without inputs or loading.

    Attributes
    ----------
    models : dict(:class:`msdss_models_api.models.Model`)
        Dictionary of available models from parameter ``models``, where:

        * Each key is the class name
        * Each value is the class itself

    instances : dict(:class:`msdss_models_api.models.Model`)
        Dictionary of loaded model instances created from method ``create``.
    folder : str
        Same as parameter ``folder``.
    handler : :class:`msdss_models_api.handlers.ModelsHandler`
        Same as parameter ``handler``.
    suffix : str
        Same as parameter ``suffix``.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        import tempfile
        from msdss_models_api.models import Model
        from msdss_models_api.managers import ModelsManager

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models
            models = [Model]
            
            # Create manager
            models_manager = ModelsManager(models, folder=folder_path)

            # Create model instance
            models_manager.create('temp_model', 'Model')

            # Initialize a model instance with inputs
            train_data = [
                {'col_a': 1, 'col_b': 'a'},
                {'col_a': 2, 'col_b': 'b'}
            ]
            models_manager.input('temp_model', train_data)
            
            # Update model instance with new data
            new_data = [
                {'col_a': 2, 'col_b': 'c'},
                {'col_a': 3, 'col_b': 'd'}
            ]
            models_manager.update('temp_model', new_data)

            # Produce output from a model instance
            test_data = [
                {'col_a': 2, 'col_b': 'c'},
                {'col_a': 3, 'col_b': 'd'}
            ]
            results = models_manager.output('temp_model', test_data)

            # Delete model instance
            models_manager.delete('temp_model')
    """
    def __init__(
        self,
        models=[],
        folder=DEFAULT_MODELS_FOLDER,
        handler=None,
        suffix='_base.pickle'
    ):

        # (ModelsManager_folder) Create folder if not exists
        if not os.path.isdir(folder):
            os.makedirs(folder)

        # (ModelsManager_attr) Set attributes
        self.folder = folder
        self.models = {(m.__name__):m for m in models}
        self.instances = {}
        self.handler = handler if handler else ModelsHandler()
        self.suffix = suffix

        # (ModelsManager_load) Load base model instances
        self._load_base()

    def _get_file(self, name):
        """
        Get the path of the base file for the model instance.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        
        Returns
        -------
        str
            File path for the base file of the model instance.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Delete model instance
                path = models_manager._get_file('temp_model')
        """
        folder = self._get_folder(name)
        out = os.path.join(folder, name + self.suffix)
        return out

    def _get_folder(self, name):
        """
        Get the path of the subfolder for the model instance.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        
        Returns
        -------
        str
            File path for the subfolder of the model instance.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Delete model instance
                folder_path = models_manager._get_folder('temp_model')
        """
        out = os.path.join(self.folder, name)
        return out

    def _get_save_file(self, name):
        """
        Get the path of the save file for the model instance without the extension.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        
        Returns
        -------
        str
            File path for the save file of the model instance. Does not include extension.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Delete model instance
                save_path = models_manager._get_save_file('temp_model')
        """
        folder = self._get_folder(name)
        out = os.path.join(folder, name)
        return out

    def _load_base(self, force=False):
        """
        Load all base models.

        Sets attribute ``.instances`` to be initialized :class:`msdss_models_api.models.Model` instances based on the subfolders in attribute ``folders``

        Parameters
        ----------
        force : bool
            Whether to force loading whether instance is in ``.instances`` attribute or not.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Load all base models
                models_manager._load_base()
        """
        names = [name for name in os.listdir(self.folder) if os.path.isdir(os.path.join(self.folder, name))]
        for name in names:
            if name not in self.instances or force:
                path = self._get_file(name)
                with open(path, 'rb') as file:
                    self.instances[name] = pickle.load(file)

    def create(self, name, model, settings={}):
        """
        Creates a model instance.

        * Stores the instance in attribute ``instances``
        * Creates a subfolder and base model file for the instance

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        model : str
            Name of the model to use for the instance. This is the same as the class name from attribute
        settings : dict
            Settings to be passed to :class:`msdss_models_api.models.Model` to instantiate the instance.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')
        """
        self.handler.handle_create(name, model, self.instances, self.models)
        
        # (ModelsManager_create_subfolder) Create subfolder if not exists for model
        folder = self._get_folder(name)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        
        # (ModelsManager_create_obj) Create base model object
        save_file = self._get_save_file(name)
        base_model = self.models[model](file_path=save_file, **settings)

        # (ModelsManager_create_save) Save base model object
        with open(self._get_file(name), 'wb') as base_file:
            pickle.dump(base_model, base_file)
            self.instances[name] = base_model

    def delete(self, name, settings={}):
        """
        Creates a model instance.

        * Removes the instance in attribute ``instances``
        * Removes the subfolder and base model file for the instance

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        settings : dict
            Settings to be passed to :meth:`msdss_models_api.models.Model.delete`.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                models_manager.input('temp_model', train_data)

                # Delete model instance
                models_manager.delete('temp_model')
        """

        # (ModelsManager_delete_instance) Run instance deletion
        instance = self.get(name)
        instance.delete(**settings)

        # (ModelsManager_delete_folder) Delete folder
        folder = self._get_folder(name)
        shutil.rmtree(folder)
        del self.instances[name]

    def get(self, name):
        """
        Get a model instance by name.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Delete model instance
                models_manager.get('temp_model')
        """
        self.handler.handle_read(name, self.instances)
        out = self.instances[name]
        return out

    def input(self, name, data, settings={}):
        """
        Train an initial model instance and save it by adding input data.

        * Modifies ``.instance[name]`` by calling the ``input`` and ``save`` methods
        * Modifies ``.states[name]`` with action and results for inputting data into the model instance

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        data : dict or list or :class:`pandas:pandas.DataFrame`
            Data to use for initializing the model instance. Should accept a ``list`` or ``dict`` to be input in a :class:`pandas:pandas.DataFrame` or the dataframe itself.
        settings : dict
            Keyword arguments passed to the :meth:`msdss_models_api.models.Model.input`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                models_manager.input('temp_model', train_data)
        """
        instance = self.get(name)
        instance.input(data, **settings)
        instance.save()

    def load(self, name, settings={}):
        """
        Load a model instance if the save exists and has not changed from last loaded instance.

        * Modifies ``.instance[name]`` by calling the ``load`` method
        * Modifies ``.states[name]`` with action and results for loading the model instance

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        settings : dict
            Keyword arguments passed to the :meth:`msdss_models_api.models.Model.load`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                models_manager.input('temp_model', train_data)

                # Load model instance if possible
                models_manager.load('temp_model')
        """
        instance = self.get(name)
        self.handler.handle_load(instance)
        instance.load(**settings)

    def output(self, name, data, settings={}):
        """
        Get the output of a model instance.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        data : dict or list or :class:`pandas:pandas.DataFrame`
            Data to use for obtaining the model instance output. Should accept a ``list`` or ``dict`` to be input in a :class:`pandas:pandas.DataFrame` or the dataframe itself.
        settings : dict
            Keyword arguments passed to the :meth:`msdss_models_api.models.Model.output`.

        Returns
        -------
        :class:`pandas:pandas.DataFrame`
            Output data from the ``name`` model instance using the input data from parameter ``data``.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                models_manager.input('temp_model', train_data)

                # Produce output from a model instance
                test_data = [
                    {'col_a': 2, 'col_b': 'c'},
                    {'col_a': 3, 'col_b': 'd'}
                ]
                results = models_manager.output('temp_model', test_data)
        """
        instance = self.get(name)
        out = instance.output(data, **settings)
        return out
    
    def update(self, name, data, settings={}):
        """
        Update a model instance with new data.

        * Modifies ``.instance[name]`` by calling the ``update`` and ``save`` methods
        * Modifies ``.states[name]`` with action and results for updating the model instance

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        data : dict or list or :class:`pandas:pandas.DataFrame`
            Data to use for updating the model instance. Should accept a ``list`` or ``dict`` to be input in a :class:`pandas:pandas.DataFrame` or the dataframe itself.
        settings : dict
            Keyword arguments passed to the :meth:`msdss_models_api.models.Model.update`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                models_manager.input('temp_model', train_data)

                # Update model instance with new data
                new_data = [
                    {'col_a': 2, 'col_b': 'c'},
                    {'col_a': 3, 'col_b': 'd'}
                ]
                models_manager.update('temp_model', new_data)
        """
        instance = self.get(name)
        instance.update(data, **settings)
        instance.save()

class ModelsBackgroundManager:
    """
    Class to manage :class:`msdss_models_api.models.Model` background processes using a :class:`msdss_models_api.managers.ModelsManager`.
    
    * Note: it is expected that the model outputs are not long running processes

    Parameters
    ----------
    worker : :class:`celery:celery.Celery`
        A ``celery`` app object to manage background tasks.
    models_manager : :class:`msdss_models_api.managers.ModelsManager` or None
        A models manager object to manage models. If ``None``, a default manager will be created.
        The handler for the models manager will be disabled as model operations will be handled with parameter ``handler`` instead.
    handler : :class:`msdss_models_api.handlers.ModelsBackgroundHandler`
        Handler object to manage background operations.

    Attributes
    ----------
    worker : :class:`celery:celery.Celery` or None
        Same as parameter ``worker``.
    models_manager : dict(:class:`msdss_models_api.manager.ModelsManager`)
        Same as parameter ``models_manager``.
    tasks : dict
        Dictionary of background tasks from the ``worker`` object with the following keys:

        * ``create`` (func): background task to create a model instance
        * ``input`` (func): background task to initialize models with input data
        * ``update`` (func): background task to update models

    states : dict
        Dictionary of processing states for each instance, consisting of the following keys:

        * ``task`` (str): the action that the process is performing - one of: ``CREATE``, ``INPUT``, ``UPDATE``
        * ``result`` (:class:`celery:celery.result.AsyncResult`): celery async object for getting states, ids, etc (see `celery.result <https://docs.celeryproject.org/en/stable/reference/celery.result.html#celery.result.AsyncResult>`_)
        * ``started_at`` (:class:`datetime.datetime`): datetime object for when the task was started

    handler : :class:`msdss_models_api.handlers.ModelsBackgroundHandler`
        Same as parameter ``handler``.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. code::

        import tempfile
        from celery import Celery
        from msdss_models_api.models import Model
        from msdss_models_api.managers import *
        from pprint import pprint

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models
            models = [Model]
            
            # Create manager
            models_manager = ModelsManager(models, folder=folder_path)

            # Create model instance
            models_manager.create('temp_model', 'Model')

            # Create background manager
            worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
            bg_manager = ModelsBackgroundManager(worker, models_manager)

            # Initialize a model instance with inputs as a background process
            train_data = [
                {'col_a': 1, 'col_b': 'a'},
                {'col_a': 2, 'col_b': 'b'}
            ]
            bg_manager.input('temp_model', train_data)

            # Check status
            status = bg_manager.get_status('temp_model')
            pprint(status)
            
            # Update model instance with new data as background process
            new_data = [
                {'col_a': 2, 'col_b': 'c'},
                {'col_a': 3, 'col_b': 'd'}
            ]
            bg_manager.update('temp_model', new_data)

            # Produce output from a model instance
            test_data = [
                {'col_a': 2, 'col_b': 'c'},
                {'col_a': 3, 'col_b': 'd'}
            ]
            results = bg_manager.output('temp_model', test_data)

            # Delete model instance
            bg_manager.delete('temp_model')
    """
    def __init__(self, worker, models_manager=None, handler=None):

        # (ModelsBackgroundManager_attr) Set attributes
        self.models_manager = models_manager if models_manager else ModelsManager()
        self.models_manager.handler.enable = False
        self.worker = worker
        self.tasks = {}
        self.states = {}
        self.handler = handler if handler else ModelsBackgroundHandler()

        # (ModelsBackgroundManager_task_create) Define create task
        @self.worker.task
        def create(name, model, settings={}):
            models_manager.create(name, model, settings)
        self.tasks['create'] = create

        # (ModelsBackgroundManager_task_input) Define input task
        @self.worker.task
        def input(name, data, settings={}):
            models_manager.input(name, data, settings)
        self.tasks['input'] = input

        # (ModelsBackgroundManager_task_update) Define update task
        @self.worker.task
        def update(name, data, settings={}):
            models_manager.load(name)
            models_manager.update(name, data, settings)
        self.tasks['update'] = update

    def _add_model_task(self, task, name, *args, **kwargs):
        """
        Add a background task for a model instance.

        * Sets attribute ``.states`` with a key referring to the model instance ``name``

        Parameters
        ----------
        task : str
            The name of the task in attribute ``.tasks``.
        name : str
            The name of the model instance to add tasks for.
        *args, **kwargs
            Additional arguments passed to the associated task function in attribute ``.tasks``.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager._add_model_task('input', 'temp_model', train_data)
        """
        result = self.tasks[task].delay(name, *args, **kwargs)
        self.states[name] = {
            'task': task.upper(),
            'result': result,
            'started_at': datetime.now()
        }

    def cancel(self, name):
        """
        Cancel background task for model instance.

        Parameters
        ----------
        name : str
            The name of the model instance to cancel tasks for.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)
                
                # Cancel any bg tasks for model instance
                bg_manager.cancel('temp_model')
        """
        self.handler.handle_cancel(name, self.states)
        result = self.state[name]['result']
        result.revoke(terminate=True)

    def create(self, name, model, *args, **kwargs):
        """
        Create a model instance.

         * Runs :meth:`msdss_models_api.managers.ModelsManager.create`

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.create`.
        model : str
            See parameter ``model`` in :meth:`msdss_models_api.managers.ModelsManager.create`.
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_models_api.managers.ModelsManager.create`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Create model instance
                bg_manager.create('temp_model', 'Model')
        """
        self.models_manager._load_base()
        self.handler.handle_create(name, model, self.models_manager.instances, self.models_manager.models)
        self._add_model_task('create', name, model, *args, **kwargs)

    def delete(self, name, *args, **kwargs):
        """
        Delete a model instance and stop any associated background tasks.

        * Runs :meth:`msdss_models_api.managers.ModelsManager.delete` and :meth:`msdss_models_api.managers.ModelsBackgroundManager.cancel`

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.delete`.
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_models_api.managers.ModelsManager.delete`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)
                
                # Delete the model instance and any associated bg tasks
                bg_manager.delete('temp_model')
        """
        self.handler.handle_processing(name, self.states)
        self.models_manager.delete(name, *args, **kwargs)
        self.cancel(name)

    def get_status(self, name):
        """
        Get the status of a model instance.

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.load`.

        Returns
        -------
        dict
            A dictionary representing the status of the model instance with ``name``, containing the following keys:

            * ``task`` (str): the processing task of the model instance
            * ``status`` (str): the processing status of the model instance 
            * ``started_at`` (:class:`datetime.datetime): when the process was started

            If the model instance is not processing, it will return a dict of the status only ``{'status': 'NOT_PROCESSING'}``.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *
            from pprint import pprint

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)
                
                # Get the status of the model instance
                status = bg_manager.get_status('temp_model')
                pprint(status)
        """
        self.handler.handle_read_state(name, self.states)
        if name in self.states:
            state = self.states[name]
            out = {
                'task': state['task'],
                'status': state['result'].state,
                'started_at': state['started_at']
            }
        else:
            out = {
                'status': 'NOT_PROCESSING'
            }
        return out

    def input(self, name, *args, **kwargs):
        """
        Initialize a model instance with data as a background task.

        Runs :meth:`msdss_models_api.managers.ModelsManager.input`.

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.input`.
        *args, **kwargs
            Additional arguments passed to the :meth:`msdss_models_api.managers.ModelsManager.input`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)
        """
        self.models_manager._load_base()
        self.handler.handle_read(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)
        self._add_model_task('input', name, *args, **kwargs)

    def output(self, name, *args, **kwargs):
        """
        Get output from a model, only if a model is not processing.

        Runs :meth:`msdss_models_api.managers.ModelsManager.output`.

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.output`.
        *args, **kwargs
            Additional arguments passed to the :meth:`msdss_models_api.managers.ModelsManager.output`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)
                
                # Get output from model instance
                test_data = [
                    {'col_a': 2, 'col_b': 'c'},
                    {'col_a': 3, 'col_b': 'd'}
                ]
                bg_manager.output('temp_model', new_data)
        """
        self.models_manager._load_base()
        self.handler.handle_read(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)
        self.models_manager.load(name)
        return self.models_manager.output(name, *args, **kwargs)

    def start(self, *args, worker_kwargs={}, **kwargs):
        """
        Start the background worker to process background tasks.

        Parameters
        ----------
        worker_kwargs : dict
            Keyword arguments for :class:`celery:celery.apps.worker`.
        *args, **kwargs
            Additional arguments passed to :meth:`celery:celery.apps.worker.start`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager._add_model_task('input', 'temp_model', train_data)

                # Start worker
                bg_manager.start()
        """
        self.worker.Worker(**worker_kwargs).start(*args, **kwargs)
    
    def update(self, name, *args, **kwargs):
        """
        Update a model instance with new data as a background task.

        Runs :meth:`msdss_models_api.managers.ModelsManager.update`.

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.update`.
        *args, **kwargs
            Additional arguments passed to the :meth:`msdss_models_api.managers.ModelsManager.update`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)
                
                # Update model instance with new data as background process
                new_data = [
                    {'col_a': 2, 'col_b': 'c'},
                    {'col_a': 3, 'col_b': 'd'}
                ]
                bg_manager.update('temp_model', new_data)
        """
        self.models_manager._load_base()
        self.handler.handle_read(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)
        self._add_model_task('update', name, *args, **kwargs)

class ModelsDBManager(ModelsManager):
    """
    Class to manage :class:`msdss_models_api.models.Model` objects with added methods for processing models with data from a database.

    * Inherits from :class:`msdss_models_api.models.ModelsManager`
    
    Parameters
    ----------
    models : list(:class:`msdss_models_api.models.Model`)
        List of available ``Model`` objects to use for creating and managing model instances.
        Ensure that the class names are unique, otherwise the last object takes priority.
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        A database object for using models with data from the database.
    data_manager : :class:`msdss_data_api.managers.DataManager` or None
        A data manager object for managing data in and out of a database.
        If ``None``, one will be configured from parameter ``database``.
    *args, **kwargs
        Additional arguments for :class:`msdss_models_api.models.ModelsManager`
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        import tempfile
        from msdss_base_database import Database
        from msdss_models_api.models import Model
        from msdss_models_api.managers import ModelsDBManager

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models and database
            database = Database()
            models = [Model]
            
            # Create manager
            models_manager = ModelsDBManager(models, database, folder=folder_path)

            # Create model instance
            models_manager.create('temp_model', 'Model')

            # Add training data to database
            train_data = [
                {'col_a': 1, 'col_b': 'a'},
                {'col_a': 2, 'col_b': 'b'}
            ]
            database.insert('models_test', train_data)

            # Initialize a model instance with inputs from database
            models_manager.input_db('temp_model', 'models_test')
            
            # Update model instance with new data
            new_data = [
                {'col_a': 3, 'col_b': 'c'},
                {'col_a': 4, 'col_b': 'd'}
            ]
            database.insert('models_test', new_data)
            models_manager.update_db('temp_model', 'models_test', where=['col_a > 2'])

            # Delete test table
            database.drop_table('models_test')
    """
    def __init__(self, models=[], database=Database(), data_manager=None, *args, **kwargs):
        super().__init__(models=models, *args, **kwargs)
        self.database = database
        self.data_manager = data_manager if data_manager else DataManager(database=database)
    
    def input_db(self, name, dataset, settings={}, *args, **kwargs):
        """
        Initialize a model instance with data from the database.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        dataset : str
            Name of the table from the database. See parameter ``dataset`` :meth:`msdss_data_api.managers.DataManager.get`.
        settings : dict
            Keyword arguments passed to the :meth:`msdss_models_api.models.Model.input`.
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_data_api.managers.DataManager.get`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_base_database import Database
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsDBManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models and database
                database = Database()
                models = [Model]
                
                # Create manager
                models_manager = ModelsDBManager(models, database, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Add training data to database
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                database.insert('models_test', train_data)

                # Initialize a model instance with inputs from database
                models_manager.input_db('temp_model', 'models_test')

                # Delete test table
                database.drop_table('models_test')
        """
        data = self.data_manager.get(dataset, *args, **kwargs)
        self.input(name, data, settings)

    def update_db(self, name, dataset, settings={}, *args, **kwargs):
        """
        Update a model instance with data from the database.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        dataset : str
            Name of the table from the database. See parameter ``dataset`` :meth:`msdss_data_api.managers.DataManager.get`.
        settings : dict
            Keyword arguments passed to the :meth:`msdss_models_api.models.Model.update`.
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_data_api.managers.DataManager.get`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_base_database import Database
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsDBManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models and database
                database = Database()
                models = [Model]
                
                # Create manager
                models_manager = ModelsDBManager(models, database, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Add training data to database
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                database.insert('models_test', train_data)

                # Update model instance with new data
                new_data = [
                    {'col_a': 3, 'col_b': 'c'},
                    {'col_a': 4, 'col_b': 'd'}
                ]
                database.insert('models_test', new_data)
                models_manager.update_db('temp_model', 'models_test', where=['col_a > 2'])

                # Delete test table
                database.drop_table('models_test')
        """
        data = self.data_manager.get(dataset, *args, **kwargs)
        self.update(name, data, settings)

class ModelsDBBackgroundManager(ModelsBackgroundManager):
    """
    Class to manage :class:`msdss_models_api.models.Model` background processes using a :class:`msdss_models_api.managers.ModelsManager`.
    
    * Inherits from :class:`msdss_models_api.managers.ModelsBackgroundManager`

    Parameters
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        A database object for using models with data from the database.
    models_manager : :class:`msdss_models_api.managers.ModelsDBManager` or None
        A models DB manager object to manage models that can receive data from a database. If ``None``, a default manager will be created.
        The handler for the models manager will be disabled as model operations will be handled with parameter ``handler`` instead.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_models_api.managers.ModelsBackgroundManager`.

    Attributes
    ----------
    models_manager : dict(:class:`msdss_models_api.manager.ModelsDBManager`)
        Same as parameter ``models_manager``.
    tasks : dict
        Dictionary of background tasks from the ``worker`` object with the following keys (in addition to the ones in attribute ``tasks`` of :class:`msdss_models_api.managers.ModelsBackgroundManager`):

        * ``input_db`` (func): background task to initialize models with input data from a database
        * ``update_db`` (func): background task to update models using data from a database
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. code::

        import tempfile
        from celery import Celery
        from msdss_base_database import Database
        from msdss_models_api.models import Model
        from msdss_models_api.managers import *
        from pprint import pprint

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models
            models = [Model]
            
            # Create manager
            database = Database()
            models_manager = ModelsDBManager(models, database, folder=folder_path)

            # Create model instance
            models_manager.create('temp_model', 'Model')

            # Create background manager
            worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
            bg_manager = ModelsDBBackgroundManager(worker, models_manager)

             # Add training data to database
            train_data = [
                {'col_a': 1, 'col_b': 'a'},
                {'col_a': 2, 'col_b': 'b'}
            ]
            database.insert('models_test', train_data)

            # Initialize a model instance with inputs from database
            bg_manager.input_db('temp_model', 'models_test')
            
            # Update model instance with new data
            new_data = [
                {'col_a': 3, 'col_b': 'c'},
                {'col_a': 4, 'col_b': 'd'}
            ]
            database.insert('models_test', new_data)
            bg_manager.update_db('temp_model', 'models_test', where=['col_a > 2'])
    """
    def __init__(self, database=Database(), models_manager=None, *args, **kwargs):

        # (ModelsDBBackgroundManager_init) Initialize inherited class
        models_manager = models_manager if models_manager else ModelsDBManager(database=database)
        super().__init__(models_manager=models_manager, *args, **kwargs)
        
        # (ModelsDBBackgroundManager_task_input) Define input db task
        @self.worker.task
        def input_db(name, dataset, settings={}, *args, **kwargs):
            models_manager.input_db(name, dataset, settings, *args, **kwargs)
        self.tasks['input_db'] = input_db

        # (ModelsDBBackgroundManager_task_update) Define update db task
        @self.worker.task
        def update_db(name, dataset, settings={}, *args, **kwargs):
            models_manager.load(name)
            models_manager.update_db(name, dataset, settings, *args, **kwargs)
        self.tasks['update_db'] = update_db

    def input_db(self, name, dataset, settings={}, where=None, *args, **kwargs):
        """
        Initialize a model instance with data from the database.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        dataset : str
            Name of the table from the database. See parameter ``dataset`` :meth:`msdss_data_api.managers.DataManager.get`.
        settings : dict
            Keyword arguments passed to the :meth:`msdss_models_api.models.Model.input`.
        where : list(str)
            See parameter ``where`` in :meth:`msdss_data_api.managers.DataManager.get`.
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_data_api.managers.DataManager.get`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_base_database import Database
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *
            from pprint import pprint

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                database = Database()
                models_manager = ModelsDBManager(models, database, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsDBBackgroundManager(worker, models_manager)

                # Add training data to database
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                database.insert('models_test', train_data)

                # Initialize a model instance with inputs from database
                bg_manager.input_db('temp_model', 'models_test')
        """
        self.models_manager._load_base()
        
        # (ModelsDBBackgroundManager_input_db_data) Handle database read and query
        where = [split(w) for w in where] if where else where
        self.models_manager.data_manager.handler.handle_read(dataset)
        self.models_manager.data_manager.handler.handle_where(where)

        # (ModelsDBBackgroundManager_input_db_handle) Handle model read and processing
        self.handler.handle_read(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)

        # (ModelsDBBackgroundManager_input_db_add) Add input db task
        self._add_model_task('input_db', name, dataset, settings=settings, where=where, *args, **kwargs)

    def update_db(self, name, dataset, settings={}, where=None, *args, **kwargs):
        """
        Update a model instance with new data from the database as a background task.

        Runs :meth:`msdss_models_api.managers.ModelsDBManager.update_db`.

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.update`.
        dataset : str
            Name of the table from the database. See parameter ``dataset`` :meth:`msdss_data_api.managers.DataManager.get`.
        settings : dict
            Keyword arguments passed to the :meth:`msdss_models_api.models.Model.update`.
        where : list(str)
            See parameter ``where`` in :meth:`msdss_data_api.managers.DataManager.get`.
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_data_api.managers.DataManager.get`.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. code::

            import tempfile
            from celery import Celery
            from msdss_base_database import Database
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *
            from pprint import pprint

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                database = Database()
                models_manager = ModelsDBManager(models, database, folder=folder_path)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Create background manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsDBBackgroundManager(worker, models_manager)

                # Add training data to database
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                database.insert('models_test', train_data)

                # Initialize a model instance with inputs from database
                bg_manager.input_db('temp_model', 'models_test')
                
                # Update model instance with new data
                new_data = [
                    {'col_a': 3, 'col_b': 'c'},
                    {'col_a': 4, 'col_b': 'd'}
                ]
                database.insert('models_test', new_data)
                bg_manager.update_db('temp_model', 'models_test', where=['col_a > 2'])
        """
        self.models_manager._load_base()

        # (ModelsDBBackgroundManager_update_db_data) Handle database read and query
        where = [split(w) for w in where] if where else where
        self.models_manager.data_manager.handler.handle_read(dataset)
        self.models_manager.data_manager.handler.handle_where(where)

        # (ModelsDBBackgroundManager_update_db_handle) Handle model read and processing
        self.handler.handle_read(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)

        # (ModelsDBBackgroundManager_update_db_add) Add update db task
        self._add_model_task('update_db', name, dataset, settings=settings, where=where, *args, **kwargs)

class ModelsMetadataManager:

    def __init__(
        self,
        models_manager,
        table=DEFAULT_MODELS_TABLE,
        columns=DEFAULT_MODELS_COLUMNS,
        database=Database()
    ):

        # (ModelsMetadataManager_table) Create table if not exists
        if not database.has_table(table):
            database.create_table(table, columns)

        # (ModelsMetadataManager_attr) Set attributes
        self.models_manager = models_manager
        self.table = table
        self.database = database

    def create(self, name, data):

        # (ModelsMetadataManager_create_vars) Set variables
        data = [data] if isinstance(data, dict) else data
        instance = self.models_manager.instances[name]

        # (ModelsMetadataManager_create_add) Add metadata for model
        data[0]['name'] = name
        data[0]['model'] = type(instance).__name__
        self.database.insert(self.table, data)