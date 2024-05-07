from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import os
import itertools
from functools import partial
import yaml
import os.path
import pandas as pd
import inspect
import os
import sys

print("Initiating...")

parts = pd.read_csv('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv', index_col=[0, 1, 2, 3],
                    header=[0, 1, 2], skipinitialspace=True)
parts.columns.names = [None] * len(parts.columns.names)

with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
    hierarchy_of_types = yaml.safe_load(file)

tcl_path = "N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/tcl_functions.tcl"

# Slovník pro uchování vytvořených widgetů
widgetyBuildup = {}
widgetyAddPart = {}
widgetyEditPart = {}
dialogSetCompatibility = gui.Dialog(caption="Set compatibility")
dialogModelBuildup = gui.Dialog(caption="Bus model build-up")
dialogAddPart = gui.Dialog(caption="Add Part")
dialogEditPart = gui.Dialog(caption="Edit Part")


selectedSolver = 2 #2-optistruct, 3-radioss - it corresponds to column in csv, where first is index, second is type but it s columnt No. 0, then is OptiStruct as No.1,...


def mainFunc(*args, **kwargs):
    ModelBuildupGUI()
    print("Initiated...")


def find_all_of_type(searched_type, remove_empty=False):

    all_of_type = ["---"]
    # print(searched_type)
    if remove_empty:
        all_of_type = []
    for index, row in parts.iterrows():
        # print(index)
        if index[0] == searched_type and not pd.isna(index[selectedSolver]):
            all_of_type.append(index[1])
    return all_of_type


def find_path_to_name(hierarchy, name, current_path=[]):
    # print(f"name: {name}")
    # print(f"hierarchy: {hierarchy}")
    if isinstance(hierarchy, list):
        for index, item in enumerate(hierarchy):
            new_path = current_path + [index]
            result = find_path_to_name(item, name, new_path)
            if result is not None:
                return result
    elif isinstance(hierarchy, dict):
        for key, value in hierarchy.items():
            new_path = current_path + [key]
            if key == "name" and value == name:
                return new_path[:-1]
            result = find_path_to_name(value, name, new_path)
            if result is not None:
                return result
    return None


def load_include_file(part):
    hw.evalTcl(f'puts "Importing {part}..."')
    include_file_path = find_path_to_include_file(parts, part).replace("\\","/")
    return include_file_path


def get_element_by_path(hierarchy, path):
    element = hierarchy
    try:
        for key_or_index in path:
            element = element[key_or_index]
        return element
    except (KeyError, IndexError):
        return None


def find_superordinant_fts(hierarchy, name, superordinants = []):
    path = find_path_to_name(hierarchy, name)
    # print(f'path:{path}')

    if path is None:
        # print(f'superordinants:{superordinants}')
        return superordinants

    # if it first level under vehicle_spec, use vehicle_spec as superordinant
    if len(path)>3:
        if path[-4] == "FT groups":
            for vehicle_spec in get_element_by_path(hierarchy, ["groups", "vehicle_spec"]):
                superordinants.append(vehicle_spec.get("name",""))
            # print(f'superordinants:{superordinants}')
            return superordinants

    level_up = -4 if path[-2] == "FTs" else -2

    path_level_up = path[:level_up]
    superordinant_element = get_element_by_path(hierarchy, path_level_up)
    superordinant_name = get_element_by_path(hierarchy, path_level_up[:-2]).get("name", "")
    for ft in superordinant_element.get("FTs", []):
        superordinants.append(ft.get("name", ""))
    if superordinant_element.get("skippable", False):
        find_superordinant_fts(hierarchy, superordinant_name, superordinants)


    # print(f'superordinants:{superordinants}')
    return superordinants


def find_subordinant_fts(hierarchy, name, subordinants = None):
    subordinants = [] if subordinants is None else subordinants
    caller = inspect.stack()[1]
    caller_name = caller.function
    print(f"{caller_name} called my_function")
    print(f"name: {name} - subordinants: {subordinants}")
    path = find_path_to_name(hierarchy, name)
    print(f"name: {name} - path: {path}")
    if path is None:
        return subordinants

    if path[-2] == "FTs":
        level_up = -2
        superordinant_element = get_element_by_path(hierarchy, path[:level_up])
        groups_for_searching = superordinant_element.get("groups", [])
    elif path[-2] == "vehicle_spec":
        groups_for_searching = hierarchy["groups"]["FT groups"]
    elif path[-2] == "groups":
        level_up = -4
        superordinant_element = get_element_by_path(hierarchy, path[:level_up])
        groups_for_searching = superordinant_element.get("groups", [])
    elif path[-2] == "FT groups":
        level_up = 0
        superordinant_element = get_element_by_path(hierarchy, path)
        groups_for_searching = superordinant_element.get("groups", [])


    for group in groups_for_searching:
        for ft in group.get("FTs", []):
            subordinants.append(ft.get("name",""))

        if group.get("skippable", False):
            find_subordinant_fts(hierarchy, group.get("name", ""), subordinants)

    return subordinants


