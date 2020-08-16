#!/usr/bin/env python3

"""Convert .mesc files to .h5 and apply suite2p motion correction"""

import time
from pathlib import Path
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename

import h5py


class Data:
    def __init__(self, **kwargs):
        self.h5keys = ["Open file to select h5 keys"]
        self.h5key = ""
        self.loadpath = kwargs["loadpath"] if "loadpath" in kwargs else None
        self.savepath = kwargs["savepath"] if "savepath" in kwargs else None

    def load_h5keys(self):
        with h5py.File(self.loadpath, "r") as f:
            h5tree = []
            f.visit(h5tree.append)
            self.h5keys = [
                h5key for h5key in h5tree if isinstance(f[h5key], h5py.Dataset)
            ]

    def load_dataset(self):
        with h5py.File(self.loadpath, "r") as f:  # , driver="mpio"
            self.dataset = f[self.h5key][()]

    def get_linear_offset(self):
        group = str(Path(self.h5key).parent)
        dataset = str(Path(self.h5key).name)
        attribute = f"{dataset}_Conversion_ConversionLinearOffset"
        with h5py.File(self.loadpath, "r") as f:
            self.linear_offset = f[group].attrs[attribute]

    def get_linear_scale(self):
        group = str(Path(self.h5key).parent)
        dataset = str(Path(self.h5key).name)
        attribute = f"{dataset}_Conversion_ConversionLinearScale"
        with h5py.File(self.loadpath, "r") as f:
            self.linear_scale = f[group].attrs[attribute]

    def linear_conversion(self):
        self.get_linear_offset()
        self.get_linear_scale()
        self.dataset = self.linear_offset + self.linear_scale * self.dataset
        self.dataset = self.dataset.astype("int16")

    def save_dataset(self):
        with h5py.File(self.savepath, "w") as f:
            f.create_dataset(self.h5key, data=self.dataset)

    # https://suite2p.readthedocs.io/en/latest/registration.html
    def suite2p_set_parameters(self):
        pass

    def suite2p_motion_correction(self):
        pass


class Gui:
    def __init__(self):
        self.data = Data()
        self.add_root()
        self.add_menu()
        self.add_h5keys_dropdown()
        self.add_dataset_label()
        self.root.mainloop()

    # Gui layout
    def add_root(self):
        self.root = Tk()
        self.root.title("Mesc Converter")
        self.root.geometry("250x50")
        self.root.resizable(width=False, height=False)

    def add_menu(self):
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_mesc)
        filemenu.add_command(label="Save", command=self.save_dataset_gui)
        filemenu.add_command(
            label="Motion correct and save", command=self.mcorr_save_dataset
        )
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def add_h5keys_dropdown(self):
        self.h5key = self.data.h5keys[0] if not self.data.h5key else self.data.h5key
        self.h5key_entry = StringVar(self.root)
        self.h5key_entry.set(self.h5key)
        self.h5keys_dd = OptionMenu(
            self.root, self.h5key_entry, *self.data.h5keys, command=self.select_h5key
        )
        self.h5keys_dd.pack(side="top", fill=X, expand=True)

    def add_dataset_label(self):
        self.dataset_la = Label(self.root, text="No dataset loaded")
        self.dataset_la.pack(side="bottom", fill=X, expand=True)

    # Gui functions
    def open_mesc(self):
        self.data.loadpath = askopenfilename(parent=self.root, initialdir="data")
        self.data.load_h5keys()
        self.update_h5keys_dd()

    def update_h5keys_dd(self):
        self.h5keys_dd.destroy()
        self.add_h5keys_dropdown()

    def select_h5key(self, menu_selection):
        self.data.h5key = menu_selection
        self.load_dataset_gui()

    def load_dataset_gui(self):
        self.dataset_la.config(text="Loading dataset...")
        self.dataset_la.update()
        time_start = time.time()
        self.data.load_dataset()
        exec_time = time.time() - time_start
        self.dataset_la.config(text=f"Dataset loaded in {exec_time:.2f} s")

    def save_dataset_gui(self):
        self.data.savepath = asksaveasfilename(
            parent=self.root, initialfile=self.data.h5key.replace("/", "-") + ".h5"
        )
        self.dataset_la.config(text="Saving dataset...")
        self.dataset_la.update()
        time_start = time.time()
        self.data.save_dataset()
        exec_time = time.time() - time_start
        self.dataset_la.config(text=f"Dataset saved in {exec_time:.2f} s")

    def mcorr_save_dataset(self):
        self.savepath = asksaveasfilename(
            parent=self.root,
            initialfile=self.data.h5key.replace("/", "-") + "-mcorr.h5",
        )
        self.data.save_dataset()


if __name__ == "__main__":
    gui = Gui()
