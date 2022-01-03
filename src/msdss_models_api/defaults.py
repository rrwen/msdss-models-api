DEFAULT_DOTENV_KWARGS = dict(
    env_file='./.env',
    key_path=None,
    broker_url='MSDSS_MODELS_BROKER_URL',
    backend_url='MSDSS_MODELS_BACKEND_URL',
    folder='MSDSS_MODELS_FOLDER'
)

DEFAULT_MODELS_FOLDER = './models'
DEFAULT_BROKER_URL = 'redis://localhost:6379/0'
DEFAULT_BACKEND_URL = 'redis://localhost:6379/0'

DEFAULT_METADATA_TABLE = 'model'
DEFAULT_BASE_METADATA_TABLE = 'base_model'
DEFAULT_NAME_COLUMN = 'name'
DEFAULT_UPDATE_COLUMN = 'updated_at'
DEFAULT_METADATA_COLUMNS = [
    dict(name='id', type_='Integer', primary_key=True),
    dict(name='name', type_='String', unique=True),
    ('title', 'String'),
    ('description', 'String'),
    ('tags', 'String'),
    ('source', 'String'),
    ('model', 'String'),
    ('can_input', 'Boolean'),
    ('can_output', 'Boolean'),
    ('can_update', 'Boolean'),
    ('created_by', 'String'),
    ('created_at', 'DateTime'),
    ('updated_at', 'DateTime')
]
DEFAULT_BASE_METADATA_COLUMNS = [
    ('model', 'String'),
    ('description', 'String'),
    ('input_description', 'String'),
    ('output_description', 'String'),
    ('update_description', 'String')
]

DEFAULT_MODELS_ROUTE_SETTINGS = dict(
    cancel=dict(
        path='/{name}/cancel',
        _enable=True,
        _get_user={'superuser': True}
    ),
    create=dict(
        path='/',
        _enable=True,
        _get_user={'superuser': True}
    ),
    delete=dict(
        path='/{name}',
        _enable=True,
        _get_user={'superuser': True}
    ),
    input=dict(
        path='/{name}',
        _enable=True,
        _get_user={'superuser': True}
    ),
    input_db=dict(
        path='/{name}/data',
        _enable=True,
        _get_user={'superuser': True}
    ),
    metadata=dict(
        path='/{name}/metadata',
        tags=['metadata'],
        _enable=True,
        _get_user={}
    ),
    metadata_update=dict(
        path='/{name}/metadata',
        tags=['metadata'],
        _enable=True,
        _get_user={'superuser': True}
    ),
    output=dict(
        path='/{name}/output',
        _enable=True,
        _get_user={}
    ),
    status=dict(
        path='/{name}/status',
        _enable=True,
        _get_user={}
    ),
    search=dict(
        path='/',
        _enable=True,
        _get_user={}
    ),
    update=dict(
        path='/{name}',
        _enable=True,
        _get_user={'superuser': True}
    ),
    update_db=dict(
        path='/{name}/data',
        _enable=True,
        _get_user={'superuser': True}
    )
)