03 Dec 2024

Hello! This is the README document for the PCDP Lesion Detection App. This tool is designed to help researchers quickly assess the presence of skin lesions in a dolphin population using photographic data.

////////////////////

Important Dependencies

Before running the app, you will need to ensure you have all of the following:

- Python 3.11 (Python 3.12 will not work with Roboflow's inference package)
- packages
    - inference (Roboflow's Python package for using models hosted on their site)
    - numpy
    - pandas
    - OpenCV (imported as cv2) 
    - (the code also uses tkinter and os, which should be included with your installation of Python)
- A Roboflow account (roboflow.com), from which you will need to retrieve your account's API key. More detailed guidance on retrieving 
this key will be added to this document soon.

////////////////////

Instructions for Use

To use the app, you may either double-click on the associated python file or open it in an IDE of your choosing and then run the code.
Once the app is open, you should click on the text field at the very top labeled "Input API Key". Enter your account's API key into this
box, then press the "Set New API Key" button directly to its right. Under the label for the text field is a line of text that says
"Current API Key Is:" - when you have successfully loaded in your API key, it should appear under this line of text.

Next, click on the button labeled "Load Image Folder", to the very left of the row of buttons. This will open a file navigation window
from which you can select the folder containing all of your images. Please ensure you select only the folder, and not any individual
images. Also, please ensure that all image files are immediately within the folder and not nested within subfolders, as the app will not
check images in subfolders. To the right of the text that displays the current API Key, there is a line that says "Current Folder Is:".
Like with the API key, ensure that the correct folder is written beneath this line before proceeding.

Once both the API key and the image folder are correctly loaded, please press the "Run Model" button. At this point in time, the app may
appear to freeze or otherwise prevent interaction with itself; please be patient, as the app is likely still functioning as intended. A
progress bar will appear, and will fill as the app progresses through your data. Sometimes it may stutter/not update for every image, but
so far it has not fully crashed with the current build. Do not exit the app or click on anything as soon as the bar fills; this is an
indication that it has started the final image but may not have actually finished it. The app is finished running the model when the text
underneath the progress bar says "Done".

*Note - Presently, a bug occurs where the Back and Forward buttons at the bottom of the app may duplicate while the model is running.
While annoying, it doesn't break the app, and so we have focused our efforts elsewhere for now and will fix this issue if/when we decide
to come back for any GUI/ease-of-use updates.

Once the model has finished running, press Save Results as CSV to save a CSV of all of the model's lesion predictions. Please note that 
the model will not export its predictions unless you press this button.

////////////////////

The "Initial Resize" Folder

In the process of running the models, the app makes a folder nested within your initial folder named "Initial Resize". Please ensure that
your image folder has no existing folders of the same name before running the model; the app will not delete or overwrite the folder, but
it will add in new images as the app runs. 

The purpose of this folder is to sequester any images produced by the model in steps where it needs to resize large original source images
before running them through the model (as images of sufficient size cause errors that can completely stop the model). This is why your
images cannot be in subfolders; the model is trained to ignore images in subfolders so that it does not treat its own resized image
generations as new images on subsequent runs.

Resized images are named [original image name]_rsX, where X is the number of resizes performed. Images named rs0 have been resized 0 
times; these are copies of the original-sized source images. Future optimizations may be made to remove this duplication step to prevent 
model runs from consuming undue memory on users' devices, but for the time being we apologize for any inconvenience.

////////////////////

Reading the Generated CSV File

The CSV file has 8 columns:
- image: The original file name of the image from which the prediction is sourced
- part: The specific subimage from which the prediction is sourced. Is either Body or Dorsal Fin; for Body, the associated tile (Leftmost, 
Mid-Left, Mid-Right, Rightmost) is also listed.
- class: The classification for the lesion. Either Spot or Fringe Ring.
- x: The x-coordinate within the subimage for the top-left corner of the lesion bounding box.
- y: The y-coordinate within the subimage for the top-left corner of the lesion bounding box.
- width: The width of the lesion bounding box
- height: The height of the lesion bounding box
- confidence: The confidence associated with that row's prediction.


////////////////////

Visualization and Reset

Currently, buttons appear labeled "Visualize Results" and "Reset". These are presently in development and are indicative of functions we
hope to add to the app in future updates. Please do not click these. 

////////////////////

Please reach out if you face any bugs or have questions!