#pylint: disable=C0103, C0301, R0903, E1101
#celery -A src.run:celery worker --pool=solo --loglevel=info

#turn RabbitMQ off then on, then remove celery collection from
#MongoDB & "celery amqp queue.delete queue1" finally, "celery purge"
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#First Party Imports
from src.utils.swagger import swaggerToYAML, swaggerToJSON
from src import initApp, createApp, makeCelery, generateSwagger


app = initApp()
celery = makeCelery(app)
app = createApp(app)
docs = generateSwagger()
swaggerToJSON(docs.spec)

if __name__ == '__main__':
    app.run()
