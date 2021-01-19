#celery -A src.kel.celery worker --pool=solo --loglevel=info
from src import createApp
from src.celeryApp import cel
from src.utils.celeryHelpers import init_celery


celery = cel
app = createApp()
init_celery(app, celery)