def update_subordinant_items(hierarchy, name):
    subordinants = find_subordinant_fts(hierarchy, name)
    print(f"subordinants in update_subordinant_items: {subordinants}")
    for subordinant in subordinants:
        # if it is multiselection ListBox
        # if type(widgetyBuildup[f'vyber_{subordinant}']) == gui2.ListBox:
        if isinstance(widgetyBuildup[f'vyber_{subordinant}'], gui2.ListBox):
            widgetyBuildup["vyber_" + subordinant].clear()
            widgetyBuildup["vyber_" + subordinant].append(find_compatible_parts(hierarchy, subordinant, removeEmpty=True))
        # if it is onlyselection Combo
        else:
            pass
            widgetyBuildup["vyber_" + subordinant].setValues(find_compatible_parts(hierarchy, subordinant, removeEmpty=False))


def onSelectedCombo(event):
    print(f"event.widget.value: {event.widget.value}")
    update_subordinant_items(hierarchy_of_types, event.widget.name)
    return

def find_path_to_include_file(part_db, name):
    print(f"name: {name}")
    if name != "---":
        path = part_db[part_db.index.get_level_values(1) == name].index.get_level_values(selectedSolver).tolist()[0]
    else:
        path = ""
    return path.replace("\\","/")


def get_widget_structure(structure, levelWidgets=[], offset=0):
    subgrouping = True if levelWidgets else False
    for index, level in enumerate(structure):
        label_group = gui.Label(text=level.get("name"), font={'bold': True})
        if subgrouping:
            levelWidgets[-1].append([(10, (offset*10, label_group))])
        else:
            levelWidgets.append([(label_group)])
        for ft in level.get("FTs", []):
            label_objekt = gui.Label(text=ft.get("name", ""))

            if ft.get("multiselection", False):
                vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=ft.get('name', ""))
                vyber_objekt.append(find_all_of_type(ft.get('name',""),remove_empty=True))
            else:
                vyber_objekt = gui2.ComboBox(find_all_of_type(ft.get('name',""),remove_empty=False), command=onSelectedCombo, name=ft.get('name',""))

            widgetyBuildup[f'label_{ft.get("name", "")}'] = label_objekt
            widgetyBuildup[f'vyber_{ft.get("name", "")}'] = vyber_objekt

            levelWidgets[-1].append(
                (offset*10, widgetyBuildup[f'label_{ft.get("name", "")}'], 5, widgetyBuildup[f'vyber_{ft.get("name", "")}']))
        if level.get("groups"):
            get_widget_structure(level['groups'], levelWidgets, offset=offset+1)

    return levelWidgets

def get_widget_vehicle_spec_structure(structure, vehicle_spec_Widgets=[]):
    for vehicle_spec in structure:
        label_objekt = gui.Label(text=vehicle_spec.get("name", ""), font={'bold': True})

        if vehicle_spec.get("multiselection", False):
            vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=vehicle_spec.get('name', ""))
        else:
            vyber_objekt = gui2.ComboBox(get_values_for_vehicle_spec(vehicle_spec.get('name', ""), remove_empty=False), command=onSelectedCombo, name=vehicle_spec.get('name',""))

        widgetyBuildup[f'label_{vehicle_spec.get("name", "")}'] = label_objekt
        widgetyBuildup[f'vyber_{vehicle_spec.get("name", "")}'] = vyber_objekt

        vehicle_spec_Widgets.append([[(widgetyBuildup[f'label_{vehicle_spec.get("name", "")}'],widgetyBuildup[f'vyber_{vehicle_spec.get("name", "")}'])]])

    return vehicle_spec_Widgets


def find_compatible_parts(hierarchy, name, removeEmpty = False):
    global selectedSolver
    compatibles = [] if removeEmpty else ["---"]
    superordinant_types = find_superordinant_fts(hierarchy, name, superordinants=[])
    all_of_type = find_all_of_type(name, remove_empty=True)
    # print("find compatibles")
    print(selectedSolver)
    for part in all_of_type:
        compatible = True
        #if the part has not file for current solver, go next

        if pd.isna(parts[parts.index.get_level_values(1) == part].index.get_level_values(selectedSolver)):
            print("not compatible")
            continue
        # print(f"part: {part}")
        for superordinant_type in superordinant_types:
            # print(f"superordinant type: {superordinant_type}")
            if widgetyBuildup[f'vyber_{superordinant_type}'].get() != "---":
                if pd.isna(parts.loc[(slice(None), part), (slice(None), slice(None), widgetyBuildup[f'vyber_{superordinant_type}'].get())].iat[0, 0]):
                    compatible = False
                    break
        if compatible:
            compatibles.append(part)
    return compatibles


