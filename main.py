import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from cynes import NESHeadless as NES
from cynes import (
    NES_INPUT_A, NES_INPUT_B, NES_INPUT_DOWN, NES_INPUT_LEFT,
    NES_INPUT_RIGHT, NES_INPUT_SELECT, NES_INPUT_START, NES_INPUT_UP
)
import numpy as np
import time
import pickle
import os

class NES_Emulator_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cynes NES Emulator")
        self.root.iconbitmap("nes.ico")

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
        self.frame_time = 1 / self.desired_fps

        # Set scaling factor for video output
        self.scaling_factor = 2

        # Menu Bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM", command=self.open_rom)
        file_menu.add_command(label="Save State", command=self.save_state)
        file_menu.add_command(label="Load State", command=self.load_state)
        file_menu.add_command(label="Exit", command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_command(label="Reset", command=self.reset_emulator)
        menubar.add_command(label="Pause", command=self.pause_emulator)
        menubar.add_command(label="Resume", command=self.resume_emulator)
        menubar.add_command(label="Help", command=self.show_help)
        self.root.config(menu=menubar)

        # Calculate the canvas size based on scaling factor
        self.canvas_width = 256 * self.scaling_factor
        self.canvas_height = 240 * self.scaling_factor

        # Canvas to display emulator output
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack()

        # Status Bar
        self.status_bar = tk.Label(self.root, text="Welcome to Cynes NES Emulator", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind key events
        self.root.bind("<KeyPress>", self.key_pressed)
        self.root.bind("<KeyRelease>", self.key_released)

        self.last_frame_time = 0

        # Directory for saving states
        self.save_dir = "saves"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        # Pause flag
        self.paused = False

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

    def reset_emulator(self):
        if self.nes:
            self.nes.reset()
            self.last_frame_time = time.time()
            self.update_emulator_output()
            self.update_status("Emulator reset.")

    def open_rom(self):
        rom_path = filedialog.askopenfilename(title="Select NES ROM", filetypes=[("NES ROM Files", "*.nes")])
        if rom_path:
            if self.nes:
                self.nes.close()
            self.nes = NES(rom_path)
            self.last_frame_time = time.time()
            self.update_emulator_output()
            self.update_status(f"ROM loaded: {rom_path}")

    def save_state(self):
        if self.nes:
            state = self.nes.save()
            try:
                file = filedialog.asksaveasfile(mode="wb", filetypes=[("NES Save Files", "*.pkl")], title="Save State", initialfile="save.pkl", initialdir=self.save_dir)
                if file:
                    with file as f:
                        pickle.dump(state, f)
                    self.update_status("State saved successfully.")
            except Exception as e:
                self.update_status(f"Failed to save state: {e}")
                messagebox.showerror("Save State Error", f"Failed to save state: {e}")

    def load_state(self):
        try:
            file = filedialog.askopenfile(mode="rb", filetypes=[("NES Save Files", "*.pkl")], title="Load State", initialdir=self.save_dir)
            if file:
                with file as f:
                    state = pickle.load(f)
                    if self.nes:
                        self.nes.load(state)
                self.update_status("State loaded successfully.")
        except FileNotFoundError:
            self.update_status("No save state found.")
            messagebox.showerror("Load State Error", "No save state found.")
        except Exception as e:
            self.update_status(f"Failed to load state: {e}")
            messagebox.showerror("Load State Error", f"Failed to load state: {e}")

    def exit(self):
        if self.nes:
            self.nes.close()
        self.root.quit()

    def update_emulator_output(self):
        if self.nes and not self.paused:
            framebuffer = self.nes.step()
            screenshot_image = Image.fromarray(framebuffer)
            screenshot_image = screenshot_image.resize((self.canvas_width, self.canvas_height), Image.NEAREST)  # Resize the image
            screenshot_photo = ImageTk.PhotoImage(screenshot_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_photo)
            self.canvas.image = screenshot_photo

            current_time = time.time()
            elapsed_time = current_time - self.last_frame_time
            self.last_frame_time = current_time

            wait_time = self.frame_time - elapsed_time
            if wait_time > 0:
                self.root.after(int(wait_time * 1000), self.update_emulator_output)
            else:
                self.root.after(0, self.update_emulator_output)

    def pause_emulator(self):
        self.paused = True
        self.update_status("Emulator paused.")

    def resume_emulator(self):
        self.paused = False
        self.last_frame_time = time.time()
        self.update_emulator_output()
        self.update_status("Emulator resumed.")

    def update_status(self, message):
        self.status_bar.config(text=message)

    def show_help(self):
        help_message = (
            "Cynes NES Emulator Help\n\n"
            "Controls:\n"
            "  Arrow Keys: D-Pad\n"
            "  Z: A Button\n"
            "  X: B Button\n"
            "  A: Select\n"
            "  S: Start\n\n"
            "Menu Options:\n"
            "  File > Open ROM: Load a new ROM\n"
            "  File > Save State: Save the current state\n"
            "  File > Load State: Load a saved state\n"
            "  File > Exit: Exit the emulator\n"
            "  Reset: Reset the emulator\n"
            "  Pause: Pause the emulator\n"
            "  Resume: Resume the emulator\n\n"
            "For more information, visit the Cynes documentation."
        )
        messagebox.showinfo("Help", help_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = NES_Emulator_GUI(root)
    root.mainloop()
