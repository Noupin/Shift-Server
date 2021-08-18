#pylint: disable=C0103, C0301
"""
Shift Category endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

#First Party Imports
from src.constants import ITEMS_PER_PAGE
from src.models.SQL.ShiftCategory import ShiftCategory as ShiftCategoryModel
from src.models.Request.CategoriesRequest import (CategoriesRequest,
                                                      CategoryRequestDescription)
from src.models.Response.CategoriesResponse import (CategoriesResponse,
                                                        categoriesResponseDescription)


class Categories(MethodResource, Resource):

    @use_kwargs(CategoriesRequest.Schema(), location='query',
                description=CategoryRequestDescription)
    @marshal_with(CategoriesResponse,
                  description=categoriesResponseDescription)
    @doc(description="""The shifts for the queried category to display on the \
home page.""", tags=["Category"], operationId="Categories")
    def get(self, queryParams: CategoriesRequest) -> dict:
        categories: List[ShiftCategoryModel] = ShiftCategoryModel.query.paginate(queryParams.page, ITEMS_PER_PAGE).items
        categoryNames: List[str] = [x.category_name for x in categories]

        return CategoriesResponse().dump(dict(categories=categoryNames))
