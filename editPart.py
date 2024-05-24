import os
import sys
# Získání cesty k aktuálně běžícímu skriptu
currentDir = os.path.dirname(os.path.realpath(__file__))
print(f"dirname: {currentDir}")
# Přidání této cesty do sys.path
sys.path.append(currentDir)
import pandas as pd
from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2

from common import (
    findPathToIncludeFile, getWidgetStructure, getWidgetVehicleSpecStructure, saveSetup,
    loadSetup, resetModelBuildup, parts, hierarchyOfTypes, tclPath, findCompatibleParts,
    findAllOfType, getValuesForVehicleSpec, extractAllTypes, findAllParts
)

from compatibility import SetCompatibilityGUI, showCompatibilityGUI

class DialogEditPart:
    def __init__(self):
        self.currentDir = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(self.currentDir)
        self.widgetyEditPart = {}
        self.dialogEditPart = gui.Dialog(caption="Edit Part")
        self.width = 200
        self.height = 200
        self.setupUI()

    def setupUI(self):
        self.widgetyEditPart['label_typ_original'] = gui.Label(text="Original type of part:")
        self.widgetyEditPart['vyber_typ_original'] = gui2.ComboBox(
            extractAllTypes(hierarchyOfTypes, onlyNames=True), name="vyber_typ_original", command=self.onSelectedTypeOriginal
        )

        self.widgetyEditPart['label_nazev_original'] = gui.Label(text="Original name of part:")
        self.widgetyEditPart['vyber_nazev_original'] = gui2.ComboBox(
            findAllOfType(parts, None, self.widgetyEditPart['vyber_typ_original'].value, removeEmpty=True), name="vyber_nazev_original", command=self.onSelectedNameOriginal
        )

        self.widgetyEditPart['label_typ_new'] = gui.Label(text="New type of part:")
        self.widgetyEditPart['vyber_typ_new'] = gui2.ComboBox(
            extractAllTypes(hierarchyOfTypes, onlyNames=True), name="vyber_typ_new"
        )

        self.widgetyEditPart['label_nazev_new'] = gui.Label(text="New name of part:")
        self.widgetyEditPart['vyber_nazev_new'] = gui.LineEdit(
            findAllOfType(parts, None, self.widgetyEditPart['vyber_typ_original'].value)[1]
        )

        self.widgetyEditPart['label_cesta_new_OptiStruct'] = gui.Label(text="New path to OptiStruct:")
        self.widgetyEditPart['vyber_cesta_new_OptiStruct'] = gui.OpenFileEntry(
            findPathToIncludeFile(parts, 2, self.widgetyEditPart['vyber_nazev_original'].get()), placeholdertext="Path to OptiStruct"
        )

        self.widgetyEditPart['label_cesta_new_Radioss'] = gui.Label(text="New path to Radioss:")
        self.widgetyEditPart['vyber_cesta_new_Radioss'] = gui.OpenFileEntry(
            findPathToIncludeFile(parts, 3, self.widgetyEditPart['vyber_nazev_original'].get()), placeholdertext="Path to Radioss"
        )

        close = gui.Button('Close', command=self.onCloseEditPartGUI)
        add = gui.Button('Set compatibility >>>', command=self.checkNotEmpty)
        reset = gui.Button('Reset', command=self.onResetEditPartGUI)

        upperFrame = gui.HFrame(
            (5),
            (self.widgetyEditPart['label_typ_original'], 5, self.widgetyEditPart['vyber_typ_original']),
            (self.widgetyEditPart['label_nazev_original'], 5, self.widgetyEditPart['vyber_nazev_original']),
            (230)
        )

        middleFrame = gui.HFrame(
            (
                self.widgetyEditPart['label_typ_new'], 5, self.widgetyEditPart['vyber_typ_new'], 15,
                self.widgetyEditPart['label_cesta_new_OptiStruct'], 5, self.widgetyEditPart['vyber_cesta_new_OptiStruct'], 30
            ),
            (
                self.widgetyEditPart['label_nazev_new'], 5, self.widgetyEditPart['vyber_nazev_new'], 15,
                self.widgetyEditPart['label_cesta_new_Radioss'], 5, self.widgetyEditPart['vyber_cesta_new_Radioss'], 30
            )
        )

        lowerFrame = gui.HFrame(100, add, reset, close)
        sep = gui.Separator(orientation='horizontal', spacing='15')

        self.dialogEditPart.recess().add(upperFrame)
        self.dialogEditPart.recess().add(sep)
        self.dialogEditPart.recess().add(middleFrame)
        self.dialogEditPart.recess().add(lowerFrame)
        self.dialogEditPart.setButtonVisibile('ok', False)
        self.dialogEditPart.setButtonVisibile('cancel', False)

    def onSelectedTypeOriginal(self):
        self.widgetyEditPart['vyber_typ_new'].set(self.widgetyEditPart['vyber_typ_original'].get())
        self.widgetyEditPart['vyber_nazev_original'].setValues(
            findAllOfType(parts, None, self.widgetyEditPart['vyber_typ_original'].get(), removeEmpty=True)
        )
        self.widgetyEditPart['vyber_nazev_new'].set(self.widgetyEditPart['vyber_nazev_original'].get())
        self.widgetyEditPart['vyber_cesta_new_OptiStruct'].set(
            findPathToIncludeFile(parts, 2, self.widgetyEditPart['vyber_nazev_original'].get())
        )
        self.widgetyEditPart['vyber_cesta_new_Radioss'].set(
            findPathToIncludeFile(parts, 3, self.widgetyEditPart['vyber_nazev_original'].get())
        )

    def onSelectedNameOriginal(self):
        self.widgetyEditPart['vyber_nazev_new'].set(self.widgetyEditPart['vyber_nazev_original'].get())
        self.widgetyEditPart['vyber_cesta_new_OptiStruct'].set(
            findPathToIncludeFile(parts, 2, self.widgetyEditPart['vyber_nazev_original'].get())
        )
        self.widgetyEditPart['vyber_cesta_new_Radioss'].set(
            findPathToIncludeFile(parts, 3, self.widgetyEditPart['vyber_nazev_original'].get())
        )

    def onCloseEditPartGUI(self, event):
        self.dialogEditPart.Hide()

    def onResetEditPartGUI(self, event):
        self.widgetyEditPart['vyber_typ_original'].value = ""
        self.widgetyEditPart['vyber_nazev_original'].setValues(
            findAllOfType(parts, None, self.widgetyEditPart['vyber_typ_original'].get(), removeEmpty=True)
        )
        self.widgetyEditPart['vyber_typ_new'].value = self.widgetyEditPart['vyber_typ_original'].value
        self.widgetyEditPart['vyber_nazev_new'].value = self.widgetyEditPart['vyber_nazev_original'].value
        self.widgetyEditPart['vyber_cesta_new_OptiStruct'].value = findPathToIncludeFile(
            parts, 2, self.widgetyEditPart['vyber_nazev_original'].get()
        )
        self.widgetyEditPart['vyber_cesta_new_Radioss'].value = findPathToIncludeFile(
            parts, 3, self.widgetyEditPart['vyber_nazev_original'].get()
        )

    def checkNotEmpty(self):
        if self.widgetyEditPart['vyber_nazev_new'].value in findAllParts(parts):
            if self.widgetyEditPart['vyber_nazev_original'].value != self.widgetyEditPart['vyber_nazev_new'].value:
                gui2.tellUser("New name of part is not unique")
                return

        if self.widgetyEditPart['vyber_cesta_new_OptiStruct'].value == "" and self.widgetyEditPart['vyber_cesta_new_Radioss'].value == "":
            gui2.tellUser("Paths to files are both empty.")
            return
        else:
            if self.widgetyEditPart['vyber_cesta_new_OptiStruct'].value != "" and not os.path.isfile(self.widgetyEditPart['vyber_cesta_new_OptiStruct'].value):
                gui2.tellUser("Path for OptiStruct is not valid. The file does not exist.")
                return
            if self.widgetyEditPart['vyber_cesta_new_Radioss'].value != "" and not os.path.isfile(self.widgetyEditPart['vyber_cesta_new_Radioss'].value):
                gui2.tellUser("Path for Radioss is not valid. The file does not exist.")
                return

        partInfo = {
            "partType": self.widgetyEditPart['vyber_typ_new'].value,
            "partName": self.widgetyEditPart['vyber_nazev_new'].value,
            "optistruct": self.widgetyEditPart['vyber_cesta_new_OptiStruct'].value or "",
            "radioss": self.widgetyEditPart['vyber_cesta_new_Radioss'].value or "",
            "oldName": self.widgetyEditPart['vyber_nazev_original'].value
        }
        showCompatibilityGUI(self.dialogEditPart, self.widgetyEditPart['vyber_typ_new'].value, hierarchyOfTypes, parts, partInfo)
        self.dialogEditPart.hide()

    def show(self):
        self.onResetEditPartGUI(None)
        self.dialogEditPart.show(width=600, height=80)

def mainFunc(*args, **kwargs):
    dialog = DialogEditPart()
    dialog.show()
    print("Initiated...")

if __name__ == "__main__":
    mainFunc()
