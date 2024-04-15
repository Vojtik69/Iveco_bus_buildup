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

selectedSolver="OptiStruct"

def mainFunc(*args,**kwargs):
    ModelBuildupGUI()
    print("Initiated...")


def extractAllNames(data, onlynames=False):
    names = []
    for item in data:
        if onlynames:
            names.append(item['name'])
        else:
            names.append([item['name'], item['multiselection']])
        if 'subordinates' in item:
            names.extend(extractAllNames(item['subordinates'],onlynames))
    return names

def najit_prvek_podle_hodnoty(data, hodnota):
    if isinstance(data, dict):
        for klic, hodnota_vnitrni in data.items():
            if isinstance(hodnota_vnitrni, (dict, list)):
                nalezeny_prvek = najit_prvek_podle_hodnoty(hodnota_vnitrni, hodnota)
                if nalezeny_prvek is not None:
                    return nalezeny_prvek
            elif klic == 'name' and hodnota_vnitrni == hodnota:
                return data
    elif isinstance(data, list):
        for prvek in data:
            if isinstance(prvek, (dict, list)):
                nalezeny_prvek = najit_prvek_podle_hodnoty(prvek, hodnota)
                if nalezeny_prvek is not None:
                    return nalezeny_prvek
    return None


def findParent(data, target_name, parent=None):
    for item in data:
        if item['name'] == target_name:
            return parent
        elif 'subordinates' in item:
            result = findParent(item['subordinates'], target_name, item)
            if result is not None:
                return result

def getSubordinantsNames(hierarchie_typu, node_name, onlynames=False, descendants=[]):
    # print(node_name)
    node = najit_prvek_podle_hodnoty(hierarchie_typu, node_name)
    # print(node)
    try:
        for subordinate in node['subordinates']:
            if onlynames:
                descendants.append(subordinate['name'])
            else:
                descendants.append([subordinate['name'], subordinate['multiselection']])
            if subordinate['skippable']:
                getSubordinantsNames([subordinate], subordinate['name'],onlynames,descendants)
    except Exception as e: print("Chyba v getSubordinantsNames(): " + str(e))
    return descendants


def najdi_kompatibilni_radky(hledany_sloupec, pozadovany_typ, only_names=False, removeEmpty = False):
    kompatibilni_radky = [("---","---")]
    if removeEmpty: kompatibilni_radky = []
    try:
        sloupec = parts.columns.get_loc(hledany_sloupec)
        # print(sloupec)
    except KeyError:
        return []

    for index, row in parts.iterrows():

        if row.iloc[0] == pozadovany_typ and row.iloc[sloupec] != 0 and not pd.isnull(row.iloc[sloupec]):
            kompatibilni_radky.append((row.iloc[1], row.name))

    if only_names:
        kompatibilni_radky = [item[1] for item in kompatibilni_radky]

    print("kompatibilni_radky: " + str(kompatibilni_radky))
    return kompatibilni_radky

def najdi_cestu(hledany_komponent, solver=None):
    cesta = "Nenalezeno"
    if not solver:
        solver=selectedSolver
    if hledany_komponent == "---":
        return "---"
    for index, row in parts.iterrows():
        print(str(index))

        if (str(index) == hledany_komponent):
            cesta = row.iloc[1] if solver=="OptiStruct" else row.iloc[2]
            break
    return cesta

def najdi_vsechny_daneho_typu(hledany_typ, removeEmpty=False):
    vsechny = ["---"]
    if removeEmpty: vsechny = []
    for index, row in parts.iterrows():
        if row.iloc[0] == hledany_typ:
            vsechny.append(index)  # přidá obsah druhého a prvního sloupce
    return vsechny

def najdi_vsechny_party():
    vsechny_party = []
    for index, row in parts.iterrows():
        vsechny_party.append(index)  # přidá obsah prvního sloupce
    return vsechny_party

def najdiLabelPodleCesty(cesta):
    label = "Nenalezeno"
    for index, row in parts.iterrows():
        if row.iloc[1] == cesta:
            label = row.name
            break
    return label

