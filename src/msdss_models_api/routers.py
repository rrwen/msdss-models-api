from copy import deepcopy
from fastapi import APIRouter, Body, Depends, Query

from .defaults import *
from .managers import *
from .tools import *

async def _no_current_user():
    return None

def get_models_router(
    bg_manager,
    users_api=None,
    route_settings=DEFAULT_MODELS_ROUTE_SETTINGS,
    prefix='/models',
    tags=['models'],
    *args, **kwargs
):

    # (get_models_router_defaults) Merge defaults and user params 
    get_user = {}
    settings = deepcopy(DEFAULT_MODELS_ROUTE_SETTINGS)
    for k in settings:
        if k in route_settings:
            settings[k].update(route_settings[k])

    # (get_models_router_apply) Apply settings to obtain dependencies
    get_user = {}
    enable = {}
    for k, v in settings.items():
        get_user[k] = users_api.get_current_user(**v['_get_user']) if users_api and '_get_user' in v else _no_current_user
        del v['_get_user']
        enable[k] = v.pop('_enable')

    # (get_models_router_bg) Create bg manager func
    get_bg_manager = create_models_bg_manager_func(bg_manager=bg_manager)

    # (get_models_router_api) Create api router for model routes
    out = APIRouter(prefix=prefix, tags=tags, *args, **kwargs)

    # (get_models_router_create) Add create route to models router
    if enable['create']:
        @out.post(**settings['create'])
        async def create_data(
            name: str = Query(..., description='Name of the model instance to create'),
            model: str = Query(..., description='Type of model to create an instance of'),
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['create'])
        ):
            bg_manager.create(name, model)