# -*- coding: utf-8 -*-
"""
Final application to distribute our model to other researchers.
Notes on use can be found in accompanying README.

@author: [redacted as required by submission guidelines]
"""

###IMPORTANT
#Code is presently broken due to an issue loading models via the Roboflow
#python package. We hope to push an update on or close to 16 July 2024


#####DEBUG Mode
#Used by developer to load in API keys faster when testing model
#When debug=True, pressing the buttons to load API keys will autofill the fields
#with the values kept here
#API keys have been included for submission of this code for review.
#At this time, we are still examining ways to share this code 
apikey1 = "mlPRHB1dT9IoYe2dnziD"
apikey2 = "g5v0jZU6GVF1lPc3atH8"
debug=True



import tkinter as tk
from tkinter import ttk, filedialog
import roboflow

import os
import cv2
import pandas as pd


#Function utilized in run method to perpetually resize files until they no longer
#throw 'file too big' exceptions
#TODO - return to handle where images are saved (i.e. don't drop resizes in
#    the base folder where they can mess with future runs)
def resizeUntilPredict(model, file, cvImg, filePath, initial):
    #count number of resize steps and track current image filename
    #file gets assigned to a new variable to make renaming steps more simple
    rs=0
    fname=file
    print(fname)
    print(model)
    resized = cvImg
    
    #repeat until it works
    while True:
        try:
            #attempt to predict with current file
            predictions = model.predict(fname)
        except Exception as e: 
            print(repr(e))
            #Assume exception is due to file size error and resize it
            #Generally, only errors we get are file size or lack of API Credits
            
            #rename file as to not overwrite original and to keep trail of
            #   resized images
            
            while True:
                import time
                time.sleep(9999)
            
            if initial:
                #initial resize step shouldn't save images to same folder as
                #    parent image, because that would cause them to be called
                #    as a starting image in future runs
                fname = filePath + "/Initial_Resize/" + \
                    file.strip(".JPG")+"_rs"+str(rs)+".JPG"
            else:
                fname = file.strip(".JPG")+"_rs"+str(rs)+".JPG"
            #resizes to 81% of the area of the previous resize (loses 10% off
            #   each dimension)
            resized = cv2.resize(cvImg, (0,0), fx=0.9, fy=0.9, interpolation=cv2.INTER_AREA)
            cv2.imwrite(fname, resized)
            
            #iterate resize counter
            rs+=1
        else:
            #no exceptions, successful prediction, end loop
            break
    
    return [predictions, rs, resized]

