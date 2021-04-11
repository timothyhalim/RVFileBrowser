import sys
import os
from glob import glob

try:
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QVBoxLayout, QWidget, QDockWidget
except:
    from PySide.QtCore import Qt
    from PySide.QtGui import QVBoxLayout, QWidget, QDockWidget

import rv
import rv.runtime
import rv.qtutils

currentPath = os.path.dirname(os.path.abspath(__file__))
if not currentPath in sys.path:
    sys.path.append(currentPath)

from FileBrowser import FileBrowser
        
class FB(rv.rvtypes.MinorMode):
    def __init__(self):
        rv.rvtypes.MinorMode.__init__(self)
        self.init("File Browser", None, None,
                    [("File Browser",
                    [("Show File Browser", self.toggle, None, self._state)])])
        self.setupUI()

        self._visible = False
        self.dock.visibilityChanged.connect(self.setVisible)

    def setupUI(self):
        self.dock = QDockWidget()
        self.dock.setWindowTitle("File Browser")

        self.masterWidget = QWidget()
        self.masterLayout = QVBoxLayout(self.masterWidget)
        self.dock.setWidget(self.masterWidget)

        movieExt = ["*.mov", "*.mp4", "*.wmv", "*.movieproc"]
        imgExt = ["*.ext", "*.tiff", "*.tif", "*.dpx", "*.iff", "*.jpeg", "*.png", "*.ari"]
        rawCam = [".arw", ".cr2", ".crw", ".dng", ".nef", ".orf", ".pef", ".ptx", ".raf", ".rdc", ".rmf"]
        self.fileBrowser = FileBrowser(filterExtension=movieExt+imgExt+rawCam)
        self.fileBrowser.executed.connect(self.play)
        self.masterLayout.addWidget(self.fileBrowser)

    def readPrefs(self):
        self._visible = rv.commands.readSettings("File Browser", "visible", False)

    def writePrefs(self, state):
        rv.commands.writeSettings("File Browser", "visible", state)

    def setVisible(self, visible):
        self._visible = visible

    def dockToggle(self):
        if self._visible:
            self.dock.show()
        else:
            self.dock.hide()
        self.writePrefs(self._visible)

    def toggle(self, event):
        self._visible = not self._visible
        self.dockToggle()

    def _state(self):
        if self._visible:
            return rv.commands.CheckedMenuState
        return rv.commands.UncheckedMenuState

    def activate(self):
        print("Activating QCTools")
        try:
            rv.rvtypes.MinorMode.activate(self)
            self.window = rv.qtutils.sessionWindow()
            self.window.addDockWidget(Qt.BottomDockWidgetArea, self.dock)
            self.dockToggle()
        except Exception as e:
            print("-" * 50)
            print(str(e))
            print("-" * 50)

    def deactivate(self):
        print("Deactivating QCTools")
        self.window.removeDockWidget(self.dock)
        self.dock.hide()
        rv.rvtypes.MinorMode.deactivate(self)

    def clearSession(self):
        rv.commands.clearSession()

    def play(self, file, new=True):
        if new:
            self.clearSession()
        source = rv.commands.addSourceVerbose([file], None)
        mediaInfo = rv.commands.sourceMediaInfo(source)
        print(mediaInfo)
        rv.commands.setRealtime(True)
        rv.commands.setCacheMode(1)

def createMode():
    return FB()