from pynput import keyboard


def on_press(key, callback):
    try:
        callback()
    except AttributeError:
        print("special key {0} pressed".format(key))


def on_release(key, callback):
    callback()
    if key == keyboard.Key.esc:
        # Stop listener
        return False


# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()
