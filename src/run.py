#pylint: disable=C0103, C0301, R0903, E1101
#celery -A src.run:celery worker --pool=solo --loglevel=info
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#First Party Imports
from src import initApp, createApp, makeCelery, generateSwagger


app = initApp()
celery = makeCelery(app)
app = createApp(app)
generateSwagger()

if __name__ == '__main__':
    app.run()
