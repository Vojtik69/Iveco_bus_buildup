import os
import sys
# Získání cesty k aktuálně běžícímu skriptu
currentDir = os.path.dirname(os.path.realpath(__file__))
print(f"dirname: {currentDir}")
# Přidání této cesty do sys.path
sys.path.append(currentDir)
import re
from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
from common import (
    findPathToIncludeFile, getWidgetStructure, getWidgetVehicleSpecStructure,
    saveSetup, loadSetup, resetModelEdit, importParts, hierarchyOfTypes, paths,
    findCompatibleParts, findAllOfType, getValuesForVehicleSpec, getSelectedSolver,
    solverInterface, print_caller_info, findLevel, findCompatibility
)


class ModelBuildup:
    def __init__(self):
        self.currentDir = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(self.currentDir)

        self.parts = importParts()
        self.widgetyBuildup = {}
        self.dialogModelBuildup = gui.Dialog(caption="Bus model build-up")
        self.selectedSolver = getSelectedSolver()
        self.columnWidth = 230

        print("Initiating...")

    def solverChange(self, event):
        self.selectedSolver = event.widget.value
        print(f"solverChange() selectedSolver: {self.selectedSolver}")

        for label, widget in self.widgetyBuildup.items():
            print(f"label: {label}")
            print(f"widget: {widget}")

            if isinstance(widget, gui2.ListBox):
                items = widget.items
                selectedIndexes = widget.selectedIndexes
                selectedItems = [items[index] for index in selectedIndexes] if selectedIndexes else []

                widget.clear()
                widget.append(
                    findCompatibleParts(hierarchyOfTypes, self.parts, self.widgetyBuildup, self.selectedSolver,
                                        label.replace("vyber_", ""), removeEmpty=True))

                for index, item in enumerate(widget.items):
                    if item in selectedItems:
                        print(f"selected items: {selectedItems}")
                        print(f"index: {index}, {item}")
                        widget.select(index)

            elif isinstance(widget, gui2.ComboBox):
                selected_value = widget.value
                if label.replace("vyber_", "") in [item['name'] for item in hierarchyOfTypes['groups']['vehicle_spec']]:
                    values = getValuesForVehicleSpec(self.parts, label.replace("vyber_", ""), removeEmpty=False)
                else:
                    values = findAllOfType(self.parts, self.selectedSolver, label.replace("vyber_", ""),
                                           removeEmpty=False)

                print(f"all values: {values}")
                print_caller_info()
                widget.setValues(values)
                try:
                    widget.value = selected_value
                except:
                    pass

    def onCloseModelBuildup(self, event):
        self.dialogModelBuildup.hide()

    def onBuildUpModelBuildup(self, event):
        print(f"BuildUp")
        print(f"selectedSolver: {self.selectedSolver}")
        print(f"solverInterface: {solverInterface[self.selectedSolver - 2]}")

        hw.evalTcl(
            f'source "{paths["tcl"]}"; set change_finished false; ::UserProfiles::LoadUserProfile {solverInterface[self.selectedSolver - 2]} changing_interface_finished; vwait change_finished')
        hw.evalTcl(f'*start_batch_import 2')

        # Příprava potřebných dat
        import_data = []

        for label, widget in self.widgetyBuildup.items():
            label = label.replace('vyber_', '')
            if isinstance(widget, gui2.ListBox):
                items = widget.items
                selectedIndexes = widget.selectedIndexes
                selectedItems = [items[index] for index in selectedIndexes] if selectedIndexes else []

                for selectedItem in selectedItems:
                    if selectedItem != "---":
                        path = findPathToIncludeFile(self.parts, self.selectedSolver, selectedItem)
                        hierarchy = findLevel(hierarchyOfTypes, label)
                        import_data.append((label, path, selectedItem, self.selectedSolver, hierarchy))
                    else:
                        print(f"selectedItem: {selectedItem}")

            elif isinstance(widget, gui2.ComboBox):
                selectedValue = widget.value
                if selectedValue != "---":
                    path = findPathToIncludeFile(self.parts, self.selectedSolver, selectedValue)
                    hierarchy = findLevel(hierarchyOfTypes, label)
                    import_data.append((label, path, selectedValue, self.selectedSolver, hierarchy))
                else:
                    print(f"selectedItem: {selectedValue}")

        print(import_data)
        sortedImportData = sorted(import_data, key=lambda x: x[4], reverse=True)
        print(sortedImportData)

        # Realizace loop a příkazů na připravených datech
        for label, path, selectedItem, selectedSolver, hierarchy in import_data:
            print(f"Label: {label}, path: {path}")
            if os.path.exists(path):
                hw.evalTcl(
                    f'source "{paths["tcl"]}"; import_data "{path}" "{selectedItem}" "{selectedSolver}"')
                for label2, path2, selectedItem2, selectedSolver2, hierarchy2 in sortedImportData:
                    if hierarchy2 < hierarchy:
                        compatibilityValue = findCompatibility(self.parts, selectedItem, selectedItem2)
                        print(f"compatibilita: {selectedItem} + {selectedItem2}: {compatibilityValue}")
                        if not isinstance(compatibilityValue, int):
                            if '[' in compatibilityValue and ']' in compatibilityValue:
                                print("budeme posouvat")
                                numbers = re.findall(r'\d+', compatibilityValue)
                                x, y, z = map(int, numbers)
                                hw.evalTcl(
                                    f'source "{paths["tcl"]}"; move_include "{selectedItem}" {x} {y} {z}')
                                break
                            else:
                                print("compatibility value is not int and does not contain both brackets [ and ]")
            else:
                print(f"Include file {path} does not exist. Skipping this include.")


        print("ending batch import")
        hw.evalTcl(f'puts "Going to end batch import"')
        hw.evalTcl(f'*end_batch_import')
        print("realizing connectors")
        try:
            hw.evalTcl(f'source "{paths["tcl"]}"; realize_connectors')
        except:
            print("not able to realize connectors")

        self.onCloseModelBuildup(None)
        gui2.tellUser('Model build-up has finished!')
        self.dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    def onResetModelBuildup(self, event):
        resetModelEdit(event, self.widgetyBuildup, self.selectedSolver, self.parts)

    def modelBuildupGui(self):
        close = gui.Button('Close', command=self.onCloseModelBuildup)
        buildup = gui.Button('Build-up', command=self.onBuildUpModelBuildup)
        reset = gui.Button('Reset', command=self.onResetModelBuildup)

        solver_values = [(2, "OptiStruct"), (3, "Radioss")] if hw.evalTcl(
            f"hm_framework getuserprofile") == "OptiStruct {}" else [(3, "Radioss"), (2, "OptiStruct")]
        solver = gui2.ComboBox(solver_values, command=lambda event: self.solverChange(event), name="solver", width=150)

        load = gui.Button('Load setup',
                          command=lambda event: loadSetup(event, self.widgetyBuildup, self.selectedSolver, self.parts))
        save = gui.Button('Save setup', command=lambda event: saveSetup(event, self.widgetyBuildup))

        vehicleSpecFrame = gui.HFrame(
            getWidgetVehicleSpecStructure(hierarchyOfTypes["groups"]["vehicle_spec"], hierarchyOfTypes, self.parts,
                                          self.widgetyBuildup, self.selectedSolver), container=True, maxwidth=500)

        widgetStructure, columns = getWidgetStructure(hierarchyOfTypes["groups"]["FT groups"], hierarchyOfTypes,
                                                      self.parts, self.selectedSolver, self.widgetyBuildup)

        widgetFrame = gui.HFrame(widgetStructure, container=True)
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

        self.dialogModelBuildup.recess().add(mainFrame)
        self.dialogModelBuildup.setButtonVisibile('ok', False)
        self.dialogModelBuildup.setButtonVisibile('cancel', False)

        width = columns * self.columnWidth
        height = widgetFrame.maxheight + 100

        return width, height


def mainFunc(*args, **kwargs):
    model_buildup = ModelBuildup()
    width, height = model_buildup.modelBuildupGui()
    model_buildup.dialogModelBuildup.show(width=width, height=height)
    print("Initiated...")

if __name__ == "__main__":
    mainFunc()