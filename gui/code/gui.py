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
pyinstaller --onefile --icon=dependencies\windows\windows_icon.ico gui.py
"""

import tkinter as tk
from tkinter import filedialog as fd
import tkinter.scrolledtext as tkst

import time
import numpy as np
import cv2
from PIL import Image, ImageTk


class Gui:
    """ Initialization """

    def __init__(self):
        gui_height = 300
        gui_width = 400
        self.tk_root = tk.Tk()
        self.tk_root.title("Data Manipulator Neurophysiology Tuebingen")
        self.tk_canvas = tk.Canvas(self.tk_root, height=gui_height, width=gui_width)
        self.tk_frame = tk.Frame(self.tk_canvas)
        self.tk_load_button = tk.Button(
            self.tk_frame, text="Load file", command=self.load_video
        )
        self.tk_save_button = tk.Button(
            self.tk_frame, text="Save file", command=self.save_video
        )
        self.tk_printout = tkst.ScrolledText(
            self.tk_canvas, wrap=tk.WORD, font=("*", 12)
        )
        self.filetypes_load = (("avi", ".avi"), ("mp4", ".mp4"), ("tiff", ".tif .tiff"))
        self.filetypes_save = (("tiff", ".tif .tiff"), ("avi", ".avi"))
        self.filename = ""
        self.frames = []
        self.frame_count = 0
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0

    def load_video(self):
        self.filename = fd.askopenfilename(filetypes=self.filetypes_load)
        if self.filename == "":
            return
        filetype = self.filename.split(".")[1]
        if filetype in ["avi", "mp4"]:
            start = time.time()
            self.load_frames()
        elif filetype in ["h5", "hdf5"]:
            pass
        else:
            print(f"Unknown file type of file {self.filename}")
        stop = time.time()
        self.print_tk(f"\nLoaded {self.filename} in {np.round(stop - start,2)} seconds")

    def load_frames(self):
        cap = cv2.VideoCapture(self.filename)
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

            #            img = ImageTk.PhotoImage(image=Image.fromarray(frame))
            #            self.tk_canvas.create_image(50, 50, image=img, anchor="se")
            frame_counter += 1
        cap.release()

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
            f"\nSaved file as {filename_save} in {np.round(stop - start,2)} seconds"
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

    def print_tk(self, to_be_printed):
        self.tk_printout.insert(tk.INSERT, str(to_be_printed) + "\n")
        self.tk_printout.see(tk.END)

    def activate_gui_elements(self):
        self.tk_canvas.pack(fill="both", expand=True)
        self.tk_frame.place(relwidth=1, relheight=1)
        self.tk_load_button.place(relx=0, rely=0, anchor="nw")
        self.tk_save_button.place(relx=1, rely=0, anchor="ne")
        self.tk_printout.place(relx=0, rely=1, relwidth=0.5, relheight=0.5, anchor="sw")
        self.print_tk("Data Manipulator ready!\n")

    def main(self):
        self.activate_gui_elements()
        self.tk_root.mainloop()


if __name__ == "__main__":
    program = Gui()
    program.main()
