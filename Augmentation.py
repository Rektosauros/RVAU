import cv2
import sys
import math
import numpy as np
import pickle
from tkinter.filedialog import askopenfilename
import tkinter
from ImageData import ImageData



MIN_MATCH_COUNT = 45
def getData():
    root = tkinter.Tk()
    root.withdraw()
    filename = askopenfilename(title = "Select Preparation Data")
    with open(filename, 'rb') as f:
        global imagedata
        imagedata = pickle.load(f)
        f.close()
        for ipoint in imagedata.ipoints:
            imagedata.image = cv2.rectangle(imagedata.image,tuple(ipoint.pt2),tuple(ipoint.pt1),(0,0,255))
        
def getCVKeypoints(kps):
    keypoints = []
    for point in kps:
      keypoints.append(cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], 
                            _response=point[3], _octave=point[4], _class_id=point[5]))
    return keypoints

def filterMatches(matches):
    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append(m)
    return good

def buildCentersList(ips):
    centers = []
    for ip in ips:
        centers.append(ip.center)
    return centers

def captureVideo():
    # Initialize feature matching objects and convert pickled data to original format as needed
    sift = cv2.xfeatures2d.SIFT_create()
    bf = cv2.BFMatcher()
    kp1 = getCVKeypoints(imagedata.kp)
    # Start video capture and loop for continuous frame capturing
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        if ret:  
            # Match natural features of original image with captured video frame  
            kp2, frame_desc = sift.detectAndCompute(frame,None)
            if(kp2 is None or frame_desc is None):
                continue
            matches = bf.knnMatch(imagedata.desc,frame_desc, k=2)
            if(len(matches)==0):
                continue
            # Apply ratio test to filter bad matches out
            good = filterMatches(matches)
            # If enough matches
            if len(good)>MIN_MATCH_COUNT:
                # Calculate Homography between keypoints in the original image and the matching keypoints in frame
                src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
                # Check if Homography matrix was found
                if(M is None):
                    continue
                matchesMask = mask.ravel().tolist()
                if(len(imagedata.image.shape)==3):
                    h,w,channels = imagedata.image.shape
                else:
                    h,w = imagedata.image.shape 
                # get centers of interest points in original image
                centers = buildCentersList(imagedata.ipoints)
                # append center of original image
                centers.append([w/2,h/2])
                # Calculate coordinates of the corners and center of the map based on homography matrix
                pts = np.float32([centers]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)
                # Draw yellow circle in center of image
                image_center = np.int32(dst[-1])[0]
                frame = cv2.circle(frame,(image_center[0],image_center[1]),10,(0,255,255),-1)
                # Check for nearest interest point
                minDistance=sys.maxsize
                closestIPoint = None
                for idx in range(0,len(centers)-1):
                    tempDistance=calcEuclidean(image_center,centers[idx])
                    if minDistance > tempDistance:
                        minDistance = tempDistance
                        closestIPoint = np.int32(dst[idx])[0]
                if(closestIPoint is not None):
                    frame = cv2.circle(frame,(closestIPoint[0],closestIPoint[1]),10,(0,255,0),-1)
                # draw rest of interestpoint stuff
            else:
                print("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
                matchesMask = None
            draw_params = dict(matchColor = (0,255,0), # draw matches in green color
            singlePointColor = None,
            matchesMask = matchesMask, # draw only inliers
            flags = 2)
            #frame = cv2.drawMatches(imagedata.image,kp1,frame,kp2,good,0,**draw_params)
            cv2.imshow('AR Detection',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    cap.release()
    cv2.destroyAllWindows()

def printPickle(imagedata):
    for ipoint in imagedata.ipoints:
        print(ipoint)

def calcEuclidean(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def main():
    getData()
    captureVideo()

if __name__ == '__main__':
    main()  