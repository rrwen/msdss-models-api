import os

from fastapi import HTTPException

class ModelsHandler:
    """
    Class to handle model operations.

    Parameters
    ----------
    enable : bool
        Whether to enable handling or not. If ``False``, then all methods for handling will not raise exceptions.
        This is useful for allowing higher level control of handling model operations.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        import tempfile
        from msdss_models_api.models import Model
        from msdss_models_api.managers import ModelsManager
        from msdss_models_api.handlers import ModelsHandler

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models
            models = [Model]

            # Create handler
            handler = ModelsHandler()
            
            # Create manager
            models_manager = ModelsManager(models, folder=folder_path, handler=handler)

            # Check if model and instance name available
            # Should not raise exceptions
            handler.handle_create('temp_model', 'Model', models_manager.instances, models_manager.models)

            # Check if instance name available
            # Should not raise exceptions
            handler.handle_write('temp_model', models_manager.instances)

            # Create model instance
            models_manager.create('temp_model', 'Model')

            # Check if instance exists to read
            # Should not raise exceptions
            handler.handle_read('temp_model', models_manager.instances)
    """
    def __init__(self, enable=True):
        self.enable = enable
    
    def handle_create(self, name, model, instances, models):
        """
        Handle model creation operation.

        Parameters
        ----------
        name : str
            Name of the model instance.
        model : str
            Name of the model to create.
        models : dict(:class:`msdss_models_api.models.Model`)
            Dictionary of available models from parameter ``models``, where:

            * Each key is the class name
            * Each value is the class itself

        instances : dict(:class:`msdss_models_api.models.Model`)
            Dictionary of loaded model instances.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager
            from msdss_models_api.handlers import ModelsHandler

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]

                # Create handler
                handler = ModelsHandler()
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path, handler=handler)

                # Check if model and instance name available
                # Should not raise exceptions
                handler.handle_create('temp_model', 'Model', models_manager.instances, models_manager.models)
        """
        if self.enable:
            if model not in models:
                raise HTTPException(status_code=404, detail='Model not found')
            self.handle_write(name, instances)

    def handle_load(self, instance):
        """
        Handle model load operation.

        Parameters
        ----------
        instance : :class:`msdss_models_api.models.Model`
            Model instance to be loaded.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager
            from msdss_models_api.handlers import ModelsHandler

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]

                # Create handler
                handler = ModelsHandler()
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path, handler=handler)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                models_manager.input('temp_model', train_data)

                # Recreate manager where instance is not loaded
                models_manager = ModelsManager(models, folder=folder_path, handler=handler)

                # Check if instance can be loaded
                # Should not raise exceptions
                instance = models_manager.get('temp_model')
                handler.handle_load(instance)
        """
        if self.enable:
            if instance.can_load():
                raise HTTPException(status_code=400, detail='Model instance has not been initialized')
            if not instance.needs_load():
                raise HTTPException(status_code=400, detail='Model instance already loaded')
    
    def handle_read(self, name, instances):
        """
        Handle model read operation.

        Parameters
        ----------
        name : str
            Name of the model instance.
        instances : dict(:class:`msdss_models_api.models.Model`)
            Dictionary of loaded model instances.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager
            from msdss_models_api.handlers import ModelsHandler

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]

                # Create handler
                handler = ModelsHandler()
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path, handler=handler)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Check if instance exists to read
                # Should not raise exceptions
                handler.handle_read('temp_model', models_manager.instances)
        """
        if self.enable:
            if name not in instances:
                raise HTTPException(status_code=404, detail='Model instance not found')

    def handle_write(self, name, instances):
        """
        Handle model write operation.

        Parameters
        ----------
        name : str
            Name of the model instance.
        instances : dict(:class:`msdss_models_api.models.Model`)
            Dictionary of loaded model instances.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model
            from msdss_models_api.managers import ModelsManager
            from msdss_models_api.handlers import ModelsHandler

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]

                # Create handler
                handler = ModelsHandler()
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path, handler=handler)

                # Check if instance name available
                # Should not raise exceptions
                handler.handle_write('temp_model', models_manager.instances)
        """
        if self.enable:
            if name in instances:
                raise HTTPException(status_code=400, detail='Model instance already exists')

