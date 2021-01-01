#pylint: disable=C0103, C0301
"""
The Inference Request Data Model for the Shift API
"""
__author__ = "Noupin"


class InferenceRequest:
    uuid: str
    usePTM: bool
    prebuiltShiftModel: str

    def __init__(self, uuid, usePTM, prebuiltShiftModel):
        self.uuid = uuid
        self.usePTM = usePTM
        self.prebuiltShiftModel = prebuiltShiftModel
