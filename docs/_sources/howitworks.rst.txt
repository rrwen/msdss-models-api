How it Works
============

This package creates an extended :class:`msdss_base_api:msdss_base_api.core.API` application using :class:`msdss_models_api.core.ModelsAPI`. The ``ModelsAPI`` class uses :func:`msdss_models_api.routers.get_models_router` to setup routes for managing models. Model management is handled by managers in :mod:`msdss_models_api.managers`, which use handlers in :mod:`msdss_models_api.handlers` to check for route inputs. The general idea is: ``handlers -> managers -> get_models_router -> ModelsAPI``.

**Other notes:**

* Database operations are handled by :class:`msdss_data_api:msdss_data_api.managers.DataManager` and :class:`msdss_data_api:msdss_data_api.managers.MetadataManager`.
* Long-running background tasks are managed by :class:`msdss_models_api.managers.ModelsBackgroundManager` (non-database) and :class:`msdss_models_api.managers.ModelsDBBackgroundManager` (with database) using `Celery <https://docs.celeryproject.org/en/stable/index.html>`_ and `Redis <https://redis.io/>`_.
* For user authentication and management, the :class:`msdss_users_api:msdss_users_api.core.UsersAPI` object is used to create user management routes and dependencies.

.. digraph:: methods

   compound=true;
   rankdir=LR;
   graph [pad="0.75", nodesep="0.25", ranksep="1"];

   baseapi[label="msdss-base-api" URL="https://rrwen.github.io/msdss-base-api/" style=filled];
   basedb[label="msdss-base-database" URL="https://rrwen.github.io/msdss-base-database/" style=filled];
   usersapi[label="msdss-users-api" URL="https://rrwen.github.io/msdss-users-api/" style=filled];

   model[label="Model" shape=rect];
   modelcreate[label="ModelCreate" shape=rect];
   modelmetadataupdate[label="ModelMetadataUpdate" shape=rect];

   datamanager[label="DataManager" shape=rect];
   metadatamanager[label="MetadataManager" shape=rect];

   modelsmanager[label="ModelsManager" shape=rect];
   modelsbgmanager[label="ModelsBackgroundManager" shape=rect];
   modelsdbmanager[label="ModelsDBManager" shape=rect];
   modelsdbbgmanager[label="ModelsDBBackgroundManager" shape=rect];
   modelsmetadatamanager[label="ModelsMetadataManager" shape=rect];

   modelshandler[label="ModelsHandler" shape=rect];
   modelsbghandler[label="ModelsBackgroundHandler" shape=rect];

   getmodelsrouter[label="get_models_router" shape=rect style=rounded];

   subgraph cluster0 {
      label=< <B>msdss_models_api.core.ModelsAPI</B> >;
      style=rounded;

      subgraph cluster1 {
         label=< <B>msdss_models_api.models</B> >;
         model;
         modelcreate;
         modelmetadataupdate;
      }
      modelmetadataupdate -> getmodelsrouter[lhead=cluster1 ltail=cluster1];

      subgraph cluster2 {
         label=< <B>msdss_models_api.handlers</B> >;
         modelshandler;
         modelsbghandler;
      }
      modelshandler -> modelsmanager[lhead=cluster3 ltail=cluster2];

      subgraph cluster3 {
         label=< <B>msdss_models_api.managers</B> >;
         modelsmanager;
         modelsbgmanager;
         modelsdbmanager;
         modelsdbbgmanager;
         modelsmetadatamanager;
      }
      modelsdbbgmanager -> getmodelsrouter[lhead=cluster3 ltail=cluster3];

      subgraph cluster4 {
         label=< <B>msdss_data_api.managers</B> >;
         datamanager;
         metadatamanager;
      }
      basedb -> datamanager[lhead=cluster4 ltail=cluster4];
      datamanager -> modelsmanager[lhead=cluster3 ltail=cluster4];

      {usersapi;getmodelsrouter} -> baseapi;
   }