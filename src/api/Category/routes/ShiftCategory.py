#pylint: disable=C0103, C0301
"""
Shift Category endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from src.DataModels.Marshmallow.Shift import ShiftSchema

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.MongoDB.ShiftCategory import ShiftCategory as ShiftCategoryModel
from src.DataModels.Response.ShiftCategoryResponse import (ShiftCategoryResponse,
                                                           ShiftCategoryResponseDescription)


class ShiftCategory(MethodResource, Resource):

    @marshal_with(ShiftCategoryResponse,
                  description=ShiftCategoryResponseDescription)
    @doc(description="""The shifts for the queried category to display on the \
home page.""", tags=["Category"], operationId="Category")
    def get(self, categoryName: str) -> dict:
        category: ShiftCategoryModel = ShiftCategoryModel.objects(name=categoryName).first()
        categoryShifts = []

        if not category:
            return ShiftCategoryResponse().load(dict(shifts=categoryShifts))

        for shift in category.shifts:
            try:
                shift = Shift.objects(uuid=shift.uuid).first()
                categoryShifts.append(ShiftSchema().dump(shift))
            except AttributeError:
                category.update(pull__shifts=shift)

        return ShiftCategoryResponse().load(dict(shifts=categoryShifts))
