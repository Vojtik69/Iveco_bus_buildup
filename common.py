import os
import sys
# Get path to currently running script
currentDir = os.path.dirname(os.path.realpath(__file__))
# Add path to sys.path
sys.path.append(currentDir)
import logger
from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import yaml
import pandas as pd
import csv
import inspect
import os
import re
import traceback

logger.debug("loading common.py")

# load config file
with open(f'{currentDir}\config.yaml', 'r') as file:
    config = yaml.safe_load(file)
config['paths']['tcl'] = (currentDir + r'\tcl_functions.tcl').replace("\\", "/")
paths = config['paths']

def print_caller_info():
    stack_trace = traceback.extract_stack()
    caller_name = stack_trace[-3].name
    caller_file = os.path.basename(stack_trace[-3].filename)
    caller_line = stack_trace[-3].lineno
    logger.debug(f"Called by function {caller_name} from file: {caller_file}, on line: {caller_line}")

def alphanum_key(s):
    # Rozdělí řetězec na části, kde čísla jsou konvertována na int a zbytek zůstává jako string
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def sortAlphabetically(items):
    # print_caller_info()
    new_items = items
    if hasattr(new_items, '__iter__') and not isinstance(new_items, str):
        # Použije přirozené řazení s použitím alphanum_key jako klíčové funkce
        # logger.debug(f"list pred: {new_items}")
        if '---' in new_items:
            new_items.remove('---')
            # logger.debug(f"list po: {['---'] + sorted(new_items, key=alphanum_key)}")
            return ['---'] + sorted(new_items, key=alphanum_key)
        else:
            # logger.debug(f"list po: {['---'] + sorted(new_items, key=alphanum_key)}")
            return sorted(new_items, key=alphanum_key)

    else:
        return new_items

def findAllOfType(parts, selectedSolver, searchedType, removeEmpty=False):
    allOfType = ["---"]
    logger.debug(searchedType)
    if removeEmpty:
        allOfType = []
    for index, row in parts.iterrows():
        # logger.debug(index)
        if index[0] == searchedType:
            if selectedSolver:
                if not pd.isna(index[selectedSolver]):
                    allOfType.append(index[1])
            else:
                allOfType.append(index[1])

    return sortAlphabetically(allOfType)


def findPathToName(hierarchy, name, currentPath=[]):
    # logger.debug(f"name: {name}")
    # logger.debug(f"hierarchy: {hierarchy}")
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
    # logger.debug(f'path:{path}')

    if path is None:
        # logger.debug(f'superordinants:{superordinants}')
        return superordinants

    # if it first level under vehicle_spec, use vehicle_spec as superordinant
    if len(path)>3:
        if path[-4] == "FT groups":
            for vehicleSpec in getElementByPath(hierarchy, ["groups", "vehicle_spec"]):
                superordinants.append(vehicleSpec.get("name",""))
            # logger.debug(f'superordinants:{superordinants}')
            return superordinants

    levelUp = -4 if path[-2] == "FTs" else -2

    pathLevelUp = path[:levelUp]
    superordinantElement = getElementByPath(hierarchy, pathLevelUp)
    superordinantName = getElementByPath(hierarchy, pathLevelUp[:-2]).get("name", "")
    for ft in superordinantElement.get("FTs", []):
        superordinants.append(ft.get("name", ""))
    if superordinantElement.get("skippable", False):
        findSuperordinantFts(hierarchy, superordinantName, superordinants)


    # logger.debug(f'superordinants:{superordinants}')
    return superordinants


def findSubordinantFts(hierarchy, name, subordinants = None):
    subordinants = [] if subordinants is None else subordinants
    caller = inspect.stack()[1]
    caller_name = caller.function
    logger.debug(f"{caller_name} called my_function")
    logger.debug(f"name: {name} - subordinants: {subordinants}")
    path = findPathToName(hierarchy, name)
    logger.debug(f"name: {name} - path: {path}")
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
    logger.debug(f'allSpecTypes: {allSpecTypes}')
    return allSpecTypes


