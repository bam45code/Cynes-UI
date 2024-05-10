import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from cynes import *
import numpy as np
import time

class NES_Emulator_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cynes NES Emulator")

        # Initialize NES emulator
        self.nes = None

        # Map keycodes to NES inputs
        self.key_mappings = {
            "Up": NES_INPUT_UP,
            "Down": NES_INPUT_DOWN,
            "Left": NES_INPUT_LEFT,
            "Right": NES_INPUT_RIGHT,
            "z": NES_INPUT_A,
            "x": NES_INPUT_B,
            "a": NES_INPUT_SELECT,
            "s": NES_INPUT_START
        }

        # Desired FPS
        self.desired_fps = 60.098814
        # Time for one frame in milliseconds
        self.frame_time = 1 / self.desired_fps

        # Set scaling factor for video output
        self.scaling_factor = 2

        # Menu Bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM", command=self.open_rom)
        file_menu.add_command(label="Exit", command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        # Calculate the canvas size based on scaling factor
        self.canvas_width = 256 * self.scaling_factor
        self.canvas_height = 240 * self.scaling_factor

        # Canvas to display emulator output
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack()

        # Bind key events
        self.root.bind("<KeyPress>", self.key_pressed)
        self.root.bind("<KeyRelease>", self.key_released)

        # Initialize last frame time
        self.last_frame_time = 0

    def key_pressed(self, event):
        key = event.keysym
        if key in self.key_mappings:
            if self.nes:
                self.nes.controller |= self.key_mappings[key]

    def key_released(self, event):
        key = event.keysym
        if key in self.key_mappings:
            if self.nes:
                self.nes.controller &= ~self.key_mappings[key]

    def open_rom(self):
        rom_path = filedialog.askopenfilename(title="Select NES ROM", filetypes=[("NES ROM Files", "*.nes")])
        if rom_path:
            if self.nes:
                self.nes.close()
            self.nes = NES(rom_path)
            self.last_frame_time = time.time()
            self.update_emulator_output()

    def exit(self):
        if self.nes:
            self.nes.close()
        self.root.quit()

    def update_emulator_output(self):
        if self.nes:
            framebuffer = self.nes.step()
            screenshot_image = Image.fromarray(framebuffer)
            screenshot_image = screenshot_image.resize((self.canvas_width, self.canvas_height), Image.NEAREST)  # Resize the image
            screenshot_photo = ImageTk.PhotoImage(screenshot_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_photo)
            self.canvas.image = screenshot_photo

            # Calculate the time for one frame based on the desired frame rate
            self.frame_time = 1 / self.desired_fps

            # Calculate the time elapsed since the last frame
            current_time = time.time()
            elapsed_time = current_time - self.last_frame_time
            self.last_frame_time = current_time

            # Calculate the time to wait until the next frame
            wait_time = self.frame_time - elapsed_time

            if wait_time > 0:
                self.root.after(int(wait_time * 1000), self.update_emulator_output)
            else:
                # If the frame took longer than expected, update immediately
                self.root.after(0, self.update_emulator_output)


if __name__ == "__main__":
    root = tk.Tk()
    app = NES_Emulator_GUI(root)
    root.mainloop()
