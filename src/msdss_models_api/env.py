from msdss_base_dotenv import DotEnv

from .defaults import DEFAULT_DOTENV_KWARGS

class ModelsDotEnv(DotEnv):
    """
    Class to manage model environment variables.

    * Extends :class:`msdss_base_dotenv:msdss_base_dotenv.core.DotEnv`

    Parameters
    ----------
    broker_url : str
        Link to connect to a `RabbitMQ <https://www.rabbitmq.com/>`_ broker.
    backend_url : str
        Link to connect to a `RabbitMQ <https://www.rabbitmq.com/>`_ backend.
    folder : str
        Path to the folder to store saved models and instances.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_models_api.env import ModelsDotEnv
        
        # Get default env vars
        env = ModelsDotEnv()
        env.save() # save to .env file
        env.load() # load the same file
        
        # Print defaults
        print('default_env:\\n')
        for k, name in env.mappings.items():
            value = str(env.get(k))
            print(f'{name}: {value}')

        # Remove saved .env file
        env.clear()

        # Create models env with diff var names
        alt_env = ModelsDotEnv(
            broker_url='MSDSS_MODELS_BROKER_URL_B',
            backend_url='MSDSS_MODELS_BACKEND_URL_B',
            folder='MSDSS_MODELS_FOLDER_B'
        )

        # Set secret
        alt_env.set('broker_url', 'redis://localhost:6379/0')

        # Set folder
        alt_env.set('folder', './path/to/folder')
        alt_env.delete('folder')

        # Check if backend url is set
        backend_is_set = alt_env.is_set('backend_url')

        # Print custom env
        # See new env
        print('\\nalt_env:\\n')
        for k, name in alt_env.mappings.items():
            value = str(alt_env.get(k))
            print(f'{name}: {value}')
        print('backend_is_set: ' + str(backend_is_set))

        # Clear alt env files
        alt_env.clear()
    """
    def __init__(
        self,
        broker_url=DEFAULT_DOTENV_KWARGS['broker_url'],
        backend_url=DEFAULT_DOTENV_KWARGS['backend_url'],
        folder=DEFAULT_DOTENV_KWARGS['folder'],
        env_file=DEFAULT_DOTENV_KWARGS['env_file'],
        key_path=DEFAULT_DOTENV_KWARGS['key_path']):
        kwargs = locals()
        del kwargs['self']
        del kwargs['__class__']
        super().__init__(**kwargs)