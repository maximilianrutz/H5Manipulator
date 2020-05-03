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
gui.py

on Windows:
pyinstaller --onefile --windowed --icon=dependencies\windows_icon.ico gui.py
"""
import os

import tkinter as tk
from tkinter import filedialog as fd
import tkinter.scrolledtext as tkst

import time
import numpy as np
import cv2
from PIL import Image, ImageTk


class DataManipulator:
    """ Initialization """

    def __init__(self):
        gui_height = 300
        gui_width = 450
        self.filetypes_load = [("avi", ".avi")]
        self.filetypes_save = [("tiff", ".tif .tiff")]
        self.filepath = ""
        self.frames = []
        self.frame_count = 0
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0

        self.tk_root = tk.Tk()
        self.tk_root.title("Data Manipulator Neurophysiology Tuebingen")
        self.tk_canvas_main = tk.Canvas(
            self.tk_root, height=gui_height, width=gui_width, bd=0, highlightthickness=0
        )
        self.tk_canvas_image = tk.Canvas(self.tk_canvas_main)
        self.tk_load_button = tk.Button(
            self.tk_canvas_main, text="Load file", command=self.load_video
        )
        self.tk_save_button = tk.Button(
            self.tk_canvas_main, text="Save file", command=self.save_video
        )
        self.tk_printout = tkst.ScrolledText(
            self.tk_canvas_main,
            wrap=tk.WORD,
            font=("ComicSans", 12),
            borderwidth=2,
            relief="solid",
        )
        self.active_file_label = tk.Label(
            self.tk_canvas_main, justify="left", text="Active file:"
        )

    def load_video(self):
        self.filepath = fd.askopenfilename(filetypes=self.filetypes_load)
        if self.filepath == "":
            return
        filetype = self.filepath.split(".")[1]
        if filetype in ["avi", "mp4"]:
            start = time.time()
            self.load_frames()
        elif filetype in ["h5", "hdf5"]:
            pass
        else:
            print(f"Unknown file type of file {self.filepath}")
        stop = time.time()
        self.print_tk(f"Loaded {self.filepath} in {np.round(stop - start,2)} seconds\n")
        self.active_file_label.config(
            text=f"Active file:\n{os.path.basename(self.filepath)}"
        )

    def load_frames(self):
        cap = cv2.VideoCapture(self.filepath)
        self.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.frames = np.empty(
            (self.frame_count, self.frame_height, self.frame_width, 3),
            np.dtype("uint8"),
        )
        frame_counter = 0
        ret = True
        while frame_counter < self.frame_count and ret:
            self.print_tk(f"Loading frame {frame_counter + 1}/{self.frame_count}")

            ret, frame = cap.read()
            self.frames[frame_counter] = frame
            frame_counter += 1
        self.print_tk()
        cap.release()
        # img = ImageTk.PhotoImage(image=Image.fromarray(self.frames[1]))
        # self.tk_canvas_main.create_image(0, 0, image=img, anchor="nw")

    def save_video(self):
        start = time.time()
        filename_save = fd.asksaveasfilename(filetypes=self.filetypes_save)
        if filename_save == "":
            return
        filetype = filename_save.split(".")[1]
        start = time.time()
        if filetype == "avi":
            self.save_avi(filename_save)
        elif filetype in ["tif", "tiff"]:
            self.save_tiff(filename_save)
        stop = time.time()
        self.print_tk(
            f"Saved file as {filename_save} in {np.round(stop - start,2)} seconds\n"
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
            imlist.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)))
        imlist[0].save(
            filename_save, save_all=True, append_images=imlist[1:],
        )

    def print_tk(self, to_be_printed=""):
        self.tk_printout.insert(tk.INSERT, str(to_be_printed) + "\n")
        self.tk_printout.see(tk.END)

    def activate_gui_elements(self):
        self.tk_canvas_main.pack(fill="both", expand=True)
        self.active_file_label.place(relx=0, rely=0.1, anchor="nw")
        self.tk_load_button.place(relx=0, rely=0, anchor="nw")
        self.tk_save_button.place(relx=1, rely=0, anchor="ne")
        self.tk_canvas_image.place(
            relx=1, rely=1, relwidth=0.5, relheight=0.5, anchor="se"
        )
        self.tk_printout.place(relx=0, rely=1, relwidth=0.4, relheight=0.5, anchor="sw")
        self.print_tk("Data Manipulator ready!\n")

    def main(self):
        self.activate_gui_elements()
        self.tk_root.mainloop()


if __name__ == "__main__":
    program = DataManipulator()
    program.main()