def zjistiTypPodleCesty(cesta):
    typ = None
    for index, row in parts.iterrows():
        if row.iloc[1] == cesta:
            typ = row.iloc[0]  # přidá obsah prvního sloupce
            break
    return typ

def updateLabelyCest():
    for [typ,multiselection] in extractAllNames(hierarchie_typu):
        try:
            widgetyBuildup[f'cesta_{typ}'].text = najdi_cestu(widgetyBuildup[f'vyber_{typ}'].value)
        except:
            pass

def onSelectedCombo(event):
    print(event.widget.value)
    widgetyBuildup[f'cesta_{event.widget.name}'].text = najdi_cestu(event.widget.value)
    subordinants = getSubordinantsNames(hierarchie_typu, event.widget.name,onlynames=False, descendants=[])
    print("Subordinants: "+str(subordinants))
    for [typ, multiselection] in subordinants:
        if widgetyBuildup[f'vyber_{event.widget.name}'].value == "---":
            if najit_prvek_podle_hodnoty(hierarchie_typu, event.widget.name).get("skippable",False):
                parent = findParent(hierarchie_typu, event.widget.name)
                if multiselection:
                    widgetyBuildup["vyber_" + typ].clear()
                    widgetyBuildup["vyber_" + typ].append(
                        najdi_kompatibilni_radky(widgetyBuildup[f'vyber_{parent["name"]}'].value,
                                                 typ),only_names=True,removeEmpty=True)
                else:
                    widgetyBuildup["vyber_" + typ].setValues(najdi_kompatibilni_radky(widgetyBuildup[f'vyber_{parent["name"]}'].value, typ, only_names=True, removeEmpty = False))
            else:
                if multiselection:
                    widgetyBuildup["vyber_" + typ].clear()
                    widgetyBuildup["vyber_" + typ].append(najdi_vsechny_daneho_typu(typ,removeEmpty=True))
                else:
                    widgetyBuildup["vyber_" + typ].setValues(najdi_vsechny_daneho_typu(typ,removeEmpty=False))
        else:
            if multiselection:
                widgetyBuildup["vyber_" + typ].clear()
                widgetyBuildup["vyber_" + typ].append(najdi_kompatibilni_radky(event.value, typ,only_names=True,removeEmpty=True))
            else:
                widgetyBuildup["vyber_" + typ].setValues(najdi_kompatibilni_radky(event.value, typ,only_names=True,removeEmpty=False))
                widgetyBuildup[f'cesta_{typ}'].text = widgetyBuildup[f'vyber_{typ}'].value

def solverChange(event):
    global selectedSolver
    selectedSolver = event.widget.value
    updateLabelyCest()


