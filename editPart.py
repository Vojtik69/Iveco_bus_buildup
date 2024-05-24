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

from common import findPathToIncludeFile, getWidgetStructure, \
    getWidgetVehicleSpecStructure, saveSetup, loadSetup, resetModelBuildup, parts, hierarchyOfTypes, tclPath, \
    findCompatibleParts, findAllOfType, getValuesForVehicleSpec, extractAllTypes, findAllParts

from compatibility import SetCompatibilityGUI, showCompatibilityGUI

print("Initiating EditPart...")


widgetyEditPart = {}
dialogEditPart = gui.Dialog(caption="Edit Part")

width = 200
height = 200


def EditPartGUI():
    global widgetyEditPart

    def onSelectedTypeOriginal():
        widgetyEditPart['vyber_typ_new'].set(widgetyEditPart['vyber_typ_original'].get())
        widgetyEditPart['vyber_nazev_original'].setValues(findAllOfType(parts, None, widgetyEditPart['vyber_typ_original'].get(), removeEmpty=True))
        widgetyEditPart['vyber_nazev_new'].set(widgetyEditPart['vyber_nazev_original'].get())
        widgetyEditPart['vyber_cesta_new_OptiStruct'].set(findPathToIncludeFile(parts, 2, widgetyEditPart['vyber_nazev_original'].get()))
        widgetyEditPart['vyber_cesta_new_Radioss'].set(findPathToIncludeFile(parts, 3, widgetyEditPart['vyber_nazev_original'].get()))

    def onSelectedNameOriginal():
        widgetyEditPart['vyber_nazev_new'].set(widgetyEditPart['vyber_nazev_original'].get())
        widgetyEditPart['vyber_cesta_new_OptiStruct'].set(findPathToIncludeFile(parts, 2, widgetyEditPart['vyber_nazev_original'].get()))
        widgetyEditPart['vyber_cesta_new_Radioss'].set(findPathToIncludeFile(parts, 3, widgetyEditPart['vyber_nazev_original'].get()))


    widgetyEditPart['label_typ_original'] = gui.Label(text="Original type of part:")
    widgetyEditPart['vyber_typ_original'] = gui2.ComboBox(extractAllTypes(hierarchyOfTypes, onlyNames=True), name="vyber_typ_original", command=onSelectedTypeOriginal)

    widgetyEditPart['label_nazev_original'] = gui.Label(text="Original name of part:")
    widgetyEditPart['vyber_nazev_original'] = gui2.ComboBox(findAllOfType(parts, None, widgetyEditPart['vyber_typ_original'].value, removeEmpty=True), name="vyber_typ_original", command=onSelectedNameOriginal)

    widgetyEditPart['label_typ_new'] = gui.Label(text="New type of part:")
    widgetyEditPart['vyber_typ_new'] = gui2.ComboBox(extractAllTypes(hierarchyOfTypes, onlyNames=True), name="vyber_typ_new")

    widgetyEditPart['label_nazev_new'] = gui.Label(text="New name of part:")
    widgetyEditPart['vyber_nazev_new'] = gui.LineEdit(findAllOfType(parts, None, widgetyEditPart['vyber_typ_original'].value)[1])

    widgetyEditPart['label_cesta_new_OptiStruct'] = gui.Label(text="New path to OptiStruct:")
    widgetyEditPart['vyber_cesta_new_OptiStruct'] = gui.OpenFileEntry(findPathToIncludeFile(parts, 2, widgetyEditPart['vyber_nazev_original'].get()), placeholdertext="Path to OptiStruct")

    widgetyEditPart['label_cesta_new_Radioss'] = gui.Label(text="New path to Radioss:")
    widgetyEditPart['vyber_cesta_new_Radioss'] = gui.OpenFileEntry(findPathToIncludeFile(parts, 3, widgetyEditPart['vyber_nazev_original'].get()), placeholdertext="Path to Radioss")


    # Method called on clicking 'Close'.
    def onCloseEditPartGUI(event):
        global dialogEditPart
        dialogEditPart.Hide()

    def onResetEditPartGUI(event):
        widgetyEditPart['vyber_typ_original'].value = ""
        widgetyEditPart['vyber_nazev_original'].setValues(findAllOfType(parts, None, widgetyEditPart['vyber_typ_original'].get(), removeEmpty=True))
        widgetyEditPart['vyber_typ_new'].value = widgetyEditPart['vyber_typ_original'].value
        widgetyEditPart['vyber_nazev_new'].value = widgetyEditPart['vyber_nazev_original'].value
        widgetyEditPart['vyber_cesta_new_OptiStruct'].value = findPathToIncludeFile(parts, 2, widgetyEditPart['vyber_nazev_original'].get())
        widgetyEditPart['vyber_cesta_new_Radioss'].value = findPathToIncludeFile(parts, 3, widgetyEditPart['vyber_nazev_original'].get())

    def checkNotEmpty():
        if widgetyEditPart['vyber_nazev_new'].value in findAllParts(parts):
            if widgetyEditPart['vyber_nazev_original'].value != widgetyEditPart['vyber_nazev_new'].value:
                gui2.tellUser("New name of part is not unique")
                return

        if widgetyEditPart['vyber_cesta_new_OptiStruct'].value == "" and widgetyEditPart['vyber_cesta_new_Radioss'].value == "":
            gui2.tellUser("Paths to files are both empty.")
            return
        else:
            if widgetyEditPart['vyber_cesta_new_OptiStruct'].value != "" and not os.path.isfile(
                    widgetyEditPart['vyber_cesta_new_OptiStruct'].value):
                gui2.tellUser("Path for OptiStruct is not valid. The file does not exist.")
                return
            if widgetyEditPart['vyber_cesta_new_Radioss'].value != "" and not os.path.isfile(
                    widgetyEditPart['vyber_cesta_new_Radioss'].value):
                gui2.tellUser("Path for Radioss is not valid. The file does not exist.")
                return

        partInfo = {"partType": widgetyEditPart['vyber_typ_new'].value,
                    "partName": widgetyEditPart['vyber_nazev_new'].value,
                    "optistruct": widgetyEditPart['vyber_cesta_new_OptiStruct'].value or "",
                    "radioss" : widgetyEditPart['vyber_cesta_new_Radioss'].value or "",
                    }
        showCompatibilityGUI(dialogEditPart, widgetyEditPart['vyber_typ_new'].value, hierarchyOfTypes, parts, partInfo)
        dialogEditPart.hide()

    # TODO: při editování hledat kompatibilitu podle starého názvu a nového typu

    close = gui.Button('Close', command=onCloseEditPartGUI)
    add   = gui.Button('Set compatibility >>>', command=checkNotEmpty)
    reset = gui.Button('Reset', command=onResetEditPartGUI)

    upperFrame = gui.HFrame(
        (5),
        (widgetyEditPart['label_typ_original'], 5, widgetyEditPart['vyber_typ_original']),
        (widgetyEditPart['label_nazev_original'], 5, widgetyEditPart['vyber_nazev_original']),
        (230)

    )
    middleFrame = gui.HFrame(
        (widgetyEditPart['label_typ_new'], 5, widgetyEditPart['vyber_typ_new'], 15, widgetyEditPart['label_cesta_new_OptiStruct'], 5, widgetyEditPart['vyber_cesta_new_OptiStruct'], 30),
        (widgetyEditPart['label_nazev_new'], 5, widgetyEditPart['vyber_nazev_new'],  15, widgetyEditPart['label_cesta_new_Radioss'], 5, widgetyEditPart['vyber_cesta_new_Radioss'], 30)
    )

    lowerFrame = gui.HFrame(100, add, reset, close)
    sep = gui.Separator(orientation='horizontal', spacing='15')

    dialogEditPart.recess().add(upperFrame)
    dialogEditPart.recess().add(sep)
    dialogEditPart.recess().add(middleFrame)
    dialogEditPart.recess().add(lowerFrame)
    dialogEditPart.setButtonVisibile('ok', False)
    dialogEditPart.setButtonVisibile('cancel', False)
    dialogEditPart.show(width=600, height=80)


EditPartGUI()
def mainFunc(*args, **kwargs):
    global dialogEditPart
    dialogEditPart.show(width=width, height=height)
    print("Initiated...")

if __name__ == "__main__":
    mainFunc()