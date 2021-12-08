import pyautogui
import win32gui, win32ui, win32con
import numpy as np
import cv2 as cv
import core

BROWSER_NO_SUPPORT = ["brave", "chrome", "firefox"]
DEBUG_MODE = False
THRESHOLD = .8
DEFAULT_CV2_METHOD = cv.TM_CCOEFF_NORMED
DEFAULT_CV2_BORDERCOLOR = (255, 0, 176)

class Vision:

    # Window Settings
    w, h = pyautogui.size()

    # Browser Settings
    browser = "Chrome"

    def __init__(self, browser="Chrome"):
        self.browser = browser

    def screenshot(self):
        hwnd = None

        if not self.browser.lower() in BROWSER_NO_SUPPORT:
            hwnd = win32gui.FindWindow(None, core.get_window(self.browser))

        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (0, 0), win32con.SRCCOPY)
        signedIntsArray = dataBitMap.GetBitmapBits(True)

        img = np.fromstring(signedIntsArray, dtype="uint8")
        img.shape = (self.h, self.w, 4)
        img.astype(np.uint8)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        img = img[..., :3]
        img = np.ascontiguousarray(img)

        return img

    def find(
        self,
        needle,
        haystack,
        threshold=THRESHOLD,
        method=DEFAULT_CV2_METHOD,
    ):
        result = cv.matchTemplate(haystack, needle, method)
        _, max_val, _, max_loc = cv.minMaxLoc(result)

        if max_val >= threshold:
            if DEBUG_MODE:
                print("Found needle accuracy of: {}".format(max_val))
                needle_w, needle_h = (needle.shape[0], needle.shape[1])
                self.mark_target((needle_w, needle_h), max_loc, haystack)
                self.show(haystack)
            return True
        else:
            print("Failed to find needle with {} accuracy".format(max_val))
            return False
        
    def find_position(self, needle, haystack):
        result = cv.matchTemplate(haystack, needle, DEFAULT_CV2_METHOD)
        _, _, _, max_loc = cv.minMaxLoc(result)
        return max_loc

    def show(self, screenshot):
        cv.imshow("Bot", screenshot)

    def mark_target(self, size, max_loc, screenshot):
        h, w = size
        x, y = max_loc
        color = DEFAULT_CV2_BORDERCOLOR

        top_left = (x, y)
        bottom_right = (x + w, y + h)
        cv.rectangle(
            screenshot, top_left, bottom_right, color, thickness=2, lineType=cv.LINE_8
        )
