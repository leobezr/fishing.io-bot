from player import Player
from vision import Vision
import numpy as np
import cv2 as cv
import time

vision = Vision("brave")


# FISHING TARGETS
HOOK = cv.imread(r"./src/objects/hook.jpg")
FISH_HOOKED = cv.imread(r"./src/objects/warning.jpg")
STATUS_GREEN = cv.imread(r"./src/objects/fishing_status_green.jpg")
STATUS_RED = cv.imread(r"./src/objects/fishing_status_red.jpg")
FISH_TO_BASKET = cv.imread(r"./src/objects/fish_caught_box.jpg")

# STORE TARGETS
STORE_OPENED = cv.imread(r"./src/objects/fish_store_logo.jpg")
STORE_SHOP = cv.imread(r"./src/objects/fish_shop.jpg")
STORE_SELECT_ALL = cv.imread(r"./src/objects/select_all.jpg")
STORE_SELL = cv.imread(r"./src/objects/sell_for.jpg")
STORE_SELL_CONFIRM = cv.imread(r"./src/objects/sell_confirm.jpg")


# DEFAULTS
POS_LEAVE_STORE_X = 150
POS_LEAVE_STORE_Y = 500

BOT_IN_ACTION = "action"
BOT_IDLE = "idle"

DEBUG_MODE = False
SAFE_TIMEOUT = 23

FISHING_BAR_HEIGHT = 200
FISHING_BAR_WIDTH = 800
FISHING_HOOK_OFFSET_Y = 100