class App():
    def __init__(self):
        #initialize app with name, dimensions, and formatting
        self.root = tk.Tk()
        self.root.geometry('900x600')
        self.root.title('Dolphin Lesion Detection App')
        self.mainframe = tk.Frame(self.root)
        self.mainframe.pack(fill='both', expand=True)
        
        #define variables to hold api keys/certificate info?
        self.apiKey = ''
        self.apiKey2 = ''
        
        #display currently loaded api keys for validation
        apiDisplay = 'Current API Key Is: '
        self.apiDisplayText = ttk.Label(self.mainframe, text=apiDisplay)
        self.apiDisplayText.grid(row=1, column=0)
        
        apiDisplay2 = 'Current API Key 2 Is: '
        self.apiDisplayText2 = ttk.Label(self.mainframe, text=apiDisplay2)
        self.apiDisplayText2.grid(row=1, column=1)
        
        #initialize input fields for api keys/cert info
        self.apiPromptText = ttk.Label(self.mainframe, text='Input API Key:')
        self.apiPromptText.grid(row=0, column=0, sticky='E')
        self.apiKeyField = ttk.Entry(self.mainframe)
        self.apiKeyField.grid(row=0, column=1, sticky='NWSE')
        setAPIKeyButton = ttk.Button(self.mainframe, text="Set New API Key", command=lambda:self.apiUpdate(1))
        setAPIKeyButton.grid(row=0, column=2)
        
        self.apiPromptText2 = ttk.Label(self.mainframe, text='Input API Key 2:')
        self.apiPromptText2.grid(row=0, column=3, sticky='E')
        self.apiKeyField2 = ttk.Entry(self.mainframe)
        self.apiKeyField2.grid(row=0, column=4, sticky='NWSE')
        setAPIKeyButton2 = ttk.Button(self.mainframe, text="Set New API Key", command=lambda:self.apiUpdate(2))
        setAPIKeyButton2.grid(row=0, column=5)
        
        #Display current filepath to images and input new path as needed
        #The folder selected should contain the images to be run through the models
        #It can have files other than images (.txt, .csv, etc) or other folders, but
        #it will treat any image in this main folder as a dolphin image to be
        #passed through the detection process
        self.filePath = ''
        self.imgTotal = 0
        pathDisplay = 'Current Folder Is: '
        self.pathDisplayText = ttk.Label(self.mainframe, text=pathDisplay)
        self.pathDisplayText.grid(row=1, column=2)
        load_button = ttk.Button(self.mainframe, text='Load Image Folder', command=self.loadFolder)
        load_button.grid(row=2, column=0)
        
        #Set up buttons to run the models, save the results, visualize the
        #predictions, and clear all api keys/folder reference/prediction data/etc
        run_button = ttk.Button(self.mainframe, text='Run Model', command=self.runLDModel)
        run_button.grid(row=2, column=1)
        self.currentPredictions = []
        save_button = ttk.Button(self.mainframe, text='Save Results as CSV', command=self.saveCSV)
        save_button.grid(row=2, column=2)
        #This is gonna require some delicate work within the run method, and isn't
        #critical to the functioning of the tool, and as such is not yet implemented
        #We plan to finish this ASAP though!
        vis_button = ttk.Button(self.mainframe, text='Visualize Results', command=self.visPrediction)
        vis_button.grid(row=2, column=3)
        #Might need to double check that reset is really resetting everything
        reset_button = ttk.Button(self.mainframe, text='Reset', command=self.reset)
        reset_button.grid(row=2, column=4)
        
        #Progress bar for when the model runs
        self.progress = tk.IntVar()
        self.progressBar = ttk.Progressbar(self.mainframe, variable=self.progress, length = 300)
        self.progressBar.grid(row=3, column=0, columnspan=5)
        
        self.root.mainloop()
        return
    
    #allows the user to enter their api key. single method can handle key inputs from
    #both buttons
    def apiUpdate(self, keyNum):
        if not debug:
            #If the first API button is pressed, sets the API Key field, which
            #   is the API key for the workspace where the Body/Dorsal Fin detector
            #   is housed
            if keyNum == 1:
                self.apiKey = self.apiKeyField.get().strip()
                self.apiDisplayText.config(text='Current API Key Is:\n' + str(self.apiKey))
            #If the second API button is pressed, sets the API Key 2 field, which
            #   is the API key for the workspace where the various specific lesion
            #   detection models are housed
            else:
                self.apiKey2 = self.apiKeyField2.get().strip()
                self.apiDisplayText2.config(text='Current API Key 2 Is:\n' + str(self.apiKey2))
        #this is only here for the debug mode
        #TODO - prepare this section for submission by removing the Debug with 
        #    auto-filled API keys
        else:
            if keyNum == 1:
                self.apiKey = apikey1
                self.apiDisplayText.config(text='Current API Key Is:\n' + str(self.apiKey))
            else:
                self.apiKey2 = apikey2
                self.apiDisplayText2.config(text='Current API Key 2 Is:\n' + str(self.apiKey2))
    
    #Opens a file dialog to allow the user to easily select the folder where
    #    their images are
    def loadFolder(self):
        self.filePath=filedialog.askdirectory()
        #Splits off the folder name as to display just the folder name and not
        #    the whole filepath
        #Make sure if you have multiple folders with the same name that you
        #    pick the right one!
        folder = self.filePath.split('/')[-1]
        self.pathDisplayText.config(text='Current Folder Is: ' + folder)
        #At this time, also counts the number of images directly within the folder
        #    (does not count images within subfolders of the folder loaded)
        #    (only counts .JPG, .JPEG, and .PNG images)
        for file in os.listdir(self.filePath):
            if file.upper().endswith('.JPG') or file.upper().endswith('.JPEG')\
                or file.upper().endswith('.PNG'):
                self.imgTotal += 1
        
    #Runs the models and saves the results
    def runLDModel(self):
        #if the model has never been run in this image folder before, or if these
        #    folders weren't otherwise created beforehand, makes folders to store
        #    images.
        
        #Store the full images fed to the Body/Dorsal Fin detector with the
        #    detection annotations visible
        if not os.path.exists(self.filePath+"/Body_Dorsal_Fin_Boxes"):
            os.makedirs(self.filePath+"/Body_Dorsal_Fin_Boxes")
        #Store the cropped subimages resulting from those annotations
        if not os.path.exists(self.filePath+"/Body_Dorsal_Fin_Crops"):
            os.makedirs(self.filePath+"/Body_Dorsal_Fin_Crops")
        #Store the subimages fed to the lesion detectors with the detection
        #    annotations visible
        if not os.path.exists(self.filePath+"/Lesion_Boxes"):
            os.makedirs(self.filePath+"/Lesion_Boxes")
        #Store any initial resized images to keep them from interfering with 
        #    future runs
        if not os.path.exists(self.filePath+"/Initial_Resize"):
            os.makedirs(self.filePath+"/Initial_Resize")
        
        #Initialize the progress bar
        self.showProgress(0, self.imgTotal)
        
        #Begin loading in models
        #For each, chose the model with the highest reported mAP from training
        
        #Load in the first workspace
        rf=roboflow.Roboflow(api_key=self.apiKey)
        #Load in the body/dorsal fin detector
        project_bd = rf.workspace("pcdp-new").project("body-dorsal-detector-new")
        version_bd = project_bd.version(6)
        model_bd = version_bd.model
        
        #load in the second workspace
        rf2=roboflow.Roboflow(api_key=self.apiKey2)
        #load in the fringe detector for crops of the body
        project_bf = rf2.workspace("melissa-colin").project("body-fringe-detector")
        version_bf = project_bf.version(12)
        model_bf = version_bf.model
        
        #load in the spot detector for crops of the body
        project_bs = rf2.workspace("melissa-colin").project("body-spot-detector")
        version_bs = project_bs.version(2)
        model_bs = version_bs.model
        
        #load in the fringe detector for crops of the dorsal fin
        project_df = rf2.workspace("melissa-colin").project("dorsal-fin-fringe-detector")
        version_df = project_df.version(1)
        model_df = version_df.model
        print(model_df)
        
        #load in the spot detector for crops of the dorsal fin
        project_ds = rf2.workspace("melissa-colin").project("dorsal-fin-spot-detector")
        version_ds = project_ds.version(10)
        model_ds = version_ds.model
        
        #count how many images have been processed so far for the progress bar
        imgcount=0
        
        #iterate through images (.jpg, .jpeg, .png) in the directory selected
        for file in os.listdir(self.filePath):
            if file.upper().endswith('.JPG') or file.upper().endswith('.JPEG')\
                or file.upper().endswith('.PNG'):
                #update progress bar
                imgcount += 1
                self.showProgress(imgcount, self.imgTotal)
                
                #access image and predict the Body/Dorsal Fin locations
                imagePath = self.filePath + "/" + file
                img = cv2.imread(imagePath)
                bdPredicts = resizeUntilPredict(model_bd, imagePath, img, \
                                                self.filePath, True)
                bdPredictsDict = bdPredicts[0].json()['predictions']
                #use the number of resizes to ensure reference of the correct image
                #Saves image to the folder storing Body/Dorsal Fin predictions
                #TODO - modify this to separate out initial resizes
                rs = bdPredicts[1]
                if rs>0:
                    bdPredicts[0].save(self.filePath+"/Body_Dorsal_Fin_Boxes/"+file+"_rs"+str(rs)+"_bdPredicts.JPG")
                else:
                    bdPredicts[0].save(self.filePath+"/Body_Dorsal_Fin_Boxes/"+file+"_bdPredicts.JPG")
                #Count the number of body/dorsal fin boxes found
                #    ideally, for photos of one dolphin, should be either 0 or 1 
                #    for each, but sometimes the model gets quirky and gives multiple
                #    Not sure yet, but considering implementing a gate that
                #    only allows one box of each type (perhaps the one with
                #    greatest confidence)
                bodyCount = 0
                finCount = 0
                #iterate through each prediction from the body/dorsal fin model
                for bbox in bdPredictsDict:
                    #determine the coordinates of the bounding box within the 
                    #    given image
                    x1 = bbox['x'] - int(bbox['width']/2)
                    x2 = bbox['x'] + int(bbox['width']/2)
                    y1 = bbox['y'] - int(bbox['height']/2)
                    y2 = bbox['y'] + int(bbox['height']/2)
                    #record the cropped region as a new cv image
                    cropped = bdPredicts[2][y1:y2, x1:x2]
                    #Body and Dorsal Fin subimages need to be handled differently
                    if bbox['class']=='body':
                        #give each body box from this base image an identifier
                        #    (b0, b1, b2, ..., bn)
                        #    also use this identifier to save the image (both for
                        #    reference and to use in next steps)
                        bboxID = 'b'+str(bodyCount)
                        bboxFileName = self.filePath+"/Body_Dorsal_Fin_Crops/"+file.split(".")[0]+"_"+bboxID+".JPG"
                        cv2.imwrite(bboxFileName, cropped)
                        bodyCount += 1
                        #Body images are generally at a poor aspect ratio for 
                        #    object detection. We found that the average image
                        #    was close to 2000x500 px, so we tile all images into
                        #    four images (so the average image is about 500x500px)
                        #    this will be an issue for some images, but improves
                        #    the rest by enough that it helped with performance
                        for count in range(4):
                            #determine the new x-coordinates for each of the "tiles"
                            x3=int((x2-x1)*count/4)
                            x4=int((x2-x1)*(count+1)/4)
                            #create the tile subimages
                            #    tile files are saved with the crop subimage files
                            #    also for reference and next steps
                            croptile = cropped[0:cropped.shape[0], x3:x4]
                            tileFileName = bboxFileName.strip(".JPG") + "_t"+str(count)+".JPG"
                            cv2.imwrite(tileFileName, croptile)
                            
                            #call on the spot detector for crops of the body
                            #    still in the resize loop framework just in case
                            spotPredictions = resizeUntilPredict(model_bs, tileFileName, croptile, self.filePath, False)
                            #use the number of resizes to ensure reference of the correct image
                            rs = spotPredictions[1]
                            if rs > 0:
                                newFName = self.filePath+"/Lesion_Boxes/"+file.split(".")[0]+"_"+bboxID+"_"+str(count)+"_rs"+str(rs)+"_spots.JPG"
                            else:
                                newFName = self.filePath+"/Lesion_Boxes/"+file.split(".")[0]+"_"+bboxID+"_"+str(count)+"_spots.JPG"
                            #save image of predictions of spots on the body crop
                            spotPredictions[0].save(newFName)
                            #repeat above, but for fringes
                            #May try to work out some function call to handle 
                            #    this to prevent repetition in a future version
                            #    (would also make debugs easier/less prone to error)
                            fringePredictions = resizeUntilPredict(model_bf, tileFileName, croptile, self.filePath, False)
                            rs = fringePredictions[1]
                            if rs > 0:
                                newFName = self.filePath+"/Lesion_Boxes/"+file.split(".")[0]+"_"+bboxID+"_"+str(count)+"_rs"+str(rs)+"_fringes.JPG"
                            else:
                                newFName = self.filePath+"/Lesion_Boxes/"+file.split(".")[0]+"_"+bboxID+"_"+str(count)+"_fringes.JPG"
                            fringePredictions[0].save(newFName)
                            #save the predictions in the app's predictions records
                            self.currentPredictions.append((spotPredictions[0], fringePredictions[0]))
                    else:
                        #dorsal fin is significantly easier to handle because
                        #    they're usually pretty square, so there's not really
                        #    a need to tile
                        
                        #give each dorsal fin box from this base image an identifier
                        #    (df0, df1, df2, ..., dfn)
                        #    also use this identifier to save the image (both for
                        #    reference and to use in next steps)
                        bboxID = 'df'+str(finCount)
                        bboxFileName = self.filePath+"/Body_Dorsal_Fin_Crops/"+file.split(".")[0]+"_"+bboxID+".JPG"
                        cv2.imwrite(bboxFileName, cropped)
                        finCount += 1
                        #call on the spot detector for crops of the dorsal fin
                        #    still in the resize loop framework just in case
                        spotPredictions = resizeUntilPredict(model_ds, bboxFileName, cropped, self.filePath, False)
                        #use the number of resizes to ensure reference of the correct image
                        rs = spotPredictions[1]
                        if rs > 0:
                            newFName = self.filePath+"/Lesion_Boxes/"+file.split(".")[0]+"_"+bboxID+"_rs"+str(rs)+"_spots.JPG"
                        else:
                            newFName = self.filePath+"/Lesion_Boxes/"+file.split(".")[0]+"_"+bboxID+"_spots.JPG"
                        #save image of predictions of spots on the dorsal fin crop
                        spotPredictions[0].save(newFName)
                        #repeat above, but for fringes
                        #May try to work out some function call to handle 
                        #    this to prevent repetition in a future version
                        #    (would also make debugs easier/less prone to error)
                        fringePredictions = resizeUntilPredict(model_df, bboxFileName, cropped, self.filePath, False)
                        rs = fringePredictions[1]
                        if rs > 0:
                            newFName = self.filePath+"/Lesion_Boxes/"+file.split(".")[0]+"_"+bboxID+"_rs"+str(rs)+"_fringes.JPG"
                        else:
                            newFName = self.filePath+"/Lesion_Boxes/"+file.split(".")[0]+"_"+bboxID+"_fringes.JPG"
                        fringePredictions[0].save(newFName)
                        print(newFName)
                        #save the predictions in the app's predictions records
                        self.currentPredictions.append((spotPredictions[0], fringePredictions[0]))
                
                
                
                            
                    
      
    def showProgress(self, done, total):
        #updates the progress bar as the run progresses
        self.progress.set(done/total * 100)
        self.root.update_idletasks()
        
                    
    def saveCSV(self):
        #saves the app's predictions records as a CSV file for later analysis
        #currently, no implementation for immediate jump to prevalence calculations
        #    but certainly possible, would just need either an input file and/or 
        #    rules for naming the image files to tie photos to IDs
        #    would need to work out a system that is both customizable and user
        #    -friendly, though, so might not be the first update we push
        
        #Establish a data frame to format the data before export to csv
        #Stores (for every lesion prediction):
        #    - Which image the prediction is from
        #    - What part of the dolphin it's from (body or dorsal fin)
        #    - What lesion class is being predicted (pale spot, dark spot, 
        #      pale fringe, dark fringe)
        #    - The coordinates and dimensions of the box (top left corner plus
        #      width and height)
        #    - The model's confidence associated with the prediction
        outputFrame = pd.DataFrame(columns=["image", "part", "class", "x", "y", "width", "height", "confidence"])
        for predictPair in self.currentPredictions:
            #accesses Spot/Fringe prediction pairs from each dorsal fin/body tile
            #    stored in the app's prediction records
            for predictionGroup in predictPair:
                #separates out either spot or fringe predictions alone
                for prediction in predictionGroup:
                    #takes each individual spot or fringe prediction from the set
                    #    of spot or fringe predictions fort that image
                    
                    #The prediction is a dictionary, so it's easy to tease apart
                    #    most of the components, but the body/dorsal fin 
                    #    distinction isn't built in so this becomes necessary
                    
                    #access the bn/dfn ID tag in the filename
                    part = prediction["image_path"].split('/')[-1].split('_')[2]
                    if part.startswith('b'):
                        part = 'body'
                    else:
                        part = 'dorsal fin'
                    #turns desired prediction components into a new dictionary
                    preDict = {"image":prediction["image_path"], "part":part, "class":prediction["class"],\
                               "x":prediction["x"],"y":prediction["y"],"width":prediction["width"],\
                               "height":prediction["height"],"confidence":prediction["confidence"]}
                    #turn that dictionary into a dataframe
                    predictFrame = pd.DataFrame(preDict, index=[0])
                    #add that dataframe to the slowly accumulating dataframe
                    #    to be used for export
                    outputFrame = pd.concat([outputFrame, predictFrame], ignore_index=True)
        #will be saved to the same folder as the base images with the name
        #    "predictions.csv"
        outputFrame.to_csv(self.filePath+"/predictions.csv", index=False)
    def visPrediction(self):
        #Visualization of predictions within the greater image is not yet 
        #    implemented, as the CSV export was deemed more important. For now,
        #    limited visualization is still possible outside of the app by
        #    going through the Body_Dorsal_Fin_Boxes and Lesion_Boxes folders.
        print('hello world')
    def reset(self):
        #Resets all API Key inputs, file path inputs, progress bar, and stored
        #    predictions
        self.apiKey = ''
        self.apiDisplayText.config(text='Current API Key Is:')
        self.apiKey2 = ''
        self.apiDisplayText2.config(text='Current API Key 2 Is:')
        self.filePath = ''
        self.pathDisplayText.config(text='Current Folder Is:')
        self.progress.set(0)
        self.currentPredictions = []
        self.root.update_idletasks()
        
#run app    
if __name__ == '__main__':
    App()
