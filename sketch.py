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

print("Initiating...")

parts = pd.read_csv('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv', index_col=0,
                    header=0)
with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
    hierarchie_typu = yaml.safe_load(file)

# Slovník pro uchování vytvořených widgetů
widgetyBuildup = {}
widgetyAddPart = {}
widgetyEditPart = {}
dialogSetCompatibility = gui.Dialog(caption="Set compatibility")
dialogModelBuildup = gui.Dialog(caption="Bus model build-up")
dialogAddPart = gui.Dialog(caption="Add Part")
dialogEditPart = gui.Dialog(caption="Edit Part")

selectedSolver = "OptiStruct"


def mainFunc(*args, **kwargs):
    ModelBuildupGUI()
    print("Initiated...")


def find_all_of_type(searched_type, remove_empty=False):
    all_of_type = ["---"]
    print(searched_type)
    if remove_empty:
        all_of_type = []
    for index, row in parts.iterrows():
        print(index)
        if index == searched_type:
            all_of_type.append(row.iloc[0])
    return all_of_type

def onSelectedCombo():
    pass

def get_widget_structure(structure, levelWidgets=[]):
    subgrouping = True if levelWidgets else False
    for index, level in enumerate(structure):
        label_group = gui.Label(text=level.get("name"), font={'bold': True})
        if subgrouping:
            levelWidgets[-1].append([(10, label_group)])
        else:
            levelWidgets.append([(label_group)])
        for ft in level.get("FTs", []):
            label_objekt = gui.Label(text=ft.get("name", ""))

            if ft.get("multiselection", False):
                vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=ft.get('name', ""))
            else:
                vyber_objekt = gui2.ComboBox(find_all_of_type(ft.get('name',""),remove_empty=False), command=onSelectedCombo, name=ft.get('name',""))

            widgetyBuildup[f'label_{ft.get("name", "")}'] = label_objekt
            widgetyBuildup[f'vyber_{ft.get("name", "")}'] = vyber_objekt

            levelWidgets[-1].append(
                (widgetyBuildup[f'label_{ft.get("name", "")}'], 5, widgetyBuildup[f'vyber_{ft.get("name", "")}']))
        if level.get("groups"):
            get_widget_structure(level['groups'], levelWidgets)

    return levelWidgets

def get_widget_header_structure(structure, headerWidgets=[]):
    for header in structure:
        label_objekt = gui.Label(text=header.get("name", ""))

        if header.get("multiselection", False):
            vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=header.get('name', ""))
        else:
            vyber_objekt = gui2.ComboBox(find_all_of_type(header.get('name',""),remove_empty=False), command=onSelectedCombo, name=header.get('name',""))

        widgetyBuildup[f'label_{header.get("name", "")}'] = label_objekt
        widgetyBuildup[f'vyber_{header.get("name", "")}'] = vyber_objekt

        headerWidgets.append([[(widgetyBuildup[f'label_{header.get("name", "")}'],widgetyBuildup[f'vyber_{header.get("name", "")}'])]])

    return headerWidgets


def solverChange(event):
    global selectedSolver
    selectedSolver = event.widget.value
    #TODO: updateLabelyCest()


def ModelBuildupGUI():
    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        global dialogModelBuildup
        dialogModelBuildup.Hide()
        dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    # Method called on clicking 'Build-up'.
    def onBuildUpModelBuildup(event):
        pass
        # TODO global dialogModelBuildup
        # dialogModelBuildup.Hide()
        # gui2.tellUser('Done!')
        # dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    # Method called on clicking 'Reset'.
    def onResetModelBuildup(event):
        pass
        # TODO for [typ, multiselection] in extractAllTypes(hierarchie_typu):
        #     if multiselection:
        #         widgetyBuildup[f'vyber_{typ}'].clear()
        #     else:
        #         widgetyBuildup[f'vyber_{typ}'].setValues(najdi_vsechny_daneho_typu(typ))
        #         widgetyBuildup[f'vyber_{typ}'].value = "---"
        # updateLabelyCest()

    close = gui.Button('Close', command=onCloseModelBuildup)
    buildup = gui.Button('Build-up', command=onBuildUpModelBuildup)
    reset = gui.Button('Reset', command=onResetModelBuildup)
    solver = gui2.ComboBox(["OptiStruct", "Radioss"], command=solverChange, name="solver", width=150)

    header_frame = gui.HFrame(get_widget_header_structure(hierarchie_typu["groups"]["headers"]), container=True, maxwidth=300 )

    widget_frame = gui.HFrame(get_widget_structure(hierarchie_typu["groups"]["FT groups"]), container=True, )
    widget_frame.maxheight = widget_frame.reqheight

    main_frame = gui.VFrame(
        solver,
        15,
        header_frame,
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
