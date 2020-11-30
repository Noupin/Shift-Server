#pylint: disable=C0103, C0301
"""
Finds open port can creates a data server to pass between front-end and backend
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
import flask
import flask_cors
import numpy as np

#First Party Imports
from constants import Constants
from preprocess import Preprocess
from tunable import Tunable
from shift import Shift
import utilities


#Port serving variables
portOpen = False
port = 3000

#Picking open port
while not portOpen and port <= 9999:
    portOpen = utilities.checkPortOpen(port)
    if not portOpen:
        port += 1

#Save port to json for IPC
utilities.changeJSON('port', port)

#External variables
shiftVars = Shift()
preproVars = Preprocess()

#Create app
app = flask.Flask("Shift")
cors = flask_cors.CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

@app.route('/load', methods=["GET", "POST"])
def load():
    """
    Server sided calls for the load page of the Shift GUI
    """

    if flask.request.method == "POST":
        apiIn = flask.request.get_json()

        preproVars.exhibitShiftImg = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])
        preproVars.exhibitMaskImg = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])
        preproVars.exhibitBaseImg = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])

        preproVars.maskName = apiIn["maskName"][:apiIn["maskName"].find('.')]
        preproVars.maskPath = apiIn["maskPath"][8:].replace('%20', ' ')

        preproVars.baseName = apiIn["baseName"][:apiIn["baseName"].find('.')]
        preproVars.basePath = apiIn["basePath"][8:].replace('%20', ' ')

        makeOrLoad = apiIn["makeOrLoad"]
        modelID = apiIn["modelID"]


        print(f"\nMask Name: {preproVars.maskName}\nBase Name: {preproVars.baseName}")
        preproVars.projectDataPath = os.path.join(Constants.userDataPath,
                                                  f"{preproVars.maskName}-shift-{preproVars.baseName}")
        #Project data path
        utilities.checkPathExistsAndMake(preproVars.projectDataPath, full=True)

        #Project model path
        preproVars.modelPath = os.path.join(preproVars.projectDataPath, "models")
        utilities.checkPathExistsAndMake(preproVars.modelPath, full=True)

        #Project mask and base images paths
        preproVars.maskImgPath = os.path.join(preproVars.projectDataPath, "maskImages")
        utilities.checkPathExistsAndMake(preproVars.maskImgPath, full=True)

        preproVars.baseImgPath = os.path.join(preproVars.projectDataPath, "baseImages")
        utilities.checkPathExistsAndMake(preproVars.baseImgPath, full=True)

        if makeOrLoad == 0:
            print("Creating & Loading Data.")
            preproVars.imageBufferSize = utilities.getImageMemBufferSize([preproVars.imgSize, preproVars.imgSize])
            preproVars.imageBufferSizeRAMCheck = preproVars.imageBufferSize

            preproVars.saveAndPreproImgs(preproVars.maskPath,
                                         preproVars.maskImgPath,
                                         1, 2,
                                         Tunable.tunableDict["imgX"],
                                         Tunable.tunableDict["imgY"])
            preproVars.saveAndPreproImgs(preproVars.basePath,
                                         preproVars.baseImgPath,
                                         2, 2,
                                         Tunable.tunableDict["imgX"],
                                         Tunable.tunableDict["imgY"])
            with open(os.path.join(preproVars.projectDataPath, "data.json"), 'w') as jsonFile:
                json.dump({"maskName": preproVars.maskName,
                           "baseName": preproVars.baseName,
                           "maskPath": preproVars.maskPath,
                           "basePath": preproVars.basePath,
                           "vidFPS": Tunable.tunableDict["vidOutFPS"],
                           "maxTrainableImages": preproVars.maxTrainableImages,
                           "audioPath": preproVars.projectDataPath}, jsonFile)

        elif makeOrLoad == 1:
            print("Loading Data.")
            preproVars.imageBufferSize = utilities.getImageMemBufferSize([preproVars.imgSize, preproVars.imgSize])
            preproVars.imageBufferSizeRAMCheck = preproVars.imageBufferSize

            preproVars.preproImgs(preproVars.maskImgPath)
            preproVars.preproImgs(preproVars.baseImgPath)

            shiftVars.Enc.load(preproVars.modelPath, f"{preproVars.maskName}-{preproVars.baseName}")
            shiftVars.DecMask.load(preproVars.modelPath, f"{preproVars.maskName}")
            shiftVars.DecBase.load(preproVars.modelPath, f"{preproVars.baseName}")

            shiftVars.updateAEMask(shiftVars.Enc.model, shiftVars.DecMask.model)
            shiftVars.updateAEBase(shiftVars.Enc.model, shiftVars.DecBase.model)

        preproVars.progress = 100
        return json.dumps("Success. Got Paths")

    #Else
    return json.dumps(preproVars.progress)

@app.route('/train', methods=["GET", "POST"])
def train():
    """
    Server sided calls for the train page of the Shift GUI
    """

    preproVars.progress = 0

    if flask.request.method == "POST":
        apiIn = flask.request.get_json()

        shiftVars.stopTrain = apiIn["stopTrain"]
        convertToVid = apiIn["convertToVid"]

        preproVars.progress = 0

        if shiftVars.stopTrain == 0:
            print("Got POST Saving Models.")
            shiftVars.Enc.save(preproVars.modelPath, f"{preproVars.maskName}-{preproVars.baseName}")
            shiftVars.DecMask.save(preproVars.modelPath, f"{preproVars.maskName}")
            shiftVars.DecBase.save(preproVars.modelPath, f"{preproVars.baseName}")

        if convertToVid == 1:
            print("Got POST Convert To Video.")

            preproVars.imgs2vid(preproVars.baseImgPath, preproVars.projectDataPath, shiftVars)
            preproVars.progress = 100

            return apiIn

        while shiftVars.stopTrain != 0:
            print("Training.")
            shiftVars.train(preproVars)
            shiftVars.updateModels()

            predictedImg = shiftVars.AEMask.predict(preproVars.originalBaseImg)
            preproVars.exhibitShiftImg = preproVars.shiftFace(preproVars.exhibitFullFrame, predictedImg)


        return json.dumps("Training Finished.")

    return json.dumps([preproVars.encodeRawImage(preproVars.exhibitShiftImg), preproVars.progress])

@app.route('/advTrain', methods=["GET", "POST"])
def advTrain():
    """
    Server sided calls for the advanced train page of the Shift GUI
    """

    preproVars.progress = 0

    if flask.request.method == "POST":
        apiIn = flask.request.get_json()

        shiftVars.stopTrain = apiIn["stopTrain"]
        convertToVid = apiIn["convertToVid"]

        preproVars.progress = 0

        if shiftVars.stopTrain == 0:
            print("Got POST Saving Models.")
            shiftVars.Enc.save(preproVars.modelPath, f"{preproVars.maskName}-{preproVars.baseName}")
            shiftVars.DecMask.save(preproVars.modelPath, f"{preproVars.maskName}")
            shiftVars.DecBase.save(preproVars.modelPath, f"{preproVars.baseName}")

        if convertToVid == 1:
            print("Got POST Converting To Video.")

            preproVars.imgs2vid(preproVars.baseImgPath, preproVars.projectDataPath, shiftVars)
            preproVars.progress = 100

            return json.dumps('Success. Video Compiled.')

        while shiftVars.stopTrain != 0:
            print("Training.")
            shiftVars.train(preproVars)
            shiftVars.updateModels()

            preproVars.exhibitMaskImg = shiftVars.AEMask.predict(preproVars.originalMaskImg)
            preproVars.exhibitBaseImg = shiftVars.AEBase.predict(preproVars.originalBaseImg)

            shiftPredictedImg = shiftVars.AEMask.predict(preproVars.originalBaseImg)
            preproVars.exhibitShiftImg = preproVars.shiftFace(preproVars.exhibitFullFrame, shiftPredictedImg)

        return json.dumps('Success. Trained.')

    return json.dumps([preproVars.encodeRawImage(preproVars.exhibitMaskImg),
                       preproVars.encodeRawImage(preproVars.originalMaskImg),
                       preproVars.encodeRawImage(preproVars.exhibitBaseImg),
                       preproVars.encodeRawImage(preproVars.originalBaseImg),
                       preproVars.encodeRawImage(preproVars.exhibitShiftImg),
                       preproVars.progress])

@app.route('/view', methods=["GET"])
def view():
    """
    Server sided calls for the view page of the Shift GUI
    """

    if flask.request.method == "GET":
        return json.dumps([preproVars.maskPath, preproVars.basePath, preproVars.projectDataPath])

    return "No Data Transfer."


#Run server
app.run(port=port)