def ModelBuildupGUI():
    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        global dialogModelBuildup
        dialogModelBuildup.Hide()
        dialogModelBuildup = gui.Dialog(caption  = "Bus model build-up")

    def onRunModelBuildup(event):
        global dialogModelBuildup
        dialogModelBuildup.Hide()
        gui2.tellUser('Done!')
        dialogModelBuildup = gui.Dialog(caption="Bus model build-up")

    def onResetModelBuildup(event):
        for [typ, multiselection] in extractAllNames(hierarchie_typu):
            if multiselection:
                widgetyBuildup[f'vyber_{typ}'].clear()
            else:
                widgetyBuildup[f'vyber_{typ}'].setValues(najdi_vsechny_daneho_typu(typ))
                widgetyBuildup[f'vyber_{typ}'].value = "---"
        updateLabelyCest()

    obrazek = gui.Label(icon='N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/bus.png')

    close  = gui.Button('Close', command=onCloseModelBuildup)
    create = gui.Button('Build-up', command=onRunModelBuildup)
    reset  = gui.Button('Reset', command=onResetModelBuildup)
    add =    gui.Button('Add Part', command=AddPartGUI)
    edit =   gui.Button('Edit Part', command=EditPartGUI)
    solver = gui2.ComboBox(["OptiStruct", "Radioss"], command=solverChange, name="solver", width=150)

    # Vytvoř widgetyBuildup
    for [typ,multiselection] in extractAllNames(hierarchie_typu):
        if multiselection:
            label_objekt = gui.Label(text=f'{typ.capitalize()}')
            vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=typ)

            # Uložení objektů do slovníku
            widgetyBuildup[f'label_{typ}'] = label_objekt
            widgetyBuildup[f'vyber_{typ}'] = vyber_objekt
        else:
            label_objekt = gui.Label(text=f'{typ.capitalize()}')
            vyber_objekt = gui2.ComboBox(najdi_vsechny_daneho_typu(typ,removeEmpty=False), command=onSelectedCombo, name=typ)
            cesta_objekt = gui2.Label("---", font=dict(size=8, italic=True))

            # Uložení objektů do slovníku
            widgetyBuildup[f'label_{typ}'] = label_objekt
            widgetyBuildup[f'vyber_{typ}'] = vyber_objekt
            widgetyBuildup[f'cesta_{typ}'] = cesta_objekt

    # Napolohuj Widgety
    mainFrame = gui.VFrame (
                (solver, 300, widgetyBuildup['label_na_strechu'], 300, add, edit),
                (350, widgetyBuildup['vyber_na_strechu'], 350),
                (900, widgetyBuildup['label_front_accessories']),
                (150, obrazek, 10, widgetyBuildup['vyber_front_accessories']),
                (5),
                (widgetyBuildup['label_rear'], 10, widgetyBuildup['label_prodluzovaci'], 10, widgetyBuildup['label_middle'], 10, widgetyBuildup['label_front']),
                (widgetyBuildup['vyber_rear'], 10, widgetyBuildup['vyber_prodluzovaci'], 10, widgetyBuildup['vyber_middle'], 10, widgetyBuildup['vyber_front']),
                (widgetyBuildup['cesta_rear'], 10, widgetyBuildup['cesta_prodluzovaci'], 10, widgetyBuildup['cesta_middle'], 10, widgetyBuildup['cesta_front']),
                (15),
                (500,create,reset,close)
        )

    dialogModelBuildup.recess().add(mainFrame)
    dialogModelBuildup.setButtonVisibile('ok',False)
    dialogModelBuildup.setButtonVisibile('cancel',False)
    dialogModelBuildup.show(width=1000, height=500)


def SetCompatibilityGUI(typ):
    boxesParents = []
    boxesSubordinants = []
    rada1 = ()
    rada2 = ()
    tabulky_parents = {}
    tabulky_subordinants = {}

    def onCancelCompatibilityGUI():
        global dialogSetCompatibility
        dialogSetCompatibility.Hide()
        dialogSetCompatibility = gui.Dialog(caption = "Set compatibility")
        global tabulky_parents
        global tabulky_subordinants
        tabulky_parents = {}
        tabulky_subordinants = {}

    parent = findParent(hierarchie_typu, typ)
    if parent:
        boxesParents = [parent["name"]]
        while parent["skippable"]:
            parent = findParent(hierarchie_typu, parent["name"])
            boxesParents.append(parent["name"])

    boxesSubordinants = getSubordinantsNames(hierarchie_typu, typ, onlynames=True,descendants=[])

    def createTable(type):
        root = gui.TableCellData(headers=[{'text': 'Part'}, {'text': 'Position'}])
        row = 0
        for part in najdi_vsechny_daneho_typu(type, removeEmpty=True):
            root.setData(row, 0, value=part, type='string', state='disabled')
            root.setData(row, 1, value='[,,]', type='string', state='enabled')
            row += 1

        tabulka = gui.TableView()
        model = gui.TableDataModel(root, parent=tabulka)
        delegate = gui.TableDelegate(parent=tabulka)
        tabulka.SetItemDelegate(delegate)
        sort_filter_model = gui.TableSortFilterModel(model)
        tabulka.model = sort_filter_model
        return tabulka

    for parent in boxesParents:
        label_objekt = gui.Label(text=f'{parent.capitalize()}')
        tabulky_parents[parent] = createTable(parent)

        rada1 = rada1 + (label_objekt,10,)
        rada2 = rada2 + (tabulky_parents[parent],10,)

    rada1 = rada1[:-1]
    rada2 = rada2[:-1]
    parentsFrame = gui.VFrame(rada1, rada2)
    rada1 = ()
    rada2 = ()

    for subordinate in boxesSubordinants:
        label_objekt = gui.Label(text=f'{subordinate.capitalize()}')
        tabulky_subordinants[subordinate] = createTable(subordinate)

        rada1 = rada1 + (label_objekt,10,)
        rada2 = rada2 + (tabulky_subordinants[subordinate],10,)

    rada1 = rada1[:-1]
    rada2 = rada2[:-1]
    subordinatesFrame = gui.VFrame(rada1, rada2)
    rada1 = ()
    rada2 = ()



    global compatibilityGuiFrame

    cancel  = gui.Button('Cancel', command=onCancelCompatibilityGUI)
    confirm = gui.Button('Confirm')

    sep = gui.Separator(orientation='vertical', spacing='30')

    upperFrame = gui.HFrame(parentsFrame, sep, subordinatesFrame)
    compatibilityGuiFrame = gui.VFrame(upperFrame, (800, confirm, cancel))

    dialogSetCompatibility.recess().add(compatibilityGuiFrame)

    dialogSetCompatibility.setButtonVisibile('ok', False)
    dialogSetCompatibility.setButtonVisibile('cancel', False)
    dialogSetCompatibility.show(width=900, height=500)


