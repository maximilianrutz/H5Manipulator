#!/usr/bin/env python3

"""Select datasets from .h5 files, reverse offset and linear scaling and save as .h5"""

import time
from pathlib import Path
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory

import h5py


class Data:
    def __init__(self, **kwargs):
        """Initialize an object which stores the data"""
        self.h5keys = ["Open file to select h5 dataset(s)"]
        self.h5key = ""
        self.loadpath = kwargs["loadpath"] if "loadpath" in kwargs else None
        self.savepath = kwargs["savepath"] if "savepath" in kwargs else None

    ##########
    # Data Loading
    ##########

    def load_h5keys(self):
        """Extract h5keys of all datasets in a .h5 file"""
        with h5py.File(self.loadpath, "r") as f:
            h5tree = []
            f.visit(h5tree.append)
            self.h5keys = [
                h5key for h5key in h5tree if isinstance(f[h5key], h5py.Dataset)
            ]

    def load_dataset_batch(self, batch=0):
        """Load batches of dataset for given h5key from .h5 file"""
        with h5py.File(self.loadpath, "r") as f:

            dataset_size = f[self.h5key].shape[0]
            batch_start = int(batch * dataset_size / self.num_batches)
            batch_end = int((batch + 1) * dataset_size / self.num_batches)
            print(self.num_batches)
            print(batch)
            print(dataset_size)
            self.dataset = f[self.h5key][batch_start:batch_end, :, :]

    def find_num_batches(self):
        """Find the minimal number of batches for which numpy ndarrays can hold the data"""
        self.num_batches = 1
        while True:
            try:
                self.load_dataset_batch()
                break
            except (ValueError, MemoryError):
                self.num_batches += 1

    ##########
    # Data Correction
    ##########

    def get_linear_offset(self):
        """Read linear offset which is stored as attribute in parent group of dataset"""
        group = "/".join(self.h5key.split("/")[0:-1])
        dataset = self.h5key.split("/")[-1]
        attribute = f"{dataset}_Conversion_ConversionLinearOffset"
        with h5py.File(self.loadpath, "r") as f:
            self.linear_offset = f[group].attrs[attribute]

    def get_linear_scale(self):
        """Read linear scale factor which is stored as attribute in parent group of dataset"""
        group = "/".join(self.h5key.split("/")[0:-1])
        dataset = self.h5key.split("/")[-1]
        attribute = f"{dataset}_Conversion_ConversionLinearScale"
        with h5py.File(self.loadpath, "r") as f:
            self.linear_scale = f[group].attrs[attribute]

    def linear_correction(self):
        """Use linear offset and linear scale factor to reverse a linear transformation"""
        self.get_linear_offset()
        self.get_linear_scale()
        self.dataset_corr = self.linear_offset + self.linear_scale * self.dataset

    ##########
    # Data Saving
    ##########

    def full_savepath(self, dataset, corr, batch):
        """Create full savepath depending on correction and batches"""
        savepath = self.savepath
        if corr:
            savepath += "-corr"
        if self.num_batches > 1:
            savepath += f"_batch{batch}"
        savepath += ".h5"
        return savepath

    def save_dataset(self, dataset, corr, batch):
        """Save dataset with batch number if more than one batch"""
        savepath = self.full_savepath(dataset, corr, batch)
        with h5py.File(savepath, "w") as f:
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
        self.root.title("H5 Manipulator")
        self.root.geometry("350x50")
        self.root.resizable(width=False, height=False)
        self.selected_h5keys = []
        self.corr = False

    def add_menu(self):
        """Add menubar with options for file manipulation"""
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_h5)
        filemenu.add_command(label="Save", command=lambda: self.save_h5(corr=False))
        filemenu.add_command(
            label="Corr + Save", command=lambda: self.save_h5(corr=True)
        )
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def add_h5keys_dropdown(self):
        """Add dropdown button for selection of h5key from a dataset"""
        self.h5key_entry = StringVar(self.root)
        self.h5key_entry.set("Select h5 dataset(s)")
        self.h5keys_dd = OptionMenu(
            self.root,
            self.h5key_entry,
            *self.data.h5keys,
            command=self.select_h5key,
        )
        for h5key in self.selected_h5keys:
            index = self.data.h5keys.index(h5key)
            self.h5keys_dd["menu"].entryconfig(index, background="lightgrey")
        self.h5keys_dd.pack(side="top", fill=X, expand=True)

    def add_dataset_label(self):
        """Add label to show information when Loading/Saving a dataset"""
        self.dataset_la = Label(self.root, text="No file opened")
        self.dataset_la.pack(side="bottom", fill=X, expand=True)

    ##########
    # Gui keypress functions
    ##########

    def open_h5(self):
        """Ask for filepath and load all h5keys from that .h5 file"""
        self.data.loadpath = askopenfilename(parent=self.root)
        self.data.load_h5keys()
        self.selected_h5keys = []
        self.update_h5keys_dd()
        self.dataset_la.config(text="Select Datasets")

    def select_h5key(self, menu_selection):
        """Add or remove input from OptionMenu to list of selected keys"""
        if menu_selection not in self.selected_h5keys:
            self.selected_h5keys.append(menu_selection)
            self.dataset_la.config(text="Dataset selected")
        else:
            self.selected_h5keys.remove(menu_selection)
            self.dataset_la.config(text="Dataset deselected")
        self.update_h5keys_dd()

    def save_h5(self, corr):
        """Handle and save selected datasets"""
        self.corr = corr
        self.check_number_of_datasets()

    ##########
    # Gui information label functions
    ##########

    def update_h5keys_dd(self):
        """Update dropdown button h5keys to h5keys from opened .h5 file"""
        self.h5keys_dd.destroy()
        self.add_h5keys_dropdown()

    def load_dataset_info(self, batch):
        """Show information while loading dataset"""
        self.dataset_la.config(text=f"Loading {self.data.h5key}")
        self.dataset_la.update()
        time_start = time.time()
        self.data.load_dataset_batch(batch)
        exec_time = time.time() - time_start
        self.dataset_la.config(text=f"Dataset loaded in {exec_time:.2f} s")

    def correct_dataset_info(self):
        """Show information while correcting dataset"""
        self.dataset_la.config(text=f"Correcting {self.data.h5key}")
        self.dataset_la.update()
        time_start = time.time()
        self.data.linear_correction()
        exec_time = time.time() - time_start
        self.dataset_la.config(text=f"Dataset corrected in {exec_time:.2f} s")

    def save_dataset_info(self, dataset, corr, batch):
        """Show information while saving dataset"""
        self.dataset_la.config(text=f"Saving {self.data.h5key}")
        self.dataset_la.update()
        time_start = time.time()
        self.data.save_dataset(dataset, corr, batch)
        exec_time = time.time() - time_start
        self.dataset_la.config(text=f"Dataset saved in {exec_time:.2f} s")

    ##########
    # Gui after keypress decision tree functions
    ##########

    def check_number_of_datasets(self):
        "Check if a single or multiple datasets were selected"
        if len(self.selected_h5keys) == 1:
            self.single_dataset()
        elif len(self.selected_h5keys) > 1:
            self.multiple_datasets()
        else:
            self.dataset_la.config(text=f"No dataset selected")

    def single_dataset(self):
        """For a single dataset a full filename for saving can be chosen"""
        self.data.h5key = self.selected_h5keys[0]
        self.data.savepath = asksaveasfilename(
            parent=self.root, initialfile=self.data.h5key.replace("/", "-")
        )
        if self.data.savepath:
            self.handle_dataset()

    def multiple_datasets(self):
        """For multiple datasets only the directory for saving can be chosen"""
        save_directory = askdirectory()
        if save_directory:
            for h5key in self.selected_h5keys:
                self.data.h5key = h5key
                self.data.savepath = str(Path(save_directory, h5key.replace("/", "-")))
                self.handle_dataset()

    ##########
    # Gui handle dataset functions
    ##########

    def handle_dataset(self):
        """Load, correct and save a single dataset and split it into batches if necessary"""
        self.dataset_la.config(text=f"Finding number of load batches")
        self.data.find_num_batches()
        self.handle_batches()

    def handle_batches(self):
        """Load, correct and save batches sequentially"""
        for batch in range(self.data.num_batches):
            self.data.load_dataset_batch(batch)
            if self.corr:
                self.correct_dataset_info()
                self.save_dataset_info(self.data.dataset_corr, self.corr, batch)
            else:
                self.save_dataset_info(self.data.dataset, self.corr, batch)


if __name__ == "__main__":
    gui = Gui()
