#pylint: disable=C0103, C0301, R0903, E1101
"""
Runs the server for Shift
"""
__author__ = "Noupin"

#First Party Imports
from src import createApp


#print("\n\n", __name__, "\n\n")
print("App Running")
app = createApp()

if __name__ == '__main__':
    app.run()
