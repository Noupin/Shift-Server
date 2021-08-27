#pylint: disable=C0103, C0301, R0903, E1101
#celery -A src.run:celery worker --pool=solo --loglevel=info
#flask run --host=0.0.0.0 --port="PORT"

#turn RabbitMQ off then on, then remove celery collection from
#SQL Alchemy & "celery amqp queue.delete queue1" finally, "celery purge"

#Kill NGinx taskkill /f /IM nginx.exe
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import os

#First Party Imports
from src.constants import URL_PREFIX
from src.utils.swagger import swaggerToYAML
from src.middleware.URLPrefix import URLPrefixMiddleware
from src import initApp, createApp, makeCelery, generateSwagger, addMiddleware


app = initApp()
celery = makeCelery(app)
app = createApp(app)
addMiddleware(app, middleware=URLPrefixMiddleware, prefix=URL_PREFIX)
docs = generateSwagger()
swaggerToYAML(docs.spec, filename="shift.yaml", path=os.path.join(os.getcwd(), os.pardir))

if __name__ == '__main__':
    app.run()
