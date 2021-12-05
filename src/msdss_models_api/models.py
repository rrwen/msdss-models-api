import os
import pickle

from datetime import datetime

class Model:
    """
    Template class to standardize modelling.

    * Methods ``delete``, ``load``, and ``save`` are handled by default using :class:`pickle` and do not need to be defined if there is no need for custom model saving and loading.
    * Methods ``input``, ``output`` and ``update`` need to be defined as they are placeholders for standardized functions of the model
    
    Parameters
    ----------
    model : class
        Object to use for modelling. Can be used in methods as ``self.model``.
    file_path : str
        Path to save, load, and delete the model for persistence without the extension. Can be used in methods as ``self.file``.
    file_ext : str
        File extension to save the model in.

    Attributes
    ----------
    model : class
        Same as parameter ``model``.
    instance : obj or None
        An instance of the model initialized with method :meth:`msdss_models_api.models.Model.input`. Initial value is ``None``.
    file : str
        File path to save the model for persistence in. Includes the ``file_ext``.
    last_loaded : :class:`datetime.datetime` or None
        The date and time that the model was last loaded. If ``None``, model has not been loaded. Useful for lazy loading.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        import tempfile
        from msdss_models_api.models import Model

        with tempfile.NamedTemporaryFile() as file:

            # Create template model
            # Note - typically, you want to set all of the following:
            # Model(model=obj, file_path='path/to/model')
            model_path = file.name
            blank_model = Model(file_path=model_path)
            
            # Not saved yet, should be False
            can_load_before = blank_model.can_load()

            # Save the model
            blank_model.save()

            # Saved, should be True
            can_load_after = blank_model.can_load()
            blank_model.load() # loading works after save

            # To use the model, .input() and .output() needs to be defined
            # To update the model, .update() needs to be defined
            # The template model does nothing for these methods
            # It is recommended to extend this model and redefine these methods
            data = [1,2,3,4,5]
            blank_model.input(data)
            blank_model.output(data)
            blank_model.update(data)

            # After saving, you can delete the saved model
            # This will also set .instance to None
            blank_model.delete()
    """
    def __init__(self, model=None, file_path='./model', file_ext='pickle'):
        self.model = model
        self.instance = None
        self.file = os.path.join(file_path, file_ext)
        self.last_loaded = None

    def can_load(self):
        """
        Checks if a model can be loaded using the save file.

        Returns
        -------
        bool
            Whether the model can be loaded from the save file or not.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model

            with tempfile.NamedTemporaryFile() as file:

                # Create template model
                model_path = file.name
                blank_model = Model(file_path=model_path)

                # Check if model can be loaded
                blank_model.can_load()
        """
        out = os.path.isfile(self.file)
        return out

    def delete(self):
        """
        Deletes the saved model and sets the attribute ``.instance`` to ``None``.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model

            with tempfile.NamedTemporaryFile() as file:

                # Create template model
                model_path = file.name
                blank_model = Model(file_path=model_path)

                # Save model
                blank_model.save()

                # Delete saved model
                blank_model.delete()
        """
        self.instance = None
        os.remove(self.file)

    def input(self, data):
        """
        Template method for input data to initialize model.
        
        Requirements:

        * The first argument should be the input data seen in the parameters
        * Other arguments can be defined as any for the model after the first argument
        * Should set ``self.instance`` to the initialized model

        Notes:

        * Does nothing but act as a template reference for class extension
        * This method should be re-defined using a class extension

        Parameters
        ----------
        data : dict or list or :class:`pandas:pandas.DataFrame`
            Data to use for initializing the model. Should accept a ``list`` or ``dict`` to be input in a :class:`pandas:pandas.DataFrame` or the dataframe itself.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model

            with tempfile.NamedTemporaryFile() as file:

                # Create template model
                model_path = file.name
                blank_model = Model(file_path=model_path)

                # Calling this should initialize the model instance
                # blank_model.instance should be set
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                blank_model.input(train_data)
        """
        pass

    def load(self, force=False):
        """
        Loads a saved model.

        If the model file has not been changed, skips loading based on ``last_loaded``.

        Parameters
        ----------
        force : bool
            Whether to force loading whether the saved model has been changed or not.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model

            with tempfile.NamedTemporaryFile() as file:

                # Create template model
                model_path = file.name
                blank_model = Model(file_path=model_path)

                # Save model
                blank_model.save()

                # Load model
                blank_model.load()
        """

        # (Model_load_cond) Get conditions for loading
        last_modified = datetime.fromtimestamp(os.path.getmtime(self.file))
        changed = last_modified > self.last_loaded if self.last_loaded else True

        # (Model_load_file) Load the saved model
        if force or changed:
            self.instance = pickle.loads(self.file)
            self.last_loaded = datetime.now()

    def output(self, data):
        """
        Template method for a model to output data such as predictions or clusters.
        
        Requirements:

        * The first argument should be the input data seen in the parameters
        * Other arguments can be defined as any for the model output after the first argument
        * Ideally, should use ``self.instance`` to produce the output

        Notes:

        * Does nothing but act as a template reference for class extension
        * This method should be re-defined using a class extension

        Parameters
        ----------
        data : dict or list or :class:`pandas:pandas.DataFrame`
            Data to use as input for the model. Should accept a ``list`` or ``dict`` to be input in a :class:`pandas:pandas.DataFrame` or the dataframe itself.

        Returns
        -------
        :class:`pandas:pandas.DataFrame`
            Output data from the model using the input data from parameter ``data``.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model

            with tempfile.NamedTemporaryFile() as file:

                # Create template model
                model_path = file.name
                blank_model = Model(file_path=model_path)

                # Calling this should initialize the model instance
                # blank_model.instance should be set
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                blank_model.input(train_data)

                # Calling this will produce model outputs but only after .input() is used
                # blank_model.instance should be used to produce the outputs
                test_data = [
                    {'col_a': 2, 'col_b': 'c'},
                    {'col_a': 3, 'col_b': 'd'}
                ]
                out = blank_model.output(test_data)
        """
        pass

    def save(self):
        """
        Saves the model to a file to be loaded.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model

            with tempfile.NamedTemporaryFile() as file:

                # Create template model
                model_path = file.name
                blank_model = Model(file_path=model_path)

                # Save model
                blank_model.save()
        """
        pickle.dumps(self.instance, self.file)

    def update(self, data):
        """
        Template method for updating a model with new data.
        
        Requirements:

        * The first argument should be the input data seen in the parameters
        * Other arguments can be defined as any for the model output after the first argument
        * Ideally, should update ``self.instance``

        Notes:

        * Does nothing but act as a template reference for class extension
        * This method should be re-defined using a class extension

        Parameters
        ----------
        data : dict or list or :class:`pandas:pandas.DataFrame`
            Data to use for updating the model. Should accept a ``list`` or ``dict`` to be input in a :class:`pandas:pandas.DataFrame` or the dataframe itself.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            import tempfile
            from msdss_models_api.models import Model

            with tempfile.NamedTemporaryFile() as file:

                # Create template model
                model_path = file.name
                blank_model = Model(file_path=model_path)

                # Calling this should initialize the model instance
                # blank_model.instance should be set
                train_data = [
                    {'col_a': 1, 'col_b': 'a'},
                    {'col_a': 2, 'col_b': 'b'}
                ]
                blank_model.input(train_data)

                # Calling this will update the model but only after .input() is used
                # blank_model.instance should be updated with the new data
                new_data = [
                    {'col_a': 2, 'col_b': 'c'},
                    {'col_a': 3, 'col_b': 'd'}
                ]
                blank_model.update(new_data)
        """
        pass