#pylint: disable=C0103, C0301
"""
Shift Category endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource

#First Party Imports
from src.DataModels.MongoDB.ShiftCategory import ShiftCategory as ShiftCategoryModel
from src.DataModels.Response.CategoriesResponse import (CategoriesResponse,
                                                        categoriesResponseDescription)


class Categories(MethodResource, Resource):

    @marshal_with(CategoriesResponse,
                  description=categoriesResponseDescription)
    @doc(description="""The shifts for the queried category to display on the \
home page.""", tags=["Category"], operationId="Categories")
    def get(self, maximum: int) -> dict:
        categories: ShiftCategoryModel = ShiftCategoryModel.objects()
        categoryNames: List[str] = []

        for index, category in enumerate(categories):
            if index == maximum:
                break
            categoryNames.append(category.name)

        return CategoriesResponse().dump(dict(categories=categoryNames))
