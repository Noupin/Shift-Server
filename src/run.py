#pylint: disable=C0103, C0301, R0903, E1101
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#First Party Imports
from . import createApp
from .ServerData import ServerData

app = createApp()

if __name__ == '__main__':
    app.run(debug=True, port=ServerData.port)
