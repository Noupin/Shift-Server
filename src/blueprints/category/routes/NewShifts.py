#pylint: disable=C0103, C0301
"""
New endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from sqlalchemy import desc
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource

#First Party Imports
from src import db
from src.models.SQL.Shift import Shift
from src.constants import AMOUNT_OF_NEW
from src.models.Marshmallow.Shift import ShiftSchema
from src.models.Response.NewShiftsResponse import (NewShiftsResponse,
                                                       NewShiftsResponseDescription)


class NewShifts(MethodResource, Resource):

    @marshal_with(NewShiftsResponse,
                  description=NewShiftsResponseDescription)
    @doc(description="""The new shifts to display on the home page.""", tags=["Category"],
operationId="new")
    def get(self) -> dict:
        newShifts = Shift.query.order_by(desc(Shift.dateCreated)).limit(AMOUNT_OF_NEW)
        newShiftsJSON: List[ShiftSchema] = [ShiftSchema().dump(x) for x in newShifts]

        return NewShiftsResponse().dump(dict(shifts=newShiftsJSON))
