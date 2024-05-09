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

print("loading common.py")

def find_all_of_type(parts, selectedSolver, searched_type, remove_empty=False):

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


# not used
# def load_include_file(parts, part):
#     hw.evalTcl(f'puts "Importing {part}..."')
#     include_file_path = find_path_to_include_file(parts, part).replace("\\","/")
#     return include_file_path


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


def update_subordinant_items(hierarchy, parts, widgetyBuildup, selectedSolver, name):
    subordinants = find_subordinant_fts(hierarchy, name)
    print(f"subordinants in update_subordinant_items: {subordinants}")
    for subordinant in subordinants:
        # if it is multiselection ListBox
        if isinstance(widgetyBuildup[f'vyber_{subordinant}'], gui2.ListBox):
            widgetyBuildup["vyber_" + subordinant].clear()
            widgetyBuildup["vyber_" + subordinant].append(
                find_compatible_parts(hierarchy, parts, widgetyBuildup, selectedSolver, subordinant, removeEmpty=True))
        # if it is onlyselection Combo
        else:
            pass
            widgetyBuildup["vyber_" + subordinant].setValues(
                find_compatible_parts(hierarchy, parts, widgetyBuildup, selectedSolver, subordinant, removeEmpty=False))


def find_path_to_include_file(part_db, selectedSolver, name):
    print(f"name: {name}")
    if name != "---":
        path = part_db[part_db.index.get_level_values(1) == name].index.get_level_values(selectedSolver).tolist()[0]
    else:
        path = ""
    return path.replace("\\","/")


def find_compatible_parts(hierarchy, parts, widgetyBuildup, selectedSolver, name, removeEmpty=False):
    compatibles = [] if removeEmpty else ["---"]
    superordinant_types = find_superordinant_fts(hierarchy, name, superordinants=[])
    all_of_type = find_all_of_type(parts, selectedSolver, name, remove_empty=True)
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


def solverChange(event, hierarchy_of_types, parts, widgetyBuildup, selectedSolver):
    selectedSolver = event.widget.value
    # print(selectedSolver)
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
                find_compatible_parts(hierarchy_of_types, parts, widgetyBuildup, selectedSolver,
                                      label.replace("vyber_", ""), removeEmpty=True))

            for index, item in enumerate(widget.items):
                if item in selectedItems:
                    print(f"selected items: {selectedItems}")
                    print(f"index: {index}, {item}")
                    widget.select(index)


        # if it is onlyselection Combo
        elif isinstance(widget, gui2.ComboBox):
            selected_value = widget.value
            values = find_all_of_type(parts, selectedSolver, label.replace("vyber_", ""), remove_empty=False)
            print(f"values: {values}")
            if len(values) == 1:
                values = get_values_for_vehicle_spec(parts, label.replace("vyber_", ""), remove_empty=False)
            widget.setValues(values)

            try:
                widget.value = selected_value
            except:
                pass


def onSelectedCombo(event, parts, hierarchy_of_types, widgetyBuildup, selectedSolver):
    print(f"event.widget.value: {event.widget.value}")
    update_subordinant_items(hierarchy_of_types, parts, widgetyBuildup, selectedSolver, event.widget.name)
    return


def get_values_for_vehicle_spec(parts, vehicle_spec_type, remove_empty=False):
    print(f"vehicle_spec_type: {vehicle_spec_type}")
    all_values = [] if remove_empty else ["---"]
    print(f"all_values: {all_values}")
    vehicle_spec_columns = [idx for idx, col in enumerate(parts.columns) if col[1] == vehicle_spec_type]
    all_values.extend([parts.columns[col][2] for col in vehicle_spec_columns])
    print(f"all_values: {all_values}")
    return all_values

