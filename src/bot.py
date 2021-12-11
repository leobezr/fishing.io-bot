from player import Player
from vision import Vision
import numpy as np
import cv2 as cv
import time

vision = Vision("brave")


# FISHING TARGETS
HOOK = cv.imread(r"./src/objects/hook.jpg")
FISH_CAUGHT = cv.imread(r"./src/objects/warning.jpg")
STATUS_GREEN = cv.imread(r"./src/objects/fishing_status_green.jpg")
STATUS_RED = cv.imread(r"./src/objects/fishing_status_red.jpg")

# STORE TARGETS
STORE = cv.imread(r"./src/objects/fish_store_logo.jpg")
STORE_SHOP = cv.imread(r"./src/objects/fish_shop.jpg")
STORE_SELECT_ALL = cv.imread(r"./src/objects/select_all.jpg")
STORE_SELL = cv.imread(r"./src/objects/sell_for.jpg")
STORE_SELL_CONFIRM = cv.imread(r"./src/objects/sell_confirm.jpg")


# DEFAULTS
POS_LEAVE_STORE_X = 150
POS_LEAVE_STORE_Y = 500

BOT_IN_ACTION = "action"
BOT_IDLE = "idle"

DEBUG_MODE = True
SAFE_TIMEOUT = 15000

FISHING_BAR_HEIGHT = 200
FISHING_BAR_WIDTH = 800
FISHING_HOOK_OFFSET_Y = 100


class Bot:

    player = None
    bot_in_action = False
    scene = None
    last_action = time.time()

    _hook_found = False
    _hook_bar_position = (0, 0)

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
            self.player.click_and_release(x, y, 0.3)
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

    def _register_hook_pos(self):
        (x, y) = vision.find_position(needle=HOOK, haystack=self.scene)
        self._hook_bar_position = (
            x - round(FISHING_BAR_WIDTH / 2),
            y - FISHING_HOOK_OFFSET_Y,
        )
        print("Hook props set")

    def find_hook_bar_position(self):
        self.refresh_scene()

        if self._hook_found:
            x, y = self._hook_bar_position

            scene = vision.screenshot(
                left=x,
                top=y,
                width=FISHING_BAR_WIDTH,
                height=FISHING_BAR_HEIGHT,
            )

            return scene

        self.refresh_timeout("Finding hook props")

        if vision.find(needle=HOOK, haystack=self.scene):
            self._hook_found = True
            self._register_hook_pos()
            
    def _get_distance(self, hook, bar, bar_name):
        self.refresh_timeout("Keeping hook to bar")
        hook_x = hook
        bar_x = bar

        if hook_x >= bar_x:
            print(f"Bar {bar_name} is at the left from hook")
            self.player.fishing_hook_click("release")
        else:
            print(f"Bar {bar_name} is at the right from hook")
            self.player.fishing_hook_click("press")

    def auto_manage_hook(self):
        x, y = self._hook_bar_position
        scene = vision.screenshot(x, y, FISHING_BAR_WIDTH, FISHING_BAR_HEIGHT)

        green_target = vision.green_mask(scene)
        red_target = vision.red_mask(scene)

        green_x = vision.find_position(needle=STATUS_GREEN, haystack=green_target)[0]
        red_x = vision.find_position(needle=STATUS_RED, haystack=red_target)[0]
        hook_x = vision.find_position(needle=HOOK, haystack=scene)[0]

        if DEBUG_MODE:
            vision.find(
                needle=STATUS_GREEN, haystack=green_target, show_window=True, silent=True
            )
            vision.find(
                needle=STATUS_RED, haystack=red_target, show_window=True, silent=True
            )
            vision.find(needle=HOOK, haystack=scene, show_window=True, silent=True)

            vision.show(green_target, "green view")
            vision.show(red_target, "red view")
            vision.show(scene)

        if hook_x:
            if green_x:
                self._get_distance(hook_x, green_x, "Green")
            elif red_x:
                self._get_distance(hook_x, red_x, "Red")
