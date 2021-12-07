from time import time
import win32gui

def get_window(window_name):
    open_windows = []

    def win_handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            win_name = window_name.lower()
            win_title = win32gui.GetWindowText(hwnd)

            if win_title.lower().find(win_name) >= 0:
                ctx.append(win_title)

    win32gui.EnumWindows(win_handler, open_windows)

    if len(open_windows) > 0:
        return open_windows[0]
    else:
        return None


def fps(fps_counter):
      fps_count = (time() - fps_counter) or 1
      fps = "FPS: {} ".format(round(1 / fps_count))
      
      print(fps)
      return time()