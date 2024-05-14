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
    getWidgetVehicleSpecStructure, saveSetup, loadSetup, resetModelBuildup, parts, hierarchyOfTypes, tclPath, \
    findCompatibleParts, findAllOfType, getValuesForVehicleSpec

print("Initiating...")

# Slovník pro uchování vytvořených widgetů
widgetyBuildup = {}
widgetyAddPart = {}
widgetyEditPart = {}
dialogSetCompatibility = gui.Dialog(caption="Set compatibility")
dialogModelBuildup = gui.Dialog(caption="Bus model build-up")
dialogAddPart = gui.Dialog(caption="Add Part")
dialogEditPart = gui.Dialog(caption="Edit Part")

selectedSolver = 2 #2-optistruct, 3-radioss - it corresponds to column in csv, where first is index, second is type but it s columnt No. 0, then is OptiStruct as No.1,...
solverInterface = ['"OptiStruct" {}', '"RadiossBlock" "Radioss2023"']


def modelBuildupGui():
    global dialogModelBuildup
    global selectedSolver

    def solverChange(event, hierarchyOfTypes, parts, widgetyBuildup):
        global selectedSolver
        selectedSolver = event.widget.value
        print(f"solverchange() selectedSolver: {selectedSolver}")
        # print(widgetyBuildup)
        for label, widget in widgetyBuildup.items():
            # print(label)
            # print(widget)

            # if it is Multiselection
            if isinstance(widget, gui2.ListBox):
                items = widget.items
                selectedIndexes = widget.selectedIndexes
                if selectedIndexes:
                    selectedItems = [items[index] for index in selectedIndexes]
                else:
                    selectedItems = []

                widget.clear()
                widget.append(
                    findCompatibleParts(hierarchyOfTypes, parts, widgetyBuildup, selectedSolver,
                                        label.replace("vyber_", ""), removeEmpty=True))

                for index, item in enumerate(widget.items):
                    if item in selectedItems:
                        print(f"selected items: {selectedItems}")
                        print(f"index: {index}, {item}")
                        widget.select(index)


            # if it is onlyselection Combo
            elif isinstance(widget, gui2.ComboBox):
                selected_value = widget.value
                values = findAllOfType(parts, selectedSolver, label.replace("vyber_", ""), removeEmpty=False)
                print(f"values: {values}")
                if len(values) == 1:
                    values = getValuesForVehicleSpec(parts, label.replace("vyber_", ""), removeEmpty=False)
                widget.setValues(values)

                try:
                    widget.value = selected_value
                except:
                    pass

    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        dialogModelBuildup.hide()


    # Method called on clicking 'Build-up'.
    def onBuildUpModelBuildup(event):
        global selectedSolver
        print(f"BuildUp")
        print(f"selectedSolver: {selectedSolver}")
        print(f"solverInterface: {solverInterface[selectedSolver - 2]}")
        hw.evalTcl(f'source "{tclPath}"; puts "jdu na to"; set global_variable false; ::UserProfiles::LoadUserProfile {solverInterface[selectedSolver - 2]} changing_interface_finished; vwait global_variable; puts "jdu dal"')
        hw.evalTcl(f' puts "konec"; *start_batch_import 2')
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
                        if os.path.exists(path):
                            hw.evalTcl(f'source "{tclPath}"; import_data "{path}"')
                        else:
                            print(f"Include file {path} does not exist. Skipping this include.")
                    else:
                        print(f"selectedItem: {selectedItem}")

            # if it is onlyselection Combo
            elif isinstance(widget, gui2.ComboBox):
                print(f"Combo: {widget}")
                selectedValue = widget.value
                if selectedValue != "---":
                    path = findPathToIncludeFile(parts, selectedSolver, selectedValue)
                    print(f"path: {path}")
                    if os.path.exists(path):
                        hw.evalTcl(f'source "{tclPath}"; import_data "{path}"')
                    else:
                        print(f"Include file {path} does not exist. Skipping this include.")
                else:
                    print(f"selectedItem: {selectedValue}")
        print("ending batch import")
        hw.evalTcl(f'puts "Going to end batch import"')
        hw.evalTcl(f'*end_batch_import')
        print("realizing connectors")
        hw.evalTcl(f'source "{tclPath}"; realize_connectors')
        onCloseModelBuildup(None)
        gui2.tellUser('Model build-up has finished!')
        dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    # Method called on clicking 'Reset'.
    def onResetModelBuildup(event):
        global selectedSolver
        resetModelBuildup(event, widgetyBuildup, selectedSolver, parts)
        return

    close = gui.Button('Close', command=onCloseModelBuildup)
    buildup = gui.Button('Build-up', command=lambda event: onBuildUpModelBuildup(event))
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

modelBuildupGui()

if __name__ == "__main__":
    mainFunc()
