import cv2 as cv
import core
import time
# from player import Player
from vision import Vision

vision = Vision("firefox")
needle = cv.imread(r"./src/objects/fish_store_logo.jpg")
haystack = cv.imread(r"./src/scenes/fish_caught.jpg")

# player = Player("BEZRCoder")

def __main__():
    print("Script initiated", end="")
    time.sleep(.5)
    
    for i in range(3):
        print(".", end="")
        time.sleep(1)
        
    print("Running")
    start_game_loop()
        

def start_game_loop():
    print("Starting game loop")
    fps_counter = 0
    
    while True:
        scene = vision.screenshot()
        vision.find(needle=needle, haystack=scene)
        
        # player.start_listeners()
        
        if cv.waitKey(1) == ord("f"):
            fps_counter = core.fps(fps_counter)

        if cv.waitKey(1) == ord("q"):
            cv.destroyAllWindows()
            break
        
if __name__ == "__main__":
    __main__()
