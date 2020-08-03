"""
TODO:
- mp4
- open h5 and multitiff
- h5py automatically detect video files
- tickbox with names
- if size(dataset) == 1: save one file
- h5 files a lot of small files - save as multitiffs

how to make executables with pyinstaller

on Mac: pyinstaller
--onefile
--windowed
--add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk'
--add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl'
datamanipulator.py

on Windows:
pyinstaller --onefile --windowed --icon=dependencies\windows_icon.ico datamanipulator.py
"""
import os

import tkinter as tk
from tkinter import filedialog as fd
import tkinter.scrolledtext as tkst

import time
import numpy as np
import h5py
import cv2
from PIL import Image, ImageTk


class DataManipulator:
    """ Initialization """

    def __init__(self):
        gui_height = 300
        gui_width = 400
        self.filetypes_load = [("avi", ".avi"), ("hdf5", ".h5 .hdf5 .mesc")]
        self.filetypes_save = [("tiff", ".tif .tiff")]
        self.filepath = ""
        self.keys = []
        self.frames = []
        self.frame_count = 0
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0
        self.tk_root = tk.Tk()
        self.tk_root.geometry(f"{gui_width}x{gui_height}")
        self.tk_root.resizable(width=False, height=False)
        self.tk_root.title("Data Manipulator Neurophysiology Tuebingen")
        self.tk_canvas_image = tk.Canvas(self.tk_root)
        self.tk_load_button = tk.Button(
            self.tk_root, text="Load file", command=self.load_file
        )
        self.tk_save_button = tk.Button(
            self.tk_root, text="Save file", command=self.save_file
        )
        self.tk_printout = tkst.ScrolledText(
            self.tk_root, wrap=tk.WORD, font=("*", 12), borderwidth=2, relief="solid",
        )
        self.tk_active_file_text = tk.Label(self.tk_root, justify="left", text="")
        self.tk_active_file_label = tk.Label(
            self.tk_root, justify="left", text="Active file:"
        )
        self.tk_h5key_label = tk.Label(self.tk_root, text="Enter h5 key:")
        self.tk_h5key_entry = tk.Entry(self.tk_root)
        self.tk_h5loadkey_button = tk.Button(
            self.tk_root, text="Load h5 key", command=self.load_h5key
        )
        self.tk_invert_button = tk.Button(
            self.tk_root, text="Invert images", command=self.invert
        )

    def load_file(self):
        self.filepath = fd.askopenfilename(filetypes=self.filetypes_load)
        if self.filepath == "":
            return
        filetype = self.filepath.split(".")[1]
        if filetype in ["avi", "mp4"]:
            self.load_frames()
        elif filetype in ["mesc", "h5", "hdf5"]:
            self.show_h5keys()
        else:
            self.tk_print(f"Unknown file type of file {self.filepath}")
        self.tk_active_file_text.config(text=os.path.basename(self.filepath))

    def load_h5key(self):
        with h5py.File(self.filepath, "r") as f:
            h5key = self.tk_h5key_entry.get()
            self.frames = np.array(f[h5key])
        self.tk_active_file_text.config(
            text=f"{os.path.basename(self.filepath)}/{h5key}"
        )

    def show_h5keys(self):
        with h5py.File(self.filepath, "r") as f:
            self.tk_print("Found h5 keys:")
            f.visit(self.tk_print)

    def load_frames(self):
        self.cap = cv2.VideoCapture(self.filepath)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.frames = np.empty(
            (self.frame_count, self.frame_height, self.frame_width, 3),
        )
        frame_counter = 0
        ret = True
        while frame_counter < self.frame_count and ret:
            self.tk_print(f"Loading frame {frame_counter + 1}/{self.frame_count}")

            ret, frame = self.cap.read()
            self.frames[frame_counter] = frame
            frame_counter += 1
        self.cap.release()
        # img = ImageTk.PhotoImage(image=Image.fromarray(self.frames[1]))
        # self.tk_root.create_image(0, 0, image=img, anchor="nw")

    def save_file(self):
        self.start = time.time()
        filename_save = fd.asksaveasfilename(filetypes=self.filetypes_save)
        if filename_save == "":
            return
        filetype = filename_save.split(".")[1]
        self.start = time.time()
        if filetype == "avi":
            self.save_avi(filename_save)
        elif filetype in ["tif", "tiff"]:
            self.save_tiff(filename_save)
        stop = time.time()
        self.tk_print(
            f"\nSaved file as {filename_save} in {np.round(stop - self.start,2)} seconds\n"
        )

    def save_avi(self, filename_save):
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(
            filename_save, fourcc, self.fps, (self.frame_width, self.frame_height)
        )
        for frame in self.frames:
            out.write(frame)
        out.release()

    def save_tiff(self, filename_save):
        imlist = []
        for frame in self.frames:
            imlist.append(Image.fromarray(frame))
            # imlist.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)))
        imlist[0].save(
            filename_save, save_all=True, append_images=imlist[1:],
        )

    def tk_print(self, to_be_printed):
        self.tk_printout.insert(tk.END, str(to_be_printed) + "\n")
        self.tk_printout.see(tk.END)

    def activate_gui_elements(self):
        self.tk_root.grid_columnconfigure(0, weight=1)
        self.tk_root.grid_columnconfigure(1, weight=1)
        self.tk_root.grid_rowconfigure(6, weight=1)
        self.tk_load_button.grid(row=0, column=0, sticky="W")
        self.tk_active_file_label.grid(row=1, column=0, sticky="W")
        self.tk_active_file_text.grid(row=2, column=0, sticky="W")
        self.tk_h5key_label.grid(row=3, column=0, sticky="W")
        self.tk_h5key_entry.grid(row=4, column=0, sticky="W")
        self.tk_h5loadkey_button.grid(row=5, column=0, sticky="W")
        self.tk_printout.grid(row=6, column=0, sticky="W")
        self.tk_print("Data Manipulator ready!\n")

        self.tk_save_button.grid(row=0, column=0, sticky="E")
        self.tk_invert_button.grid(row=5, column=0, sticky="E")
        self.tk_canvas_image.grid(row=6, column=0, sticky="E")

    def invert(self):
        self.frames = np.invert(self.frames)

    def main(self):
        self.activate_gui_elements()
        self.tk_root.mainloop()


if __name__ == "__main__":
    program = DataManipulator()
    program.main()