class ModelsBackgroundHandler(ModelsHandler):
    """
    Class to handle model background operations.

    * Inherits from :class:`msdss_models_api.handlers.ModelsHandler`
    
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
        from msdss_models_api.handlers import *

        with tempfile.TemporaryDirectory() as folder_path:

            # Setup available models
            models = [Model]

            # Create handler
            handler = ModelsBackgroundHandler()
            
            # Create manager
            models_manager = ModelsManager(models, folder=folder_path, handler=handler)

            # Create bg manager
            worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
            bg_manager = ModelsBackgroundManager(worker, models_manager)

            # Create model instance
            models_manager.create('temp_model', 'Model')

            # Initialize a model instance with inputs as a background process
            train_data = [
                {'col_a': 1, 'col_b': 'a'},
                {'col_a': 2, 'col_b': 'b'}
            ]
            bg_manager.input('temp_model', train_data)

            # Check if instance is processing
            # Should not raise exceptions
            handler.handle_processing('temp_model', bg_manager.states)

            # Check if state exists
            # Should not raise exceptions
            handler.handle_read_state('temp_model', bg_manager.states)
    """

    def handle_cancel(self, name, states):
        """
        Handle model background task cancellation.

        Parameters
        ----------
        name : str
            Name of the model instance.
        states : dict
            Dictionary of processing states for each instance, consisting of the following keys:

            * ``task`` (str): the action that the process is performing - one of: ``INPUT``, ``UPDATE``, ``LOAD``
            * ``result`` (:class:`celery:celery.result.AsyncResult`): celery async object for getting states, ids, etc (see `celery.result <https://docs.celeryproject.org/en/stable/reference/celery.result.html#celery.result.AsyncResult>`_)
            * ``started_at`` (:class:`datetime.datetime`): datetime object for when the task was started
        
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
            from msdss_models_api.handlers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]

                # Create handler
                handler = ModelsBackgroundHandler()
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path, handler=handler)

                # Create bg manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)

                # Check if instance processing can be cancelled
                # Should raise an exception
                handler.handle_cancel('temp_model', bg_manager.states)
        """
        self.handle_read_state(name, states)
        status = states[name]['result'].state
        if status not in ['PENDING', 'STARTED', 'RETRY']:
            raise HTTPException(status_code=400, detail='Model instance is not processing')

    def handle_processing(self, name, states):
        """
        Handle model background task processing.

        Parameters
        ----------
        name : str
            Name of the model instance.
        states : dict
            Dictionary of processing states for each instance, consisting of the following keys:

            * ``task`` (str): the action that the process is performing - one of: ``INPUT``, ``UPDATE``, ``LOAD``
            * ``result`` (:class:`celery:celery.result.AsyncResult`): celery async object for getting states, ids, etc (see `celery.result <https://docs.celeryproject.org/en/stable/reference/celery.result.html#celery.result.AsyncResult>`_)
            * ``started_at`` (:class:`datetime.datetime`): datetime object for when the task was started
        
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
            from msdss_models_api.handlers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]

                # Create handler
                handler = ModelsBackgroundHandler()
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path, handler=handler)

                # Create bg manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)

                # Check if instance is processing
                # Should not raise exceptions
                handler.handle_processing('temp_model', bg_manager.states)
        """
        has_status = name in states
        if has_status:
            status = states[name]['result'].state
            if status in ['PENDING', 'STARTED', 'RETRY']:
                raise HTTPException(status_code=400, detail='Model instance still processing')

    def handle_read_state(self, name, states):
        """
        Handle model background task state read.

        Parameters
        ----------
        name : str
            Name of the model instance.
        states : dict
            Dictionary of processing states for each instance, consisting of the following keys:

            * ``task`` (str): the action that the process is performing - one of: ``INPUT``, ``UPDATE``, ``LOAD``
            * ``result`` (:class:`celery:celery.result.AsyncResult`): celery async object for getting states, ids, etc (see `celery.result <https://docs.celeryproject.org/en/stable/reference/celery.result.html#celery.result.AsyncResult>`_)
            * ``started_at`` (:class:`datetime.datetime`): datetime object for when the task was started
        
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
            from msdss_models_api.handlers import *

            with tempfile.TemporaryDirectory() as folder_path:

                # Setup available models
                models = [Model]

                # Create handler
                handler = ModelsBackgroundHandler()
                
                # Create manager
                models_manager = ModelsManager(models, folder=folder_path, handler=handler)

                # Create bg manager
                worker = Celery(broker='redis://localhost:6379/0', backend='redis://localhost:6379/0') # rabbitmq
                bg_manager = ModelsBackgroundManager(worker, models_manager)

                # Create model instance
                models_manager.create('temp_model', 'Model')

                # Initialize a model instance with inputs as a background process
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                bg_manager.input('temp_model', train_data)

                # Check if state exists
                # Should not raise exceptions
                handler.handle_read_state('temp_model', bg_manager.states)
        """
        if name not in states:
            raise HTTPException(status_code=404, detail='Model instance has not gone through any processing')