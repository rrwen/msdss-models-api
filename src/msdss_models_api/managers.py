from datetime import datetime
import os
import pickle
import shutil
import warnings

from msdss_data_api.managers import DataManager, MetadataManager
from shlex import split

from .defaults import *
from .handlers import *
from .tools import *

class ModelsManager:
    """
    Class to manage :class:`msdss_models_api.models.Model` objects.
    
    Parameters
    ----------
    models : list(:class:`msdss_models_api.models.Model`) or dict(:class:`msdss_models_api.models.Model`)
        List or dict of available ``Model`` objects to use for creating and managing model instances.
        If ``list``, ensure that the class names are unique, otherwise the last object in the list takes priority.
    folder : str
        The folder path to store models in.
    handler : :class:`msdss_models_api.handlers.ModelsHandler` or bool None
        Handler object to manage model operations.
        
        * If ``None``, then a default handler will be created
        * If ``False``, then inputs for model operations will not be handled

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

        # (ModelsManager_attr) Set attributes
        handler = ModelsHandler() if handler is None else handler
        self.folder = folder
        self.models = {(m.__name__):m for m in models} if isinstance(models, list) else models
        self.instances = {}
        self.handler = handler
        self.suffix = suffix

        # (ModelsManager_load) Load base model instances
        self._load_base_files()

    def _get_base_file(self, name):
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
                path = models_manager._get_base_file('temp_model')
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

    def _get_instance(self, name):
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
                models_manager._get_instance('temp_model')
        """
        out = self.instances[name]
        return out

    def _get_model_name(self, name):
        """
        Get the model name of a model instance.

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
                models_manager._get_model_name('temp_model')
        """
        instance = self._get_instance(name)
        out = type(instance).__name__
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

    def _load_base_files(self, force=False):
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
                models_manager._load_base_files()
        """
        names = [name for name in os.listdir(self.folder) if os.path.isdir(os.path.join(self.folder, name))]
        for name in names:
            if name not in self.instances or force:
                path = self._get_base_file(name)
                with open(path, 'rb') as file:
                    self.instances[name] = pickle.load(file)

    def create(self, name, model, parameters={}):
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
        parameters : dict
            parameters to be passed to :class:`msdss_models_api.models.Model` to instantiate the instance.
        
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

        # (ModelsMAnager_create_handle) Handle create operation
        if self.handler:
            self.handler.handle_create(name, model, self.instances, self.models)
        
        # (ModelsManager_create_subfolder) Create subfolder if not exists for model
        folder = self._get_folder(name)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        
        # (ModelsManager_create_obj) Create base model object
        save_file = self._get_save_file(name)
        base_model = self.models[model](file_path=save_file, **parameters)
        base_model.metadata['model'] = model

        # (ModelsManager_create_save) Save base model object
        with open(self._get_base_file(name), 'wb') as base_file:
            pickle.dump(base_model, base_file)
            self.instances[name] = base_model

    def delete(self, name, parameters={}):
        """
        Creates a model instance.

        * Removes the instance in attribute ``instances``
        * Removes the subfolder and base model file for the instance

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        parameters : dict
            parameters to be passed to :meth:`msdss_models_api.models.Model.delete`.
        
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

        # (ModelsManager_delete_handle) Handle read operation
        if self.handler:
            self.handler.handle_read(name, self.instances)

        # (ModelsManager_delete_instance) Run instance deletion
        instance = self._get_instance(name)
        instance.delete(**parameters)

        # (ModelsManager_delete_folder) Delete folder
        folder = self._get_folder(name)
        shutil.rmtree(folder)
        del self.instances[name]

    def input(self, name, data, parameters={}):
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
        parameters : dict
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

        # (ModelsManager_input_handle) Handle input operation
        if self.handler:
            self.handler.handle_input(name, self.instances)

        # (ModelsManager_input_run) Initialize model with input data
        instance = self._get_instance(name)
        instance.input(data, **parameters)
        instance.save()

    def output(self, name, data, parameters={}):
        """
        Get the output of a model instance.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        data : dict or list or :class:`pandas:pandas.DataFrame`
            Data to use for obtaining the model instance output. Should accept a ``list`` or ``dict`` to be input in a :class:`pandas:pandas.DataFrame` or the dataframe itself.
        parameters : dict
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

        # (ModelsManager_output_handle) Handle output operation
        if self.handler:
            self.handler.handle_output(name, self.instances)

        # (ModelsManager_output_run) Get model output
        instance = self._get_instance(name)
        instance.load()
        out = instance.output(data, **parameters)
        return out
    
    def update(self, name, data, parameters={}):
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
        parameters : dict
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

        # (ModelsManager_update_handle) Handle update operation
        if self.handler:
            self.handler.handle_update(name, self.instances)

        # (ModelsManager_update_run) Update model instance
        instance = self._get_instance(name)
        instance.load()
        instance.update(data, **parameters)
        instance.save()

class ModelsBackgroundManager:
    """
    Class to manage :class:`msdss_models_api.models.Model` background processes using a :class:`msdss_models_api.managers.ModelsManager`.
    
    * Note: it is expected that the model outputs and creation are not long running processes

    Parameters
    ----------
    worker : :class:`celery:celery.Celery`
        A ``celery`` app object to manage background tasks.
    models_manager : :class:`msdss_models_api.managers.ModelsManager`
        A models manager object to manage models.
        The handler for the models manager will be disabled (set to ``None``) as model operations will be handled with attribute ``models_handler`` instead.
    handler : :class:`msdss_models_api.handlers.ModelsBackgroundHandler` or None
        Handler object to manage background operations. If ``None``, a default handler will be created.
    metadata_manager : :class:`msdss_models_api.managers.ModelsMetadataManager` or ``None``
        A metadata manager object. If ``None``, metadata will not be managed based on model operations.

    Attributes
    ----------
    worker : :class:`celery:celery.Celery` or None
        Same as parameter ``worker``.
    models_manager : dict(:class:`msdss_models_api.manager.ModelsManager`)
        Same as parameter ``models_manager``.
    tasks : dict
        Dictionary of background tasks from the ``worker`` object with the following keys:

        * ``input`` (func): background task to initialize models with input data
        * ``update`` (func): background task to update models

    states : dict
        Dictionary of processing states for each instance, consisting of the following keys:

        * ``task`` (str): the action that the process is performing - one of: ``INPUT``, ``UPDATE``
        * ``result`` (:class:`celery:celery.result.AsyncResult`): celery async object for getting states, ids, etc (see `celery.result <https://docs.celeryproject.org/en/stable/reference/celery.result.html#celery.result.AsyncResult>`_)
        * ``started_at`` (:class:`datetime.datetime`): datetime object for when the task was started
    
    models_handler : :class:`msdss_models_api.handlers.ModelsHandler`
        Handler extracted from parameter ``models_manager``.
    handler : :class:`msdss_models_api.handlers.ModelsBackgroundHandler`
        Same as parameter ``handler``.
    metadata_manager : :class:`msdss_models_api.managers.ModelsMetadataManager`
        Same as parameter ``metadata_manager``.
    
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
    def __init__(self, worker, models_manager, handler=None, metadata_manager=None):

        # (ModelsBackgroundManager_models_manager) Setup models manager and disable handler
        handler = ModelsBackgroundHandler() if handler is None else handler
        self.models_manager = models_manager
        self.models_handler = self.models_manager.handler
        self.models_manager.handler = False
        self.metadata_manager = metadata_manager

        # (ModelsBackgroundManager_attr) Set other attributes
        self.worker = worker
        self.tasks = {}
        self.states = {}
        self.handler = handler

        # (ModelsBackgroundManager_task_input) Define input task
        @self.worker.task
        def input(name, data, parameters={}):
            models_manager._load_base_files()
            models_manager.input(name, data, parameters)
            if metadata_manager:
                metadata_manager.updated_at(name)
        self.tasks['input'] = input

        # (ModelsBackgroundManager_task_update) Define update task
        @self.worker.task
        def update(name, data, parameters={}):
            models_manager._load_base_files()
            models_manager.update(name, data, parameters)
            if metadata_manager:
                metadata_manager.updated_at(name)
        self.tasks['update'] = update

    def _add_task(self, task, name, *args, **kwargs):
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
                bg_manager._add_task('input', 'temp_model', train_data)
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

    def create(self, name, model, metadata={}, *args, **kwargs):
        """
        Create a model instance.

         * Runs :meth:`msdss_models_api.managers.ModelsManager.create`

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.create`.
        model : str
            See parameter ``model`` in :meth:`msdss_models_api.managers.ModelsManager.create`.
        metadata : dict
            Metadata to add for the model if attribute ``.metadata_manager`` is not ``None``.
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

        # (ModelsBackgroundManager_create_model) Create model
        self.models_manager._load_base_files()
        self.models_handler.handle_create(name, model, self.models_manager.instances, self.models_manager.models)
        self.models_manager.create(name, model, *args, **kwargs)

        # (ModelsBackgroundManager_create_metadata) Add initial metadata for model
        if self.metadata_manager:
            instance = self.models_manager._get_instance(name)
            metadata['name'] = name
            metadata['created_at'] = datetime.now()
            metadata['updated_at'] = datetime.now()
            metadata['model'] = instance.metadata['model'] if 'model' in instance.metadata else type(instance).__name__
            metadata['can_input'] = instance.metadata['can_input']
            metadata['can_output'] = instance.metadata['can_output']
            metadata['can_update'] = instance.metadata['can_update']
            self.metadata_manager.create(name=name, data=metadata)

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
        self.models_manager._load_base_files()
        self.models_handler.handle_read(name, self.models_manager.instances)
        if name in self.states:
            status = self.states[name]['result'].state
            if status in ['PENDING', 'STARTED', 'RETRY']:
                self.cancel(name)
        self.models_manager.delete(name, *args, **kwargs)
        self.metadata_manager.delete(name)

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
            * ``started_at`` (:class:`datetime.datetime`): when the process was started

            If the model instance is not processing, it will return a dict of the status only ``{'status': 'IDLE'}``.

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
        if name in self.states:
            state = self.states[name]
            out = {
                'task': state['task'],
                'status': state['result'].state,
                'started_at': state['started_at']
            }
        else:
            out = {
                'status': 'IDLE'
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
        self.models_manager._load_base_files()
        self.models_handler.handle_input(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)
        self._add_task('input', name, *args, **kwargs)

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
        self.models_manager._load_base_files()
        self.models_handler.handle_output(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)
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
                bg_manager._add_task('input', 'temp_model', train_data)

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
        self.models_manager._load_base_files()
        self.models_handler.handle_update(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)
        self._add_task('update', name, *args, **kwargs)

class ModelsDBManager(ModelsManager):
    """
    Class to manage :class:`msdss_models_api.models.Model` objects with added methods for processing models with data from a database.

    * Inherits from :class:`msdss_models_api.models.ModelsManager`
    
    Parameters
    ----------
    models : list(:class:`msdss_models_api.models.Model`)
        List of available ``Model`` objects to use for creating and managing model instances.
        Ensure that the class names are unique, otherwise the last object takes priority.
    data_manager : :class:`msdss_data_api.managers.DataManager` or None
        A data manager object for managing data in and out of a database. If ``None``, a default data manager will be used.
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
        from msdss_data_api.managers import DataManager
        from msdss_models_api.models import Model
        from msdss_models_api.managers import ModelsDBManager

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models and database
            database = Database()
            models = [Model]
            
            # Create manager
            data_manager = DataManager(database=database)
            models_manager = ModelsDBManager(models, data_manager, folder=folder_path)

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
    def __init__(self, models=[], data_manager=None, *args, **kwargs):
        data_manager = data_manager if data_manager else DataManager()
        super().__init__(models=models, *args, **kwargs)
        self.data_manager = data_manager
    
    def input_db(self, name, dataset, parameters={}, *args, **kwargs):
        """
        Initialize a model instance with data from the database.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        dataset : str
            Name of the table from the database. See parameter ``dataset`` :meth:`msdss_data_api.managers.DataManager.get`.
        parameters : dict
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
            from msdss_data_api.managers import DataManager
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsDBManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models and database
                database = Database()
                models = [Model]
                
                # Create manager
                data_manager = DataManager(database=database)
                models_manager = ModelsDBManager(models, data_manager, folder=folder_path)

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
        self.input(name, data, parameters)

    def update_db(self, name, dataset, parameters={}, *args, **kwargs):
        """
        Update a model instance with data from the database.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        dataset : str
            Name of the table from the database. See parameter ``dataset`` :meth:`msdss_data_api.managers.DataManager.get`.
        parameters : dict
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
            from msdss_data_api.managers import DataManager
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsDBManager

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models and database
                database = Database()
                models = [Model]
                
                # Create manager
                data_manager = DataManager(database=database)
                models_manager = ModelsDBManager(models, data_manager, folder=folder_path)

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
        data = self.data_manager.get(dataset, *args, **kwargs)
        self.update(name, data, parameters)

