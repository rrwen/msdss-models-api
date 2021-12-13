from copy import deepcopy
from fastapi import APIRouter, Body, Depends, Query
from typing import Any, Dict, List, Literal, Optional

from .defaults import *
from .managers import *
from .tools import *

async def _no_current_user():
    return None

def get_models_router(
    bg_manager,
    users_api=None,
    database=None,
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
    if isinstance(bg_manager, ModelsDBBackgroundManager):
        get_bg_manager = create_models_db_bg_manager_func(bg_manager=bg_manager)
    else:
        get_bg_manager = create_models_bg_manager_func(bg_manager=bg_manager)

    # (get_models_router_api) Create api router for model routes
    out = APIRouter(prefix=prefix, tags=tags, *args, **kwargs)

    # (get_models_router_cancel) Add cancel route to models router
    if enable['cancel']:
        @out.post(**settings['cancel'])
        async def cancel_model_instance_processing(
            name: str = Query(..., description='Name of the model instance'),
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['cancel'])
        ):
            bg_manager.cancel(name)
            response = bg_manager.get_status(name)
            return response

    # (get_models_router_create) Add create route to models router
    if enable['create']:
        @out.post(**settings['create'])
        async def create_model_instance(
            name: str = Query(..., description='Name of the model instance'),
            model: str = Query(..., description='Type of model to create an instance of'),
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['create'])
        ):
            bg_manager.create(name, model)
            response = bg_manager.get_status(name)
            return response

    # (get_models_router_delete) Add delete route to models router
    if enable['delete']:
        @out.delete(**settings['delete'])
        async def delete_model_instance(
            name: str = Query(..., description='Name of the model instance'),
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['delete'])
        ):
            bg_manager.delete(name)

    # (get_models_router_status) Add status route to models router
    if enable['status']:
        @out.get(**settings['status'])
        async def model_instance_status(
            name: str = Query(..., description='Name of the model instance'),
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['status'])
        ):
            response = bg_manager.get_status(name)
            return response

    # (get_models_router_input) Add input route to models router
    if enable['input']:
        @out.post(**settings['input'])
        async def model_instance_input(
            name: str = Query(..., description='Name of the model instance - the request body is used to upload JSON data under the "data" key in the form of "[{col: val, col2: val2, ...}, {col: val, col2: val2, ...}]", where each key represents a column and its corresponding value. Objects in this list should have the same keys. The "settings" key is used for specific model input settings, where each key is a setting name.'),
            data: List[Dict[str, Any]] = Body(...),
            settings: Dict[str, Any] = {},
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['input'])
        ):
            bg_manager.input(name, data, settings)
            response = bg_manager.get_status(name)
            return response

    # (get_models_router_input_db) Add input db route to models router
    if enable['input_db']:
        @out.post(**settings['input_db'])
        async def model_instance_input_with_dataset(
            name: str = Query(..., description='Name of the model instance - the "settings" key in the response body is used for specific model input settings, where each key is a setting name.'),
            dataset: str = Query(..., description='Dataset name to use for initializing the model instance'),
            settings: Dict[str, Any] = {},
            select: Optional[List[str]] = Query('*', description='Columns to include - "*" means all columns and "None" means to omit selection (useful for aggregate queries)'),
            where: Optional[List[str]] = Query(None, description='Where statements to filter data in the form of "column operator value" (e.g. "var < 3") - valid operators are: =, !=, >, >=, >, <, <=, !=, LIKE, ILIKE, NOTLIKE, NOTILIKE, CONTAINS, STARTSWITH, ENDSWITH'),
            group_by: Optional[List[str]] = Query(None, alias='group-by', description='column names to group by - should be used with aggregate and aggregate_func parameters'),
            aggregate: Optional[List[str]] = Query(None, description='Column names to aggregate with the same order as the aggregate_func parameter'),
            aggregate_func: Optional[List[str]] = Query(None, alias='aggregate-func', description='Aggregate functions in the same order as the aggregate parameter'),
            order_by: Optional[List[str]] = Query(None, alias='order-by', description='Column names to order by in the same order as parameter order_by_sort'),
            order_by_sort: Optional[List[Literal['asc', 'desc']]] = Query(None, alias='order-by-sort', description='Either "asc" for ascending or "desc" for descending order in the same order as parameter order_by'),
            limit: Optional[int] = Query(None, description='Number of items to return'),
            where_boolean: Literal['AND', 'OR'] = Query('AND', alias='where-boolean', description='Either "AND" or "OR" to combine where statements'),
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['input_db'])
        ):
            bg_manager.input_db(
                name,
                dataset,
                settings=settings,
                select=select,
                where=where,
                group_by=group_by,
                aggregate=aggregate,
                aggregate_func=aggregate_func,
                order_by=order_by,
                order_by_sort=order_by_sort,
                limit=limit,
                where_boolean=where_boolean)
            response = bg_manager.get_status(name)
            return response

    # (get_models_router_output) Add output route to models router
    if enable['output']:
        @out.post(**settings['output'])
        async def model_instance_output(
            name: str = Query(..., description='Name of the model instance - the request body is used to upload JSON data under the "data" key in the form of "[{col: val, col2: val2, ...}, {col: val, col2: val2, ...}]", where each key represents a column and its corresponding value. Objects in this list should have the same keys. The "settings" key is used for specific model output settings, where each key is a setting name.'),
            data: List[Dict[str, Any]] = Body(...),
            settings: Dict[str, Any] = {},
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['output'])
        ):
            response = bg_manager.output(name, data, settings).to_dict('records')
            return response

    # (get_models_router_update) Add update route to models router
    if enable['update']:
        @out.put(**settings['update'])
        async def update_model_instance(
            name: str = Query(..., description='Name of the model instance - the request body is used to upload JSON data under the "data" key in the form of "[{col: val, col2: val2, ...}, {col: val, col2: val2, ...}]", where each key represents a column and its corresponding value. Objects in this list should have the same keys. The "settings" key is used for specific model update settings, where each key is a setting name.'),
            data: List[Dict[str, Any]] = Body(...),
            settings: Dict[str, Any] = {},
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['update'])
        ):
            bg_manager.update(name, data, settings)
            response = bg_manager.get_status(name)
            return response

    # (get_models_router_update_db) Add update db route to models router
    if enable['update_db']:
        @out.put(**settings['update_db'])
        async def update_model_instance_with_dataset(
            name: str = Query(..., description='Name of the model instance - the "settings" key in the response body is used for specific model update settings, where each key is a setting name.'),
            dataset: str = Query(..., description='Dataset name to use for updating the model instance'),
            settings: Dict[str, Any] = {},
            select: Optional[List[str]] = Query('*', description='Columns to include - "*" means all columns and "None" means to omit selection (useful for aggregate queries)'),
            where: Optional[List[str]] = Query(None, description='Where statements to filter data in the form of "column operator value" (e.g. "var < 3") - valid operators are: =, !=, >, >=, >, <, <=, !=, LIKE, ILIKE, NOTLIKE, NOTILIKE, CONTAINS, STARTSWITH, ENDSWITH'),
            group_by: Optional[List[str]] = Query(None, alias='group-by', description='Column names to group by - should be used with aggregate and aggregate_func parameters'),
            aggregate: Optional[List[str]] = Query(None, description='Column names to aggregate with the same order as the aggregate_func parameter'),
            aggregate_func: Optional[List[str]] = Query(None, alias='aggregate-func', description='Aggregate functions in the same order as the aggregate parameter'),
            order_by: Optional[List[str]] = Query(None, alias='order-by', description='cClumn names to order by in the same order as parameter order_by_sort'),
            order_by_sort: Optional[List[Literal['asc', 'desc']]] = Query(None, alias='order-by-sort', description='Either "asc" for ascending or "desc" for descending order in the same order as parameter order_by'),
            limit: Optional[int] = Query(None, description='Number of items to return'),
            offset: Optional[int] = Query(None, description='Number of items to skip'),
            where_boolean: Literal['AND', 'OR'] = Query('AND', alias='where-boolean', description='Either "AND" or "OR" to combine where statements'),
            bg_manager = Depends(get_bg_manager),
            user = Depends(get_user['update_db'])
        ):
            bg_manager.update_db(
                name,
                dataset,
                settings=settings,
                select=select,
                where=where,
                group_by=group_by,
                aggregate=aggregate,
                aggregate_func=aggregate_func,
                order_by=order_by,
                order_by_sort=order_by_sort,
                limit=limit,
                offset=offset,
                where_boolean=where_boolean)
            response = bg_manager.get_status(name)
            return response

    return out