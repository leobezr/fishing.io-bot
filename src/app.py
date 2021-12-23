from bot import Bot
import cv2 as cv
import time

def __main__():
    print("Script initiated")
    time.sleep(2)

    print("Running")
    start_game_loop()


def start_game_loop():
    print("Starting game loop")

    bot = Bot(fish_in_basket=0, max_basket=11)

    while True:
        bot.run()

        if cv.waitKey(1) == ord("q"):
            break

    cv.destroyAllWindows()


if __name__ == "__main__":
    __main__()
