from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import yaml
import pandas as pd
import inspect

print("loading common.py")

def findAllOfType(parts, selectedSolver, searchedType, removeEmpty=False):
    # TODO: .sort()
    allOfType = ["---"]
    # print(searchedType)
    if removeEmpty:
        allOfType = []
    for index, row in parts.iterrows():
        # print(index)
        if index[0] == searchedType and not pd.isna(index[selectedSolver]):
            allOfType.append(index[1])
    return allOfType


def findPathToName(hierarchy, name, currentPath=[]):
    # print(f"name: {name}")
    # print(f"hierarchy: {hierarchy}")
    if isinstance(hierarchy, list):
        for index, item in enumerate(hierarchy):
            newPath = currentPath + [index]
            result = findPathToName(item, name, newPath)
            if result is not None:
                return result
    elif isinstance(hierarchy, dict):
        for key, value in hierarchy.items():
            newPath = currentPath + [key]
            if key == "name" and value == name:
                return newPath[:-1]
            result = findPathToName(value, name, newPath)
            if result is not None:
                return result
    return None


# not used
# def load_include_file(parts, part):
#     hw.evalTcl(f'puts "Importing {part}..."')
#     include_file_path = find_path_to_include_file(parts, part).replace("\\","/")
#     return include_file_path


def getElementByPath(hierarchy, path):
    element = hierarchy
    try:
        for keyOrIndex in path:
            element = element[keyOrIndex]
        return element
    except (KeyError, IndexError):
        return None


def findSuperordinantFts(hierarchy, name, superordinants = []):
    path = findPathToName(hierarchy, name)
    # print(f'path:{path}')

    if path is None:
        # print(f'superordinants:{superordinants}')
        return superordinants

    # if it first level under vehicle_spec, use vehicle_spec as superordinant
    if len(path)>3:
        if path[-4] == "FT groups":
            for vehicleSpec in getElementByPath(hierarchy, ["groups", "vehicle_spec"]):
                superordinants.append(vehicleSpec.get("name",""))
            # print(f'superordinants:{superordinants}')
            return superordinants

    levelUp = -4 if path[-2] == "FTs" else -2

    pathLevelUp = path[:levelUp]
    superordinantElement = getElementByPath(hierarchy, pathLevelUp)
    superordinantName = getElementByPath(hierarchy, pathLevelUp[:-2]).get("name", "")
    for ft in superordinantElement.get("FTs", []):
        superordinants.append(ft.get("name", ""))
    if superordinantElement.get("skippable", False):
        findSuperordinantFts(hierarchy, superordinantName, superordinants)


    # print(f'superordinants:{superordinants}')
    return superordinants


def findSubordinantFts(hierarchy, name, subordinants = None):
    subordinants = [] if subordinants is None else subordinants
    caller = inspect.stack()[1]
    caller_name = caller.function
    print(f"{caller_name} called my_function")
    print(f"name: {name} - subordinants: {subordinants}")
    path = findPathToName(hierarchy, name)
    print(f"name: {name} - path: {path}")
    if path is None:
        return subordinants

    if path[-2] == "FTs":
        levelUp = -2
        superordinantElement = getElementByPath(hierarchy, path[:levelUp])
        groupsForSearching = superordinantElement.get("groups", [])
    elif path[-2] == "vehicle_spec":
        groupsForSearching = hierarchy["groups"]["FT groups"]
    elif path[-2] == "groups":
        levelUp = -4
        superordinantElement = getElementByPath(hierarchy, path[:levelUp])
        groupsForSearching = superordinantElement.get("groups", [])
    elif path[-2] == "FT groups":
        levelUp = 0
        superordinantElement = getElementByPath(hierarchy, path)
        groupsForSearching = superordinantElement.get("groups", [])


    for group in groupsForSearching:
        for ft in group.get("FTs", []):
            subordinants.append(ft.get("name",""))

        if group.get("skippable", False):
            findSubordinantFts(hierarchy, group.get("name", ""), subordinants)

    return subordinants


def updateSubordinantItems(hierarchy, parts, widgetyBuildup, selectedSolver, name):
    subordinants = findSubordinantFts(hierarchy, name)
    print(f"subordinants in update_subordinant_items: {subordinants}")
    for subordinant in subordinants:
        # if it is multiselection ListBox
        if isinstance(widgetyBuildup[f'vyber_{subordinant}'], gui2.ListBox):
            widgetyBuildup["vyber_" + subordinant].clear()
            widgetyBuildup["vyber_" + subordinant].append(
                findCompatibleParts(hierarchy, parts, widgetyBuildup, selectedSolver, subordinant, removeEmpty=True))
        # if it is onlyselection Combo
        else:
            pass
            widgetyBuildup["vyber_" + subordinant].setValues(
                findCompatibleParts(hierarchy, parts, widgetyBuildup, selectedSolver, subordinant, removeEmpty=False))


