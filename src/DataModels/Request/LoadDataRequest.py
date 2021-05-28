#pylint: disable=C0103, C0301
"""
The Load Data Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from marshmallow import fields
from marshmallow.schema import Schema
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Marshmallow.BinaryFileField import BinaryFileField


class LoadDataBodyRequest(Schema):
    requestFiles = fields.List(BinaryFileField(format="binary", required=True), required=True)

@dataclass(frozen=True)
class LoadDataHeaderRequest:
    trainingDataTypes: List[str]

LoadDataBodyRequestDescription = """The files to be downloaded to the server for \
the training of the shift model."""

LoadDataHeaderRequestDescription = """A list of file types (base or mask) to \
determine which folder to save the files to. The first type does not matter \
as it is reserved for the original media."""
