# -*- coding: utf-8 -*-
"""
Final application to distribute our model to other researchers.
Notes on use can be found in accompanying README.

@author: [redacted as required by submission guidelines]

Switch to workflow in this version.
"""

###IMPORTANT
#This program will only run with the roboflow 'inference' package in your environment.
#Therefore, you must be running Python 3.11 or older; Python 3.12 is not compatible
#with inference


#####DEBUG Mode
#Used by developer to load in API keys faster when testing model
#When debug=True, pressing the buttons to load API keys will autofill the fields
#with the values kept here
#Dev API key has been removed for public upload; please refer to readme for guide
#to retrieving your own key.
apikey = ""
debug=False


import tkinter as tk
from tkinter import ttk, filedialog
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageTk

import os
import cv2
import pandas as pd
import numpy as np


#Function utilized in run method to perpetually resize files until they no longer
#throw 'file too big' exceptions
#CURRENT BUG - The model refuses to run on our original images, but will run once 
#they've been saved via cv2. Making it so that initial resize step is ^0 for now
#and will return later to make things nicer.

#As of right now, this just contributes to slower speeds and more image bloat
#(essentially copying the images over) but until I'm sure it's not losing important
#details, I don't want it overwriting users' images.
def resizeUntilPredict(client, file, filePath):
    #count number of resize steps and track current image filename
    #file gets assigned to a new variable to make renaming steps simpler
    rs=0
    fname=file
    print(fname)
    
    #repeat until it works
    while True:
        try:
            #attempt to predict with current file
            predictions = client.run_workflow(workspace_name="pcdp-new", \
                                              workflow_id="pcdp-2sdld",
                                              images={"image": fname})
        except Exception as e: 
            print(repr(e))
            #Assume exception is due to file size error and resize it
            #Generally, only errors we get are file size or lack of API Credits
            
            #rename file as to not overwrite original and to keep trail of
            #   resized images
            
            #resize step shouldn't save images to same folder as
            #    parent image, because that would cause them to be called
            #    as a starting image in future runs
            fname = filePath + "/Initial_Resize/" + \
                file.strip(".JPG")+"_rs"+str(rs)+".JPG"
            
            #resizes to 81% of the area of the previous resize (loses 10% off
            #   each dimension)
            cvImg = cv2.imread(filePath + "/" + file)
            resized = cv2.resize(cvImg, (0,0), fx=0.9**rs, fy=0.9**rs, interpolation=cv2.INTER_AREA)
            cv2.imwrite(fname, resized)
            
            #iterate resize counter, turn off initial
            rs+=1
        else:
            #no exceptions, successful prediction, end loop
            break
    if not rs-1<0:
        rs = rs-1
    return [predictions, rs, file]

