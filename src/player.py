import sys
sys.path.insert(1, "./lib/")

import listener
import pyautogui
import default
from pynput.mouse import Button, Controller
from pynput import keyboard


mouse = Controller()
keyboard = Keyboard()

class Player:

   player_name=None
   height_offset=None
   window_w, window_h = pyautogui.size()
   
   mov_status=PLAYER_STATUS_IDLE

   def __init__(self, player_name, height_offset=300):
      self.player_name=player_name
      self.height_offset=height_offset
      # self.start_listeners()
      self.start_fishing()
      
   def start_listeners(self):
      if keyboard.is_pressed("home"):
         self.start_fishing()
      
   def change_status(self, status):
      if not status in default.PLAYER_STATUS:
         raise NameError("Invalid status") # Nonecompliant
      else:
         self.mov_status = status
      
   def start_fishing(self):
      print("Started fishing")
      self.change_status(default.PLAYER_STATUS.get("PLAYER_STATUS_FISHING"))
      
      click_pos_x = round(self.window_w / 2)
      click_pos_y = round(self.window_h / 2) + self.height_offset
      pyautogui.click(click_pos_x, click_pos_y, 5000)