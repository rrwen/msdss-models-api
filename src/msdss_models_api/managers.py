import os
import pickle
import shutil

from msdss_base_database import Database

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

    instances : dict
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

            # 

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
        
        # (ModelsManager_create_subfolder) Create subfolder if not exists for model
        folder = self.get_folder(name)
        if not os.path.isdir(folder):
            os.path.makedirs(folder)
        
        # (ModelsManager_create_obj) Create base model object
        save_file = self.get_save_file(name)
        base_model = self.models[model](file_path=save_file, **settings)

        # (ModelsManager_create_save) Save base model object
        base_file = self.get_file(name)
        pickle.dumps(base_model, base_file)
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

                # Delete model instance
                models_manager.delete('temp_model')
        """

        # (ModelsManager_delete_instance) Run instance deletion
        instance = self.instances[name]
        instance.delete(**settings)

        # (ModelsManager_delete_folder) Delete folder
        folder = self.get_folder(name)
        shutil.rmtree(folder)
        del self.instances[name]

    def get_file(self, name):
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
                path = models_manager.get_file('temp_model')
        """
        folder = self.get_folder(name)
        out = os.path.join(folder, name + self.suffix)
        return out

    def get_folder(self, name):
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
                folder_path = models_manager.get_folder('temp_model')
        """
        out = os.path.join(self.folder, name)
        return out

    def get_save_file(self, name):
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
                save_path = models_manager.get_save_file('temp_model')
        """
        folder = self.get_folder(name)
        out = os.path.join(folder, name)
        return out

    def load(self):
        """
        Load all base models.

        Sets attribute ``.instances`` to be initialized :class:`msdss_models_api.models.Model` instances based on the subfolders in attribute ``folders``

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
                models_manager.load()
        """
        names = [name for name in os.listdir(self.folder) if os.path.isdir(name)]
        for name in names:
            self.instances[name] = pickle.load(self.get_file(name))

    def input(self, name, data, settings={}):
        """
        Train an initial model instance and save it by adding input data.

        Modifies ``.instance[name]`` by calling the ``input`` and ``save`` methods.

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
        instance = self.instances[name]
        instance.input(data, **settings)
        instance.save()

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

                # Produce output from a model
                test_data = [
                    {'col_a': 2, 'col_b': 'c'},
                    {'col_a': 3, 'col_b': 'd'}
                ]
                models_manager.output('temp_model', test_data)
        """
        instance = self.instances[name]
        if instance.can_load():
            instance.load()
        instance.output(data, **settings)
    
    def update(self, name, data, settings={}):
        """
        Update a model instance with new data.

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

                # Produce output from a model
                new_data = [
                    {'col_a': 2, 'col_b': 'c'},
                    {'col_a': 3, 'col_b': 'd'}
                ]
                models_manager.update('temp_model', new_data)
        """
        instance = self.get(name)
        if instance.can_load():
            instance.load()
        instance.update(data, **settings)
        instance.save()

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
        instance = self.models_manager.get(name)

        # (ModelsMetadataManager_create_add) Add metadata for model
        data[0]['name'] = name
        data[0]['model'] = instance.__name__
        data[0]['directory'] = instance.file
        self.database.insert(self.table, data)