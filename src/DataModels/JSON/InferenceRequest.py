#pylint: disable=C0103, C0301
"""
The Inference Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import bson


class InferenceRequest:
    shiftUUID: str
    usePTM: bool
    prebuiltShiftModel: str

    def __init__(self, shiftUUID, usePTM, prebuiltShiftModel):
        self.shiftUUID = shiftUUID
        self.usePTM = usePTM
        self.prebuiltShiftModel = prebuiltShiftModel

    def __repr__(self) -> str:
        return f"TrainRequest(shiftUUID: {self.shiftUUID}, usePTM: {self.usePTM}, prebuiltShiftModel: {self.prebuiltShiftModel})"
