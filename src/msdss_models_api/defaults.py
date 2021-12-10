DEFAULT_DOTENV_KWARGS = dict(
    env_file='./.env',
    key_path=None,
    broker_url='MSDSS_MODELS_BROKER_URL',
    backend_url='MSDSS_MODELS_BACKEND_URL',
    folder='MSDSS_MODELS_FOLDER'
)

DEFAULT_MODELS_FOLDER = './models'
DEFAULT_MODELS_TABLE = 'model'
DEFAULT_BROKER_URL = 'redis://localhost:6379/0'
DEFAULT_BACKEND_URL = 'redis://localhost:6379/0'

DEFAULT_MODELS_COLUMNS = [
    dict(name='id', type_='Integer', primary_key=True),
    dict(name='name', type_='String', unique=True),
    ('title', 'String'),
    ('description', 'String'),
    ('model', 'String'),
    ('directory', 'String'),
    ('created_by', 'String'),
    ('created_at', 'DateTime'),
    ('updated_at', 'DateTime')
]

DEFAULT_MODELS_ROUTE_SETTINGS = dict(
    create=dict(
        path='/',
        _enable=True,
        _get_user={'superuser': True}
    ),
)