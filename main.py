import os
import sys
# Získání cesty k aktuálně běžícímu skriptu
current_dir = os.path.dirname(os.path.realpath(__file__))
print(f"dirname: {current_dir}")
# Přidání této cesty do sys.path
sys.path.append(current_dir)
from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import yaml
import pandas as pd

from common import find_all_of_type, update_subordinant_items, find_path_to_include_file, find_compatible_parts

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

solver_interface = ['"OptiStruct" {}', '"RadiossBlock" "Radioss2023"']


def onSelectedCombo(event):
    print(f"event.widget.value: {event.widget.value}")
    update_subordinant_items(hierarchy_of_types, parts, widgetyBuildup, selectedSolver, event.widget.name)
    return


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
                vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=ft.get('name', ""), width=150-(offset*5))
                vyber_objekt.append(find_all_of_type(parts, selectedSolver, ft.get('name', ""), remove_empty=True))
            else:
                vyber_objekt = gui2.ComboBox(
                    find_all_of_type(parts, selectedSolver, ft.get('name', ""), remove_empty=False), command=onSelectedCombo, name=ft.get('name', ""), width=150 - (offset * 5))

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
            vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=vehicle_spec.get('name', ""), width=150)
        else:
            vyber_objekt = gui2.ComboBox(get_values_for_vehicle_spec(vehicle_spec.get('name', ""), remove_empty=False), command=onSelectedCombo, name=vehicle_spec.get('name',""), width=150)

        widgetyBuildup[f'label_{vehicle_spec.get("name", "")}'] = label_objekt
        widgetyBuildup[f'vyber_{vehicle_spec.get("name", "")}'] = vyber_objekt

        vehicle_spec_Widgets.append([[(widgetyBuildup[f'label_{vehicle_spec.get("name", "")}'],widgetyBuildup[f'vyber_{vehicle_spec.get("name", "")}'])]])

    return vehicle_spec_Widgets


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
                values = get_values_for_vehicle_spec(label.replace("vyber_", ""), remove_empty=False)
            widget.setValues(values)

            try:
                widget.value = selected_value
            except:
                pass


def save_setup():
    def save_file():
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
                selected_value = widget.value
                data[label] = selected_value

        with open(file_ent1.value, 'w') as file:
            yaml.dump(data, file)
        dialogSaveSetup.hide()
        gui2.tellUser("Vehicle setup saved.")

    label_1 = gui.Label(text="Select File :")
    file_ent1 = gui.OpenFileEntry(placeholdertext='Setup file to save', filetypes='(*.yaml)')

    save_setup_frame = gui.VFrame(label_1, file_ent1)

    dialogSaveSetup = gui.Dialog(caption="Select setup file to save")
    dialogSaveSetup.recess().add(save_setup_frame)
    dialogSaveSetup._controls["ok"].command = save_file
    dialogSaveSetup.show(height = 100)

def load_setup():
    def load_file():
        resetModelBuildup(None)
        with open(file_ent1.value, 'r') as file:
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

    label_1 = gui.Label(text="Select File :")
    file_ent1 = gui.OpenFileEntry(placeholdertext='Setup file to open', filetypes='(*.yaml)')

    load_setup_frame = gui.VFrame(label_1, file_ent1)

    dialogLoadSetup = gui.Dialog(caption="Select setup file to open")
    dialogLoadSetup.recess().add(load_setup_frame)
    dialogLoadSetup._controls["ok"].command = load_file
    dialogLoadSetup.show(height = 100)


# Method called on clicking 'Reset'.
def resetModelBuildup(event):
    for label, widget in widgetyBuildup.items():
        # print(label)
        # print(widget)
        typ = label.replace("vyber_", "")

        # if it is multiselection ListBox
        if isinstance(widget, gui2.ListBox):
            widget.clear()
            widget.append(find_all_of_type(parts, selectedSolver, typ, remove_empty=True))
        # if it is onlyselection Combo
        elif isinstance(widget, gui2.ComboBox):
            values = find_all_of_type(parts, selectedSolver, typ, remove_empty=False)
            print(f"values: {values}")
            if len(values) == 1:
                values = get_values_for_vehicle_spec(typ, remove_empty=False)
            widget.setValues(values)
            widget.value = "---"
    return

def ModelBuildupGUI():
    global dialogModelBuildup

    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        dialogModelBuildup.hide()


    # Method called on clicking 'Build-up'.
    def onBuildUpModelBuildup(event):
        print(f"BuildUp")
        print(solver_interface[selectedSolver-2])
        hw.evalTcl(f'::UserProfiles::LoadUserProfile {solver_interface[selectedSolver-2]}')
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

                for selected_item in selectedItems:
                    if selected_item != "---":
                        path = find_path_to_include_file(parts, selectedSolver, selected_item)
                        print(f"path: {path}")
                        hw.evalTcl(f'source "{tcl_path}"; import_data "{path}"')
                    else:
                        print(f"selected_item: {selected_item}")

            # if it is onlyselection Combo
            elif isinstance(widget, gui2.ComboBox):
                print(f"Combo: {widget}")
                selected_value = widget.value
                if selected_value != "---":
                    path = find_path_to_include_file(parts, selectedSolver, selected_value)
                    print(f"path: {path}")
                    hw.evalTcl(f'source "{tcl_path}"; import_data "{path}"')
                else:
                    print(f"selected_item: {selected_value}")
        onCloseModelBuildup(None)
        gui2.tellUser('Model build-up has finished!')
        dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    # Method called on clicking 'Reset'.
    def onResetModelBuildup(event):
        resetModelBuildup(event)
        return

    close = gui.Button('Close', command=onCloseModelBuildup)
    buildup = gui.Button('Build-up', command=onBuildUpModelBuildup)
    reset = gui.Button('Reset', command=onResetModelBuildup)
    solver = gui2.ComboBox([(2,"OptiStruct"), (3,"Radioss")], command=solverChange, name="solver", width=150)
    load = gui.Button('Load setup', command=load_setup)
    save = gui.Button('Save setup', command=save_setup)

    vehicle_spec_frame = gui.HFrame(get_widget_vehicle_spec_structure(hierarchy_of_types["groups"]["vehicle_spec"]), container=True, maxwidth=500)

    widget_frame = gui.HFrame(get_widget_structure(hierarchy_of_types["groups"]["FT groups"]), container=True, )
    widget_frame.maxheight = widget_frame.reqheight

    main_frame = gui.VFrame(
        (solver, "<->", load, save),
        15,
        vehicle_spec_frame,
        15,
        widget_frame,
        15,
        ("<->", buildup, reset, close)
    )


    dialogModelBuildup.recess().add(main_frame)

    dialogModelBuildup.setButtonVisibile('ok', False)
    dialogModelBuildup.setButtonVisibile('cancel', False)

    # main_frame.move(x = 1, y = 1)

def mainFunc(*args, **kwargs):
    global dialogModelBuildup

    dialogModelBuildup.show(width=1000, height=500)
    print("Initiated...")

ModelBuildupGUI()

if __name__ == "__main__":
    mainFunc()