def updateSubordinantItems(hierarchy, parts, widgetyBuildup, selectedSolver, name):
    subordinants = findSubordinantFts(hierarchy, name)
    logger.debug(f"subordinants in update_subordinant_items: {subordinants}")
    for subordinant in subordinants:
        # if it is multiselection ListBox
        if isinstance(widgetyBuildup[f'vyber_{subordinant}'], gui2.ListBox):
            logger.debug(f"{subordinant} - multiselection ListBox")
            # save selected
            items = widgetyBuildup["vyber_" + subordinant].items
            selectedIndexes = widgetyBuildup["vyber_" + subordinant].selectedIndexes
            if selectedIndexes:
                selectedItems = [items[index] for index in selectedIndexes]
            else:
                selectedItems = []

            # load compatibles
            widgetyBuildup["vyber_" + subordinant].clear()
            widgetyBuildup["vyber_" + subordinant].append(
                findCompatibleParts(hierarchy, parts, widgetyBuildup, selectedSolver, subordinant, removeEmpty=True))

            # restore selected
            for index, item in enumerate(widgetyBuildup["vyber_" + subordinant].items):
                if item in selectedItems:
                    widgetyBuildup["vyber_" + subordinant].select(index)

        # if it is onlyselection Combo
        else:
            logger.debug(f"{subordinant} - onlyselection Combo")
            logger.debug(f"compatibleParts returned: {findCompatibleParts(hierarchy, parts, widgetyBuildup, selectedSolver, subordinant, removeEmpty=False)}")
            widgetyBuildup["vyber_" + subordinant].setValues(
                findCompatibleParts(hierarchy, parts, widgetyBuildup, selectedSolver, subordinant, removeEmpty=False))


def findPathToIncludeFile(partDb, selectedSolver, name):
    logger.debug(f"name: {name}")
    if name != "---":
        matching_parts = partDb[partDb.index.get_level_values(1) == name].index.get_level_values(
            selectedSolver).tolist()
        # logger.debug(f"matching_parts: {matching_parts}")
        # logger.debug(f"type: {type(matching_parts[0])}")
        if matching_parts and isinstance(matching_parts[0], str):
            path = matching_parts[0]
        else:
            path = ""
    else:
        path = ""
    # logger.debug(f"Path: {path}")
    return path.replace("\\","/")

def findTypeOfPart(partDb, name):
    # logger.debug(f"name: {name}")
    if name != "---":
        # Get the level values of the columns
        header_values = partDb.columns.get_level_values(2).tolist()
        # logger.debug(f"header_values: {header_values}")
        if name in header_values:
            # Get the index of the header value
            index_of_name = header_values.index(name)
            # Get the corresponding value from the 0th level of multi-header
            partType = partDb.columns.get_level_values(1)[index_of_name]
        else:
            partType = ""
    else:
        partType = ""
    # logger.debug(f"partType: {partType}")
    return partType

