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

# GAME
PLAYER_DISCONNECTED = cv.imread(r"./src/objects/player_disconnected.jpg")


# DEFAULTS
POS_LEAVE_STORE_X = 150
POS_LEAVE_STORE_Y = 500

BOT_IN_ACTION = "action"
BOT_IDLE = "idle"

DEBUG_MODE = False
SAFE_TIMEOUT = 33
DISCONNECT_WAIT = 33

FISHING_BAR_HEIGHT = 200
FISHING_BAR_WIDTH = 800
FISHING_HOOK_OFFSET_Y = 100


class Bot:

    player = None
    bot_in_action = False
    scene = None

    bot_got_stuck_timeout = time.time() + SAFE_TIMEOUT
    bot_pending_reload = False

    is_disconnected = False
    disconnected_times = 0
    disconnected_time_lock = 0

    _hook_bar_position = (0, 0)
    _hook_position_found = False

    def __init__(self, fish_in_basket=0, max_basket=6):
        self.player = Player(
            "BEZR Coder", basket_count=max_basket, fish_in_basket=fish_in_basket
        )

        print("Bot setup ready")

    def run(self):
        self.refresh_scene()
        self.show_timeout_countdown()
        self.check_if_disconnected()

        if self.is_bot_lock():
            return
        elif self.is_disconnected:
            self.reloading_script()
        elif self.check_bot_action():
            self.check_target_conditions()

    def check_if_disconnected(self):
        self.refresh_scene()

        if self.is_bot_lock():
            return

        if vision.find(PLAYER_DISCONNECTED, self.scene):
            print("~ Bot disconnected ~")

            self.is_disconnected = True
            self.disconnected_time_lock = time.time() + DISCONNECT_WAIT
            self.player.reload_game()

    def is_bot_lock(self):
        return time.time() < self.disconnected_time_lock

    def reloading_script(self):
        self.refresh_scene()
        
        if vision.find(PLAYER_DISCONNECTED, self.scene):
            return

        self.refresh_timeout("Disconnected")
        
        self.player.click_self()
        self.player.move("west", 6)
        self.player.move("south", 2)
        self.player.move("east", 2.3)
        self.player.move("south", 4)
        
        self.in_action(BOT_IDLE)
        self.disconnected_times += 1
        self.is_disconnected = False

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
            self.auto_manage_hook()
            return False

        return self.check_timeout()

    def check_target_conditions(self):
        if self.player.get_is_basket_full():
            self.move_to_store()
        elif vision.find(FISH_HOOKED, self.scene):
            self.player.click_and_release(self.player.center_x, self.player.center_y)
            time.sleep(1)
            self.auto_manage_hook()

    def show_timeout_countdown(self):
        if self.is_disconnected:
            bot_locked_remaining = int(self.disconnected_time_lock - time.time())
            print(f"Bot disconnected, waiting reload {bot_locked_remaining}s")
            print("--------------------------------------------------------------")
            return

        timeout = int(self.bot_got_stuck_timeout - time.time())

        if timeout < 0:
            print("Bot timeout")
        else:
            print(f"Playing as {self.player.player_name}")
            print(f"Bot disconnected: {self.disconnected_times} times")
            self.player.log_fish_count()
            print("--------------------------------------------------------------")
            print(f"Next timeout: {timeout}")
            print("--------------------------------------------------------------")

    def open_store(self):
        print("Opening store")
        self.refresh_scene()

        if vision.find(STORE_SHOP, self.scene):
            x, y = vision.find_position(STORE_SHOP, self.scene)
            self.player.click_and_release(x, y, 0.3)
            self.sell_fish()
        else:
            time.sleep(1)
            self.move_to_store()

    def move_to_store(self):
        self.refresh_timeout("Fish basket full, going to store")
        self.in_action(BOT_IN_ACTION)
        self.player.change_status("moving")

        self.player.click_self()
        self.player.move("north", 2)
        self.open_store()

    def move_back_fishing_point(self):
        self.player.move("south", 4)
        self.player.change_status("idle")
        self.in_action(BOT_IDLE)

    def leave_shop(self):
        self.player.fish_sold()
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
            self.refresh_timeout("Clicking on sell button")

            x, y = vision.find_position(STORE_SELL, self.scene)
            self.player.click_and_release(x, y)
            self._shop_action_confirm_sell()
        else:
            self.sell_fish()

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
        self.refresh_scene()

        if vision.find(STORE_OPENED, self.scene):
            self.refresh_timeout("Player selling fish")
            self.player.change_status("selling")
            self._shop_action_select_all()
        else:
            time.sleep(1)
            self.sell_fish()

    def _register_hook_pos(self):
        if self._hook_position_found:
            return

        (x, y) = vision.find_position(HOOK, vision.orange_mask(self.scene))

        self._hook_bar_position = (
            x - round(FISHING_BAR_WIDTH / 2),
            y - FISHING_HOOK_OFFSET_Y,
        )

        if self._hook_bar_position[0] > 0:
            self._hook_position_found = True
            print("Hook props set")

    def find_hook_position(self):
        self.refresh_scene()

        if vision.find(HOOK, vision.orange_mask(self.scene)):
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

    def _debug_masks(self, needle, scene, name):
        vision.find(needle, scene, show_window=True, silent=True)
        vision.show(scene, name)

    def auto_manage_hook(self):
        self.in_action(BOT_IN_ACTION)
        self.player.change_status("pulling")
        self.find_hook_position()

        x, y = self._hook_bar_position

        scene = vision.screenshot(x, y, FISHING_BAR_WIDTH, FISHING_BAR_HEIGHT)
        green_target = vision.green_mask(scene)
        red_target = vision.red_mask(scene)

        hook_x = vision.find_position(HOOK, vision.orange_mask(scene))[0]
        green_x = vision.find_position(STATUS_GREEN, green_target)[0]
        red_x = vision.find_position(STATUS_RED, red_target)[0]

        if DEBUG_MODE:
            self._debug_masks(STATUS_GREEN, green_target, "green view")
            self._debug_masks(STATUS_RED, red_target, "red view")
            self._debug_masks(HOOK, vision.orange_mask(scene), "Bot")

        if hook_x:
            self.refresh_timeout("Tracking hook")

            if green_x:
                self._get_distance(hook_x, green_x, "Green")
            elif red_x:
                self._get_distance(hook_x, red_x, "Red")
        else:
            waiting_time = 1.8
            print(f"Waiting sleep of {waiting_time} seconds")
            time.sleep(waiting_time)

            self.refresh_scene()
            print("Met the condition hook not found")

            if vision.find(FISH_TO_BASKET, vision.yellow_mask(self.scene)):
                print("Trying to close basket")
                self.refresh_timeout("Closing fish caught notification")
                self.add_fish_to_basket()
            elif not vision.find(HOOK, vision.orange_mask(self.scene)):
                print("Lost fish")
                cv.destroyAllWindows()
                self.in_action(BOT_IDLE)
                self.player.log_fish_lost()

    def add_fish_to_basket(self):
        self.refresh_scene()

        x, y = vision.find_position(
            FISH_TO_BASKET,
            vision.yellow_mask(self.scene),
            threshhold=0.7,
        )
        w, h = tuple(FISH_TO_BASKET.shape[1::-1])

        self.player.click_and_release(int(x + w / 2), int(y + h / 2))
        time.sleep(1)

        self.refresh_scene()

        if vision.find(FISH_TO_BASKET, vision.yellow_mask(self.scene)):
            self.add_fish_to_basket()
        else:
            self.player.add_fish_count()
            self.player.change_status("idle")
            self.in_action(BOT_IDLE)

    def start_fishing(self):
        self.refresh_timeout("Started fishing")
        self.in_action(BOT_IN_ACTION)

        self.player.start_fishing()
