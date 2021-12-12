import pyautogui
import numpy as np
import cv2 as cv
import mss

DEBUG_MODE = False

BROWSER_NO_SUPPORT = ["brave", "chrome", "firefox"]

THRESHHOLD = 0.8
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

    def mark_scene(self, size, position, scene, window_name):
        self.mark_target(size, position, scene)
        self.show(scene, window_name)

    def find(
        self,
        needle,
        haystack,
        window_name="Bot",
        threshhold=THRESHHOLD,
        method=DEFAULT_CV2_METHOD,
        show_window=False,
        label=False,
        silent=False,
    ):
        result = cv.matchTemplate(haystack, needle, method)
        _, max_val, _, max_loc = cv.minMaxLoc(result)

        if max_val >= threshhold:
            message = str("Found needle accuracy of: {}".format(max_val))

            if label:
                message += str(" with label name: {}".format(label))

            if not silent:
                print(message)

            if DEBUG_MODE or show_window:
                needle_w, needle_h = (needle.shape[0], needle.shape[1])
                self.mark_scene((needle_w, needle_h), max_loc, haystack, window_name)

            return True
        else:
            if DEBUG_MODE:
                print(f"Failed to find needle with {max_val} accuracy")

            return False

    def find_position(self, needle, haystack, threshhold=THRESHHOLD):
        result = cv.matchTemplate(haystack, needle, DEFAULT_CV2_METHOD)
        _, max_val, _, max_loc = cv.minMaxLoc(result)

        if max_val > threshhold:
            print(f"Found position: {max_loc}")
            return max_loc
        else:
            print(f"Position not found! Threshhold: {threshhold} | MaxVal: {max_val}")
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

    def add_text(self, frame, message, position, color=(0, 0, 255)):
        return cv.putText(frame, message, position, cv.FONT_HERSHEY_SIMPLEX, 0.7, color)

    def add_rect(self, frame, position, size, color=(0, 0, 255)):
        return cv.rectangle(frame, position, size, color, thickness=2)

    def green_mask(self, scene):
        return self.hsv(scene, 56, 213, 165, 89, 255, 255)

    def red_mask(self, scene):
        return self.hsv(scene, 0, 161, 0, 6, 199, 255)

    def orange_mask(self, scene):
        return self.hsv(scene, 0, 16, 226, 84, 215, 255)

    def yellow_mask(self, scene):
        return self.hsv(scene, 21, 156, 215, 40, 255, 255)

    def hsv(self, scene, h_min, s_min, v_min, h_max, s_max, v_max):
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        # Convert to HSV format and color threshold
        hsv = cv.cvtColor(scene, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(scene, scene, mask=mask)

        return result
