import pyautogui
import time

PLAYER_STATUS_IDLE = "idle"
PLAYER_STATUS_MOVING = "moving"
PLAYER_STATUS_FISHING = "fishing"
PLAYER_STATUS_PULLING = "pulling"
PLAYER_STATUS_SELLING = "selling"

STANDARD_STATUS = (
    PLAYER_STATUS_IDLE,
    PLAYER_STATUS_MOVING,
    PLAYER_STATUS_FISHING,
    PLAYER_STATUS_SELLING,
    PLAYER_STATUS_PULLING,
)

CLICK_PRESS_DOWN_DURATION = .2
HOOK_DURATION = .5


class Player:

    player_name = None
    
    basket_max_len = 6
    total_fish_caught = 0
    total_fish_lost = 0
    fish_in_basket = 0
    
    height_offset = None
    window_w, window_h = pyautogui.size()
    
    center_x = 0
    center_y = 0

    mov_status = PLAYER_STATUS_IDLE
    _fishing_hook_pressed = "release"

    def __init__(self, player_name, fish_in_basket, basket_count=6, height_offset=300):
        self.player_name = player_name
        self.height_offset = height_offset
        self.basket_max_len = basket_count
        self._set_window_props()
        self.fish_in_basket = fish_in_basket
        
    def _set_window_props(self):
        self.window_w, self.window_h = pyautogui.size()
        self.center_x = round(self.window_w / 2)
        self.center_y = round(self.window_h / 2)
        
        print(self.window_w, self.window_h, self.center_x, self.center_y )
        
        if 0 >= self.center_x:
            raise NameError("Window size error")
        
    def get_is_basket_full(self):
        return self.fish_in_basket >= self.basket_max_len
    
    def reload_game(self):
        self.click_self()
        
        pyautogui.press("f5")
        time.sleep(.8)
        pyautogui.press("enter")
    
    def fish_sold(self):
        self.fish_in_basket = 0
    
    def log_fish_lost(self):
        self.total_fish_lost += 1
        self._fishing_hook_pressed = "release"
        self.click_self()
        
    def click_self(self, duration=.2):
        pyautogui.click(self.center_x, self.center_y, 1, duration)

    def change_status(self, status):
        if not status in STANDARD_STATUS:
            raise NameError("Invalid status {}").format(status)  # Nonecompliant
        else:
            self.mov_status = status

    def move_mouse(self, x, y):
        pyautogui.moveTo(x, y)

    def click_and_release(self, x, y, duration=CLICK_PRESS_DOWN_DURATION):
        self.move_mouse(x, y)
        pyautogui.mouseDown()
        time.sleep(duration)
        pyautogui.mouseUp()

    def start_fishing(self):
        print("Start fishing")
        time.sleep(1)

        self.change_status(PLAYER_STATUS_FISHING)

        pos_x = round(self.window_w / 2)
        pos_y = round(self.window_h / 2) + self.height_offset
        self.click_and_release(pos_x, pos_y, 1.1)
        
    def fishing_hook_click(self, pressed):                
        if self._fishing_hook_pressed == pressed:
            return
        
        self._fishing_hook_pressed = pressed
        
        if pressed == "press":
            pyautogui.mouseDown()
        elif pressed == "release":
            pyautogui.mouseUp()
            
    def log_fish_count(self):
        print(f"Total fish caught: {self.total_fish_caught}")
        print(f"Total fish lost: {self.total_fish_lost}")
        print(f"Fish in basket: {self.fish_in_basket}/{self.basket_max_len}")
            
    def add_fish_count(self):
        self.fish_in_basket += 1
        self.total_fish_caught += 1
        self._fishing_hook_pressed = "release"
        self.log_fish_count()
           
    def move(self, direction, duration=0.2):
        print("Character moving direction {}".format(direction))
        
        if direction == "south":
            pyautogui.keyDown("s")
            time.sleep(duration)
            pyautogui.keyUp("s")
            
        elif direction == "north":
            pyautogui.keyDown("w")
            time.sleep(duration)
            pyautogui.keyUp("w")
            
        elif direction == "east":
            pyautogui.keyDown("d")
            time.sleep(duration)
            pyautogui.keyUp("d")
            
        elif direction == "west":
            pyautogui.keyDown("a")
            time.sleep(duration)
            pyautogui.keyUp("a")
