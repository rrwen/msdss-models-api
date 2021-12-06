import os

from fastapi import HTTPException

class ModelsHandler:
    """
    Class to handle model operations.
    
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
        if model not in models:
            raise HTTPException(status_code=404, detail='Model not found')
        self.handle_write(name, instances)
    
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
        if name in instances:
            raise HTTPException(status_code=400, detail='Model instance already exists')