def AddPartGUI():
    global widgetyAddPart

    widgetyAddPart['label_typ'] = gui.Label(text="Type of new part:")
    widgetyAddPart['vyber_typ'] = gui2.ComboBox(extractAllNames(hierarchie_typu,onlynames=True), name="vyber_typ")

    widgetyAddPart['label_cesta_OptiStruct'] = gui.Label(text="Path to OptiStruct:")
    widgetyAddPart['vyber_cesta_OptiStruct'] = gui.OpenFileEntry(placeholdertext="Path to OptiStruct")

    widgetyAddPart['label_cesta_Radioss'] = gui.Label(text="Path to Radioss:")
    widgetyAddPart['vyber_cesta_Radioss'] = gui.OpenFileEntry(placeholdertext="Path to Radioss")

    widgetyAddPart['label_nazev'] = gui.Label(text="Name of new part:")
    widgetyAddPart['vyber_nazev'] = gui.LineEdit()


    # Method called on clicking 'Close'.
    def onCloseAddPartGUI(event):
        global dialogAddPart
        dialogAddPart.Hide()
        dialogAddPart = gui.Dialog(caption  = "Add Part")

    def onResetAddPartGUI(event):
        widgetyAddPart['vyber_nazev'].value = ""
        widgetyAddPart['vyber_cesta_OptiStruct'].value = ""
        widgetyAddPart['vyber_cesta_Radioss'].value = ""
        widgetyAddPart['vyber_typ'].value = ""

    def checkNotEmpty():
        if widgetyAddPart['vyber_nazev'].value in najdi_vsechny_party():
            gui2.tellUser("Name of new part is not unique")
            return

        if widgetyAddPart['vyber_cesta_OptiStruct'].value == "" and widgetyAddPart['vyber_cesta_Radioss'].value == "":
            gui2.tellUser("Paths to files are both empty.")
            return
        else:
            if widgetyAddPart['vyber_cesta_OptiStruct'].value != "" and not os.path.isfile(widgetyAddPart['vyber_cesta_OptiStruct'].value):
                gui2.tellUser("Path for OptiStruct is not valid. The file does not exist.")
                return
            if widgetyAddPart['vyber_cesta_Radioss'].value != "" and not os.path.isfile(widgetyAddPart['vyber_cesta_Radioss'].value):
                gui2.tellUser("Path for Radioss is not valid. The file does not exist.")
                return

        SetCompatibilityGUI(widgetyAddPart['vyber_typ'].value)

    close = gui.Button('Close', command=onCloseAddPartGUI)
    add   = gui.Button('Set compatibility >>>', command=checkNotEmpty)
    reset = gui.Button('Reset', command=onResetAddPartGUI)

    upperFrame = gui.HFrame(
        (5),
        (widgetyAddPart['label_nazev'], 5, widgetyAddPart['vyber_nazev'], 10, widgetyAddPart['label_cesta_OptiStruct'], widgetyAddPart['vyber_cesta_OptiStruct'], 20),
        (widgetyAddPart['label_typ'], 5, widgetyAddPart['vyber_typ'], 10, widgetyAddPart['label_cesta_Radioss'], widgetyAddPart['vyber_cesta_Radioss'], 20),
        (10),
    )

    lowerFrame = gui.HFrame(100, add, reset, close)

    dialogAddPart.recess().add(upperFrame)
    dialogAddPart.recess().add(lowerFrame)
    dialogAddPart.setButtonVisibile('ok', False)
    dialogAddPart.setButtonVisibile('cancel', False)
    dialogAddPart.show(width=600, height=80)
    print(widgetyAddPart['vyber_cesta_OptiStruct'].value)