def findCompatibleParts(hierarchy, parts, widgetyBuildup, selectedSolver, name, removeEmpty=False):
    # print_caller_info()
    compatibles = [] if removeEmpty else ["---"]
    superordinantTypes = findSuperordinantFts(hierarchy, name, superordinants=[])
    allOfType = findAllOfType(parts, selectedSolver, name, removeEmpty=True)
    logger.debug("find compatibles")
    logger.debug(f"removeEmpty: {removeEmpty}")
    # logger.debug(f"selectedSolver: {selectedSolver}")
    for part in allOfType:
        compatible = True
        logger.debug(f"part: {part}")
        #if the part has not file for current solver, go next
        if pd.isna(parts[parts.index.get_level_values(1) == part].index.get_level_values(selectedSolver)):
            # logger.debug("not compatible")
            continue
        for superordinantType in superordinantTypes:
            # logger.debug(f"superordinant type: {superordinantType}")
            # logger.debug(f"widgetyBuildup[f'vyber_{superordinantType}'].get() = {widgetyBuildup[f'vyber_{superordinantType}'].get()}")
            if widgetyBuildup[f'vyber_{superordinantType}'].get() and widgetyBuildup[f'vyber_{superordinantType}'].get() != "---":
                # logger.debug(parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())].iat[0, 0])
                # logger.debug(parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())])
                # logger.debug(widgetyBuildup[f'vyber_{superordinantType}'].get())
                logger.debug(
                    f"value: parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())].iat[0, 0]")
                logger.debug(
                    f"widgetyBuildup[f'vyber_superordinantType'].get())]: {widgetyBuildup[f'vyber_{superordinantType}'].get()}")
                logger.debug(f"value: {parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())].iat[0, 0]}")
                value = parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinantType}'].get())].iat[0, 0]
                if pd.isna(value) or value == 0:
                    compatible = False
                    # logger.debug(f"compatible: {compatible}")
                    break
        if compatible:
            compatibles.append(part)
    sortedCompatibles = sortAlphabetically(compatibles)
    logger.debug(f"compatibles: {sortedCompatibles}")
    return sortedCompatibles



def onSelectedCombo(event, parts, hierarchyOfTypes, widgetyBuildup, selectedSolver):
    logger.debug(f"event.widget.value: {event.widget.value}")
    updateSubordinantItems(hierarchyOfTypes, parts, widgetyBuildup, selectedSolver, event.widget.name)
    return


def getValuesForVehicleSpec(parts, vehicleSpecType, removeEmpty=False):
    print_caller_info()
    logger.debug(f"vehicle_spec_type: {vehicleSpecType}")
    allValues = [] if removeEmpty else ["---"]
    logger.debug(f"all_values: {allValues}")
    vehicleSpecColumns = [idx for idx, col in enumerate(parts.columns) if col[1] == vehicleSpecType]
    allValues.extend([parts.columns[col][2] for col in vehicleSpecColumns])
    logger.debug(f"all_values: {allValues}")
    return sortAlphabetically(allValues)


def getWidgetStructure(structure, hierarchyOfTypes, parts, selectedSolver, widgetyBuildup, levelWidgets=None,
                       offset=0):
    if levelWidgets is None:
        levelWidgets = []

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
            logger.debug(f"FT název: {ft.get('name', '')}")
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
                                  vehicleSpecWidgets=None):
    if vehicleSpecWidgets is None:
        vehicleSpecWidgets = []

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


