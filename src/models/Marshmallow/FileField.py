#pylint: disable=C0103, C0301
"""
The Marshmallow File Field for a shift
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields
from src.config import marshmallowPlugin

@marshmallowPlugin.map_to_openapi_type('file', None)
class FileField(fields.Raw):
    pass
