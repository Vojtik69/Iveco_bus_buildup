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

from common import findPathToIncludeFile, solverChange, getWidgetStructure, \
    getWidgetVehicleSpecStructure, saveSetup, loadSetup, resetModelBuildup, parts, hierarchyOfTypes, tclPath, \
    config_instance, solverInterface

print("Initiating...")

# Slovník pro uchování vytvořených widgetů
widgetyBuildup = {}
widgetyAddPart = {}
widgetyEditPart = {}
dialogSetCompatibility = gui.Dialog(caption="Set compatibility")
dialogModelBuildup = gui.Dialog(caption="Bus model build-up")
dialogAddPart = gui.Dialog(caption="Add Part")
dialogEditPart = gui.Dialog(caption="Edit Part")


def modelBuildupGui(selectedSolver):
    global dialogModelBuildup

    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        dialogModelBuildup.hide()


    # Method called on clicking 'Build-up'.
    def onBuildUpModelBuildup(event, selectedSolver):
        print(f"BuildUp")
        print(f"selectedSolver: {selectedSolver}")
        print(f"solverInterface: {solverInterface[selectedSolver - 2]}")
        hw.evalTcl(f'::UserProfiles::LoadUserProfile {solverInterface[selectedSolver - 2]}')
        hw.evalTcl(f'puts "User profile changed"')
        for label, widget in widgetyBuildup.items():
            print(f"Widget: {widget}")
            # if type(widget) == gui2.ListBox:
            if isinstance(widget, gui2.ListBox):
                print(f"ListBox: {widget}")
                items = widget.items
                selectedIndexes = widget.selectedIndexes
                if selectedIndexes:
                    selectedItems = [items[index] for index in selectedIndexes]
                else:
                    selectedItems = []

                for selectedItem in selectedItems:
                    if selectedItem != "---":
                        path = findPathToIncludeFile(parts, selectedSolver, selectedItem)
                        print(f"path: {path}")
                        hw.evalTcl(f'source "{tclPath}"; import_data "{path}"')
                    else:
                        print(f"selectedItem: {selectedItem}")

            # if it is onlyselection Combo
            elif isinstance(widget, gui2.ComboBox):
                print(f"Combo: {widget}")
                selectedValue = widget.value
                if selectedValue != "---":
                    path = findPathToIncludeFile(parts, selectedSolver, selectedValue)
                    print(f"path: {path}")
                    hw.evalTcl(f'source "{tclPath}"; import_data "{path}"')
                else:
                    print(f"selectedItem: {selectedValue}")
        onCloseModelBuildup(None)
        gui2.tellUser('Model build-up has finished!')
        dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    # Method called on clicking 'Reset'.
    def onResetModelBuildup(event):
        resetModelBuildup(event, widgetyBuildup, selectedSolver, parts)
        return

    close = gui.Button('Close', command=onCloseModelBuildup)
    buildup = gui.Button('Build-up', command=lambda event: onBuildUpModelBuildup(event, selectedSolver))
    reset = gui.Button('Reset', command=onResetModelBuildup)
    solver = gui2.ComboBox([(2,"OptiStruct"), (3,"Radioss")], command=lambda event: solverChange(event,
                                                                                                 hierarchyOfTypes,
                                                                                                 parts, widgetyBuildup), name="solver", width=150)
    # solver = gui2.ComboBox([(2, "OptiStruct"), (3, "Radioss")], command=lambda event: print(selectedSolver),
    #                        name="solver", width=150)
    load = gui.Button('Load setup', command=lambda event: loadSetup(event, widgetyBuildup, selectedSolver))
    save = gui.Button('Save setup', command=lambda event: saveSetup(event, widgetyBuildup))

    vehicleSpecFrame = gui.HFrame(
        getWidgetVehicleSpecStructure(hierarchyOfTypes["groups"]["vehicle_spec"], hierarchyOfTypes, parts,
                                      widgetyBuildup, selectedSolver), container=True, maxwidth=500)

    widgetFrame = gui.HFrame(
        getWidgetStructure(hierarchyOfTypes["groups"]["FT groups"], hierarchyOfTypes, parts, selectedSolver,
                           widgetyBuildup), container=True, )
    widgetFrame.maxheight = widgetFrame.reqheight

    mainFrame = gui.VFrame(
        (solver, "<->", load, save),
        15,
        vehicleSpecFrame,
        15,
        widgetFrame,
        15,
        ("<->", buildup, reset, close)
    )


    dialogModelBuildup.recess().add(mainFrame)

    dialogModelBuildup.setButtonVisibile('ok', False)
    dialogModelBuildup.setButtonVisibile('cancel', False)

    # mainFrame.move(x = 1, y = 1)

def mainFunc(*args, **kwargs):
    global dialogModelBuildup

    dialogModelBuildup.show(width=1000, height=500)
    print("Initiated...")

modelBuildupGui(config_instance.selectedSolver)

if __name__ == "__main__":
    mainFunc()
