#pylint: disable=C0103, C0301, R0903, E1101
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#First Party Imports
from src import createApp
from src.celeryApp import cel


if __name__ == 'src.run':
    app = createApp(celery=cel)
    app.run()
