# Overview

This distro contains a script for data acquisition using a rigol oscilloscope. It has the following features:
1. Log efficiency data to CSV

Some of these features could be implemented if needed:
1. Create graphs
1. Send configuration data to oscilloscope

# Setup

The following software is required:
1. NI-VISA backend
1. Python 3, 32 bit


## NI-VISA Backend
The NI-VISA package contains USB drivers required to communicate with USB test equipment. Download the appropriate version from [this page](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#346210). Use the default installation options.

## Python Installation
To install python, download the latest 32-bit installer from [python.org](https://www.python.org/). The default installation directory is hidden in the user's appdata folder, so it is recommended to customize the installation directory. To get this option in the installer, it is required to explicitly run the installer as an administrator while launching it. A common location is `c:\python\`. You will need to add this folder to the windows path so you can run python from the command line easily.

After it is installed, the following command should work:
```
$ python --version
Python 3.8.5
```

## Python virtual environment
It is permissible to skip this step, but it is best practice to use a python virtual environment to hold the python packages required for the script to run. This is accomplised using the `virtualenv` module. It is essentially a complete copy of the python installation, but in your working directory.

The strength of a virtual environment is the containerization of python modules - once you are working with a virtual environment, all modules get installed to a local folder, separate from the global python module location. If you skip this step, you will install all packages to the global folder (which will work fine).

#### Install the virtual environment python module
`python -m pip install virtualenv`
This tells python to run the python module pip, which is used for installing other python  modules, and tells pip to install the module called virtualenv. You can probably omit the `python -m` but including it is a more robust invocation.

You only need to run this script once. `virtualenv` is now installed in the global modules location.

#### Create a virtual environment
From your working directory (the folder containing these scripts), run
`python -m virtualenv venv`
The `python -m` tells python to run the module `virtualenv`, and tells `virtualenv` to create a virtual environment called `venv`. The name can be anything, but `venv` is a de-facto standard. This will create a new folder in your active directory called `venv` containing the python interpreter (python.exe) and all of the python modules.

You only need to run this script once. You can delete the virtual environment by just deleting its folder, but then you would need to create a new one.

#### Activate the virtual environment
This changes the local variables of your terminal such that all python commands are re-routed to the virtual environment.

`source venv/scripts/activate`

Your terminal should now show `(venv)` above the prompt. It's really easy to forget this step, and you need to run it every time you open a new terminal instance. If you don't see `(venv)` on your prompt, you are using the global python installation.

To deactivate, just type `deactivate`

## Python modules
In order for this script to work, there must be several python modules installed. They are listed in `requirements.txt`. To install them, run
`python -m pip install -r requirements.txt`

If you get any `ModuleNotFound` errors, install the extra packages using
`python -m pip install <module_name>`

To update the `requirements.txt` file, use the following command:
`python -m pip freeze > requirements.txt`

# Usage

To launch the script, run `python test_efficiency.py`

The script assumes the following connections:
    Channel 1: Voltage at device input
    Channel 2: Current at device input
    Channel 3: Voltage at device output
    Channel 4: Current at device output

Start by configuring all channels to display the waveforms properly - reasonable time base and reasonable scaling. make sure the waveforms are not clipping.

Calibration must be performed once every time the script is launched. To perform calibration, connect all probes to the scope and make sure they are powered on, but disconnect all of them from the device under test. For extra accuracy on voltage probes, clip the leads together. Enter `c` to record the zero positions of every channel. After performing calibration, connect the probes to the device under test.

After recording calibration data, operate the device. Enter a blank selection in the menu to record a single data point. Data will be logged to a CSV file using the time and date for enumeration.

