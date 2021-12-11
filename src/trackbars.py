import cv2
import numpy as np


def nothing(x):
    pass


class Trackbar:
    # Initialize HSV min/max values
    hMin = sMin = vMin = hMax = sMax = vMax = 0
    phMin = psMin = pvMin = phMax = psMax = pvMax = 0
    
    result = None
    
    def __init__(self):
      # Create trackbars for color change
      # Hue is from 0-179 for Opencv
      cv2.namedWindow("controller")
      cv2.createTrackbar("HMin", "controller", 56, 179, nothing)
      cv2.createTrackbar("SMin", "controller", 213, 255, nothing)
      cv2.createTrackbar("VMin", "controller", 165, 255, nothing)
      cv2.createTrackbar("HMax", "controller", 89, 179, nothing)
      cv2.createTrackbar("SMax", "controller", 255, 255, nothing)
      cv2.createTrackbar("VMax", "controller", 255, 255, nothing)

    def trackbar(self, image):
        # Get current positions of all trackbars
        self.hMin = cv2.getTrackbarPos("HMin", "controller")
        self.sMin = cv2.getTrackbarPos("SMin", "controller")
        self.vMin = cv2.getTrackbarPos("VMin", "controller")
        self.hMax = cv2.getTrackbarPos("HMax", "controller")
        self.sMax = cv2.getTrackbarPos("SMax", "controller")
        self.vMax = cv2.getTrackbarPos("VMax", "controller")

        # Set minimum and maximum HSV values to display
        lower = np.array([self.hMin, self.sMin, self.vMin])
        upper = np.array([self.hMax, self.sMax, self.vMax])

        # Convert to HSV format and color threshold
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        self.result = cv2.bitwise_and(image, image, mask=mask)

        # Print if there is a change in HSV value
        if (
            (self.phMin != self.hMin)
            | (self.psMin != self.sMin)
            | (self.pvMin != self.vMin)
            | (self.phMax != self.hMax)
            | (self.psMax != self.sMax)
            | (self.pvMax != self.vMax)
        ):
            print(
                "(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)"
                % (self.hMin, self.sMin, self.vMin, self.hMax, self.sMax, self.vMax)
            )
            self.phMin = self.hMin
            self.psMin = self.sMin
            self.pvMin = self.vMin
            self.phMax = self.hMax
            self.psMax = self.sMax
            self.pvMax = self.vMax
