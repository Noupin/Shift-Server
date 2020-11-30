#pylint: disable=C0103, C0301, I1101, R0913, R0902, R0914
"""
The functions needed to preprocess the data and make
the data usable for AI training
"""
__author__ = "Noupin"

#Third Party Imports
import os
import io
import json
import math
import base64
import random
import numpy as np
import matplotlib.image as mimg
from cv2 import cv2
from PIL import Image
#import face_recognition
import moviepy.editor

#First Party Imports
from tunable import Tunable
from constants import Constants
import utilities

import matplotlib.pyplot as plt

class Preprocess:
    """
    Hold the preprocessing functions and variabels that need preprocessed
    """

    def __init__(self):
        #Progress bar counter
        self.progress = 0

        #Create Folders For Data Storage
        utilities.checkPathExistsAndMake("userData")

        #Project Data Filepaths
        self.projectDataPath = ""
        self.maskImgPath = ""
        self.baseImgPath = ""
        self.modelPath = ""

        #Original Video Filepaths
        self.maskVidPath = ""
        self.baseVidPath = ""
        self.shiftVidPath = ""

        #Mask & Base names for saving
        self.maskName = "mask"
        self.baseName = "base"

        #Exhibit Full Frame
        self.exhibitFullFrame = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])

        #Original Mask & Base Exhibit Images
        self.originalMaskImg = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])
        self.originalBaseImg = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])

        #Default train starting image
        self.exhibitShiftImg = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])

        #Advanced train inference exhibit image
        self.exhibitMaskImg = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])
        self.exhibitBaseImg = np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], 3])

        self.alphaMap = {0: 0.3,
                         1: 0.3,
                         2: 0.3,
                         3: 0.7,
                         4: 0.7}
        self.maskColorMap = {0: (255, 0, 0),
                             1: (0, 255, 0),
                             2: (0, 0, 255),
                             3: (0, 0, 0),
                             4: (255, 255, 255)}

        self.imageBufferSize = 0
        self.imageBufferSizeRAMCheck = 0
        self.imgSize = (Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"])
        self.bufferWindow = 0
        self.totalBufferWindows = 0
        self.maxTrainableImages = 0
        self.enoughRAM = False

        self.exhibitFrameIdx = 15

    def colorAugmentation(self, img, colorCode):
        """
        Given an input image an array of augmented images are returned
        """

        img = Image.fromarray(img)
        colorImg = Image.new("RGB", (Tunable.tunableDict["imgX"],
                                     Tunable.tunableDict["imgY"]),
                                     self.maskColorMap[colorCode])
        compImage = Image.blend(img, colorImg, self.alphaMap[colorCode])

        return np.asarray(compImage).astype(np.float32)/255
    
    def flipAugmentation(self, img):
        """
        Given an image the image flipped across the y axis will be returned
        """

        return cv2.flip(img, 1)

    def audioExtract(self, vidInPath, vidType):
        """
        Given a video with an audio track the audio trakc will be saved as an mp3
        """

        clip = moviepy.editor.VideoFileClip(vidInPath)
        try:
            clip.audio.write_audiofile(os.path.join(self.projectDataPath, f"{vidType}Audio.mp3"))
        except AttributeError:
            print("The clip has no audio.")

    def saveAndPreproImgs(self, vidInPath, imgOutPath, currentNumVid, totalNumofVid, imgX, imgY):
        """
        Reads in an video and outputs the
        frames of the video as image files
        """

        fullFramesOut = os.path.join(imgOutPath, "fullFrames")
        croppedFacesOut = os.path.join(imgOutPath, "croppedFaces")
        trainingArrayOut = os.path.join(imgOutPath, "trainingArrays")

        utilities.checkPathExistsAndMake(imgOutPath, full=True)
        utilities.checkPathExistsAndMake(fullFramesOut, full=True)
        utilities.checkPathExistsAndMake(croppedFacesOut, full=True)
        utilities.checkPathExistsAndMake(trainingArrayOut, full=True)

        if imgOutPath.split("\\")[-1].find("mask") != -1:
            vidType = "mask"
        elif imgOutPath.split("\\")[-1].find("base") != -1:
            vidType = "base"

        self.audioExtract(vidInPath, vidType)

        cap = cv2.VideoCapture(vidInPath)

        Tunable.tunableDict['vidOutFPS'] = cap.get(cv2.CAP_PROP_FPS)
        utilities.changeJSON('vidOutFPS', cap.get(cv2.CAP_PROP_FPS))

        trainingImgCounter = 0
        trainableImgCounter = 0

        _, image = cap.read()
        
        self.imageBufferSizeRAMCheck - int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.imageBufferSizeRAMCheck > 0:
            self.enoughRAM = True

        for frame in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
            self.progress = ((currentNumVid-1)/totalNumofVid)+((frame/int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))*(1/totalNumofVid))

            try:
                cv2.imwrite(os.path.join(fullFramesOut, r"image{}.jpg".format(frame)), image)
            except cv2.error:
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if frame == self.exhibitFrameIdx and vidType == "base":
                self.exhibitFullFrame = image

            croppedFaces, croppedFrameCountImages = self.detectAndCropFace(image)
            for face in croppedFrameCountImages:
                imgArray = cv2.resize(face, (imgX, imgY))
                savingImg = cv2.cvtColor(imgArray.astype('float32'), cv2.COLOR_RGB2BGR)

                cv2.imwrite(os.path.join(croppedFacesOut, r"image{}.jpg".format(frame)), savingImg)

                if frame == self.exhibitFrameIdx and vidType == "base":
                    self.originalBaseImg = imgArray.astype('float32')/255.
                if frame == self.exhibitFrameIdx and vidType == "mask":
                    self.originalMaskImg = imgArray.astype('float32')/255.

            for face in croppedFaces:
                imgArray = cv2.resize(face, (imgX, imgY))
                trainingImgCounter += 1
                if trainingImgCounter == math.ceil(Tunable.tunableDict["trainingImageInterval"]*(Tunable.tunableDict["vidOutFPS"]/30)):
                    if imgArray.tolist() == np.zeros([Tunable.tunableDict["imgX"],
                                                      Tunable.tunableDict["imgY"],
                                                      Tunable.tunableDict["colorDim"]]).astype(np.uint8).tolist():
                        print("Image Not Suitable For Training.")
                        trainingImgCounter -= 1
                        continue

                    flippedImg = self.flipAugmentation(imgArray)

                    np.save(os.path.join(trainingArrayOut, r"image{}".format(trainableImgCounter)), imgArray)
                    trainableImgCounter += 1

                    np.save(os.path.join(trainingArrayOut, r"image{}".format(trainableImgCounter)), flippedImg)
                    trainableImgCounter += 1

                    for _ in range(len(self.maskColorMap)):
                        np.save(os.path.join(trainingArrayOut,
                                             r"image{}".format(trainableImgCounter)),
                                self.colorAugmentation(imgArray, _))
                        trainableImgCounter += 1

                        np.save(os.path.join(trainingArrayOut,
                                             r"image{}".format(trainableImgCounter)),
                                self.colorAugmentation(flippedImg, _))
                        trainableImgCounter += 1
                    trainingImgCounter = 0
                    if trainableImgCounter > self.maxTrainableImages:
                        self.maxTrainableImages = trainableImgCounter

            _, image = cap.read()
        
        print("Total Trainable Images:", self.maxTrainableImages)
        if math.ceil(self.maxTrainableImages/self.imageBufferSize) > self.totalBufferWindows:
            self.totalBufferWindows = math.ceil(self.maxTrainableImages/self.imageBufferSize)
        print("Total Buffer Windows:", self.totalBufferWindows)
    
    def bufferImages(self, folderPath, window):
        print("Image Buffer Size:", self.imageBufferSize)

        bufferedImages = []
        folderImages = os.listdir(folderPath)
        folderImages.sort(key=utilities.natural_keys)

        print("Max Trainable Images:", self.maxTrainableImages)
        if math.ceil(self.maxTrainableImages/self.imageBufferSize) > self.totalBufferWindows:
            self.totalBufferWindows = math.ceil(self.maxTrainableImages/self.imageBufferSize)
        print("Total Buffer Windows:", self.totalBufferWindows)

        try:
            for arr in range(window*self.imageBufferSize, (window*self.imageBufferSize)+self.imageBufferSize):
                bufferedImages.append(np.load(os.path.join(folderPath, f"image{arr}.npy")))
        except FileNotFoundError:
            if not bufferedImages:
                return None

        random.shuffle(bufferedImages)

        #Reshape into tensor for training
        bufferedImages = np.array(bufferedImages).reshape(-1, bufferedImages[0].shape[0], bufferedImages[0].shape[1], 3)
        #Normalize data to base 1.0 for training
        bufferedImages = bufferedImages.astype('float32') / 255.

        return bufferedImages

    def preproImgs(self, imgInPath):
        """
        Reads exhibit images for the front-end and sets shifted video FPS
        """

        if imgInPath.split("\\")[-1].find("mask") != -1:
            self.originalMaskImg = cv2.cvtColor(cv2.imread(os.path.join(imgInPath,
                                                           "croppedFaces",
                                                           f"image{self.exhibitFrameIdx}.jpg")),
                                                cv2.COLOR_BGR2RGB).astype('float32')/255.
        elif imgInPath.split("\\")[-1].find("base") != -1:
            self.exhibitFullFrame = cv2.cvtColor(cv2.imread(os.path.join(imgInPath,
                                                                         "fullFrames",
                                                                         f"image{self.exhibitFrameIdx}.jpg")),
                                                 cv2.COLOR_BGR2RGB)
            #self.exhibitFullFrame = np.load(os.path.join(imgInPath, "fullFrameArrays", f"image{self.exhibitFrameIdx}.npy"))
            self.originalBaseImg = cv2.cvtColor(cv2.imread(os.path.join(imgInPath,
                                                           "croppedFaces",
                                                           f"image{self.exhibitFrameIdx}.jpg")),
                                                cv2.COLOR_BGR2RGB).astype('float32')/255.

        with open(os.path.join(self.projectDataPath, "data.json")) as jsonFile:
            projectInfoDict = json.load(jsonFile)

        Tunable.tunableDict["vidOutFPS"] = projectInfoDict["vidFPS"]
        utilities.changeJSON("vidOutFPS", projectInfoDict["vidFPS"])

        self.maxTrainableImages = projectInfoDict["maxTrainableImages"]
        print("Total Trainable Images:", self.maxTrainableImages)
        print("Image Buffer Size:", self.imageBufferSize)
        if math.ceil(self.maxTrainableImages/self.imageBufferSize) > self.totalBufferWindows:
            self.totalBufferWindows = math.ceil(self.maxTrainableImages/self.imageBufferSize)
        print("Total Buffer Windows:", self.totalBufferWindows)

    def detectAndCropFace(self, ogImg):
        """
        Given an input image the cropped image with the face will be returned
        """

        face_locations = face_recognition.face_locations(ogImg, number_of_times_to_upsample=0, model="cnn")

        faces = []
        orderedFaces = []
        frameCountFaces = []

        for face_location in face_locations:
            top, right, bottom, left = face_location
            #Pad the image to have the whole face
            faces.append(ogImg[int(top*1):int(bottom*1), int(left*1):int(right*1)])

        if len(faces) > 0:
            orderedFaces.append(ogImg[int(top*1):int(bottom*1), int(left*1):int(right*1)])
            frameCountFaces.append(ogImg[int(top*1):int(bottom*1), int(left*1):int(right*1)])

        if len(faces) == 0:
            frameCountFaces.append(np.zeros([Tunable.tunableDict["imgX"], Tunable.tunableDict["imgY"], Tunable.tunableDict["colorDim"]]))

        return orderedFaces, frameCountFaces

    def shiftFace(self, ogFrame, shiftedFace):
        """
        Given a frame and the shifted face this wil return the face overlayed on the original frame
        """

        shiftedImg = ogFrame.copy()

        shiftedFace = shiftedFace*255.
        shiftedFace = shiftedFace.astype(np.uint8)

        #Load face calssifier
        face_locations = face_recognition.face_locations(ogFrame, number_of_times_to_upsample=0, model="cnn")

        faces = []

        for face_location in face_locations:
            top, right, bottom, left = face_location
            faces.append(ogFrame[int(top*1):int(bottom*1), int(left*1):int(right*1)])

        if len(faces) > 0:
            shiftedFace = cv2.resize(shiftedFace, (int(right*1)-int(left*1), int(bottom*1)-int(top*1)))
            newFace = self.maskFace(shiftedFace, shiftedImg[int(top*1):int(bottom*1), int(left*1):int(right*1)])
            shiftedImg[int(top*1):int(bottom*1), int(left*1):int(right*1)] = newFace

        shiftedImg = np.array(shiftedImg)
        shiftedImg = shiftedImg.astype('float32') / 255.
        return shiftedImg
    
    def combineAudioVideo(self, videoPath):
        """
        Given an audio array and a video output path the audio will be combined with that video
        """

        videoclip = moviepy.editor.VideoFileClip(os.path.join(videoPath, "output.mp4"))
        try:
            audioclip = moviepy.editor.AudioFileClip(os.path.join(videoPath, "baseAudio.mp3"))
        except IOError:
            videoclip.write_videofile(os.path.join(videoPath, "shifted.mp4"), fps=Tunable.tunableDict["vidOutFPS"])
            return

        shiftedvideo = videoclip.set_audio(audioclip)
        shiftedvideo.write_videofile(os.path.join(videoPath, "shifted.mp4"), fps=Tunable.tunableDict["vidOutFPS"])

    def imgs2vid(self, arrayInPath, vidOutPath, shiftVars):
        """
        Given a path with all of the image arrays a .mp4 video will be exported
        """

        utilities.checkPathExistsAndMake(vidOutPath, full=True)
        orderedFacePath = os.path.join(arrayInPath, "croppedFaces")
        fullFramePath = os.path.join(arrayInPath, "fullFrames")

        height, width, _ = cv2.imread(os.path.join(fullFramePath, f"image{self.exhibitFrameIdx}.jpg")).shape

        print("Started Vid Compilation.")

        #height, width, _ = imgList[0].shape
        codec = cv2.VideoWriter_fourcc(*'MP4A')#H264, X264, MP42, MP4A
        videoOut = cv2.VideoWriter(os.path.join(vidOutPath, "output.mp4"),
                                   codec,
                                   Tunable.tunableDict["vidOutFPS"],
                                   (width, height))

        progressCounter = 0
        imgNames = os.listdir(fullFramePath)
        imgNames.sort(key=utilities.natural_keys)

        for imgNum in range(len(imgNames)):
            self.progress = (progressCounter/len(imgNames))
            progressCounter += 1

            img = cv2.cvtColor(cv2.imread(os.path.join(fullFramePath, f"image{imgNum}.jpg")), cv2.COLOR_BGR2RGB)
            faceImg = cv2.cvtColor(cv2.imread(os.path.join(orderedFacePath,
                                                           f"image{imgNum}.jpg")),
                                   cv2.COLOR_BGR2RGB).astype(np.float32)/255.
            img = self.shiftFace(img, shiftVars.AEMask.predict(faceImg))

            denormalized = img * 255.
            denormalized = denormalized.astype(np.uint8) #Use plt to test uint wihtout a number and uint32
            bgrImg = cv2.cvtColor(denormalized, cv2.COLOR_BGR2RGB)
            videoOut.write(bgrImg)

        videoOut.release()
        cv2.destroyAllWindows()
        del videoOut

        self.combineAudioVideo(vidOutPath)

        print("Vid Compiled.")

    def encodeRawImage(self, imgArr):
        """
        Takes in an image array then encodes it as a
        bytestring to be streamed through JSON to JavaScript
        """

        resize = cv2.resize(imgArr, (1024, 1024))
        resize = resize*255.
        img = resize.astype(np.uint8)
        img = Image.fromarray(img).convert("RGB")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        imgEnc = img_str.decode('utf-8')
        return imgEnc

    def maskFace(self, mask, base):
        """
        Given a mask and a base image the mask will be applied to the image
        """

        gray = cv2.cvtColor(base, cv2.COLOR_RGB2GRAY)

        _, thresh = cv2.threshold(gray,
                                  0, 255,
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = np.ones((3, 3), np.uint8)
        closing = cv2.morphologyEx(thresh,
                                   cv2.MORPH_CLOSE,
                                   kernel,
                                   iterations=2)

        dist_transform = cv2.distanceTransform(closing, cv2.DIST_L2, 0)
        _, fg = cv2.threshold(dist_transform,
                              0.2 * dist_transform.max(),
                              255, 0)

        fg = fg.astype(np.uint8)
        bg = cv2.bitwise_not(fg)

        base = cv2.bitwise_and(base, base, mask=fg)
        mask = cv2.bitwise_and(mask, mask, mask=bg)


        final = cv2.add(mask, base)

        return final
