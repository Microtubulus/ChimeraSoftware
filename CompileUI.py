from PyQt4 import uic
import os

f = open('ui2.py', 'w+')
uic.compileUi('mainwindow.ui', f)
f.close()