def EditPartGUI():
    global widgetyEditPart

    def onSelectedTypeOriginal():
        widgetyEditPart['vyber_typ_new'].set(widgetyEditPart['vyber_typ_original'].get())
        widgetyEditPart['vyber_nazev_original'].setValues(najdi_vsechny_daneho_typu(widgetyEditPart['vyber_typ_original'].get(), removeEmpty=True))
        widgetyEditPart['vyber_nazev_new'].set(widgetyEditPart['vyber_nazev_original'].get())
        widgetyEditPart['vyber_cesta_new_OptiStruct'].set(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get(),solver="OptiStruct"))
        widgetyEditPart['vyber_cesta_new_Radioss'].set(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get(), solver="Radioss"))

    def onSelectedNameOriginal():
        widgetyEditPart['vyber_nazev_new'].set(widgetyEditPart['vyber_nazev_original'].get())
        widgetyEditPart['vyber_cesta_new_OptiStruct'].set(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get(),solver="OptiStruct"))
        widgetyEditPart['vyber_cesta_new_Radioss'].set(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get(), solver="Radioss"))


    widgetyEditPart['label_typ_original'] = gui.Label(text="Original type of part:")
    widgetyEditPart['vyber_typ_original'] = gui2.ComboBox(extractAllNames(hierarchie_typu,onlynames=True), name="vyber_typ_original", command=onSelectedTypeOriginal)

    widgetyEditPart['label_nazev_original'] = gui.Label(text="Original name of part:")
    widgetyEditPart['vyber_nazev_original'] = gui2.ComboBox(najdi_vsechny_daneho_typu(widgetyEditPart['vyber_typ_original'].value, removeEmpty=True), name="vyber_typ_original", command=onSelectedNameOriginal)

    widgetyEditPart['label_typ_new'] = gui.Label(text="New type of part:")
    widgetyEditPart['vyber_typ_new'] = gui2.ComboBox(extractAllNames(hierarchie_typu,onlynames=True), name="vyber_typ_new")

    widgetyEditPart['label_nazev_new'] = gui.Label(text="New name of part:")
    widgetyEditPart['vyber_nazev_new'] = gui.LineEdit(najdi_vsechny_daneho_typu(widgetyEditPart['vyber_typ_original'].value)[1])

    widgetyEditPart['label_cesta_new_OptiStruct'] = gui.Label(text="New path to OptiStruct:")
    widgetyEditPart['vyber_cesta_new_OptiStruct'] = gui.OpenFileEntry(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get(),solver="OptiStruct"), placeholdertext="Path to OptiStruct")

    widgetyEditPart['label_cesta_new_Radioss'] = gui.Label(text="New path to Radioss:")
    widgetyEditPart['vyber_cesta_new_Radioss'] = gui.OpenFileEntry(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get(), solver="Radioss"), placeholdertext="Path to Radioss")


    # Method called on clicking 'Close'.
    def onCloseEditPartGUI(event):
        global dialogEditPart
        dialogEditPart.Hide()
        dialogEditPart = gui.Dialog(caption  = "Edit Part")

    def onResetEditPartGUI(event):
        widgetyEditPart['vyber_typ_original'].value = ""
        widgetyEditPart['vyber_nazev_original'].setValues(najdi_vsechny_daneho_typu(widgetyEditPart['vyber_typ_original'].get(), removeEmpty=True))
        widgetyEditPart['vyber_typ_new'].value = widgetyEditPart['vyber_typ_original'].value
        widgetyEditPart['vyber_nazev_new'].value = widgetyEditPart['vyber_nazev_original'].value
        widgetyEditPart['vyber_cesta_new_OptiStruct'].value = najdi_cestu(widgetyEditPart['vyber_nazev_original'].get(),solver="OptiStruct")
        widgetyEditPart['vyber_cesta_new_Radioss'].value = najdi_cestu(widgetyEditPart['vyber_nazev_original'].get(), solver="Radioss")

    def checkNotEmpty():
        if widgetyEditPart['vyber_nazev_new'].value in najdi_vsechny_party():
            if widgetyEditPart['vyber_nazev_original'].value != widgetyEditPart['vyber_nazev_new'].value:
                gui2.tellUser("New name of part is not unique")
                return

        if widgetyEditPart['vyber_cesta_new_OptiStruct'].value == "" and widgetyEditPart['vyber_cesta_new_Radioss'].value == "":
            gui2.tellUser("Paths to files are both empty.")
            return
        else:
            if widgetyEditPart['vyber_cesta_new_OptiStruct'].value != "" and not os.path.isfile(
                    widgetyEditPart['vyber_cesta_new_OptiStruct'].value):
                gui2.tellUser("Path for OptiStruct is not valid. The file does not exist.")
                return
            if widgetyEditPart['vyber_cesta_new_Radioss'].value != "" and not os.path.isfile(
                    widgetyEditPart['vyber_cesta_new_Radioss'].value):
                gui2.tellUser("Path for Radioss is not valid. The file does not exist.")
                return

        SetCompatibilityGUI(widgetyEditPart['vyber_typ_new'].value)



    close = gui.Button('Close', command=onCloseEditPartGUI)
    add   = gui.Button('Set compatibility >>>', command=checkNotEmpty)
    reset = gui.Button('Reset', command=onResetEditPartGUI)

    upperFrame = gui.HFrame(
        (5),
        (widgetyEditPart['label_typ_original'], 5, widgetyEditPart['vyber_typ_original']),
        (widgetyEditPart['label_nazev_original'], 5, widgetyEditPart['vyber_nazev_original']),
        (230)

    )
    middleFrame = gui.HFrame(
        (widgetyEditPart['label_typ_new'], 5, widgetyEditPart['vyber_typ_new'], 15, widgetyEditPart['label_cesta_new_OptiStruct'], 5, widgetyEditPart['vyber_cesta_new_OptiStruct'], 30),
        (widgetyEditPart['label_nazev_new'], 5, widgetyEditPart['vyber_nazev_new'],  15, widgetyEditPart['label_cesta_new_Radioss'], 5, widgetyEditPart['vyber_cesta_new_Radioss'], 30)
    )

    lowerFrame = gui.HFrame(100, add, reset, close)
    sep = gui.Separator(orientation='horizontal', spacing='15')

    dialogEditPart.recess().add(upperFrame)
    dialogEditPart.recess().add(sep)
    dialogEditPart.recess().add(middleFrame)
    dialogEditPart.recess().add(lowerFrame)
    dialogEditPart.setButtonVisibile('ok', False)
    dialogEditPart.setButtonVisibile('cancel', False)
    dialogEditPart.show(width=600, height=80)

if __name__ == "__main__":
    mainFunc()







