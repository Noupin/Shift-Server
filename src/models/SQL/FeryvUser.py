#pylint: disable=C0103, C0301
"""
The SQLQueries for a Feryv User
"""
__author__ = "Noupin"

#First Party Imports
from src import db


class FeryvUser:
    @staticmethod
    def filter_by(**kwargs):
        key, value = kwargs.items()[0]
        feryvUser = db.session.execute('select * from public."user" where :key = :value',
                                       {'key': key, 'value': value},
                                       bind='feryvDB')
        
        return feryvUser
