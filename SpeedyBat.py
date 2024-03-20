import os
import time
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
        self.feeding_buzz_var = tk.BooleanVar()
        self.none_var = tk.BooleanVar()

        self.load_annotations()
        self.master.geometry("800x600")
        self.create_widgets()

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
        self.none_var = tk.BooleanVar()
        self.none_checkbox = tk.Checkbutton(self.button_frame, text="None", variable=self.none_var, onvalue=True,
                                            offvalue=False)
        self.none_checkbox.grid(row=3, column=0, sticky="w")

        # < and > button
        self.previous_image_button = tk.Button(self.button_frame, text="<", command=self.previous_image)
        self.previous_image_button.grid(row=4, column=0, sticky="w", pady=(10,10))

        self.next_image_button = tk.Button(self.button_frame, text=">", command=self.next_image)
        self.next_image_button.grid(row=4, column=0, sticky="e", pady=(10,10))

        # Open file button
        self.open_file_button = tk.Button(self.button_frame,
                                          text="Open File",
                                          command=self.open_current_file,
                                          width=self.button_width)
        self.open_file_button.grid(row=5, column=0, sticky="w")

        # Image viewwer
        self.image_label = tk.Label(self.master)
        self.image_label.place(x=self.button_frame_width, y=0, relwidth=1, relheight=1)  # Position image label
        self.master.update_idletasks()
        window_width = self.master.winfo_width()
        image_label_width = window_width * 0.95 - self.button_frame_width

        self.image_label = tk.Label(self.master)
        self.image_label.place(x=self.button_frame_width, y=0, width=image_label_width, relheight=1)  # Position image label

        # Bindings
        self.master.bind("<s>", self.increment_social_call_key)
        self.master.bind("<Shift-S>", self.sub_social_call_key)
        self.master.bind("<f>", self.increment_feeding_buzz_key)
        self.master.bind("<Shift-F>", self.sub_feeding_buzz_key)
        self.master.bind("<n>", self.toggle_none)
        self.master.bind("<space>", lambda event: self.next_image())
        self.master.bind("<r>", lambda event: self.previous_image())

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
        excel_file_path = os.path.join(self.folder_path, 'annotations.xlsx')

        df = pd.read_excel(excel_file_path)

        while self.image_index < len(self.image_names):
            current_image_name = self.image_names[self.image_index]
            social_call_value = df.loc[df['Image Name'] == current_image_name, 'Social Call'].iloc[0]
            feeding_buzz_value = df.loc[df['Image Name'] == current_image_name, 'Feeding Buzz'].iloc[0]
            none_value = df.loc[df['Image Name'] == current_image_name, 'None'].iloc[0]

            # If annotation is found in any column, move to the next image
            if social_call_value > 0 or feeding_buzz_value > 0 or none_value == 'x':
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
            df = pd.read_excel(excel_file_path)
        else:
            # Create a new DataFrame if the file doesn't exist
            df = pd.DataFrame({'Image Name': self.image_names,
                               'Social Call': [''] * len(self.image_names),
                               'Feeding Buzz': [''] * len(self.image_names),
                               'None': [''] * len(self.image_names)})

        # Save the DataFrame to the annotations Excel file
        df.to_excel(excel_file_path, index=False)

    def check_annotations(self):
        excel_file_path = os.path.join(self.folder_path, 'annotations.xlsx')

        # Check if the annotations Excel file exists
        if not os.path.exists(excel_file_path):
            return

        df = pd.read_excel(excel_file_path)

        # Get the current image name
        index = self.image_index
        current_image_name = self.image_names[index]

        # Check 'Social Call' and 'Feeding Buzz' columns for current image
        social_call_value = df.at[index, 'Social Call']
        feeding_buzz_value = df.at[index, 'Feeding Buzz']
        none_value = df.at[index, 'None']

        # Pre-check the checkboxes if 'x' is found in the corresponding column
        if social_call_value > 0:
            self.social_call_counter_label.config(text=int(social_call_value))
            self.social_call_counter = int(social_call_value)
        else:
            self.social_call_counter_label.config(text=0)
            self.social_call_counter = 0

        if feeding_buzz_value > 0:
            self.feeding_buzz_counter_label.config(text=int(feeding_buzz_value))
            self.feeding_buzz_counter = int(feeding_buzz_value)
        else:
            self.feeding_buzz_counter_label.config(text=0)
            self.feeding_buzz_counter = 0

        self.none_var.set(none_value == 'x')

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

    def previous_image(self):
        self.update_annotations()
        self.image_index = (self.image_index - 1) % len(self.image_names)
        self.show_image()
        self.check_annotations()

    def increment_social_call(self):
        self.social_call_counter += 1
        self.social_call_counter_label.config(text=self.social_call_counter)

    def sub_social_call(self):
        if self.social_call_counter == 0:
            return

        self.social_call_counter -= 1
        self.social_call_counter_label.config(text=self.social_call_counter)

    def increment_social_call_key(self, event):
        self.increment_social_call()

    def sub_social_call_key(self, event):
        self.sub_social_call()

    def increment_feeding_buzz(self):
        self.feeding_buzz_counter += 1
        self.feeding_buzz_counter_label.config(text=self.feeding_buzz_counter)

    def sub_feeding_buzz(self):
        if self.feeding_buzz_counter == 0:
            return

        self.feeding_buzz_counter -= 1
        self.feeding_buzz_counter_label.config(text=self.feeding_buzz_counter)

    def increment_feeding_buzz_key(self, event):
        self.increment_feeding_buzz()

    def sub_feeding_buzz_key(self, event):
        self.sub_feeding_buzz()

    def toggle_none(self, event):
        self.none_var.set(not self.none_var.get())

        if self.none_var.get():
            time.sleep(0.1)
            self.next_image()

    def update_annotations(self):
        excel_file_path = os.path.join(self.folder_path, 'annotations.xlsx')

        if not os.path.exists(excel_file_path):
            raise FileNotFoundError(f"Annotations Excel file '{excel_file_path}' not found.")

        # Number of retries
        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                df = pd.read_excel(excel_file_path)

                # Find the index of the current image name in the DataFrame
                current_image_name = self.image_names[self.image_index]
                index = self.image_index

                # Update the 'Social Call' column if the checkbox is checked
                if self.social_call_counter > 0:
                    df.at[index, 'Social Call'] = self.social_call_counter
                else:
                    df.at[index, 'Social Call'] = 0

                # Update the 'Feeding Buzz' column if the checkbox is checked
                if self.feeding_buzz_counter > 0:
                    df.at[index, 'Feeding Buzz'] = self.feeding_buzz_counter
                else:
                    df.at[index, 'Feeding Buzz'] = 0

                # Update the 'None' column if the checkbox is checked
                if self.none_var.get():
                    df.at[index, 'None'] = 'x'
                else:
                    df.at[index, 'None'] = ''

                # Save the DataFrame to the annotations Excel file
                df.to_excel(excel_file_path, index=False)

                break

            except PermissionError:
                # Catch PermissionError and wait before retrying
                retries += 1
                if retries < max_retries:
                    print("PermissionError: Could not update annotations. Retrying...")
                    time.sleep(1)  # Wait for 1 second before retrying
                else:
                    print("PermissionError: Could not update annotations after multiple attempts.")
                    break


if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')
    app = ImageAnnotatorApp(root)
    root.mainloop()
