import os

from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import yaml
import pandas as pd
import inspect
import os
import re
import traceback

print("loading common.py")

def print_caller_info():
    stack_trace = traceback.extract_stack()
    caller_name = stack_trace[-3].name
    caller_file = os.path.basename(stack_trace[-3].filename)
    caller_line = stack_trace[-3].lineno
    print(f"SortAlphabetically byla volána funkcí {caller_name} ze souboru: {caller_file}, na řádku: {caller_line}")

def alphanum_key(s):
    # Rozdělí řetězec na části, kde čísla jsou konvertována na int a zbytek zůstává jako string
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def sortAlphabetically(items):
    print_caller_info()
    new_items = items
    if hasattr(new_items, '__iter__') and not isinstance(new_items, str):
        # Použije přirozené řazení s použitím alphanum_key jako klíčové funkce
        print(f"list pred: {new_items}")
        if '---' in new_items:
            new_items.remove('---')
            print(f"list po: {['---'] + sorted(new_items, key=alphanum_key)}")
            return ['---'] + sorted(new_items, key=alphanum_key)
        else:
            print(f"list po: {['---'] + sorted(new_items, key=alphanum_key)}")
            return sorted(new_items, key=alphanum_key)

    else:
        return new_items

def findAllOfType(parts, selectedSolver, searchedType, removeEmpty=False):
    allOfType = ["---"]
    # print(searchedType)
    if removeEmpty:
        allOfType = []
    for index, row in parts.iterrows():
        # print(index)
        if index[0] == searchedType:
            if selectedSolver:
                if not pd.isna(index[selectedSolver]):
                    allOfType.append(index[1])
            else:
                allOfType.append(index[1])

    return sortAlphabetically(allOfType)


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

def getVehicleSpecTypes(hierarchy):
    allSpecTypes = []
    for specType in hierarchy["groups"]["vehicle_spec"]:
        allSpecTypes.append(specType["name"])
    print(f'allSpecTypes: {allSpecTypes}')
    return allSpecTypes


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
    print_caller_info()
    compatibles = [] if removeEmpty else ["---"]
    superordinantTypes = findSuperordinantFts(hierarchy, name, superordinants=[])
    allOfType = findAllOfType(parts, selectedSolver, name, removeEmpty=True)
    print("find compatibles")
    # print(f"selectedSolver: {selectedSolver}")
    for part in allOfType:
        compatible = True
        #if the part has not file for current solver, go next

        if pd.isna(parts[parts.index.get_level_values(1) == part].index.get_level_values(selectedSolver)):
            print("not compatible")
            continue
        print(f"part: {part}")
        for superordinantType in superordinantTypes:
            # print(f"superordinant type: {superordinantType}")
            if widgetyBuildup[f'vyber_{superordinantType}'].get() != "---":
                # print(parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())].iat[0, 0])
                # print(parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())])
                # print(widgetyBuildup[f'vyber_{superordinantType}'].get())
                if pd.isna(parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())].iat[0, 0]):
                    compatible = False
                    # print(f"compatible: {compatible}")
                    break
        if compatible:
            compatibles.append(part)
    # print(f"compatibles: {sortAlphabetically(compatibles)}")
    return sortAlphabetically(compatibles)


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
    return sortAlphabetically(allValues)


def getWidgetStructure(structure, hierarchyOfTypes, parts, selectedSolver, widgetyBuildup, levelWidgets=[],
                       offset=0):
    subgrouping = True if levelWidgets else False
    # every iteration here is new column
    for index, level in enumerate(structure):
        labelGroup = gui.Label(text=level.get("name"), font={'bold': True})
        # are we in main level or any of sublevels?
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

            # add new line with label and choose
            levelWidgets[-1].append(
                (offset*10, widgetyBuildup[f'label_{ft.get("name", "")}'], 5, widgetyBuildup[f'vyber_{ft.get("name", "")}']))
        if level.get("groups"):
            getWidgetStructure(level['groups'], hierarchyOfTypes, parts, selectedSolver, widgetyBuildup,
                               levelWidgets, offset=offset + 1)

        levelWidgets[-1].append("<->")

    return levelWidgets, index


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

def extractAllTypes(hierarchy, onlyNames=False):
    names = [] if onlyNames else ["---"]

    def extract_names(groups):
        for group in groups:
            if 'FTs' in group:
                for ft in group['FTs']:
                    names.append(ft['name'])
            if 'groups' in group:
                extract_names(group['groups'])

    extract_names(hierarchy['groups']['FT groups'])
    print(names)
    return sortAlphabetically(names)


def findAllParts(parts):
    allParts = []
    for index, row in parts.iterrows():
        print(index[1])
        allParts.append(index[1])  # přidá obsah druhého sloupce indexu
    return allParts


def findCompatibility(df, name2ndColumn, name3rdRow):
    # Vyhledání řádku na základě názvu ve druhém sloupci (2. úroveň multiindexu)
    idx = df.index.get_level_values(1) == name2ndColumn
    row = df[idx]

    # Vyhledání hodnoty z daného sloupce třetího řádku (součást víceúrovňového záhlaví)
    try:
        value = row.xs(name3rdRow, level=2, axis=1).iloc[0,0]
        if pd.isna(value):
            value = 0  # Nahrazení NaN hodnotou 0
    except KeyError:
        value = 0  # Pokud neexistuje daný sloupec, vrátí None
    try:
        value = int(value)
    except:
        print(f"not possible to make it integer: {value}")
    # print(value)
    return value


parts = pd.read_csv('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv', index_col=[0, 1, 2, 3],
                    header=[0, 1, 2], skipinitialspace=True)
parts.columns.names = [None] * len(parts.columns.names)

with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
    hierarchyOfTypes = yaml.safe_load(file)
tclPath = "N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/tcl_functions.tcl"



