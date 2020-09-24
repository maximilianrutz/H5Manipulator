#!/usr/bin/env python3

"""Select datasets from .mesc files, reverse offset and linear scaling and save as .h5"""

import time
from pathlib import Path
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename

import h5py


class Data:
    def __init__(self, **kwargs):
        """Initialize an object which stores the data"""
        self.h5keys = ["Open file to select h5 keys"]
        self.h5key = ""
        self.loadpath = kwargs["loadpath"] if "loadpath" in kwargs else None
        self.savepath = kwargs["savepath"] if "savepath" in kwargs else None

    ##########
    # Data handling
    ##########

    def load_h5keys(self):
        """Extract h5keys of all datasets in a .mesc file"""
        with h5py.File(self.loadpath, "r") as f:
            h5tree = []
            f.visit(h5tree.append)
            self.h5keys = [
                h5key for h5key in h5tree if isinstance(f[h5key], h5py.Dataset)
            ]

    def load_dataset(self):
        """Load dataset for given h5key from selected .mesc file"""
        with h5py.File(self.loadpath, "r") as f:
            self.dataset = f[self.h5key][()]

    def get_linear_offset(self):
        """Read linear offset which is stored as attribute in parent group of dataset"""
        group = "/".join(self.h5key.split("/")[0:-1])
        dataset = self.h5key.split("/")[-1]
        attribute = f"{dataset}_Conversion_ConversionLinearOffset"
        with h5py.File(self.loadpath, "r") as f:
            self.linear_offset = f[group].attrs[attribute]
        print(self.linear_offset)

    def get_linear_scale(self):
        """Read linear scale factor which is stored as attribute in parent group of dataset"""
        group = "/".join(self.h5key.split("/")[0:-1])
        dataset = self.h5key.split("/")[-1]
        attribute = f"{dataset}_Conversion_ConversionLinearScale"
        with h5py.File(self.loadpath, "r") as f:
            self.linear_scale = f[group].attrs[attribute]

    def linear_correction(self):
        """Use linear offset and linear scale factor to reverse the conversion of .mesc files from Femtonics"""
        self.get_linear_offset()
        self.get_linear_scale()
        self.dataset_corr = self.linear_offset + self.linear_scale * self.dataset

    def save_dataset(self, dataset):
        """Save given dataset and name it like selected h5key"""
        with h5py.File(self.savepath, "w") as f:
            f.create_dataset(self.h5key, data=dataset)


class Gui:
    def __init__(self):
        """Initialize a GUI object to use with a data object"""
        self.data = Data()
        self.add_root()
        self.add_menu()
        self.add_h5keys_dropdown()
        self.add_dataset_label()
        self.root.mainloop()

    ##########
    # Gui layout
    ##########

    def add_root(self):
        """Set up the Tkinter window"""
        self.root = Tk()
        self.root.title("Mesc Converter")
        self.root.geometry("350x50")
        self.root.resizable(width=False, height=False)

    def add_menu(self):
        """Add menubar with options for file manipulation"""
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_mesc)
        filemenu.add_command(label="Save", command=self.save_dataset_gui)
        filemenu.add_command(label="Corr + Save", command=self.save_dataset_corr_gui)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def add_h5keys_dropdown(self):
        """Add dropdown button for selection of h5key from a dataset"""
        self.h5key = self.data.h5keys[0] if not self.data.h5key else self.data.h5key
        self.h5key_entry = StringVar(self.root)
        self.h5key_entry.set(self.h5key)
        self.h5keys_dd = OptionMenu(
            self.root,
            self.h5key_entry,
            *self.data.h5keys,
            command=self.load_dataset_gui,
        )
        self.h5keys_dd.pack(side="top", fill=X, expand=True)

    def add_dataset_label(self):
        """Add label to show information when Loading/Saving a dataset"""
        self.dataset_la = Label(self.root, text="No dataset loaded")
        self.dataset_la.pack(side="bottom", fill=X, expand=True)

    ##########
    # Gui functions
    ##########

    def open_mesc(self):
        """Ask for filepath and load all h5keys from that .mesc file"""
        self.data.loadpath = askopenfilename(parent=self.root, initialdir="data")
        self.data.load_h5keys()
        self.update_h5keys_dd()

    def update_h5keys_dd(self):
        """Update dropdown button h5keys to h5keys from currently opened .mesc file"""
        self.h5keys_dd.destroy()
        self.add_h5keys_dropdown()

    def load_dataset_gui(self, menu_selection):
        """Load dataset of selected h5key if a .mesc has been opened"""
        if not self.data.h5keys == ["Open file to select h5 keys"]:
            self.data.h5key = menu_selection
            self.load_dataset_info()

    def load_dataset_info(self):
        """Show information while loading dataset"""
        self.dataset_la.config(text="Loading dataset...")
        self.dataset_la.update()
        time_start = time.time()
        self.data.load_dataset()
        exec_time = time.time() - time_start
        self.dataset_la.config(text=f"Dataset loaded in {exec_time:.2f} s")

    def save_dataset_gui(self):
        """Save dataset of data object"""
        self.data.savepath = asksaveasfilename(
            parent=self.root, initialfile=self.data.h5key.replace("/", "-") + ".h5"
        )
        self.save_dataset_info(self.data.dataset)

    def save_dataset_corr_gui(self):
        """Correct dataset of data object and save"""
        self.data.linear_correction()
        self.data.savepath = asksaveasfilename(
            parent=self.root, initialfile=self.data.h5key.replace("/", "-") + "-corr.h5"
        )
        self.save_dataset_info(self.data.dataset_corr)

    def save_dataset_info(self, dataset):
        """Show information while saving dataset"""
        self.dataset_la.config(text="Saving dataset...")
        self.dataset_la.update()
        time_start = time.time()
        self.data.save_dataset(dataset)
        exec_time = time.time() - time_start
        self.dataset_la.config(text=f"Dataset saved in {exec_time:.2f} s")


if __name__ == "__main__":
    gui = Gui()
