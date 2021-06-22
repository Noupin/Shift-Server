#pylint: disable=C0103, C0301, R0903, E1101
#celery -A src.run:celery worker --pool=solo --loglevel=info
#flask run --host=0.0.0.0 --port="PORT"

#turn RabbitMQ off then on, then remove celery collection from
#MongoDB & "celery amqp queue.delete queue1" finally, "celery purge"
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#First Party Imports
from src.utils.swagger import swaggerToYAML
from src import initApp, createApp, makeCelery, generateSwagger, addMiddleware


app = initApp()
celery = makeCelery(app)
app = createApp(app)
app = addMiddleware(app)
docs = generateSwagger()
swaggerToYAML(docs.spec)

if __name__ == '__main__':
    app.run()