class ModelsDBBackgroundManager(ModelsBackgroundManager):
    """
    Class to manage :class:`msdss_models_api.models.Model` background processes using a :class:`msdss_models_api.managers.ModelsManager`.
    
    * Inherits from :class:`msdss_models_api.managers.ModelsBackgroundManager`

    Parameters
    ----------
    models_manager : :class:`msdss_models_api.managers.ModelsDBManager`
        A models DB manager object to manage models that can receive data from a database.
        The handler and data handler for the models manager will be disabled as model operations will be handled with parameter ``handler`` instead.
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
        from msdss_data_api.managers import DataManager
        from msdss_models_api.models import Model
        from msdss_models_api.managers import *
        from pprint import pprint

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models
            models = [Model]
            
            # Create manager
            database = Database()
            data_manager = DataManager(database=database)
            models_manager = ModelsDBManager(models, data_manager, folder=folder_path)

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
    def __init__(self, models_manager, *args, **kwargs):

        # (ModelsDBBackgroundManager_init) Initialize inherited class
        super().__init__(models_manager=models_manager, *args, **kwargs)

        # (ModelsDBBackgroundManager_data_manager) Setup data manager
        self.data_handler = self.models_manager.data_manager.handler
        self.models_manager.data_manager.handler = False
        
        # (ModelsDBBackgroundManager_task_input) Define input db task
        @self.worker.task
        def input_db(name, dataset, parameters={}, *args, **kwargs):
            models_manager.input_db(name, dataset, parameters, *args, **kwargs)
            if self.metadata_manager:
                self.metadata_manager.updated_at(name)
        self.tasks['input_db'] = input_db

        # (ModelsDBBackgroundManager_task_update) Define update db task
        @self.worker.task
        def update_db(name, dataset, parameters={}, *args, **kwargs):
            models_manager.update_db(name, dataset, parameters, *args, **kwargs)
            if self.metadata_manager:
                self.metadata_manager.updated_at(name)
        self.tasks['update_db'] = update_db

    def input_db(self, name, dataset, parameters={}, where=None, *args, **kwargs):
        """
        Initialize a model instance with data from the database.

        Parameters
        ----------
        name : str
            Unique name of the model instance. The instance is stored in ``.instances[name]``.
        dataset : str
            Name of the table from the database. See parameter ``dataset`` :meth:`msdss_data_api.managers.DataManager.get`.
        parameters : dict
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
            from msdss_data_api.managers import DataManager
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *
            from pprint import pprint

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                database = Database()
                data_manager = DataManager(database=database)
                models_manager = ModelsDBManager(models, data_manager, folder=folder_path)

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
        self.models_manager._load_base_files()
        
        # (ModelsDBBackgroundManager_input_db_data) Handle database read and query
        where = [split(w) for w in where] if where else where
        self.data_handler.handle_read(dataset)
        self.data_handler.handle_where(where)

        # (ModelsDBBackgroundManager_input_db_handle) Handle model input and processing
        self.models_handler.handle_input(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)

        # (ModelsDBBackgroundManager_input_db_add) Add input db task
        self._add_task('input_db', name, dataset, parameters=parameters, where=where, *args, **kwargs)

    def update_db(self, name, dataset, parameters={}, where=None, *args, **kwargs):
        """
        Update a model instance with new data from the database as a background task.

        Runs :meth:`msdss_models_api.managers.ModelsDBManager.update_db`.

        Parameters
        ----------
        name : str
            See parameter ``name`` in :meth:`msdss_models_api.managers.ModelsManager.update`.
        dataset : str
            Name of the table from the database. See parameter ``dataset`` :meth:`msdss_data_api.managers.DataManager.get`.
        parameters : dict
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
            from msdss_data_api.managers import DataManager
            from msdss_models_api.models import Model
            from msdss_models_api.managers import *
            from pprint import pprint

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                database = Database()
                data_manager = DataManager(database=database)
                models_manager = ModelsDBManager(models, data_manager, folder=folder_path)

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
        self.models_manager._load_base_files()

        # (ModelsDBBackgroundManager_update_db_data) Handle database read and query
        where = [split(w) for w in where] if where else where
        self.data_handler.handle_read(dataset)
        self.data_handler.handle_where(where)

        # (ModelsDBBackgroundManager_update_db_handle) Handle model update and processing
        self.models_handler.handle_update(name, self.models_manager.instances)
        self.handler.handle_processing(name, self.states)

        # (ModelsDBBackgroundManager_update_db_add) Add update db task
        self._add_task('update_db', name, dataset, parameters=parameters, where=where, *args, **kwargs)

class ModelsMetadataManager(MetadataManager):
    """
    Class to manage models metadata in a database.

    * Inherits from :class:`msdss_data_api:msdss_data_api.managers.MetadataManager`
    
    Parameters
    ----------
    data_manager : :class:`msdss_data_api.managers.DataManager` or None
        Data manager object for managing data in a database. If ``None``, a default manager will be used.
        The restricted tables for the handler will be set to ``[]`` while the only permitted table will be the table name of the parameter ``table``.
    table : str
        The name of the table to store the metadata.
    columns : list(dict) or list(list)
        List of dict (kwargs) or lists (positional args) that are passed to sqlalchemy.schema.Column. See parameter ``columns`` in :meth:`msdss_base_database:msdss_base_database.core.create_table`.
        This defines the table to store the metadata, where the default is:

        .. jupyter-execute::
            :hide-code:

            from msdss_models_api.defaults import *
            from pprint import pprint

            pprint(DEFAULT_METADATA_COLUMNS)

    name_column : str
        Name of the column identifying each entry.
    updated_column : str
        Name of the column for storing the last updated date/time.
    base_table : str
        Name of the table to store the metadata for base models.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_data_api:msdss_data_api.managers.MetadataManager`

    Attributes
    ----------
    base_table : str
        Same as parameter ``base_table``.
    
        See other attributes in :class:`msdss_data_api:msdss_data_api.managers.MetadataManager`.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        import tempfile
        from datetime import datetime
        from msdss_base_database import Database
        from msdss_data_api.managers import DataManager
        from msdss_models_api.managers import *
        from msdss_models_api.defaults import *
        
        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models
            models = [Model]
            
            # Create manager
            models_manager = ModelsManager(models, folder=folder_path)
        
            # Setup database
            db = Database()

            # Check if the metadata table exists and drop if it does
            if db.has_table(DEFAULT_METADATA_TABLE):
                db.drop_table(DEFAULT_METADATA_TABLE)

            # Setup metadata manager
            data_manager = DataManager(database=db)
            mdm = ModelsMetadataManager(data_manager, models_manager)

            # Add metadata
            metadata = [{
                'title': 'Test Model',
                'description': 'model used for testing',
                'tags': 'test exp auto',
                'source': 'Automatically generated from Python',
                'model': 'Model',
                'created_by': 'msdss',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }]
            mdm.create('test_model', metadata)

            # Get metadata
            metadata_get = mdm.get('test_model')
            
            # Search metadata
            search_results = mdm.search(where=['title = "Test Model"'])

            # Update metadata
            mdm.update('test_model', {'description': 'NEW DESCRIPTION'})

            # Delete metadata
            mdm.delete('test_model')
    """
    def __init__(
        self,
        data_manager=None,
        models_manager=None,
        table=DEFAULT_METADATA_TABLE,
        columns=DEFAULT_METADATA_COLUMNS,
        name_column=DEFAULT_NAME_COLUMN,
        updated_column=DEFAULT_UPDATE_COLUMN,
        base_table=DEFAULT_BASE_METADATA_TABLE,
        base_columns=DEFAULT_BASE_METADATA_COLUMNS,
        *args, **kwargs
    ):
        data_manager = data_manager if data_manager else DataManager()
        models_manager = models_manager if models_manager else ModelsManager()
        super().__init__(
            data_manager=data_manager,
            table=table,
            columns=columns,
            name_column=name_column,
            updated_column=updated_column,
            *args, **kwargs
        )
        self.base_table = base_table
        self.base_columns = base_columns
        self.models_manager = models_manager
        self.data_manager.handler.permitted_tables = [self.table, self.base_table]

    def load_base_models(self):
        """
        Load base model metadata into a table in the database.

        If a table with the same name exists, it will be deleted and rebuilt.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_base_database import Database
            from msdss_data_api.managers import DataManager
            from msdss_models_api.managers import *
            from msdss_models_api.defaults import *
            from msdss_models_api.models import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)
            
                # Setup database
                db = Database()

                # Check if the metadata table exists and drop if it does
                if db.has_table(DEFAULT_METADATA_TABLE):
                    db.drop_table(DEFAULT_METADATA_TABLE)

                # Setup metadata manager
                data_manager = DataManager(database=db)
                mdm = ModelsMetadataManager(data_manager, models_manager)

                # Load base models
                mdm.load_base_models()
        """

        # (ModelsMetadataManager_load_base_models_recreate) Delete table if exists and recreate
        if self.data_manager.database.has_table(self.base_table):
            self.data_manager.delete(self.base_table, delete_all=True)
        self.data_manager.database.create_table(self.base_table, self.base_columns)

        # (ModelsMetadataManager_load_base_models_data) Create base model metadata using model docstrings
        data = []
        for model_name, model in self.models_manager.models.items():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    doc = get_md_doc(model)
                    input_doc = get_md_doc(model.input) if 'input' in dir(model) else 'Not Available'
                    output_doc = get_md_doc(model.output) if 'output' in dir(model) else 'Not Available'
                    update_doc = get_md_doc(model.update) if 'update' in dir(model) else 'Not Available'
            except:
                doc = model.__doc__
                input_doc = model.input.__doc__ if 'input' in dir(model) else 'Not Available'
                output_doc = model.output.__doc__ if 'output' in dir(model) else 'Not Available'
                update_doc = model.update.__doc__ if 'update' in dir(model) else 'Not Available'
            model_data = {
                'model': model_name,
                'description': doc,
                'input_description': input_doc,
                'output_description': output_doc,
                'update_description': update_doc
            }
            data.append(model_data)

        # (ModelsMetadataManager_load_base_models_insert) Add base model metadata to database
        self.data_manager.insert(self.base_table, data)

    def search_base_models(self, *args, **kwargs):
        """
        Search base model metadata.

        See :meth:`msdss_data_api.managers.DataManager.get`.
        
        Parameters
        ----------
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_data_api.managers.DataManager.get` except for parameter ``table``.

        Returns
        -------
        list(dict)
            A dict of lists where each key is the column name and each list contains the values for columns in the order of the rows of the table.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_base_database import Database
            from msdss_data_api.managers import DataManager
            from msdss_models_api.managers import *
            from msdss_models_api.defaults import *
            from msdss_models_api.models import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path)
            
                # Setup database
                db = Database()

                # Check if the metadata table exists and drop if it does
                if db.has_table(DEFAULT_METADATA_TABLE):
                    db.drop_table(DEFAULT_METADATA_TABLE)

                # Setup metadata manager
                data_manager = DataManager(database=db)
                mdm = ModelsMetadataManager(data_manager, models_manager)

                # Load base models
                mdm.load_base_models()

                # Search base models
                out = mdm.search_base_models()
                print(out)
        """
        out = self.data_manager.get(self.base_table, *args, **kwargs)
        return out