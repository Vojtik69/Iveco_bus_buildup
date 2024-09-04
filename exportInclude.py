
import os
import sys
# Get path to currently running script
currentDir = os.path.dirname(os.path.realpath(__file__))
# Add path to sys.path
sys.path.append(currentDir)
import logger
from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import pandas as pd

from common import (
    repair_exported_include, split_text
)

class DialogExportInclude:
    def __init__(self):
        self.currentDir = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(self.currentDir)
        self.widgetyExportInclude = {}
        self.dialogExportInclude = gui.Dialog(caption="Export include")
        self.width = 200
        self.height = 100
        self.setupUI()

    def setupUI(self):
        self.widgetyExportInclude['label_include'] = gui.Label(text="Include:")
        self.widgetyExportInclude['vyber_include'] = gui2.ComboBox(
            self.extractAllIncludes(), name="vyber_include"
        )

        self.widgetyExportInclude['label_cesta'] = gui.Label(text="Path to file:")
        self.widgetyExportInclude['vyber_cesta'] = gui.SaveFileEntry(placeholdertext="Path to file")



        close = gui.Button('Close', command=self.onCloseExportIncludeGUI)
        export = gui.Button('Export', command=self.export)


        upperFrame = gui.HFrame(
            (5),
            (
                self.widgetyExportInclude['label_include'], 5, self.widgetyExportInclude['vyber_include'], 10,
                self.widgetyExportInclude['label_cesta'], self.widgetyExportInclude['vyber_cesta'], 20
            ),
            (10),
        )

        lowerFrame = gui.HFrame(100, export, close)

        self.dialogExportInclude.recess().add(upperFrame)
        self.dialogExportInclude.recess().add(lowerFrame)
        self.dialogExportInclude.setButtonVisibile('ok', False)
        self.dialogExportInclude.setButtonVisibile('cancel', False)

    def onCloseExportIncludeGUI(self, event):
        self.dialogExportInclude.Hide()

    def export(self, event=None):
        if self.widgetyExportInclude['vyber_cesta'].value == "":
            gui2.tellUser("Path is empty.")
            return

        hw.evalTcl(f'*createstringarray 2 "HMBOMCOMMENTS_XML" "HMMATCOMMENTS_XML"')
        hw.evalTcl(f'*feoutput_singleinclude 1 "{self.widgetyExportInclude["vyber_include"].value}" "C:/Program Files/Altair/2023.1/hwdesktop/templates/feoutput/radioss/radioss2023.blk" "{self.widgetyExportInclude["vyber_cesta"].value}" 1 0 2 1 2')

        repair_exported_include(self.widgetyExportInclude["vyber_cesta"].value)

        self.dialogExportInclude.hide()


    def extractAllIncludes(self):
        includes = hw.evalTcl(f'set includes [hm_getincludes -byshortname]')
        include_list = split_text(includes)
        return include_list

def mainFunc(*args, **kwargs):
    dialogExportInclude = DialogExportInclude()
    dialogExportInclude.dialogExportInclude.show(width=dialogExportInclude.width, height=dialogExportInclude.height)
    logger.debug("Initiated AddPart...")

if __name__ == "__main__":
    mainFunc()