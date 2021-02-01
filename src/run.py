#pylint: disable=C0103, C0301, R0903, E1101
#celery -A src.run:celery worker --pool=solo --loglevel=info
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#First Party Imports
from src import initApp, createApp, makeCelery


#print("\n\n", __name__, "\n\n")
app = initApp()
celery = makeCelery(app)
app = createApp(app)

if __name__ == '__main__':
    print("App Running")
    app.run()
