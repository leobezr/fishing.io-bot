from pyautogui import sleep
from bot import Bot
import cv2 as cv
import core
import time

def __main__():
    print("Script initiated")
    time.sleep(2)
        
    print("Running")
    start_game_loop()
        

def start_game_loop():
    print("Starting game loop")
    fps_counter = 0
    
    bot = Bot()
    
    while True:
        bot.run()
        
        if cv.waitKey(1) == ord("f"):
            fps_counter = core.fps(fps_counter)

        if cv.waitKey(1) == ord("q"):
            cv.destroyAllWindows()
            break
        
if __name__ == "__main__":
    __main__()
