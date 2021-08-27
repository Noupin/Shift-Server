#pylint: disable=C0103, C0301
"""
The SQLQueries for a Feryv User
"""
__author__ = "Noupin"

#Third Party Imports
from sqlalchemy import text

#First Party Imports
from src import feryvDB
from FeryvOAuthUser import FeryvUserSchema


class FeryvUser:

    @staticmethod
    def filterById(id: int):
        feryvUser = feryvDB.db.execute(
            text('select * from "user" where id = :id'),
            {'id': id}
        ).first()

        if not feryvUser:
            return {}

        userLicenses = feryvDB.db.execute(
            text('select * from "license" where "userId" = :userId'),
            {'userId': feryvUser.id}
        ).all()

        feryvDict = feryvUser._asdict()
        feryvDict['licenses'] = userLicenses
        feryvSchema = FeryvUserSchema().load(feryvDict, unknown='exclude')

        del feryvUser, userLicenses
        return feryvSchema


    @staticmethod
    def filterByUsername(username: str):
        feryvUser = feryvDB.db.execute(
            text('select * from "user" where username = :username'),
            {'username': username}
        ).first()
        
        if not feryvUser:
            return {}

        userLicenses = feryvDB.db.execute(
            text('select * from "license" where "userId" = :userId'),
            {'userId': feryvUser.id}
        ).all()

        feryvDict = feryvUser._asdict()
        feryvDict['licenses'] = userLicenses
        feryvSchema = FeryvUserSchema().load(feryvDict, unknown='exclude')

        del feryvUser, userLicenses
        return feryvSchema
