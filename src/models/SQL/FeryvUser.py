#pylint: disable=C0103, C0301
"""
The SQLQueries for a Feryv User
"""
__author__ = "Noupin"

#Third Party Imports
from sqlalchemy import text

#First Party Imports
from src import db


class FeryvUser:
    @staticmethod
    def filter_by_id(id: int):
        feryvUser = db.get_engine(bind='feryvDB').execute(text('select * from "user" where id = :id'),
                                                          {'id': id})

        return feryvUser
    
    @staticmethod
    def filter_by_username(username: str):
        feryvUser = db.get_engine(bind='feryvDB').execute(text('select * from "user" where username = :username'),
                                                          {'username': username}).first()._asdict()

        return feryvUser
