from celery import Celery

from .managers import ModelsManager

# 'amqp://msdss:msdss123@localhost:5672//'
app = Celery()
models_manager = ModelsManager()

@app.task
def input_model(name, data, settings):
    models_manager.input(name, data, **settings)

@app.task
def load_model(name, settings):
    models_manager.load(name, **settings)

@app.task
def update_model(name, data, settings):
    models_manager.output(name, data, **settings)

# app.Worker.start()
# https://docs.celeryproject.org/en/stable/reference/celery.apps.worker.html#celery.apps.worker.Worker