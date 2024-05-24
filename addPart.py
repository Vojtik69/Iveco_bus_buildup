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

from common import findPathToIncludeFile, getWidgetStructure, \
    getWidgetVehicleSpecStructure, saveSetup, loadSetup, resetModelBuildup, parts, hierarchyOfTypes, tclPath, \
    findCompatibleParts, findAllOfType, getValuesForVehicleSpec, extractAllTypes, findAllParts

from compatibility import SetCompatibilityGUI, showCompatibilityGUI

print("Initiating AddPart...")

widgetyAddPart = {}

dialogAddPart = gui.Dialog(caption="Add Part")

width = 200
height = 200

# TODO resetovat při otevření
def checkNotEmpty(event, widgetyAddPart, parts):

    if widgetyAddPart['vyber_nazev'].value in findAllParts(parts):
        gui2.tellUser("Name of new part is not unique")
        return

    if not widgetyAddPart['vyber_nazev'].value:
        gui2.tellUser("Name of new part is empty")
        return

    if widgetyAddPart['vyber_cesta_OptiStruct'].value == "" and widgetyAddPart['vyber_cesta_Radioss'].value == "":
        gui2.tellUser("Paths to files are both empty.")
        return
    else:
        if widgetyAddPart['vyber_cesta_OptiStruct'].value != "" and not os.path.isfile(widgetyAddPart['vyber_cesta_OptiStruct'].value):
            gui2.tellUser("Path for OptiStruct is not valid. The file does not exist.")
            return
        if widgetyAddPart['vyber_cesta_Radioss'].value != "" and not os.path.isfile(widgetyAddPart['vyber_cesta_Radioss'].value):
            gui2.tellUser("Path for Radioss is not valid. The file does not exist.")
            return

    partInfo = {"partType": widgetyAddPart['vyber_typ'].value,
                "partName": widgetyAddPart['vyber_nazev'].value,
                "optistruct": widgetyAddPart['vyber_cesta_OptiStruct'].value or "",
                "radioss" : widgetyAddPart['vyber_cesta_Radioss'].value or ""
                }

    showCompatibilityGUI(dialogAddPart, widgetyAddPart['vyber_typ'].value, hierarchyOfTypes, parts, partInfo)
    dialogAddPart.hide()

def AddPartGUI():
    global widgetyAddPart
    global dialogAddPart
    global selectedSolver

    # Method called on clicking 'Close'.
    def onCloseAddPartGUI(event):
        global dialogAddPart
        dialogAddPart.Hide()

    def onResetAddPartGUI(event):
        widgetyAddPart['vyber_nazev'].value = ""
        widgetyAddPart['vyber_cesta_OptiStruct'].value = ""
        widgetyAddPart['vyber_cesta_Radioss'].value = ""
        widgetyAddPart['vyber_typ'].value = ""

    widgetyAddPart['label_typ'] = gui.Label(text="Type of new part:")
    widgetyAddPart['vyber_typ'] = gui2.ComboBox(extractAllTypes(hierarchyOfTypes, onlyNames=True), name="vyber_typ")
    # Possible to replace ComboBox for SearchBar or something similar in future
    # widgetyAddPart['vyber_typ_label'] = gui.Label(text="---")
    # widgetyAddPart['vyber_typ'] = gui.SearchBar(name="vyber_typ", command=changeType)
    # for type in extractAllTypes(hierarchyOfTypes, onlyNames=True):
    #     widgetyAddPart['vyber_typ'].addItem(label=type, category="Materials")

    widgetyAddPart['label_cesta_OptiStruct'] = gui.Label(text="Path to OptiStruct:")
    widgetyAddPart['vyber_cesta_OptiStruct'] = gui.OpenFileEntry(placeholdertext="Path to OptiStruct")

    widgetyAddPart['label_cesta_Radioss'] = gui.Label(text="Path to Radioss:")
    widgetyAddPart['vyber_cesta_Radioss'] = gui.OpenFileEntry(placeholdertext="Path to Radioss")

    widgetyAddPart['label_nazev'] = gui.Label(text="Name of new part:")
    widgetyAddPart['vyber_nazev'] = gui.LineEdit()

    close = gui.Button('Close', command=onCloseAddPartGUI)
    add   = gui.Button('Set compatibility >>>', command=lambda event: checkNotEmpty(event, widgetyAddPart, parts))
    reset = gui.Button('Reset', command=onResetAddPartGUI)

    upperFrame = gui.HFrame(
        (5),
        (widgetyAddPart['label_nazev'], 5, widgetyAddPart['vyber_nazev'], 10, widgetyAddPart['label_cesta_OptiStruct'], widgetyAddPart['vyber_cesta_OptiStruct'], 20),
        (widgetyAddPart['label_typ'], 5, widgetyAddPart['vyber_typ'], 10, widgetyAddPart['label_cesta_Radioss'], widgetyAddPart['vyber_cesta_Radioss'], 20),
        (10),
    )

    lowerFrame = gui.HFrame(100, add, reset, close)

    dialogAddPart.recess().add(upperFrame)
    dialogAddPart.recess().add(lowerFrame)
    dialogAddPart.setButtonVisibile('ok', False)
    dialogAddPart.setButtonVisibile('cancel', False)

    print(widgetyAddPart['vyber_cesta_OptiStruct'].value)

AddPartGUI()
def mainFunc(*args, **kwargs):
    global dialogAddPart
    dialogAddPart.show(width=width, height=height)
    print("Initiated...")

if __name__ == "__main__":
    mainFunc()
