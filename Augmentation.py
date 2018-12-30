import cv2
import numpy as np
import pickle
from tkinter.filedialog import askopenfilename
from ImageData import ImageData

filename = askopenfilename(title = "Select Preparation Data")
with open(filename, 'rb') as f:
    imagedata = pickle.load(f)
    f.close()
print(imagedata.kp)
print(imagedata.desc)
for ipoint in imagedata.ipoints:
    print(ipoint)