import cv2
import numpy as np
import pickle
from tkinter.filedialog import askopenfilename
import tkinter
from ImageData import ImageData


MIN_MATCH_COUNT = 10
def getData():
    root = tkinter.Tk()
    root.withdraw()
    filename = askopenfilename(title = "Select Preparation Data")
    with open(filename, 'rb') as f:
        global imagedata
        imagedata = pickle.load(f)
        f.close()
  

def printPickle(imagedata):
    print(imagedata.kp)
    print(imagedata.desc)
    for ipoint in imagedata.ipoints:
        print(ipoint)

def captureVideo():
    #cv2.imshow('imagex',imagedata.image)
    #while(True):
    #    if cv2.waitKey(1) & 0xFF == ord('q'):
    #        break
    #return
    orb = cv2.ORB_create()
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    kp1 = getCVKeypoints(imagedata.kp)
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        if ret:
            # Our operations on the frame come here    
            kp2, frame_desc = orb.detectAndCompute(frame,None)
            matches = bf.match(imagedata.desc,frame_desc)
            matches = sorted(matches, key = lambda x:x.distance)
            # Do Homeography here
            if len(matches)>MIN_MATCH_COUNT:
                src_pts = np.float32([ kp1[m.queryIdx].pt for m in matches ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp2[m.trainIdx].pt for m in matches ]).reshape(-1,1,2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
                matchesMask = mask.ravel().tolist()
                slices,h,w = imagedata.image.shape
                pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)
                frame = cv2.polylines(frame,[np.int32(dst)],True,255,3, cv2.LINE_AA)
                draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                singlePointColor = None,
                matchesMask = matchesMask, # draw only inliers
                flags = 2)
                frame = cv2.drawMatches(imagedata.image,kp1,frame,kp2,matches,0,**draw_params)
            else:
                print("Not enough matches are found - %d/%d" % (len(matches),MIN_MATCH_COUNT))
                matchesMask = None
            cv2.imshow('AR Detection',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    cap.release()
    cv2.destroyAllWindows()

def getCVKeypoints(kps):
    keypoints = []
    for point in kps:
      keypoints.append(cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], 
                            _response=point[3], _octave=point[4], _class_id=point[5]))
    return keypoints

def main():
    getData()
    captureVideo()

if __name__ == '__main__':
    main()  