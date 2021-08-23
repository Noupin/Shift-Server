#pylint: disable=C0103, C0301
"""
The SQLQueries for a Feryv User
"""
__author__ = "Noupin"

#Third Party Imports
from sqlalchemy import text

#First Party Imports
from src import db
from FeryvOAuthUser import FeryvUserSchema


class FeryvUser:
    @staticmethod
    def filterById(id: int):
        feryvUser = db.get_engine(bind='feryvDB').execute(
            text('select * from "user" where id = :id'),
            {'id': id}
        ).first()

        if not feryvUser:
            return {}

        userLicenses = db.get_engine(bind='feryvDB').execute(
            text('select * from "license" where "userId" = :userId'),
            {'userId': feryvUser.id}
        ).all()

        feryvDict = feryvUser._asdict()
        feryvDict['licenses'] = userLicenses
        feryvSchema = FeryvUserSchema().load(feryvDict, unknown='exclude')

        return feryvSchema


    @staticmethod
    def filterByUsername(username: str):
        feryvUser = db.get_engine(bind='feryvDB').execute(
            text('select * from "user" where username = :username'),
            {'username': username}
        ).first()
        
        if not feryvUser:
            return {}

        userLicenses = db.get_engine(bind='feryvDB').execute(
            text('select * from "license" where "userId" = :userId'),
            {'userId': feryvUser.id}
        ).all()

        feryvDict = feryvUser._asdict()
        feryvDict['licenses'] = userLicenses
        feryvSchema = FeryvUserSchema().load(feryvDict, unknown='exclude')

        return feryvSchema
