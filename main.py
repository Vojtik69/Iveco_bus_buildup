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

from common import find_path_to_include_file, solverChange, get_widget_structure, \
    get_widget_vehicle_spec_structure, save_setup, load_setup, resetModelBuildup, parts, hierarchy_of_types, tcl_path

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

solver_interface = ['"OptiStruct" {}', '"RadiossBlock" "Radioss2023"']

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
        resetModelBuildup(event, widgetyBuildup, selectedSolver, parts)
        return

    close = gui.Button('Close', command=onCloseModelBuildup)
    buildup = gui.Button('Build-up', command=onBuildUpModelBuildup)
    reset = gui.Button('Reset', command=onResetModelBuildup)
    solver = gui2.ComboBox([(2,"OptiStruct"), (3,"Radioss")], command=lambda event: solverChange(event,
                                                                                                 hierarchy_of_types,
                                                                                                 parts, widgetyBuildup,
                                                                                                 selectedSolver), name="solver", width=150)
    load = gui.Button('Load setup', command=load_setup)
    save = gui.Button('Save setup', command=save_setup)

    vehicle_spec_frame = gui.HFrame(
        get_widget_vehicle_spec_structure(hierarchy_of_types["groups"]["vehicle_spec"], hierarchy_of_types, parts,
                                          widgetyBuildup, selectedSolver), container=True, maxwidth=500)

    widget_frame = gui.HFrame(
        get_widget_structure(hierarchy_of_types["groups"]["FT groups"], hierarchy_of_types, parts, selectedSolver,
                             widgetyBuildup), container=True, )
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
