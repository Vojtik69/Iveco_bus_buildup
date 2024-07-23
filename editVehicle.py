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
import re

from common import (findPathToIncludeFile, getWidgetStructure, \
    getWidgetVehicleSpecStructure, resetModelEdit, importParts, hierarchyOfTypes, paths, \
    findCompatibleParts, findAllOfType, getValuesForVehicleSpec, findTypeOfPart, getSelectedSolver, solverInterface,
    moveIncludes, updateSubordinantItems)

class ModelEdit:
    def __init__(self):
        self.currentDir = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(self.currentDir)

        self.parts = importParts()
        self.widgetyModelEdit = {}
        self.dialogModelEdit = gui.Dialog(caption="Bus model edit")
        self.selectedSolver = getSelectedSolver()
        self.columnWidth = 230

        print("Initiating...")

    def onCloseModelBuildup(self, event):
        self.dialogModelEdit.hide()

    def onEditModel(self, event):
        self.selectedSolver = getSelectedSolver()

        pattern = r'\{.*?\}|\S+'
        matches = re.findall(pattern, hw.evalTcl("hm_getincludes -byshortname"))
        listOfIncludesLablesOriginal = [match.strip('{}') for match in matches]

        listOfIncludes = []
        for item in listOfIncludesLablesOriginal:
            if '_moved' in item:
                base_label, moved_part = item.split('_moved', 1)
                listOfIncludes.append(base_label)
            else:
                listOfIncludes.append(item)

        print(f"listOfIncludes: {listOfIncludes}")
        listOfIncludesIds = hw.evalTcl("hm_getincludes").split()
        partTypes = []
        for include in listOfIncludes:
            partType = findTypeOfPart(self.parts, include)
            if partType:
                partTypes.append(partType)
        print(f"partTypes: {partTypes}")
        data = []
        for label, widget in self.widgetyModelEdit.items():
            print(f"label: {label}")
            if isinstance(widget, gui2.ListBox):
                items = widget.items
                selectedIndexes = widget.selectedIndexes
                if selectedIndexes:
                    for index in selectedIndexes:
                        data.append(items[index])
            elif isinstance(widget, gui2.ComboBox):
                selectedValue = widget.value
                data.append(selectedValue)
        print(f"data: {data}")
        # to be safe, we will end batch import if it was not terminated earlier
        hw.evalTcl('*end_batch_import')
        try:
            hw.evalTcl('*start_batch_import 2')
            for part in data:
                if part != "---":
                    if part in listOfIncludes:
                        index = listOfIncludes.index(part)
                        del listOfIncludesIds[index]
                        listOfIncludes.remove(part)
                    else:
                        path = findPathToIncludeFile(self.parts, self.selectedSolver, part)
                        print(f"part: {part}")
                        print(f"path: {path}")
                        if os.path.exists(path):
                            hw.evalTcl(f'source "{paths["tcl"]}"; import_data "{path}" "{part}" "{self.selectedSolver}"')
                        else:
                            hw.evalTcl(f'source "{paths["tcl"]}"; create_include "{part}"')
                            print(f"Include file {path} for {part} does not exist. Creating empty include.")

            try:
                hw.evalTcl(f'source "{paths["tcl"]}"; unrealize_connectors')
            except:
                print("not able to unrealize connectors")

            try:
                print(f'*removeincludes include_ids = {{ {" ".join(map(str, listOfIncludesIds))} }} remove_contents = 1')
                hw.evalTcl(
                    f'*removeincludes include_ids = {{ {" ".join(map(str, listOfIncludesIds))} }} remove_contents = 1')
            except:
                print("Unable to delete rest of includes")

            moveIncludes(self.parts)

        except Exception as e:
            print(f"Error in batch import: {e}")

        hw.evalTcl('*end_batch_import')

        print("realizing connectors")
        try:
            hw.evalTcl(f'source "{paths["tcl"]}"; realize_connectors')
        except:
            print("not able to realize connectors")

        self.onCloseModelBuildup(None)
        gui2.tellUser('Model edit has finished!')
        self.dialogModelEdit = gui.Dialog(caption="Bus model edit")

    def onResetModelBuildup(self, event):
        self.selectedSolver = getSelectedSolver()
        self.loadCurrentIncludes()

    def loadCurrentIncludes(self):
        self.selectedSolver = getSelectedSolver()
        print(f"selectedSolver: {self.selectedSolver}")

        pattern = r'\{.*?\}|\S+'
        matches = re.findall(pattern, hw.evalTcl("hm_getincludes -byshortname"))
        listOfIncludesLablesOriginal = [match.strip('{}') for match in matches]

        # remove ends of names in cases the include is moved and the name is ende by suffix _move_x_y_z
        listOfIncludes = [
            item[:item.find('_moved')] if item.find('_moved') != -1 else item
            for item in listOfIncludesLablesOriginal
        ]

        partTypes = []
        for include in listOfIncludes:
            partType = findTypeOfPart(self.parts, include)
            if partType:
                partTypes.append(partType)
        print(f"listOfIncludes: {listOfIncludes}")
        print(f"partTypes: {partTypes}")

        for i, includeName in enumerate(listOfIncludes):
            partType = partTypes[i]
            print(f"partType: {partType}")
            print(f"includeName: {includeName}")
            try:
                widget = self.widgetyModelEdit[f"vyber_{partType}"]
            except:
                continue

            try:
                if isinstance(widget, gui2.ListBox):
                    print("ListBox")
                    for index, item in enumerate(widget.items):
                        if item == includeName:
                            print(f"index, item: {index, item}")
                            widget.select(index)
                elif isinstance(widget, gui2.ComboBox):
                    print("ComboBox")
                    widget.value = includeName
                updateSubordinantItems(hierarchyOfTypes, self.parts, self.widgetyModelEdit, self.selectedSolver, partType)
            except:
                print("Error in selecting parts in ComboBox or Listbox")
                pass

    def modelEditGui(self):
        close = gui.Button('Close', command=self.onCloseModelBuildup)
        buildup = gui.Button('Edit model', command=lambda event: self.onEditModel(event))
        reset = gui.Button('Reset', command=self.onResetModelBuildup)

        vehicleSpecFrame = gui.HFrame(
            getWidgetVehicleSpecStructure(hierarchyOfTypes["groups"]["vehicle_spec"], hierarchyOfTypes, self.parts,
                                          self.widgetyModelEdit, self.selectedSolver), container=True, maxwidth=500)

        widgetStructure, columns = getWidgetStructure(hierarchyOfTypes["groups"]["FT groups"], hierarchyOfTypes,
                                                      self.parts, self.selectedSolver,
                                                      self.widgetyModelEdit)

        self.loadCurrentIncludes()

        widgetFrame = gui.HFrame(widgetStructure, container=True)
        widgetFrame.maxheight = widgetFrame.reqheight

        mainFrame = gui.VFrame(
            vehicleSpecFrame,
            15,
            widgetFrame,
            15,
            ("<->", buildup, reset, close)
        )

        self.dialogModelEdit.recess().add(mainFrame)
        self.dialogModelEdit.setButtonVisibile('ok', False)
        self.dialogModelEdit.setButtonVisibile('cancel', False)

        width = columns * self.columnWidth
        height = widgetFrame.maxheight + 100

        return width, height

def mainFunc(*args, **kwargs):
    model_edit = ModelEdit()
    width, height = model_edit.modelEditGui()
    model_edit.dialogModelEdit.show(width=width, height=height)
    print("Initiated...")


if __name__ == "__main__":
    mainFunc()