def findPathToIncludeFile(partDb, selectedSolver, name):
    print(f"name: {name}")
    if name != "---":
        path = partDb[partDb.index.get_level_values(1) == name].index.get_level_values(selectedSolver).tolist()[0]
    else:
        path = ""
    return path.replace("\\","/")


def findCompatibleParts(hierarchy, parts, widgetyBuildup, selectedSolver, name, removeEmpty=False):
    compatibles = [] if removeEmpty else ["---"]
    superordinant_types = findSuperordinantFts(hierarchy, name, superordinants=[])
    allOfType = findAllOfType(parts, selectedSolver, name, removeEmpty=True)
    # print("find compatibles")
    print(selectedSolver)
    for part in allOfType:
        compatible = True
        #if the part has not file for current solver, go next

        if pd.isna(parts[parts.index.get_level_values(1) == part].index.get_level_values(selectedSolver)):
            print("not compatible")
            continue
        # print(f"part: {part}")
        for superordinantType in superordinant_types:
            # print(f"superordinant type: {superordinant_type}")
            if widgetyBuildup[f'vyber_{superordinantType}'].get() != "---":
                if pd.isna(parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())].iat[0, 0]):
                    compatible = False
                    break
        if compatible:
            compatibles.append(part)
    return compatibles


def onSelectedCombo(event, parts, hierarchyOfTypes, widgetyBuildup, selectedSolver):
    print(f"event.widget.value: {event.widget.value}")
    updateSubordinantItems(hierarchyOfTypes, parts, widgetyBuildup, selectedSolver, event.widget.name)
    return


def getValuesForVehicleSpec(parts, vehicleSpecType, removeEmpty=False):
    print(f"vehicle_spec_type: {vehicleSpecType}")
    allValues = [] if removeEmpty else ["---"]
    print(f"all_values: {allValues}")
    vehicleSpecColumns = [idx for idx, col in enumerate(parts.columns) if col[1] == vehicleSpecType]
    allValues.extend([parts.columns[col][2] for col in vehicleSpecColumns])
    print(f"all_values: {allValues}")
    return allValues


def getWidgetStructure(structure, hierarchyOfTypes, parts, selectedSolver, widgetyBuildup, levelWidgets=[],
                       offset=0):
    subgrouping = True if levelWidgets else False
    for index, level in enumerate(structure):
        labelGroup = gui.Label(text=level.get("name"), font={'bold': True})
        if subgrouping:
            levelWidgets[-1].append([(10, (offset*10, labelGroup))])
        else:
            levelWidgets.append([(labelGroup)])
        for ft in level.get("FTs", []):
            labelObjekt = gui.Label(text=ft.get("name", ""))

            if ft.get("multiselection", False):
                vyberObjekt = gui2.ListBox(selectionMode="ExtendedSelection", name=ft.get('name', ""), width=150-(offset*5))
                vyberObjekt.append(findAllOfType(parts, selectedSolver, ft.get('name', ""), removeEmpty=True))
            else:
                vyberObjekt = gui2.ComboBox(
                    findAllOfType(parts, selectedSolver, ft.get('name', ""), removeEmpty=False), command=lambda event: onSelectedCombo(
                event, parts, hierarchyOfTypes, widgetyBuildup, selectedSolver), name=ft.get('name', ""), width=150 - (offset * 5))

            widgetyBuildup[f'label_{ft.get("name", "")}'] = labelObjekt
            widgetyBuildup[f'vyber_{ft.get("name", "")}'] = vyberObjekt

            levelWidgets[-1].append(
                (offset*10, widgetyBuildup[f'label_{ft.get("name", "")}'], 5, widgetyBuildup[f'vyber_{ft.get("name", "")}']))
        if level.get("groups"):
            getWidgetStructure(level['groups'], hierarchyOfTypes, parts, selectedSolver, widgetyBuildup,
                               levelWidgets, offset=offset + 1)

    return levelWidgets


