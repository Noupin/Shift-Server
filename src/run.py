#pylint: disable=C0103, C0301, R0903, E1101
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#First Party Imports
from . import createApp


app = createApp()

if __name__ == '__main__':
    app.run()