def loadSetup(event, widgetyBuildup, selectedSolver, parts):
    def loadFile():
        resetModelEdit(None, widgetyBuildup, selectedSolver, parts)
        with open(fileEnt1.value, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        for label, widget in widgetyBuildup.items():
            if label in data:
                if isinstance(widget, gui2.ListBox):
                    items = widget.items
                    selectedItems = data.get(label,[])
                    for index, item in enumerate(widget.items):
                        if item in selectedItems:
                            logger.debug(f"selected items: {selectedItems}")
                            logger.debug(f"index: {index}, {item}")
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
def resetModelEdit(event, ModelEdit, selectedSolver, parts):
    for label, widget in ModelEdit.items():
        # logger.debug(label)
        # logger.debug(widget)
        typ = label.replace("vyber_", "")

        # if it is multiselection ListBox
        if isinstance(widget, gui2.ListBox):
            widget.clear()
            widget.append(findAllOfType(parts, selectedSolver, typ, removeEmpty=True))
        # if it is onlyselection Combo
        elif isinstance(widget, gui2.ComboBox):
            values = findAllOfType(parts, selectedSolver, typ, removeEmpty=False)
            logger.debug(f"values: {values}")
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
    logger.debug(names)
    return sortAlphabetically(names)


def findAllParts(parts):
    allParts = []
    for index, row in parts.iterrows():
        logger.debug(index[1])
        allParts.append(index[1])  # přidá obsah druhého sloupce indexu
    return allParts


def findCompatibility(df, name2ndColumn, name3rdRow):
    # logger.debug(f"name2ndColumn, name3rdRow: {name2ndColumn}, {name3rdRow}")
    # Vyhledání řádku na základě názvu ve druhém sloupci (2. úroveň multiindexu)
    idx = df.index.get_level_values(1) == name2ndColumn
    row = df[idx]

    # Vyhledání hodnoty z daného sloupce třetího řádku (součást víceúrovňového záhlaví)
    try:
        # logger.debug(f"row.xs(name3rdRow, level=2, axis=1):  {row.xs(name3rdRow, level=2, axis=1)}")
        if not row.xs(name3rdRow, level=2, axis=1).empty:
            value = row.xs(name3rdRow, level=2, axis=1).iloc[0,0]
            if pd.isna(value):
                value = 0  # Nahrazení NaN hodnotou 0
        else:
            value = 0
    except KeyError:
        value = 0  # Pokud neexistuje daný sloupec, vrátí None
    try:
        value = int(value)
    except:
        logger.debug(f"not possible to make it integer: {value}")
    # logger.debug(f"returning value: {value}")
    return value

def setCompatibility(parts, name2ndColumn, name3rdRow, newValue):
    logger.debug(f"parts: {name2ndColumn} - {name3rdRow}, value: {newValue}")
    try:
        logger.debug(parts)
        parts.loc[(slice(None), name2ndColumn), (slice(None), slice(None), name3rdRow)] = newValue
    except KeyError:
        logger.debug(f"Not found")
    return parts

# Definice funkce pro konverzi na int nebo str
def convertToIntOrStr(x):
    if x.isdigit():
        # logger.debug(f"{x} is digit")
        try:
            return int(x)
        except ValueError:
            return str(x)
    # logger.debug(f"{x} NOT digit")
    return str(x)

def restoreHeaderInCSV(csvFile):
    # Open the CSV file in read mode
    with open(csvFile, 'r', newline='') as file:
        reader = csv.reader(file)
        lines = list(reader)

    # Modify the values in the first four cells of the third line
    if len(lines) >= 3:  # Check if the file has at least 3 lines
        lines[2][:4] = ["type","name","optistruct","radioss"]

    # Write the modified lines back to the CSV file
    with open(csvFile, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)

def importParts(csvPath=paths["csv"]):
    parts = pd.read_csv(csvPath, index_col=[0, 1, 2, 3],
                        header=[0, 1, 2], skipinitialspace=True, converters={i: convertToIntOrStr for i in range(len(pd.read_csv(csvPath).columns))})
    parts.columns.names = [None] * len(parts.columns.names)
    return parts

def getSelectedSolver():
    userProfile = hw.evalTcl(f"hm_framework getuserprofile")
    logger.debug(userProfile)
    # 2-optistruct 3-radioss - it corresponds to column in csv, where first is index, second is type but it s columnt No. 0, then is OptiStruct as No.1,...
    if userProfile == "OptiStruct {}":
        selectedSolver = 2
    else:
        selectedSolver = 3
    return selectedSolver


def findLevel(data, targetName, currentLevel=1):
    # logger.debug(f"data: {data} , type: {type(data)}")
    # logger.debug(f"targetName: {targetName}")
    if isinstance(data, list):
        for item in data:
            result = findLevel(item, targetName, currentLevel)
            if result is not None:
                return result
    elif isinstance(data, dict):
        if 'name' in data and data['name'] == targetName:
            return currentLevel
        for key, value in data.items():
            result = findLevel(value, targetName, currentLevel + 1)
            if result is not None:
                return result
    return None

def moveIncludes(parts):
    listOfIncludesIds = hw.evalTcl("hm_getincludes").split()

    pattern = r'\{.*?\}|\S+'
    matches = re.findall(pattern, hw.evalTcl("hm_getincludes -byshortname"))
    listOfIncludesLablesOriginal = [match.strip('{}') for match in matches]

    # remove ends of names in cases the include is moved and the name is ended by suffix _move_x_y_z
    listOfIncludesLables = []
    moved_data = []

    for item in listOfIncludesLablesOriginal:
        if '_moved' in item:
            base_label, moved_part = item.split('_moved', 1)
            coords = moved_part.split('_')[1:]  # Extract x, y, z
            x, y, z = map(int, coords)
            listOfIncludesLables.append(base_label)
            moved_data.append((x, y, z))
        else:
            listOfIncludesLables.append(item)
            moved_data.append((0, 0, 0))  # No move data

    listofIncludesWithHierarchy = []

    logger.debug(f'listOfIncludesLables: {listOfIncludesLables}')

    for i, label in enumerate(listOfIncludesLables):
        hierarchy = findLevel(hierarchyOfTypes, findTypeOfPart(parts, label))
        id = listOfIncludesIds[i]
        labelOriginal = listOfIncludesLablesOriginal[i]
        x, y, z = moved_data[i]
        listofIncludesWithHierarchy.append((id, label, labelOriginal, hierarchy, x, y, z))

    logger.debug(f'listofIncludesWithHierarchy: {listofIncludesWithHierarchy}')

    sortedListofIncludesWithHierarchy = sorted(listofIncludesWithHierarchy, key=lambda x: x[3], reverse=True)

    for i, (id, label, labelOriginal, hierarchy, x_orig, y_orig, z_orig) in enumerate(sortedListofIncludesWithHierarchy):
        logger.debug(f"Going to move {label}?")
        moving_finished = False
        for id2, label2, labelOriginal2, hierarchy2, _, _, _ in sortedListofIncludesWithHierarchy:
            compatibilityValue = findCompatibility(parts, label, label2)
            # logger.debug(f"compatibilita: {label} + {label2}: {compatibilityValue}")
            if not isinstance(compatibilityValue, int):
                if '[' in compatibilityValue and ']' in compatibilityValue:
                    logger.debug(f"going to move: {label} - {label2}: {compatibilityValue}")
                    numbers = re.findall(r'-?\d+', compatibilityValue)
                    x, y, z = map(int, numbers)
                    logger.debug(f"_moved x, y, z: {x_orig}, {y_orig}, {z_orig}")
                    logger.debug(f"compatibility x, y, z: {x}, {y}, {z}")
                    new_label = label + "_moved_" + str(x) + "_" + str(y) + "_" + str(z)
                    x = x - x_orig
                    y = y - y_orig
                    z = z - z_orig
                    logger.debug(f"x, y, z: {x}, {y}, {z}")
                    moving_finished = True
                    if x or y or z:
                        logger.debug("moving")
                        logger.debug(
                            f'source "{paths["tcl"]}"; move_include "{new_label}" {id} {x} {y} {z}')
                        hw.evalTcl(
                            f'source "{paths["tcl"]}"; move_include "{new_label}" {id} {x} {y} {z}')
                        break
                else:
                    logger.debug("compatibility value is not int and does not contain both brackets [ and ]")
        if not moving_finished:
            logger.debug(f"{label}: not found moving coordinates - moving back to initial position")
            logger.debug(
                f'source "{paths["tcl"]}"; move_include "{label}" {id} {-x_orig} {-y_orig} {-z_orig}')
            hw.evalTcl(
                f'source "{paths["tcl"]}"; move_include "{label}" {id} {-x_orig} {-y_orig} {-z_orig}')
        else:
            logger.debug(f"{label}: doing nothing")



solverInterface = ['"OptiStruct" {}', '"RadiossBlock" "Radioss2023"']

with open(paths["hierarchy"], 'r') as file:
    hierarchyOfTypes = yaml.safe_load(file)
