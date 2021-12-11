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

CLICK_PRESS_DOWN_DURATION = 1
HOOK_DURATION = .5


class Player:

    player_name = None
    
    basket_max_len = 6
    total_fish_caught = 0
    fish_in_basket = 0
    
    height_offset = None
    window_w, window_h = pyautogui.size()
    
    center_x = 0
    center_y = 0

    mov_status = PLAYER_STATUS_IDLE
    _fishing_hook_pressed = "release"

    def __init__(self, player_name, basket_count=6, height_offset=300):
        self.player_name = player_name
        self.height_offset = height_offset
        self.basket_max_len = basket_count
        self.center_x = round(self.window_w / 2)
        self.center_y = round(self.window_h / 2)
        
    def get_is_basket_full(self):
        return self.fish_in_basket >= self.basket_max_len
        

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
        self.click_and_release(pos_x, pos_y)
        
    def fishing_hook_click(self, pressed):                
        if self._fishing_hook_pressed == pressed:
            return
        
        self._fishing_hook_pressed = pressed
        
        if pressed == "press":
            pyautogui.mouseDown()
        elif pressed == "release":
            pyautogui.mouseUp()
            
    def add_fish_count(self):
        self.fish_in_basket += 1
        self.total_fish_caught += 1

        print(f"Total fish caught: {self.total_fish_caught}")
        print(f"Fish in basket: {self.fish_in_basket}")
           
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
