import cv2 as cv2
import numpy as np
import sqlite3

def connectDatabase():
    global conn 
    conn = sqlite3.connect('example.db')

def showWindow():
    img = cv2.imread('map.jpg',1)
    cv2.imshow('preparation',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows() 
 

def main():
   showWindow()

if __name__ == '__main__':
    main()  