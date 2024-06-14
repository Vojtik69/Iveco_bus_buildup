import os
import sys
# Získání cesty k aktuálně běžícímu skriptu
currentDir = os.path.dirname(os.path.realpath(__file__))
print(f"dirname: {currentDir}")
# Přidání této cesty do sys.path
sys.path.append(currentDir)
from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import pandas as pd

from common import (
    findPathToIncludeFile, getWidgetStructure, getWidgetVehicleSpecStructure,
    resetModelEdit, importParts, hierarchyOfTypes, paths, findCompatibleParts,
    findAllOfType, getValuesForVehicleSpec, extractAllTypes, findAllParts
)

from compatibility import SetCompatibilityGUI, showCompatibilityGUI

parts = importParts()

class DialogAddPart:
    def __init__(self):
        self.currentDir = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(self.currentDir)
        self.widgetyAddPart = {}
        self.dialogAddPart = gui.Dialog(caption="Add Part")
        self.width = 200
        self.height = 200
        self.setupUI()

    def setupUI(self):
        self.widgetyAddPart['label_typ'] = gui.Label(text="Type of new part:")
        self.widgetyAddPart['vyber_typ'] = gui2.ComboBox(
            extractAllTypes(hierarchyOfTypes, onlyNames=True), name="vyber_typ"
        )

        self.widgetyAddPart['label_cesta_OptiStruct'] = gui.Label(text="Path to OptiStruct:")
        self.widgetyAddPart['vyber_cesta_OptiStruct'] = gui.OpenFileEntry(placeholdertext="Path to OptiStruct")

        self.widgetyAddPart['label_cesta_Radioss'] = gui.Label(text="Path to Radioss:")
        self.widgetyAddPart['vyber_cesta_Radioss'] = gui.OpenFileEntry(placeholdertext="Path to Radioss")

        self.widgetyAddPart['label_nazev'] = gui.Label(text="Name of new part:")
        self.widgetyAddPart['vyber_nazev'] = gui.LineEdit()

        close = gui.Button('Close', command=self.onCloseAddPartGUI)
        add = gui.Button('Set compatibility >>>', command=self.checkNotEmpty)
        reset = gui.Button('Reset', command=self.onResetAddPartGUI)

        upperFrame = gui.HFrame(
            (5),
            (
                self.widgetyAddPart['label_nazev'], 5, self.widgetyAddPart['vyber_nazev'], 10,
                self.widgetyAddPart['label_cesta_OptiStruct'], self.widgetyAddPart['vyber_cesta_OptiStruct'], 20
            ),
            (
                self.widgetyAddPart['label_typ'], 5, self.widgetyAddPart['vyber_typ'], 10,
                self.widgetyAddPart['label_cesta_Radioss'], self.widgetyAddPart['vyber_cesta_Radioss'], 20
            ),
            (10),
        )

        lowerFrame = gui.HFrame(100, add, reset, close)

        self.dialogAddPart.recess().add(upperFrame)
        self.dialogAddPart.recess().add(lowerFrame)
        self.dialogAddPart.setButtonVisibile('ok', False)
        self.dialogAddPart.setButtonVisibile('cancel', False)

    def onCloseAddPartGUI(self, event):
        self.dialogAddPart.Hide()

    def onResetAddPartGUI(self, event):
        self.widgetyAddPart['vyber_nazev'].value = ""
        self.widgetyAddPart['vyber_cesta_OptiStruct'].value = ""
        self.widgetyAddPart['vyber_cesta_Radioss'].value = ""
        self.widgetyAddPart['vyber_typ'].value = ""

    def checkNotEmpty(self, event=None):
        if self.widgetyAddPart['vyber_nazev'].value in findAllParts(parts):
            gui2.tellUser("Name of new part is not unique")
            return

        if not self.widgetyAddPart['vyber_nazev'].value:
            gui2.tellUser("Name of new part is empty")
            return

        if self.widgetyAddPart['vyber_cesta_OptiStruct'].value == "" and self.widgetyAddPart['vyber_cesta_Radioss'].value == "":
            gui2.tellUser("Paths to files are both empty.")
            return
        else:
            if self.widgetyAddPart['vyber_cesta_OptiStruct'].value != "" and not os.path.isfile(self.widgetyAddPart['vyber_cesta_OptiStruct'].value):
                gui2.tellUser("Path for OptiStruct is not valid. The file does not exist.")
                return
            if self.widgetyAddPart['vyber_cesta_Radioss'].value != "" and not os.path.isfile(self.widgetyAddPart['vyber_cesta_Radioss'].value):
                gui2.tellUser("Path for Radioss is not valid. The file does not exist.")
                return

        partInfo = {
            "partType": self.widgetyAddPart['vyber_typ'].value,
            "partName": self.widgetyAddPart['vyber_nazev'].value,
            "optistruct": self.widgetyAddPart['vyber_cesta_OptiStruct'].value or "",
            "radioss": self.widgetyAddPart['vyber_cesta_Radioss'].value or ""
        }

        showCompatibilityGUI(
            self.dialogAddPart, self.widgetyAddPart['vyber_typ'].value, hierarchyOfTypes, parts, partInfo
        )
        self.dialogAddPart.hide()

def mainFunc(*args, **kwargs):
    dialogAddPart = DialogAddPart()
    dialogAddPart.dialogAddPart.show(width=dialogAddPart.width, height=dialogAddPart.height)
    print("Initiated AddPart...")

if __name__ == "__main__":
    mainFunc()