DEFAULT_MODELS_FOLDER = './models'
DEFAULT_MODELS_TABLE = 'model'
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