def get_values_for_vehicle_spec(vehicle_spec_type, remove_empty=False):
    print(f"vehicle_spec_type: {vehicle_spec_type}")
    all_values = [] if remove_empty else ["---"]
    print(f"all_values: {all_values}")
    vehicle_spec_columns = [idx for idx, col in enumerate(parts.columns) if col[1] == vehicle_spec_type]
    all_values.extend([parts.columns[col][2] for col in vehicle_spec_columns])
    print(f"all_values: {all_values}")
    return all_values


def solverChange(event):
    global selectedSolver
    selectedSolver = event.widget.value
    # print(selectedSolver)
    # print(widgetyBuildup)
    for label, widget in widgetyBuildup.items():
        # print(label)
        # print(widget)

        # if type(widget) == gui2.ListBox:
        if isinstance(widget, gui2.ListBox):
            items = widget.items
            selectedIndexes = widget.selectedIndexes
            if selectedIndexes:
                selectedItems = [items[index] for index in selectedIndexes]
            else:
                selectedItems = []

            widget.clear()
            widget.append(find_compatible_parts(hierarchy_of_types, label.replace("vyber_",""), removeEmpty = True))

            for index, item in enumerate(widget.items):
                if item in selectedItems:
                    print(f"selected items: {selectedItems}")
                    print(f"index: {index}, {item}")
                    widget.select(index)


        # if it is onlyselection Combo
        elif isinstance(widget, gui2.ComboBox):
            selected_value = widget.value
            values = find_all_of_type(label.replace("vyber_", ""), remove_empty=False)
            print(f"values: {values}")
            if len(values) == 1:
                values = get_values_for_vehicle_spec(label.replace("vyber_", ""), remove_empty=False)
            widget.setValues(values)

            try:
                widget.value = selected_value
            except:
                pass

def ModelBuildupGUI():
    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        global dialogModelBuildup
        dialogModelBuildup.Hide()
        dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    # Method called on clicking 'Build-up'.
    def onBuildUpModelBuildup(event):
        print(f"BuildUp")
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

                for selected_item in selectedItems:
                    if selected_item != "---":
                        path = find_path_to_include_file(parts, selected_item)
                        print(f"path: {path}")
                        hw.evalTcl(f'source "{tcl_path}"; import_data "{path}"')
                    else:
                        print(f"selected_item: {selected_item}")

            # if it is onlyselection Combo
            elif isinstance(widget, gui2.ComboBox):
                print(f"Combo: {widget}")
                selected_value = widget.value
                if selected_value != "---":
                    path = find_path_to_include_file(parts, selected_value)
                    print(f"path: {path}")
                    hw.evalTcl(f'source "{tcl_path}"; import_data "{path}"')
                else:
                    print(f"selected_item: {selected_value}")
        global dialogModelBuildup
        dialogModelBuildup.Hide()
        gui2.tellUser('Model build-up has finished!')
        dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    # Method called on clicking 'Reset'.
    def onResetModelBuildup(event):
        for label, widget in widgetyBuildup.items():
            # print(label)
            # print(widget)
            typ = label.replace("vyber_", "")
            # if it is multiselection ListBox

            # if type(widget) == gui2.ListBox:
            if isinstance(widget, gui2.ListBox):
                widget.clear()
                widget.append(find_all_of_type(typ, remove_empty=True))
            # if it is onlyselection Combo
            elif isinstance(widget, gui2.ComboBox):
                values = find_all_of_type(typ, remove_empty=False)
                print(f"values: {values}")
                if len(values) == 1:
                    values = get_values_for_vehicle_spec(typ, remove_empty=False)
                widget.setValues(values)
                widget.value = "---"
        return

    close = gui.Button('Close', command=onCloseModelBuildup)
    buildup = gui.Button('Build-up', command=onBuildUpModelBuildup)
    reset = gui.Button('Reset', command=onResetModelBuildup)
    solver = gui2.ComboBox([(2,"OptiStruct"), (3,"Radioss")], command=solverChange, name="solver", width=150)

    vehicle_spec_frame = gui.HFrame(get_widget_vehicle_spec_structure(hierarchy_of_types["groups"]["vehicle_spec"]), container=True, maxwidth=500)

    widget_frame = gui.HFrame(get_widget_structure(hierarchy_of_types["groups"]["FT groups"]), container=True, )
    widget_frame.maxheight = widget_frame.reqheight

    main_frame = gui.VFrame(
        solver,
        15,
        vehicle_spec_frame,
        15,
        widget_frame,
        15,
        (500, buildup, reset, close)

    )

    dialogModelBuildup.recess().add(main_frame)

    dialogModelBuildup.setButtonVisibile('ok', False)
    dialogModelBuildup.setButtonVisibile('cancel', False)
    dialogModelBuildup.show(width=1000, height=500)
    # main_frame.move(x = 1, y = 1)


if __name__ == "__main__":
    mainFunc()
