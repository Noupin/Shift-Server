#pylint: disable=C0103, C0301, R0903, E1101
"""
Deals with commits and rollbacks of SQLAlchemy.
"""
__author__ = "Noupin"

#Third Party Imports
from sqlalchemy.exc import DatabaseError

#First Party Imports
from src import db


def commitOrRollback(response):
    """
    Trys to commit changes if in the DB_SESSION_PATHS.
    If an error occurs then the session is rolled back.
    """

    try:
        db.session.commit()
    except DatabaseError:
        db.session.rollback()

    return response
