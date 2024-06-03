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

from common import findPathToIncludeFile, getWidgetStructure, \
    getWidgetVehicleSpecStructure, saveSetup, loadSetup, resetModelEdit, importParts, hierarchyOfTypes, paths, \
    findCompatibleParts, findAllOfType, getValuesForVehicleSpec, findTypeOfPart

print("Initiating...")

parts = importParts()

# Slovník pro uchování vytvořených widgetů
widgetyModelEdit = {}

dialogModelEdit = gui.Dialog(caption="Bus model edit")


selectedSolver = 2 #2-optistruct, 3-radioss - it corresponds to column in csv, where first is index, second is type but it s columnt No. 0, then is OptiStruct as No.1,...
solverInterface = ['"OptiStruct" {}', '"RadiossBlock" "Radioss2023"']

columnWidth = 230

def modelEditGui():
    global dialogModelEdit
    global selectedSolver

    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        dialogModelEdit.hide()


    # Method called on clicking 'Build-up'.
    def onEditModel(event):
        # TODO otestovat

        userProfile = hw.evalTcl(f"hm_framework getuserprofile")
        if userProfile == "OptiStruct {}":
            selectedSolver = 2
        else:
            selectedSolver = 3

        listOfIncludes = hw.evalTcl(f"hm_getincludes -byshortname").split()
        listOfIncludesIds = hw.evalTcl(f"hm_getincludes").split()
        partTypes = []
        for include in listOfIncludes:
            partType = findTypeOfPart(parts, include)
            if partType:
                partTypes.append(partType)

        data = []
        for label, widget in widgetyModelEdit.items():
            if isinstance(widget, gui2.ListBox):
                items = widget.items
                selectedIndexes = widget.selectedIndexes
                if selectedIndexes:
                    for index in selectedIndexes:
                        data.append(items[index])
            elif isinstance(widget, gui2.ComboBox):
                selectedValue = widget.value
                data.append(selectedValue)
        hw.evalTcl(f'*start_batch_import 2')
        for part in data:
            if part != "---":
                if part in listOfIncludes:
                    index = listOfIncludes.index(part)
                    del listOfIncludesIds[index]
                    listOfIncludes.remove(part)
                else:
                    path = findPathToIncludeFile(parts, selectedSolver, part)
                    print(f"path: {path}")
                    if os.path.exists(path):
                        hw.evalTcl(f'source "{paths["tcl"]}"; import_data "{path}" "{selectedValue}"')
                    else:
                        print(f"Include file {path} does not exist. Skipping this include.")
        hw.evalTcl(f'*end_batch_import')

        # delete the unused includes
        try:
            hw.evalTcl(f'*removeincludes include_ids = {{ {" ".join(map(str, listOfIncludesIds))} }} remove_contents = 1')
        except:
            print("Unable to delete rest of includes")

        print("realizing connectors")
        try:
            hw.evalTcl(f'source "{paths["tcl"]}"; realize_connectors')
        except:
            print("not able to realize connectors")
        onCloseModelBuildup(None)
        gui2.tellUser('Model build-up has finished!')
        dialogModelEdit = gui.Dialog(caption="Bus model edit")

    # Method called on clicking 'Reset'.
    def onResetModelBuildup(event):
        global selectedSolver
        resetModelEdit(event, widgetyModelEdit, selectedSolver, parts)
        return

    def loadCurrentIncludes():
        listOfIncludes = hw.evalTcl(f"hm_getincludes -byshortname").split()
        partTypes = []
        for include in listOfIncludes:
            partType = findTypeOfPart(parts, include)
            if partType:
                partTypes.append(partType)

        # print(f"partTypes: {partTypes}")
        for i, (widgetKey, widget) in enumerate(widgetyModelEdit.items()):
            if widgetKey.startswith("vyber"):
                # print(f"widgetKey.split('_')[1] - {widgetKey.split('_')[1]}")
                partType = widgetKey.split('_')[1]
                if partType in partTypes:
                    partIndex = partTypes.index(partType)
                    # print("is in partTypes")
                    try:
                        # print(f"listOfIncludes[partIndex]: {listOfIncludes[partIndex]}")
                        if isinstance(widget, gui2.ListBox):
                            # print(f"ListBox")
                            for index, item in enumerate(widget.items):
                                if item == listOfIncludes[partIndex]:
                                    widget.select(index)
                        elif isinstance(widget, gui2.ComboBox):
                            # print(f"ComboBox")
                            widget.value = listOfIncludes[partIndex]
                    except:
                        print(f"Error in selecting parts in ComboBox or Listbox")
                        pass
        return

    close = gui.Button('Close', command=onCloseModelBuildup)
    buildup = gui.Button('Edit model', command=lambda event: onEditModel(event))
    reset = gui.Button('Reset', command=onResetModelBuildup)


    vehicleSpecFrame = gui.HFrame(
        getWidgetVehicleSpecStructure(hierarchyOfTypes["groups"]["vehicle_spec"], hierarchyOfTypes, parts,
                                      widgetyModelEdit, selectedSolver), container=True, maxwidth=500)

    widgetStructure, columns = getWidgetStructure(hierarchyOfTypes["groups"]["FT groups"], hierarchyOfTypes, parts, selectedSolver,
                                                  widgetyModelEdit)

    loadCurrentIncludes()

    widgetFrame = gui.HFrame(widgetStructure, container=True, )
    widgetFrame.maxheight = widgetFrame.reqheight

    mainFrame = gui.VFrame(
        vehicleSpecFrame,
        15,
        widgetFrame,
        15,
        ("<->", buildup, reset, close)
    )


    dialogModelEdit.recess().add(mainFrame)

    dialogModelEdit.setButtonVisibile('ok', False)
    dialogModelEdit.setButtonVisibile('cancel', False)

    # mainFrame.move(x = 1, y = 1)

    width = columns * columnWidth
    height = widgetFrame.maxheight + 100

    return width, height

width, height = modelEditGui()
def mainFunc(*args, **kwargs):
    global dialogModelEdit
    dialogModelEdit.show(width=width, height=height)
    print("Initiated...")

if __name__ == "__main__":
    mainFunc()