class App():
    def __init__(self):
        #initialize app with name, dimensions, and formatting
        self.root = tk.Tk()
        self.root.geometry('1000x800')
        self.root.title('Dolphin Lesion Detection App')
        self.mainframe = tk.Frame(self.root)
        self.mainframe.pack(fill='both', expand=True)
        
        #define variables to mark when model run is done
        self.done = False
        
        #define variable to hold api key
        self.apiKey = ''
        
        #display currently loaded api key for validation
        apiDisplay = 'Current API Key Is: '
        self.apiDisplayText = ttk.Label(self.mainframe, text=apiDisplay)
        self.apiDisplayText.grid(row=1, column=0)
    
        #initialize input fields for api key
        self.apiPromptText = ttk.Label(self.mainframe, text='Input API Key:')
        self.apiPromptText.grid(row=0, column=0, sticky='E')
        self.apiKeyField = ttk.Entry(self.mainframe)
        self.apiKeyField.grid(row=0, column=1, sticky='NWSE')
        setAPIKeyButton = ttk.Button(self.mainframe, text="Set New API Key", command=self.apiUpdate)
        setAPIKeyButton.grid(row=0, column=2)
        
        #Display current filepath to images and input new path as needed
        #The folder selected should contain the images to be run through the models
        #It can have files other than images (.txt, .csv, etc) or other folders, but
        #it will treat any image in this main folder as a dolphin image to be
        #passed through the detection process
        self.filePath = ''
        self.imgTotal = 0
        self.images=[]
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
        
        #Image viewing space
        self.imgNum=0
        self.imageLabel = tk.Label(self.mainframe)
        self.imageLabel.grid(row=5, column=0, columnspan=5)
        
        #Image viewing important details
        self.backImage = ttk.Button(self.mainframe, text="Back", command=lambda:self.moveImage('L'))
        self.imageName = ttk.Label(self.mainframe, text='')
        self.foreImage = ttk.Button(self.mainframe, text="Forward", command=lambda:self.moveImage('R'))
        self.backImage.grid(row=6, column=1)
        self.imageName.grid(row=6, column=2)
        self.foreImage.grid(row=6, column=3)
        
        self.root.mainloop()
        return
    
    #allows the user to enter their api key.
    def apiUpdate(self):
        if not debug:
            #If the API button is pressed, sets the API Key
            self.apiKey = self.apiKeyField.get().strip()
            print('uh oh')
        #this is only here for the debug mode
        #TODO - prepare this section for submission by removing the Debug with 
        #    auto-filled API key
        else:
            self.apiKey = apikey
            
        self.apiDisplayText.config(text='Current API Key Is:\n' + str(self.apiKey))
    
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
                self.images.append(file)
        
    #Runs the models and saves the results
    def runLDModel(self):
        #if the model has never been run in this image folder before, or if these
        #    folders weren't otherwise created beforehand, makes folders to store
        #    images.
        
        #Store any initial resized images to keep them from interfering with 
        #    future runs
        if not os.path.exists(self.filePath+"/Initial_Resize"):
            os.makedirs(self.filePath+"/Initial_Resize")
        
        #Initialize the progress bar
        self.showProgress(0, self.imgTotal)
        
        #Initialize workflow
        

        client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=self.apiKey
        )
        print(self.apiKey)
        print(client)
        
        #iterate through images (.jpg, .jpeg, .png) in the directory selected
        for file in os.listdir(self.filePath):
            if file.upper().endswith('.JPG') or file.upper().endswith('.JPEG')\
                or file.upper().endswith('.PNG'):
                
                print(file)
                results = resizeUntilPredict(client, file, self.filePath)
                self.currentPredictions.append(results)
            
        self.done=True
        self.showProgress(self.imgTotal, self.imgTotal)    

                
                            
                    
      
    def showProgress(self, completed, total):
        if not self.done:
            self.progress.set(completed/total * 100)
            self.progressText = ttk.Label(self.mainframe, text=str(completed)+'/'+str(total))
            self.progressText.grid(row=4, column=0, columnspan=5) 
        else:
            self.progress.set(100)
            self.progressText = ttk.Label(self.mainframe, text='Done!')
            self.progressText.grid(row=4, column=0, columnspan=5) 
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
        for imageData in self.currentPredictions:
            resizeKey = imageData[1]
            print(resizeKey)
            for output in imageData[0]:
                for predictType in output:
                    if predictType != 'body_dorsal_predictions':
                        region = predictType.split('_')[0]
                        if region=='b':
                            region='Body'
                        elif region=='df':
                            region='Dorsal Fin'
                        lesClass = predictType.split('_')[-1]
                        if lesClass == 's':
                            lesClass='Spot'
                        elif lesClass == 'fr':
                            lesClass='Fringe Ring'
                        if region=='Body':
                            tile = predictType.split('_')[1]
                            if tile=='tRM':
                                tile='Rightmost Tile'
                            elif tile=='tMR':
                                tile='Midright Tile'
                            elif tile=='tML':
                                tile='Midleft Tile'
                            elif tile=='tLM':
                                tile='Leftmost Tile'
                        else:
                            tile='na'
                        if len(output[predictType])>0:
                            predictions = output[predictType][0]['predictions']['predictions']
                            for prediction in predictions:
                                width = prediction['width']
                                height = prediction['height']
                                x = prediction['x']
                                y = prediction['y']
                                conf = prediction['confidence']
                                
                                #turns desired prediction components into a new dictionary
                                preDict = {"image":imageData[2], "part":region+", Tile: "+tile, \
                                           "class":lesClass,"x":x,"y":y,"width":width,\
                                           "height":height,"confidence":conf}
                                #turn that dictionary into a dataframe
                                predictFrame = pd.DataFrame(preDict, index=[0])
                                #add that dataframe to the slowly accumulating dataframe
                                #    to be used for export
                                outputFrame = pd.concat([outputFrame, predictFrame], ignore_index=True)

        #will be saved to the same folder as the base images with the name
        #    "predictions.csv"
        outputFrame.to_csv(self.filePath+"/predictions.csv", index=False)       

    def visPrediction(self):
        if self.done:
            #visualize initial image
            self.imageName.config(text=self.images[self.imgNum])
            imgShown = Image.open(self.filePath + "\\" + self.images[self.imgNum])
            imgShown = np.array(imgShown)
            
            #set up collectors
            annots = {"body":[], "dorsal fin":[],\
                      "spot":[], "fringe ring":[]}
            reposAnnots = {"body":[0,0], "dorsal fin":[0,0],\
                      "spot":[], "fringe ring":[]}
                
            #gather image annotations
            for imageData in self.currentPredictions:
                filename = imageData[2]
                print(imageData)
                resizeKey = imageData[1]
                print(resizeKey)
                #will need to adjust coordinates for resize
                for output in imageData[0]:
                    for predictType in output:
                        if predictType == 'body_dorsal_predictions' and len(output[predictType])>0:
                            predictions = output[predictType]['predictions']['predictions']
                            for predict in predictions:
                                resX = predict['x']/(0.9**resizeKey)
                                resY = predict['y']/(0.9**resizeKey)
                                resW = predict['width']/(0.9**resizeKey)
                                resH = predict['height']/(0.9**resizeKey)
                                coords = [filename, predictType, resX, resY,\
                                          resW, resH]
                                annots[predict['class']].append(coords)
                        elif len(output[predictType])>0:
                            predictions = output[predictType][0]['predictions']['predictions']
                            for predict in predictions:
                                if predict['class'] == 'pale spot' or predict['class']=='dark spot':    
                                    lesionClass = 'spot'
                                else:
                                    lesionClass = 'fringe ring'
                                resX = predict['x']/(0.9**resizeKey)
                                resY = predict['y']/(0.9**resizeKey)
                                resW = predict['width']/(0.9**resizeKey)
                                resH = predict['height']/(0.9**resizeKey)
                                coords = [filename, predictType, resX, resY,\
                                          resW, resH]
                                annots[lesionClass].append(coords)
            
            #Match image annotations, reformat
            ##Known potential for bug - may assign annotations to wrong partition if model
            ##    detects more than one body/more than one dorsal fin.
            ##Will work on patch on next update - otherwise, vis should work fine.
            for lc in ['spot', 'fringe ring']:
                if lc=='spot':
                    lca = 's'
                else:
                    lca = 'fr'    
                for lesion in annots[lc]:
                    filename = lesion[0]
                    partition = lesion[1]
                    
                    #find appropriate body and dorsal fin to build from
                    i=0
                    while annots['dorsal fin'][i][0] != filename and \
                        i<len(annots['dorsal fin']):
                        i+=1
                    dorsalFinBase = annots['dorsal fin'][i]
                    
                    i=0
                    while annots['body'][i][0] != filename and i<len(annots['body']):
                        i+=1
                    bodyBase = annots['body'][i]
                    
                    if partition == 'df_'+lca:
                        newX = lesion[2] + dorsalFinBase[2]
                        newY = lesion[3] + dorsalFinBase[3]
                        reposLesion = lesion.copy()
                        reposLesion[2] = newX
                        reposLesion[3] = newY
                        reposAnnots[lc].append(reposLesion)
                    elif partition == 'b_tLM_'+lca:
                        newX = lesion[2] + bodyBase[2]
                        newY = lesion[3] + bodyBase[3]
                        reposLesion = lesion.copy()
                        reposLesion[2] = newX
                        reposLesion[3] = newY
                        reposAnnots[lc].append(reposLesion)
                    elif partition == 'b_tML_'+lca:
                        newX = lesion[2] + bodyBase[2] + int(bodyBase[4]/4)
                        newY = lesion[3] + bodyBase[3]
                        reposLesion = lesion.copy()
                        reposLesion[2] = newX
                        reposLesion[3] = newY
                        reposAnnots[lc].append(reposLesion)
                    elif partition == 'b_tMR_'+lca:
                        newX = lesion[2] + bodyBase[2] + int(bodyBase[4]/4)*2
                        newY = lesion[3] + bodyBase[3]
                        reposLesion = lesion.copy()
                        reposLesion[2] = newX
                        reposLesion[3] = newY
                        reposAnnots[lc].append(reposLesion)
                    elif partition == 'b_tRM_'+lca:
                        newX = lesion[2] + bodyBase[2] + int(bodyBase[4]/4)*3
                        newY = lesion[3] + bodyBase[3]
                        reposLesion = lesion.copy()
                        reposLesion[2] = newX
                        reposLesion[3] = newY
                        reposAnnots[lc].append(reposLesion)
                        
            
            #now to draw the rectangles
            #spots first, in red
            for spot in reposAnnots['spot']:
                filename=self.images[self.imgNum]
                if spot[0]==filename:
                    startPoint=(int(spot[2]), int(spot[3]))
                    endPoint=(int(spot[2]+spot[4]), int(spot[3]+spot[5]))
                    color=(0,0,255)
                    thickness=2
                    imgShown=cv2.rectangle(imgShown, startPoint, endPoint,\
                                           color, thickness)
                
                                
            
            
            
            #resize final image
            imgShown = Image.fromarray(imgShown, 'RGB')
            imgShown_rs = imgShown.resize((684, 456))
            imgShown_rs = ImageTk.PhotoImage(imgShown_rs)
            self.imageLabel.config(image=imgShown_rs)
            self.imageLabel.image=imgShown_rs
        
        
      
    def moveImage(self, direction):
        num = self.imgNum
        if direction=='L' and self.imgNum > 0:
            self.imgNum = num - 1 
        elif direction=='R' and self.imgNum < self.imgTotal-1:
            self.imgNum = num + 1
        self.imageName.config(text=self.images[self.imgNum])
        imgShown = Image.open(self.filePath + "\\" + self.images[self.imgNum])
        imgShown_rs = imgShown.resize((684, 456))
        imgShown_rs = ImageTk.PhotoImage(imgShown_rs)
        self.imageLabel.config(image=imgShown_rs)
        self.imageLabel.image=imgShown_rs
        self.root.update_idletasks()
        
      
    def reset(self):
        #Resets all API Key inputs, file path inputs, progress bar, and stored
        #    predictions
        self.apiKey = ''
        self.apiDisplayText.config(text='Current API Key Is:')
        self.filePath = ''
        self.pathDisplayText.config(text='Current Folder Is:')
        self.progress.set(0)
        self.currentPredictions = []
        self.root.update_idletasks()
        
#run app    
if __name__ == '__main__':
    App()