class Bot:

    player = None
    bot_in_action = False
    scene = None
    bot_got_stuck_timeout = time.time() + SAFE_TIMEOUT

    _hook_found = False
    _hook_bar_position = (0, 0)

    def __init__(self):
        self.player = Player("BEZR Coder")
        print("Bot setup ready")

    def run(self):
        self.refresh_scene()
        self.show_timeout_countdown()

        if self.check_bot_action():
            self.check_target_conditions()

    def in_action(self, status=BOT_IN_ACTION):
        self.bot_in_action = status != BOT_IDLE

    def refresh_scene(self):
        if DEBUG_MODE:
            print("Scene refreshed")

        self.scene = vision.screenshot()

    def refresh_timeout(self, step_name):
        self.bot_got_stuck_timeout = time.time() + SAFE_TIMEOUT
        print(f"Time refreshed at [{step_name}]")

    def check_timeout(self):
        if time.time() >= self.bot_got_stuck_timeout:
            print("Bot got stuck, refreshed to idle")
            self.in_action(BOT_IDLE)

            if self.player.mov_status == "fishing":
                self.player.click_and_release(
                    self.player.center_x, self.player.center_y, 2
                )

            return False
        else:
            return True

    def check_bot_action(self):
        action = self.bot_in_action
        status = self.player.mov_status

        if not action:
            self.start_fishing()
            return False
        elif action and status == "pulling":
            self.find_hook_position()
            self.auto_manage_hook()
            return False

        return self.check_timeout()

    def check_target_conditions(self):
        if self.player.get_is_basket_full():
            self.move_to_store()
        elif vision.find(FISH_HOOKED, self.scene):
            self.player.click_and_release(self.player.center_x, self.player.center_y)
            self.auto_manage_hook()

    def show_timeout_countdown(self):
        timeout = int(self.bot_got_stuck_timeout - time.time())

        if timeout < 0:
            print("Bot timeout")
        else:
            print(f"Next timeout: {timeout}")

    def open_store(self):
        print("Opening store")
        self.refresh_scene()

        if vision.find(STORE_SHOP, self.scene):
            x, y = vision.find_position(STORE_SHOP, self.scene)
            self.player.click_and_release(x, y, 0.3)
            self.sell_fish()
        else:
            time.sleep(1)
            self.open_store()

    def move_to_store(self):
        self.refresh_timeout("Fish basket full, going to store")
        self.in_action(BOT_IN_ACTION)
        self.player.change_status("moving")

        self.player.move("north", 3)
        self.open_store()

    def move_back_fishing_point(self):
        self.player.move("south", 3)
        self.player.change_status("idle")
        self.in_action(BOT_IDLE)

    def leave_shop(self):
        self.refresh_scene()

        if vision.find(STORE_OPENED, self.scene):
            self.refresh_timeout("Leaving shop")

            self.player.click_and_release(POS_LEAVE_STORE_X, POS_LEAVE_STORE_Y, 0.3)

            if vision.find(STORE_OPENED, self.scene):
                self.leave_shop()
            else:
                self.move_back_fishing_point()

    def _shop_action_confirm_sell(self):
        self.refresh_scene()

        if vision.find(STORE_SELL_CONFIRM, self.scene):
            self.refresh_timeout("Confirm Sell")

            x, y = vision.find_position(STORE_SELL_CONFIRM, self.scene)
            self.player.click_and_release(x, y)
            self.leave_shop()
        else:
            self._shop_action_sell()

    def _shop_action_sell(self):
        self.refresh_scene()

        if vision.find(STORE_SELL, self.scene):
            self.refresh_timeout("Selling all fish")

            x, y = vision.find_position(STORE_SELL, self.scene)
            self.player.click_and_release(x, y)
            self._shop_action_confirm_sell()
        else:
            self._shop_action_sell()

    def _shop_action_select_all(self):
        self.refresh_scene()

        if vision.find(STORE_SELECT_ALL, self.scene):
            self.refresh_timeout("Selecting all fish in shop")

            x, y = vision.find_position(STORE_SELECT_ALL, self.scene)
            self.player.click_and_release(x, y, 0.5)
            self._shop_action_sell()
        else:
            print("Failed to find `Select All` button")
            self._shop_action_select_all()

    def sell_fish(self):
        if vision.find(STORE_OPENED, self.scene):
            self.refresh_timeout("Player selling fish")
            self.player.change_status("selling")
            self._shop_action_select_all()
        else:
            time.sleep(1)
            self.self_fish()

    def _register_hook_pos(self):
        (x, y) = vision.find_position(needle=HOOK, haystack=self.scene)
        self._hook_bar_position = (
            x - round(FISHING_BAR_WIDTH / 2),
            y - FISHING_HOOK_OFFSET_Y,
        )
        print("Hook props set")

    def find_hook_position(self):
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
        self.in_action(BOT_IN_ACTION)
        self.player.change_status("pulling")

        x, y = self._hook_bar_position
        scene = vision.screenshot(x, y, FISHING_BAR_WIDTH, FISHING_BAR_HEIGHT)

        green_target = vision.green_mask(scene)
        red_target = vision.red_mask(scene)

        green_x = vision.find_position(needle=STATUS_GREEN, haystack=green_target)[0]
        red_x = vision.find_position(needle=STATUS_RED, haystack=red_target)[0]
        hook_x = vision.find_position(needle=HOOK, haystack=scene)[0]

        if DEBUG_MODE:
            vision.find(
                needle=STATUS_GREEN,
                haystack=green_target,
                show_window=True,
                silent=True,
            )
            vision.find(
                needle=STATUS_RED, haystack=red_target, show_window=True, silent=True
            )
            vision.find(needle=HOOK, haystack=scene, show_window=True, silent=True)

            vision.show(green_target, "green view")
            vision.show(red_target, "red view")
            vision.show(scene)

        if hook_x:
            self.refresh_timeout("Tracking hook")
            
            if green_x:
                self._get_distance(hook_x, green_x, "Green")
            elif red_x:
                self._get_distance(hook_x, red_x, "Red")
                
        elif vision.find(FISH_TO_BASKET, self.scene):
            self.add_fish_to_basket()

    def add_fish_to_basket(self):
        self.refresh_scene()

        x, y = vision.find_position(FISH_TO_BASKET, self.scene)
        w, h = FISH_TO_BASKET.size
        
        self.player.click_and_release(int(x + w/2), int(y + h/2))
        time.sleep(1)

        self.refresh_scene()
        
        if vision.find(FISH_TO_BASKET, self.scene):
            self.add_fish_to_basket()
        else:
            self.player.add_fish_count()
            self.player.change_status("idle")
            self.in_action(BOT_IDLE)

    def start_fishing(self):
        self.refresh_timeout("Started fishing")
        self.in_action(BOT_IN_ACTION)

        self.player.start_fishing()
