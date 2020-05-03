# DataManipulator
An easy to use python GUI program to convert and manipulate video data. 

## Motivation
There are some very sophisticated data analysis tools available for Neuroscience. Unfortunately, installation and usage often requires using the command line. This tool provides a simple window with buttons, so you can easily load, save and convert your video data! 

## Installation
### **Windows**
1. Click on datamanipulator.exe
2. Click on the download button on the right side and save datamanipulator.exe on your computer
3. Open datamanipulator.exe

You should get a warning that datamanipulator.exe is from the Internet by an unknown developer and potentially a security risk. Click "more information" to be able to run the program.

### **Linux**
If you are comfortable with the command line you can also run this program on Linux (and Windows) from there. \

Make sure you have python installed:
```sh
sudo apt update
sudo apt install python
```
Pipenv is used to install the necessary python packages. It is itself just a package that you can install with the python package manager pip:
```sh
pip install pipenv
```
Pipenv keeps the information about which packages need to be installed in two files named "Pipfile" and "Pipfile.lock". Move to the directory in which these files are stored and tell Pipenv to install them in a virtual environment:
```sh
cd code/
pipenv install
```
A virtual environment acts like a container within your system. Different virtual environments can have different packages installed in it. Pipenv then allows you to easily change the environment when you work on a different python project with other packages needed. In order to "enter" the environment we call
```sh
pipenv shell
```
Now we can finally call 
```sh
python datamanipulator.py
```
to run the GUI. 


## How to use?
1. Load file
2. Manipulate active file
3. Save active file

## Supported video formats
- Can load: .avi
- Can save as: .tif/.tiff

## Python packages used
- GUI programming: tkinter
- Video/image manipulation: mainly cv2 and PIL. 
- Check the Pipfile for all used packages! 

## Tests
to be implemented

## License
MIT © [Maximilian Rutz](https://github.com/maxtue)
