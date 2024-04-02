from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import os
import itertools
from functools import partial
import csv
import yaml
import os.path

# Slovník pro uchování vytvořených widgetů
widgetyBuildup = {}
widgetyAddPart = {}
widgetyEditPart = {}
dialogSetCompatibility = gui.Dialog(caption  = "Set compatibility")
dialogModelBuildup = gui.Dialog(caption  = "Bus model buildup")
dialogAddPart = gui.Dialog(caption  = "Add Part")
dialogEditPart = gui.Dialog(caption  = "Edit Part")
csv_file = 'N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv'

with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
    hierarchie_typu = yaml.safe_load(file)

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
    print(node_name)
    node = najit_prvek_podle_hodnoty(hierarchie_typu, node_name)
    print(node)
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


def najdi_kompatibilni_radky(hledany_sloupec, pozadovany_typ, only_names=False):
    kompatibilni_radky = [("---", "---")]
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # uloží hlavicku

        try:
            sloupec = header.index(hledany_sloupec)
        except:
            return []

        for row in reader:
            if row[1] == pozadovany_typ and row[sloupec] != '0' and row[sloupec] is not None:
                kompatibilni_radky.append((row[2], row[0]))  # pridá obsah prvního a tretího sloupce
    if only_names : kompatibilni_radky = [item[1] for item in kompatibilni_radky[1:]]
    return kompatibilni_radky

def najdi_cestu(hledany_komponent):
    cesta = "Nenalezeno"
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # preskoc hlavicku

        for row in reader:
            if row[0] == hledany_komponent:
                cesta = row[2]
    return cesta

def najdi_vsechny_daneho_typu(hledany_typ, only_names=False):
    vsechny = [("---", "---")]
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # preskoc hlavicku

        for row in reader:
            if row[1] == hledany_typ:
                vsechny.append((row[2], row[0]))  # pridá obsah prvního a tretího sloupce

    if only_names : vsechny = [item[1] for item in vsechny[1:]]
    return vsechny

def najdi_vsechny_party():
    vsechny_party = []
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # preskoc hlavicku
        for row in reader:
            vsechny_party.append(row[0])  # pridá obsah prvního a tretího sloupce
    return vsechny_party

def najdiLabelPodleCesty(cesta):
    label = "Nenalezeno"
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # preskoc hlavicku

        for row in reader:
            if row[2] == cesta:
                label = row[0]
    return label

def zjistiTypPodleCesty(cesta):
    with open(csv_file, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # preskoc hlavicku

        for row in reader:
            if row[2] == cesta:
                typ = row[1]  # pridá obsah prvního a tretího sloupce
    return typ

def updateLabelyCest():
    for [typ,multiselection] in extractAllNames(hierarchie_typu):
        try:
            widgetyBuildup[f'cesta_{typ}'].text = widgetyBuildup[f'vyber_{typ}'].value
        except:
            pass

def onSelectedCombo(event):
    widgetyBuildup[f'cesta_{event.widget.name}'].text = widgetyBuildup[f'vyber_{event.widget.name}'].value
    subordinants = getSubordinantsNames(hierarchie_typu, event.widget.name,[])
    for [typ, multiselection] in subordinants:
        if widgetyBuildup[f'vyber_{event.widget.name}'].value == "---":
            if najit_prvek_podle_hodnoty(hierarchie_typu, event.widget.name).get("skippable",False):
                parent = findParent(hierarchie_typu, event.widget.name)
                if multiselection:
                    widgetyBuildup["vyber_" + typ].clear()
                    widgetyBuildup["vyber_" + typ].append(
                        najdi_kompatibilni_radky(najdiLabelPodleCesty(widgetyBuildup[f'vyber_{parent["name"]}'].value),
                                                 typ),True)
                else:
                    widgetyBuildup["vyber_" + typ].setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(widgetyBuildup[f'vyber_{parent["name"]}'].value), typ, True))
            else:
                if multiselection:
                    widgetyBuildup["vyber_" + typ].clear()
                    widgetyBuildup["vyber_" + typ].append(najdi_vsechny_daneho_typu(typ))
                else:
                    widgetyBuildup["vyber_" + typ].setValues(najdi_vsechny_daneho_typu(typ))
        else:
            if multiselection:
                widgetyBuildup["vyber_" + typ].clear()
                widgetyBuildup["vyber_" + typ].append(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), typ, True))
            else:
                widgetyBuildup["vyber_" + typ].setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), typ))
                widgetyBuildup[f'cesta_{typ}'].text = widgetyBuildup[f'vyber_{typ}'].value


