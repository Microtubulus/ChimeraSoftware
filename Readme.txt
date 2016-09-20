I am running the software using python 3.5. Unfortunately OpalKelly doesn't provide a Mac version of their drivers for new python versions.

First, install opal kelly drivers (FrontPanel) on your computer.
Make a folder called ok in your pythons site-package folder.
Go to: C:\Program Files\Opal Kelly\FrontPanelUSB\API\Python
Depending on which version of python you use copy the corresponding files to the previously created folder (ok) in python site-packages.

Open ui.py to look at the import statements. Install all the necessary packages. Once all the packages are installed you can execute ui.py and start the program.

In globals.py make sure these values correspond to your chimera calibration.
freqComp = 19
SETUP_pAoffset = 1.6E-9
SETUP_TIAgain = 100E6
SETUP_preADCgain = 1.235

ISSUES:
- The User Interface is not adjusted for different screen sizes!!