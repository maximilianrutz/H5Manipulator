# MescConverter
A python script with a GUI to read calcium imaging data from Femtonics microscopes .mesc files and save to .h5 files.


## Motivation
Some Femtonics microscopes write data into .mesc files after some initial data manipulation. To reverse engineer the initial manipulations someone kind in the community wrote the Matlab script "readMEScTStack.m". This GUI performs the same transformations and saves the result to an .h5 file.


## Installation
First, download this github repository:
1. Click on the green "Code" Button
2. Click on "Download Zip"
3. Unpack the zip file locally

### Python
If it is not installed on your system already you can download the latest version here: https://www.python.org/downloads/

### Python dependencies
Open a Powershell on Windows or a Shell on Linux and type the following commands.

Install pipenv which will take care of installing all necessary python packages:
```sh
pip install pipenv
```

Move to the directory in which Pipfile and Pipfile.lock are placed and install the packages:
```sh
cd MescConverter
pipenv install
```
Pipenv creates a virtual environment into which the packages specified in the Pipfile are installed. A virtual environment acts as a container in your system. Different virtual environments can have different packages installed. This allows you to easily change the environment when you work on another project with other dependencies. 


## How to use?
Go to the directory in which you installed the pipenv environment and activate it
```sh
cd MescConverter
pipenv shell
```
Now you can run 
```sh
python3 converter.py
```
to start the GUI. 


## Tests
Unit tests are written with pytest. The use the file testfile.mesc in the tests directory. Activate the pipenv environment
```sh
cd MescConverter
pipenv shell
```
and call 
```sh
pytest
```
to run the tests in tests/test_converter.py

## Credits
Written at the [Institute for Neurophysiology](http://www.physiologie2.uni-tuebingen.de/) at the University of Tuebingen. 
