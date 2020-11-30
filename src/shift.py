#pylint: disable=C0103, C0301, R0902
"""
The master file for the Shift application
"""
__author__ = "Noupin"

#Third Party Imports
import os

#First Party Imports
import utilities
from tunable import Tunable
from autoencoder import AE
from encoder import Encoder
from decoder import Decoder


class Shift:
    """
    Master class for Shift
    """

    def __init__(self):
        self.stopTrain = 0

        utilities.memoryGrowth()

        self.Enc = Encoder()

        self.DecMask = Decoder()
        self.AEMask = AE(self.Enc.model, self.DecMask.model)


        self.DecBase = Decoder()
        self.AEBase = AE(self.Enc.model, self.DecBase.model)

        self.modMask = self.AEMask.model
        self.modBase = self.AEBase.model

    def updateModels(self):
        """
        Update the autoencoders models
        """

        self.modMask = self.AEMask.model
        self.modBase = self.AEBase.model

    def updateAEMask(self, encModel, decModel):
        """
        Update the masks autoencoder object
        """

        self.AEMask = AE(encModel, decModel)

    def updateAEBase(self, encModel, decModel):
        """
        Update the bases autoencoder object
        """

        self.AEBase = AE(encModel, decModel)
    
    def train(self, preproVars):
        """
        A shuffled train for the Autoencoders
        """

        maskTrainingFolder = os.path.join(preproVars.maskImgPath, "trainingArrays")
        baseTrainingFolder = os.path.join(preproVars.baseImgPath, "trainingArrays")

        for window in range(preproVars.totalBufferWindows):
            maskTrain = True
            baseTrain = True

            print(f"\n\nWindow: {window+1}/{preproVars.totalBufferWindows}")
            maskTrainingData = preproVars.bufferImages(maskTrainingFolder, preproVars.bufferWindow)
            if maskTrainingData is None:
                maskTrain = False
            print("Mask: ")
            if maskTrain:
                self.AEMask.train(maskTrainingData[:-1], maskTrainingData[-1:], Tunable.tunableDict["epochs"])
            if not preproVars.enoughRAM:
                del maskTrainingData
            
            print(f"Window: {window+1}/{preproVars.totalBufferWindows}")
            baseTrainingData = preproVars.bufferImages(baseTrainingFolder, preproVars.bufferWindow)
            if baseTrainingData is None:
                baseTrain = False
            print("Base: ")
            if baseTrain:
                self.AEBase.train(baseTrainingData[:-1], baseTrainingData[-1:], Tunable.tunableDict["epochs"])
            if not preproVars.enoughRAM:
                del trainingData

            preproVars.bufferWindow += 1
        preproVars.bufferWindow = 0
