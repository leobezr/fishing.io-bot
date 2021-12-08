from player import Player
from vision import Vision
import cv2 as cv
import time

vision = Vision("brave")

HOOK = cv.imread(r"./src/objects/hook.jpg")
FISH_CAUGHT = cv.imread(r"./src/objects/warning.jpg")
STORE = cv.imread(r"./src/objects/fish_store_logo.jpg")
STORE_SHOP = cv.imread(r"./src/objects/fish_shop.jpg")
STORE_SELECT_ALL = cv.imread(r"./src/objects/select_all.jpg")
STORE_SELL = cv.imread(r"./src/objects/sell_for.jpg")
STORE_SELL_CONFIRM = cv.imread(r"./src/objects/sell_confirm.jpg")

POS_LEAVE_STORE_X = 150
POS_LEAVE_STORE_Y = 500

BOT_IN_ACTION = "action"
BOT_IDLE = "idle"

DEBUG_MODE = True
SAFE_TIMEOUT = 15000


class Bot:

    player = None
    bot_in_action = False
    scene = None
    last_action = time.time()

    def __init__(self):
        self.player = Player("BEZR Coder")
        print("Bot setup ready")

    def in_action(self, status=BOT_IN_ACTION):
        self.bot_in_action = status != BOT_IDLE
        
    def refresh_scene(self):
       print("Scene refreshed")
       self.scene = vision.screenshot()

    def condition_mechanics(self):
        self.refresh_timeout("Condition mechanics")

        if self.player.mov_status == "idle":
            self.player.start_fishing()
            time.sleep(1)
        elif vision.find(needle=FISH_CAUGHT, haystack=self.scene):
            print("Fish caught")
            self.player.maintain_hook(0.5)
            time.sleep(1)
        elif vision.find(needle=HOOK, haystack=self.scene):
            print("Pushing fish back")
            self.player.change_status("pulling")
        else:
            self.player.change_status("idle")

    def refresh_timeout(self, step_name):
        self.last_action = time.time()
        print("Time refreshed at [{}]".format(step_name))

    def check_timeout(self):
        if self.last_action <= time.time() - SAFE_TIMEOUT:
            self.in_action(BOT_IDLE)
            print("Bot timed out, refreshed action state")

    def run(self):
        self.check_timeout()
        self.refresh_scene()

        if self.bot_in_action:
            return

        self.move_to_store()

        if DEBUG_MODE:
            return

        player_status = self.player.mov_status

        if not player_status == "moving" or not player_status == "selling":
            self.condition_mechanics()
        elif player_status == "selling":
            self.in_action(BOT_IN_ACTION)
            self.sell_fish()
            
    def open_store(self):
       self.refresh_timeout("Open Store")
       
       self.refresh_scene()
       if vision.find(needle=STORE_SHOP, haystack=self.scene):
          x, y = vision.find_position(needle=STORE_SHOP, haystack=self.scene)
          self.player.click_and_release(x, y, .3)
          self.sell_fish()
       else:
          self.open_store()
          time.sleep(5)
       
    def move_to_store(self):
      self.refresh_timeout("Moving to store")
      
      self.in_action(BOT_IN_ACTION)
      self.player.change_status("moving")
      self.player.move("north", 3)
      self.open_store()
       
    def move_back_fishing_point(self):
       self.refresh_timeout("Moving to fishing point")
       
       self.player.move("south", 3)
       self.player.change_status("idle")
       self.in_action(BOT_IDLE)

    def leave_shop(self):
        self.refresh_timeout("Leaving shop")

        self.refresh_scene()
        if vision.find(needle=STORE, haystack=self.scene):
            self.player.click_and_release(POS_LEAVE_STORE_X, POS_LEAVE_STORE_Y, 0.3)
            self.move_back_fishing_point()
            

    def _shop_action_confirm_sell(self):
        self.refresh_timeout("Confirm Sell")
        
        self.refresh_scene()
        if vision.find(needle=STORE_SELL_CONFIRM, haystack=self.scene):
            print("Confirming sell")
            x, y = vision.find_position(needle=STORE_SELL_CONFIRM, haystack=self.scene)
            self.player.click_and_release(x, y, 0.5)
            time.sleep(1)
            self.leave_shop()
        else:
            self._shop_action_sell()

    def _shop_action_sell(self):
        self.refresh_timeout("First Sell")

        self.refresh_scene()
        if vision.find(needle=STORE_SELL, haystack=self.scene):
            print("Selling all fish")
            x, y = vision.find_position(needle=STORE_SELL, haystack=self.scene)
            self.player.click_and_release(x, y, 0.5)
            time.sleep(1)
            self._shop_action_confirm_sell()
        else:
            self._shop_action_sell()

    def _shop_action_select_all(self):
        self.refresh_timeout("Select All")
      
        self.refresh_scene()
        if vision.find(needle=STORE_SELECT_ALL, haystack=self.scene):
            print("Selecting all fish in shop")
            x, y = vision.find_position(needle=STORE_SELECT_ALL, haystack=self.scene)
            self.player.click_and_release(x, y, 0.5)
            self._shop_action_sell()
        else:
            print("Store action select all not found, retrying")
            self._shop_action_select_all()

    def sell_fish(self):
        self.refresh_timeout("Sell fish method")

        self.refresh_scene()
        if vision.find(needle=STORE, haystack=self.scene):
            print("Player selling fish")
            self.player.change_status("selling")
            self._shop_action_select_all()