def getWidgetVehicleSpecStructure(structure, hierarchyOfTypes, parts, widgetyBuildup, selectedSolver,
                                  vehicleSpecWidgets=[]):
    for vehicleSpec in structure:
        labelObjekt = gui.Label(text=vehicleSpec.get("name", ""), font={'bold': True})

        if vehicleSpec.get("multiselection", False):
            vyberObjekt = gui2.ListBox(selectionMode="ExtendedSelection", name=vehicleSpec.get('name', ""), width=150)
        else:
            vyberObjekt = gui2.ComboBox(
                getValuesForVehicleSpec(parts, vehicleSpec.get('name', ""), removeEmpty=False), command=lambda event: onSelectedCombo(
                event, parts, hierarchyOfTypes, widgetyBuildup, selectedSolver), name=vehicleSpec.get('name', ""), width=150)

        widgetyBuildup[f'label_{vehicleSpec.get("name", "")}'] = labelObjekt
        widgetyBuildup[f'vyber_{vehicleSpec.get("name", "")}'] = vyberObjekt

        vehicleSpecWidgets.append([[(widgetyBuildup[f'label_{vehicleSpec.get("name", "")}'], widgetyBuildup[f'vyber_{vehicleSpec.get("name", "")}'])]])

    return vehicleSpecWidgets


def saveSetup(event, widgetyBuildup):
    def saveFile(event, widgetyBuildup):
        data = {}
        for label, widget in widgetyBuildup.items():
            if isinstance(widget, gui2.ListBox):
                items = widget.items
                selectedIndexes = widget.selectedIndexes
                if selectedIndexes:
                    selectedItems = [items[index] for index in selectedIndexes]
                else:
                    selectedItems = []
                data[label] = selectedItems
            elif isinstance(widget, gui2.ComboBox):
                selectedValue = widget.value
                data[label] = selectedValue

        with open(fileEnt1.value, 'w') as file:
            yaml.dump(data, file)
        dialogSaveSetup.hide()
        gui2.tellUser("Vehicle setup saved.")

    label1 = gui.Label(text="Select File :")
    fileEnt1 = gui.SaveFileEntry(placeholdertext='Setup file to save', filetypes='(*.yaml)')

    saveSetupFrame = gui.VFrame(label1, fileEnt1)

    dialogSaveSetup = gui.Dialog(caption="Select setup file to save")
    dialogSaveSetup.recess().add(saveSetupFrame)
    dialogSaveSetup._controls["ok"].command = lambda event: saveFile(event, widgetyBuildup)
    dialogSaveSetup.show(height = 100)


def loadSetup(event, widgetyBuildup, selectedSolver):
    def loadFile():
        resetModelBuildup(None, widgetyBuildup, selectedSolver, parts)
        with open(fileEnt1.value, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        for label, widget in widgetyBuildup.items():
            if label in data:
                if isinstance(widget, gui2.ListBox):
                    items = widget.items
                    selectedItems = data.get(label,[])
                    for index, item in enumerate(widget.items):
                        if item in selectedItems:
                            print(f"selected items: {selectedItems}")
                            print(f"index: {index}, {item}")
                            widget.select(index)

                elif isinstance(widget, gui2.ComboBox):
                    selected_value = data.get(label,"---")
                    widget.value = selected_value
        dialogLoadSetup.hide()

    label1 = gui.Label(text="Select File :")
    fileEnt1 = gui.OpenFileEntry(placeholdertext='Setup file to open', filetypes='(*.yaml)')

    loadSetupFrame = gui.VFrame(label1, fileEnt1)

    dialogLoadSetup = gui.Dialog(caption="Select setup file to open")
    dialogLoadSetup.recess().add(loadSetupFrame)
    dialogLoadSetup._controls["ok"].command = loadFile
    dialogLoadSetup.show(height = 100)


# Method called on clicking 'Reset'.
def resetModelBuildup(event, widgetyBuildup, selectedSolver, parts):
    for label, widget in widgetyBuildup.items():
        # print(label)
        # print(widget)
        typ = label.replace("vyber_", "")

        # if it is multiselection ListBox
        if isinstance(widget, gui2.ListBox):
            widget.clear()
            widget.append(findAllOfType(parts, selectedSolver, typ, removeEmpty=True))
        # if it is onlyselection Combo
        elif isinstance(widget, gui2.ComboBox):
            values = findAllOfType(parts, selectedSolver, typ, removeEmpty=False)
            print(f"values: {values}")
            if len(values) == 1:
                values = getValuesForVehicleSpec(parts, typ, removeEmpty=False)
            widget.setValues(values)
            widget.value = "---"
    return


parts = pd.read_csv('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv', index_col=[0, 1, 2, 3],
                    header=[0, 1, 2], skipinitialspace=True)
parts.columns.names = [None] * len(parts.columns.names)

with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
    hierarchyOfTypes = yaml.safe_load(file)
tclPath = "N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/tcl_functions.tcl"