def ModelBuildupGUI():
    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        global dialogModelBuildup
        dialogModelBuildup.Hide()
        dialogModelBuildup = gui.Dialog(caption  = "Bus model buildup")

    def onRunModelBuildup(event):
        global dialogModelBuildup
        dialogModelBuildup.Hide()
        gui2.tellUser('Done!')
        dialogModelBuildup = gui.Dialog(caption="Bus model buildup")

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
    create = gui.Button('Run', command=onRunModelBuildup)
    reset  = gui.Button('Reset', command=onResetModelBuildup)
    add =    gui.Button('Add Part', command=AddPartGUI)
    edit =   gui.Button('Edit Part', command=EditPartGUI)

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
            vyber_objekt = gui2.ComboBox(najdi_vsechny_daneho_typu(typ), command=onSelectedCombo, name=typ)
            cesta_objekt = gui2.Label("---", font=dict(size=8, italic=True))

            # Uložení objektů do slovníku
            widgetyBuildup[f'label_{typ}'] = label_objekt
            widgetyBuildup[f'vyber_{typ}'] = vyber_objekt
            widgetyBuildup[f'cesta_{typ}'] = cesta_objekt

    # Napolohuj Widgety
    mainFrame = gui.VFrame (
                (350, widgetyBuildup['label_na_strechu'], 300, add, edit),
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
        for part in najdi_vsechny_daneho_typu(type, only_names=True):
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

    widgetyAddPart['label_cesta'] = gui.Label(text="Path to part:")
    widgetyAddPart['vyber_cesta'] = gui.OpenFileEntry(placeholdertext="Path to File")

    widgetyAddPart['label_nazev'] = gui.Label(text="Name of new part:")
    widgetyAddPart['vyber_nazev'] = gui.LineEdit()


    # Method called on clicking 'Close'.
    def onCloseAddPartGUI(event):
        global dialogAddPart
        dialogAddPart.Hide()
        dialogAddPart = gui.Dialog(caption  = "Add Part")

    def onResetAddPartGUI(event):
        widgetyAddPart['vyber_nazev'].value = ""
        widgetyAddPart['vyber_cesta'].value = ""
        widgetyAddPart['vyber_typ'].value = ""

    def checkNotEmpty():
        if widgetyAddPart['vyber_nazev'].value in najdi_vsechny_party():
            gui2.tellUser("Name of new part is not unique")
            return
        if not os.path.isfile(widgetyAddPart['vyber_cesta'].value):
            gui2.tellUser("Path is not valid. The file does not exist.")
            return

        SetCompatibilityGUI(widgetyAddPart['vyber_typ'].value)

    close = gui.Button('Close', command=onCloseAddPartGUI)
    add   = gui.Button('Set compatibility >>>', command=checkNotEmpty)
    reset = gui.Button('Reset', command=onResetAddPartGUI)

    upperFrame = gui.HFrame(
		(5),
        (widgetyAddPart['label_nazev'], 5, widgetyAddPart['vyber_nazev'], 50),
        (widgetyAddPart['label_cesta'], 5, widgetyAddPart['vyber_cesta'], 50),
        (widgetyAddPart['label_typ'], 5, widgetyAddPart['vyber_typ'], 50),
	)

    lowerFrame = gui.HFrame(100, add, reset, close)

    dialogAddPart.recess().add(upperFrame)
    dialogAddPart.recess().add(lowerFrame)
    dialogAddPart.setButtonVisibile('ok', False)
    dialogAddPart.setButtonVisibile('cancel', False)
    dialogAddPart.show(width=600, height=80)

def EditPartGUI():
    global widgetyEditPart

    def onSelectedTypeOriginal():
        widgetyEditPart['vyber_typ_new'].set(widgetyEditPart['vyber_typ_original'].get())
        widgetyEditPart['vyber_nazev_original'].setValues(najdi_vsechny_daneho_typu(widgetyEditPart['vyber_typ_original'].value, only_names=True))
        widgetyEditPart['vyber_nazev_new'].set(widgetyEditPart['vyber_nazev_original'].get())
        widgetyEditPart['vyber_cesta_new'].set(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get()))

    def onSelectedNameOriginal():
        widgetyEditPart['vyber_nazev_new'].set(widgetyEditPart['vyber_nazev_original'].get())
        widgetyEditPart['vyber_cesta_new'].set(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get()))


    widgetyEditPart['label_typ_original'] = gui.Label(text="Original type of part:")
    widgetyEditPart['vyber_typ_original'] = gui2.ComboBox(extractAllNames(hierarchie_typu,onlynames=True), name="vyber_typ_original", command=onSelectedTypeOriginal)

    widgetyEditPart['label_nazev_original'] = gui.Label(text="Original name of part:")
    widgetyEditPart['vyber_nazev_original'] = gui2.ComboBox(najdi_vsechny_daneho_typu(widgetyEditPart['vyber_typ_original'].value, only_names=True), name="vyber_typ_original", command=onSelectedNameOriginal)

    widgetyEditPart['label_typ_new'] = gui.Label(text="New type of part:")
    widgetyEditPart['vyber_typ_new'] = gui2.ComboBox(extractAllNames(hierarchie_typu,onlynames=True), name="vyber_typ_new")

    widgetyEditPart['label_nazev_new'] = gui.Label(text="New name of part:")
    widgetyEditPart['vyber_nazev_new'] = gui.LineEdit(najdi_vsechny_daneho_typu(widgetyEditPart['vyber_typ_original'].value)[1][1])

    widgetyEditPart['label_cesta_new'] = gui.Label(text="New path to part:")
    widgetyEditPart['vyber_cesta_new'] = gui.OpenFileEntry(najdi_cestu(widgetyEditPart['vyber_nazev_original'].get()), placeholdertext="Path to File")


    # Method called on clicking 'Close'.
    def onCloseEditPartGUI(event):
        global dialogEditPart
        dialogEditPart.Hide()
        dialogEditPart = gui.Dialog(caption  = "Edit Part")

    def onResetEditPartGUI(event):
        widgetyEditPart['vyber_nazev_original'].value = ""
        widgetyEditPart['vyber_typ_original'].value = ""
        widgetyEditPart['vyber_typ_new'].value = ""
        widgetyEditPart['vyber_nazev_new'].value = ""
        widgetyEditPart['vyber_cesta_new'].value = ""

    def checkNotEmpty():
        if widgetyEditPart['vyber_nazev_new'].value in najdi_vsechny_party():
            if widgetyEditPart['vyber_nazev_original'].value != widgetyEditPart['vyber_nazev_new'].value:
                gui2.tellUser("New name of part is not unique")
                return
        if not os.path.isfile(widgetyEditPart['vyber_cesta_new'].value):
            gui2.tellUser("Path is not valid. The file does not exist.")
            return

        SetCompatibilityGUI(widgetyEditPart['vyber_typ_new'].value)

    close = gui.Button('Close', command=onCloseEditPartGUI)
    add   = gui.Button('Set compatibility >>>', command=checkNotEmpty)
    reset = gui.Button('Reset', command=onResetEditPartGUI)

    upperFrame = gui.HFrame(
		(5),
        (widgetyEditPart['label_typ_original'], 5, widgetyEditPart['vyber_typ_original'], 50),
        (widgetyEditPart['label_nazev_original'], 5, widgetyEditPart['vyber_nazev_original'], 50),
        (230)

	)
    middleFrame = gui.HFrame(
        (widgetyEditPart['label_typ_new'], 5, widgetyEditPart['vyber_typ_new'], 50),
        (widgetyEditPart['label_nazev_new'], 5, widgetyEditPart['vyber_nazev_new'], 50),
        (widgetyEditPart['label_cesta_new'], 5, widgetyEditPart['vyber_cesta_new'], 50),
    )

    lowerFrame = gui.HFrame(100, add, reset, close)

    dialogEditPart.recess().add(upperFrame)
    dialogEditPart.recess().add(middleFrame)
    dialogEditPart.recess().add(lowerFrame)
    dialogEditPart.setButtonVisibile('ok', False)
    dialogEditPart.setButtonVisibile('cancel', False)
    dialogEditPart.show(width=600, height=80)


        
        

        



