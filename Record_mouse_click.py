import time

import pyautogui
import pywinauto.keyboard
import pywinauto.mouse as mouse
import keyboard
from pynput.mouse import Listener as mouse_Listener
from pynput.keyboard import Listener as keyboard_Listener
from pynput.keyboard import Key
import os
import json
from PIL import ImageGrab, ImageDraw
import time as t


class MouseClickRecorder:
    def __init__(self):
        self.positions = []
        self.step = 0

    def record(self):
        while True:  # ! TODO find a way to use keyboard even listener instead of nested while loop
            if keyboard.is_pressed('space'):
                def on_press(key):
                    if key == Key.esc:
                        # Stop listener
                        raise Exception("Done!")

                def on_click(x, y, button, pressed):
                    if pressed:
                        self.step += 1
                        self.positions.append({"type": "click", "position": (x, y)})
                        print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
                        self.record_click_snap()
                        t.sleep(1)

                def on_scroll(x, y, dx, dy):
                    self.step += 1
                    self.positions.append({"type": "scroll", "position": (x, y), "wheel_dist": (dx, dy)})
                    print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))

                with mouse_Listener(
                        on_click=on_click, on_scroll=on_scroll) as m_listener, \
                        keyboard_Listener(on_press=on_press) as k_listener:
                    try:
                        k_listener.join()
                        m_listener.join()

                    except Exception as e:
                        print(f"Recording stopped by{e}")
                        print(f"Total steps: {self.step}")
                        self.save_positions()
                        return 0

    def record_click_snap(self):
        # Take a screenshot

        screenshot = ImageGrab.grab()

        # Get the mouse position
        mouse_pos = pyautogui.position()
        draw = ImageDraw.Draw(screenshot)
        # show the mouse position with a red circle
        draw.arc((mouse_pos.x - 5, mouse_pos.y - 5, mouse_pos.x + 5, mouse_pos.y + 5), 0, 360, fill='red')
        # create a folder called screenshots and save the screenshot
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')

        screenshot.save(f"screenshots/{self.step}.png")
        # confirm = input(f"Is this the correct position? ({mouse_pos.x}, {mouse_pos.y}) [y/n]: ")

        # If the user confirms the position, return it
        # if confirm.lower() == 'y':
        #     # Convert the position to the correct size
        #     self.positions.append(mouse_pos)
        #     print("Position confirmed")

    def convert_position(self, position, from_size, to_size):
        # Calculate the scale factor
        scale_x = to_size[0] / from_size[0]
        scale_y = to_size[1] / from_size[1]
        # Scale the position
        scaled_pos = (int(position[0] * scale_x), int(position[1] * scale_y))

        return scaled_pos

    def move_mouse(self, positions):
        # Move the mouse to the position
        if positions:
            self.positions = positions
        for position in self.positions:
            t.sleep(2)
            if position["type"] == "click":
                pywinauto.mouse.click(coords=(position["position"][0], position["position"][1]))
            elif position["type"] == "scroll":
                pywinauto.mouse.scroll(coords=(position["position"][0], position["position"][1]),
                                       wheel_dist=position["wheel_dist"][1])

    def save_positions(self):
        """ Save the recorded positions to a dictionary"""
        try:
            with open('positions.json', 'w') as f:
                json.dump(self.positions, f)
        except Exception as e:
            raise Exception("encountered error while saving positions", e)


if __name__ == '__main__':
    # Create a new recorder

    recorder = MouseClickRecorder()
    recorder.record()
    recorder.save_positions()
    # with open('mouse_move_data/positions.json', 'r') as f:
            # positions = json.load(f)
            # recorder.move_mouse(positions)

    # while True:
    #     if keyboard.is_pressed('space'):
    #         recorder.record_click()
    #     elif keyboard.is_pressed('esc'):
    #         break
    # print(recorder.positions)
