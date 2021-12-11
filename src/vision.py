import pyautogui
import numpy as np
import cv2 as cv
import mss

DEBUG_MODE = False

BROWSER_NO_SUPPORT = ["brave", "chrome", "firefox"]

THRESHOLD = 0.8
DEFAULT_CV2_METHOD = cv.TM_CCOEFF_NORMED
DEFAULT_CV2_BORDERCOLOR = (255, 0, 176)


class Vision:

    # Window Settings
    w, h = pyautogui.size()

    # Browser Settings
    browser = "Chrome"

    def __init__(self, browser="Chrome"):
        self.browser = browser

    def screenshot(self, left=0, top=0, width=0, height=0):
        stc = mss.mss()
        scr = stc.grab(
            {
                "left": left,
                "top": top,
                "width": width or self.w,
                "height": height or self.h,
            }
        )

        img = np.array(scr)
        img = cv.cvtColor(img, cv.IMREAD_COLOR)

        return img

    def debug_show_scene(self, size, position, scene, window_name):
        self.mark_target(size, position, scene)
        self.show(scene, window_name)

    def find(
        self,
        needle,
        haystack,
        window_name="Bot",
        threshold=THRESHOLD,
        method=DEFAULT_CV2_METHOD,
        show_window=False,
        label=False,
        silent=False,
    ):
        result = cv.matchTemplate(haystack, needle, method)
        _, max_val, _, max_loc = cv.minMaxLoc(result)

        if max_val >= threshold:
            message = str("Found needle accuracy of: {}".format(max_val))

            if label:
                message += str(" with label name: {}".format(label))

            if not silent:
                print(message)

            if DEBUG_MODE or show_window:
                needle_w, needle_h = (needle.shape[0], needle.shape[1])
                self.debug_show_scene(
                    (needle_w, needle_h), max_loc, haystack, window_name
                )

            return True
        else:
            if DEBUG_MODE:
                print(f"Failed to find needle with {max_val} accuracy")
                
            return False

    def find_position(self, needle, haystack, threshhold=THRESHOLD):
        result = cv.matchTemplate(haystack, needle, DEFAULT_CV2_METHOD)
        _, max_val, _, max_loc = cv.minMaxLoc(result)

        if max_val > threshhold:
            return max_loc
        else:
            return (0, 0)

    def show(self, screenshot, window_name="Bot"):
        cv.imshow(window_name, screenshot)

    def mark_target(self, size, max_loc, screenshot):
        h, w = size
        x, y = max_loc
        color = DEFAULT_CV2_BORDERCOLOR

        top_left = (x, y)
        bottom_right = (x + w, y + h)
        cv.rectangle(
            screenshot, top_left, bottom_right, color, thickness=2, lineType=cv.LINE_8
        )

    def hsv_color_fix(self, frame):
        hsvframe = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        red_lower = np.array([0, 150, 150], np.uint8)
        red_upper = np.array([10, 255, 255], np.uint8)
        red_mask = cv.inRange(hsvframe, red_lower, red_upper)

        green_lower = np.array([40, 200, 150], np.uint8)
        green_upper = np.array([70, 255, 255], np.uint8)
        green_mask = cv.inRange(hsvframe, green_lower, green_upper)

        kernal = np.ones((5, 5), "uint8")

        red_mask = cv.dilate(red_mask, kernal)
        cv.bitwise_and(frame, frame, mask=red_mask)

        green_mask = cv.dilate(green_mask, kernal)
        cv.bitwise_and(frame, frame, mask=green_mask)

        contours = cv.findContours(red_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)[0]
        return (contours, green_mask, red_mask)

    def add_text(self, frame, message, position, color=(0, 0, 255)):
        return cv.putText(frame, message, position, cv.FONT_HERSHEY_SIMPLEX, 0.7, color)

    def add_rect(self, frame, position, size, color=(0, 0, 255)):
        return cv.rectangle(frame, position, size, color, thickness=2)

    def green_mask(self, scene):
        lower = np.array([56, 213, 165])
        upper = np.array([89, 255, 255])

        # Convert to HSV format and color threshold
        hsv = cv.cvtColor(scene, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(scene, scene, mask=mask)

        return result

    def red_mask(self, scene):
        lower = np.array([0, 161, 0])
        upper = np.array([6, 199, 255])

        # Convert to HSV format and color threshold
        hsv = cv.cvtColor(scene, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(scene, scene, mask=mask)

        return result
