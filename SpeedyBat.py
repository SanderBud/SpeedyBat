import os
import time
import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageAnnotatorApp:
    def __init__(self, master):
        self.master = master
        master.title("SpeedyBat")

        self.button_frame_width = 150
        self.button_width = 10

        self.folder_path = ""
        self.image_names = []
        self.image_index = -1

        self.social_call_counter = 0
        self.feeding_buzz_counter = 0
        self.none_var = tk.BooleanVar()
        self.bat_var = tk.BooleanVar()

        self.annotation_changes = 0
        self.df = None

        self.bindings = {}  # Dictionary to store original bindings
        self.unbind_keys = False
        self.master.geometry("800x600")
        self.create_widgets()
        self.bind_keys()

    def create_widgets(self):

        # Create a frame to contain buttons and image label
        self.button_frame = tk.Frame(self.master, width=self.button_frame_width)
        self.button_frame.place(x=10, rely=0.5, anchor="w")

        # Create select folder button
        self.select_folder_button = tk.Button(self.button_frame,
                                              text="Select Folder",
                                              command=self.select_folder,
                                              width=self.button_width)
        self.select_folder_button.grid(row=0, column=0, sticky="w", pady=(10, 10))

        # Button social call counter
        self.social_call_button = tk.Button(self.button_frame,
                                            text="Social Call",
                                            command=self.increment_social_call,
                                            width=self.button_width)
        self.social_call_button.grid(row=1, column=0, sticky="w")

        self.social_call_counter_label = tk.Label(self.button_frame,
                                                  text=self.social_call_counter)
        self.social_call_counter_label.grid(row=1, column=1, sticky="w")

        self.social_call_button_sub = tk.Button(self.button_frame,
                                                text="-",
                                                command=self.sub_social_call)
        self.social_call_button_sub.grid(row=1, column=2, sticky="w")

        # Button feeding buzz counter
        self.feeding_buzz_button = tk.Button(self.button_frame,
                                             text="Feeding buzz",
                                             command=self.increment_feeding_buzz,
                                             width=self.button_width)
        self.feeding_buzz_button.grid(row=2, column=0, sticky="w")

        self.feeding_buzz_counter_label = tk.Label(self.button_frame, text=self.feeding_buzz_counter)
        self.feeding_buzz_counter_label.grid(row=2, column=1, sticky="w")

        self.feeding_buzz_button_sub = tk.Button(self.button_frame,
                                                 text="-",
                                                 command=self.sub_feeding_buzz)
        self.feeding_buzz_button_sub.grid(row=2, column=2, sticky="w")

        # None checkbox
        self.none_checkbox = tk.Checkbutton(self.button_frame, text="None", variable=self.none_var, onvalue=True,
                                            offvalue=False)
        self.none_checkbox.grid(row=3, column=0, sticky="w")

        # Bat checkbox
        self.bat_checkbox = tk.Checkbutton(self.button_frame, text="Bat", variable=self.bat_var, onvalue=True,
                                            offvalue=False)
        self.bat_checkbox.grid(row=4, column=0, sticky="w")

        # < and > button
        self.previous_image_button = tk.Button(self.button_frame, text="<", command=self.previous_image)
        self.previous_image_button.grid(row=5, column=0, sticky="w", pady=(10,10))

        self.next_image_button = tk.Button(self.button_frame, text=">", command=self.next_image)
        self.next_image_button.grid(row=5, column=0, sticky="e", pady=(10,10))

        # Notes
        self.note_text = tk.Text(self.button_frame, height=2, width=self.button_width, wrap="char")
        self.note_text.grid(row=6, column=0, sticky="w", pady=(10,10))

        # Open file button
        self.open_file_button = tk.Button(self.button_frame,
                                          text="Open File",
                                          command=self.open_current_file,
                                          width=self.button_width)
        self.open_file_button.grid(row=7, column=0, sticky="w")

        # Quit button
        self.quit_button = tk.Button(self.button_frame,
                                          text="Quit",
                                          command=self.quit,
                                          width=self.button_width)
        self.quit_button.grid(row=8, column=0, sticky="w", pady=(10,10))

        # Find next unannotated image
        self.next_unannotated_button = tk.Button(self.button_frame,
                                          text="Next to \nannotate",
                                          command=self.next_unannotated_image,
                                          width=self.button_width)
        self.next_unannotated_button.grid(row=9, column=0, sticky="w")

        # Image viewer
        self.master.update_idletasks()
        window_width = self.master.winfo_width()
        image_label_width = window_width * 0.95 - self.button_frame_width

        self.image_label = tk.Label(self.master)
        self.image_label.place(x=self.button_frame_width, y=0, width=image_label_width, relheight=1)

        # Essential binds
        self.note_text.bind("<FocusIn>", lambda event: self.textbox_focused())
        self.master.bind("<Escape>", lambda event: self.unfocus_text())

    def bind_keys(self):
        # Bindings
        self.bindings["<s>"] = self.master.bind("<s>", lambda event: self.increment_social_call())
        self.bindings["<Shift-S>"] = self.master.bind("<Shift-S>", lambda event: self.sub_social_call())
        self.bindings["<f>"] = self.master.bind("<f>", lambda event: self.increment_feeding_buzz())
        self.bindings["<Shift-F>"] = self.master.bind("<Shift-F>", lambda event: self.sub_feeding_buzz())
        self.bindings["<b>"] = self.master.bind("<b>", lambda event: self.toggle_bat())
        self.bindings["<n>"] = self.master.bind("<n>", lambda event: self.toggle_none())
        self.bindings["<space>"] = self.master.bind("<space>", lambda event: self.next_image())
        self.bindings["<r>"] = self.master.bind("<r>", lambda event: self.previous_image())
        self.bindings["<Shift-Escape>"] = self.master.bind("<Shift-Escape>", lambda event: self.quit())

    def open_current_file(self):
        current_file_path = os.path.join(self.folder_path, self.image_names[self.image_index])
        file_name = os.path.basename(current_file_path)
        wav_file_name = file_name[4:].split(".")[0] + ".wav"  # removes "IMG_", removes ".jpg", adds ".wav"
        path = os.path.abspath(os.path.join(current_file_path, "../.."))
        wav_path = os.path.join(path, wav_file_name)
        print(wav_path)
        try:
            os.startfile(wav_path)
        except FileNotFoundError:
            print("Unable to open file. Please check your default application settings.")

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.image_names = [f for f in os.listdir(self.folder_path) if f.endswith('.png') or f.endswith('.jpg')]
            self.image_index = 0
            self.load_annotations()
            self.find_next_image_without_annotations()
            self.show_image()

    def find_next_image_without_annotations(self):
        while self.image_index < len(self.image_names):
            social_call_value = self.df.at[self.image_index, 'Social Call']
            feeding_buzz_value = self.df.at[self.image_index, 'Feeding Buzz']
            none_value = self.df.at[self.image_index, 'None']
            bat_value = self.df.at[self.image_index, 'Bat']

            # If annotation is found in any column, move to the next image
            if social_call_value > 0 or feeding_buzz_value > 0 or none_value == 'x' or bat_value == 'x':
                self.image_index += 1
            else:
                break

        # If all images have annotations, reset the index
        if self.image_index == len(self.image_names):
            self.image_index = 0


    def load_annotations(self):
        excel_file_path = os.path.join(self.folder_path, 'annotations.xlsx')

        # Check if the annotations Excel file exists
        if os.path.exists(excel_file_path):
            self.df = pd.read_excel(excel_file_path)
        else:
            # Create a new DataFrame if the file doesn't exist
            self.df = pd.DataFrame({'Image Name': self.image_names,
                                   'Social Call': [0] * len(self.image_names),
                                   'Feeding Buzz': [0] * len(self.image_names),
                                   'None': [''] * len(self.image_names),
                                   'Bat': [''] * len(self.image_names),
                                   'Notes': [''] * len(self.image_names)})


    def check_annotations(self):
        # Get the current image name
        index = self.image_index

        # Check 'Social Call' and 'Feeding Buzz' columns for current image
        social_call_value = self.df.at[index, 'Social Call']
        feeding_buzz_value = self.df.at[index, 'Feeding Buzz']
        none_value = self.df.at[index, 'None']
        bat_value = self.df.at[index, 'Bat']
        note_value = self.df.at[index, "Notes"]

        # Change values according to previous annotations
        self.social_call_counter_label.config(text=int(social_call_value))
        self.social_call_counter = int(social_call_value)

        self.feeding_buzz_counter_label.config(text=int(feeding_buzz_value))
        self.feeding_buzz_counter = int(feeding_buzz_value)

        self.none_var.set(none_value == 'x')
        self.bat_var.set(bat_value == 'x')

        self.note_text.delete("1.0", tk.END)
        if str(note_value) != "nan":
            self.note_text.insert(tk.END, note_value)


    def show_image(self):
        if self.image_index < 0:
            return

        image_path = os.path.join(self.folder_path, self.image_names[self.image_index])
        image = Image.open(image_path)
        w, h = self.master.winfo_width(), self.master.winfo_height()  # Get window width and height
        image.thumbnail((w, h))  # Resize the image to fit the window
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo

        window_width = self.master.winfo_width()
        image_label_width = window_width * 0.95 - self.button_frame_width

        # Update the placement of the image label
        self.image_label.place(x=self.button_frame_width, y=0, width=image_label_width, relheight=1)

        # Change title to image name
        self.master.title(os.path.basename(image_path))


    def next_image(self):
        self.update_annotations()
        self.image_index = (self.image_index + 1) % len(self.image_names)
        self.show_image()
        self.check_annotations()


    def next_unannotated_image(self):
        self.find_next_image_without_annotations()
        self.show_image()
        self.check_annotations()


    def previous_image(self):
        self.update_annotations()
        self.image_index = (self.image_index - 1) % len(self.image_names)
        self.show_image()
        self.check_annotations()


    def textbox_focused(self):
        # Unbind all but unfocus keybinds
        for key, binding_id in self.bindings.items():
            self.master.unbind(key, binding_id)


    def unfocus_text(self):
        root.focus()
        self.bind_keys()


    def increment_social_call(self):
        self.social_call_counter += 1
        self.social_call_counter_label.config(text=self.social_call_counter)

        if self.social_call_counter > 0:
            self.bat_var.set(True)


    def sub_social_call(self):
        if self.social_call_counter == 0:
            return

        self.social_call_counter -= 1
        self.social_call_counter_label.config(text=self.social_call_counter)

        if self.social_call_counter == 0 and self.feeding_buzz_counter == 0:
            self.bat_var.set(False)


    def increment_feeding_buzz(self):
        self.feeding_buzz_counter += 1
        self.feeding_buzz_counter_label.config(text=self.feeding_buzz_counter)

        if self.feeding_buzz_counter > 0:
            self.bat_var.set(True)


    def sub_feeding_buzz(self):
        if self.feeding_buzz_counter == 0:
            return

        self.feeding_buzz_counter -= 1
        self.feeding_buzz_counter_label.config(text=self.feeding_buzz_counter)

        if self.social_call_counter == 0 and self.feeding_buzz_counter == 0:
            self.bat_var.set(False)


    def toggle_none(self):
        self.none_var.set(not self.none_var.get())

        if self.none_var.get():
            time.sleep(0.1)
            self.next_image()


    def toggle_bat(self):
        self.bat_var.set(not self.bat_var.get())


    def quit(self):
        self.update_annotations(force=True)
        root.destroy()


    def update_annotations(self, force=False):
        if self.df is None:
            return

        index = self.image_index

        # Update cells
        self.df.at[index, 'Social Call'] = self.social_call_counter
        self.df.at[index, 'Feeding Buzz'] = self.feeding_buzz_counter
        self.df.at[index, 'None'] = 'x' if self.none_var.get() else ''
        self.df.at[index, 'Bat'] = 'x' if self.bat_var.get() else ''
        self.df.at[index, 'Notes'] = self.note_text.get("1.0", "end-1c")

        # Another update done
        self.annotation_changes += 1
        print(self.annotation_changes)

        # Save the DataFrame to the annotations Excel file every 10 changes
        if self.annotation_changes >= 10 or force:
            excel_file_path = os.path.join(self.folder_path, 'annotations.xlsx')
            self.df.to_excel(excel_file_path, index=False)
            self.annotation_changes = 0  # Reset the counter after saving


if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')
    app = ImageAnnotatorApp(root)
    root.mainloop()
