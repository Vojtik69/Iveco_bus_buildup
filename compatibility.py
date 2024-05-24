import os
import sys
# Získání cesty k aktuálně běžícímu skriptu
currentDir = os.path.dirname(os.path.realpath(__file__))
print(f"dirname: {currentDir}")
# Přidání této cesty do sys.path
sys.path.append(currentDir)
from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
from pprint import pprint
import pandas as pd

from common import findSubordinantFts, findSuperordinantFts, findAllOfType, getVehicleSpecTypes, getValuesForVehicleSpec, findCompatibility, setCompatibility, csvPath, restoreHeaderInCSV

print("Initiating Compatibility GUI...")

dialogSetCompatibility = gui.Dialog(caption="Set compatibility")

def SetCompatibilityGUI(initiator,typ, hierarchyOfTypes, parts, partInfo):
    global dialogSetCompatibility
    boxesParents = []
    boxesSubordinants = []
    boxesVehicleSpec = []
    rada1 = ()
    rada2 = ()
    tableOfParents = {}
    tableOfSubordinants = {}
    tableOfSpecTypes = {}

    print(parts)

    def onCancelCompatibilityGUI():
        dialogSetCompatibility.Hide()
        global tableOfParents
        global tableOfSubordinants
        tableOfParents = {}
        tableOfSubordinants = {}
        initiator.show()

    boxesVehicleSpec = getVehicleSpecTypes(hierarchyOfTypes)
    boxesParents = findSuperordinantFts(hierarchyOfTypes, typ, [])
    boxesSubordinants = findSubordinantFts(hierarchyOfTypes, typ, [])

    def createTable(type, spec=False):
        root = gui.TableCellData(headers=[{'text': 'Part'}, {'text': 'Position'}])
        row = 0
        partList = getValuesForVehicleSpec(parts, type, removeEmpty=True) if spec else findAllOfType(parts,None, type, removeEmpty=True)
        for part in partList:
            if partInfo.get("partName", None):
                compatibilityValue = findCompatibility(parts, partInfo["partName"], part)
            else:
                compatibilityValue = '1'

            root.setData(row, 0, value=part, type='string', state='disabled')
            root.setData(row, 1, value=compatibilityValue, type='string', state='enabled')
            row += 1

        table = gui.TableView()
        model = gui.TableDataModel(root, parent=table)
        delegate = gui.TableDelegate(parent=table)
        table.SetItemDelegate(delegate)
        sortFilterModel = gui.TableSortFilterModel(model)
        table.model = sortFilterModel
        return table

    def goThruTable(table, parts, partName):
        print(f"celldata: {table.model.model.root.celldata}")
        # print(table.model.model.root.getData())
        print(f"len(celldata): {len(table.model.model.root.celldata)}")
        for row in table.model.model.root.celldata:
            print(f"row: {row}")
            print(f"len(row): {len(row)}")
            if len(row) > 0:
                compatibilityWith = row[0].get('value', None)
                newValue = row[1].get('value', None)
                print(f"compatibilityWith: {compatibilityWith}-{newValue}")
                parts = setCompatibility(parts, partName, compatibilityWith, newValue)
        return parts

    def forAllTables(parts, partName):
        for ft, table in tableOfSpecTypes.items():
            parts = goThruTable(table, parts, partName)

        for ft, table in tableOfParents.items():
            parts = goThruTable(table, parts, partName)

        for ft, table in tableOfSubordinants.items():
            parts = goThruTable(table, parts, partName)

        return parts

    def editCompatibilityInDB(event, parts, partInfo):

        parts = forAllTables(parts, partInfo.get("partName",""))

        print(parts)
        parts.to_csv("N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility_2.csv")
        restoreHeaderInCSV(csvPath)

    def addPartToDB(event, parts, partInfo):
        print(f"parts in addPartToDB:{parts}")
        print(f"partInfo.values(): {partInfo.values()}")
        new_row_df = pd.DataFrame(pd.NA, index=[tuple(partInfo.values())], columns=parts.columns)
        print(f"new_row_df: {new_row_df}")
        parts = pd.concat([parts, new_row_df], axis=0)
        print(f"1:{parts}")
        parts = forAllTables(parts, partInfo.get("partName",""))
        print(f"2:{parts}")
        last_row = parts.iloc[-1]
        last_index = parts.index[-1]

        ft_columns = [col for col in parts.columns if col[0] == 'ft']
        last_row_ft = last_row[ft_columns]

        new_column_name = ("ft", last_index[0], last_index[1])

        # Přidání nového sloupce s daty z posledního řádku
        parts[new_column_name] = pd.NA
        print(f"3:{parts}")
        parts.iloc[:-1, parts.columns.get_loc(new_column_name)] = last_row_ft.values
        print(f"4:{parts}")
        print(parts)
        # TODO: Změnit cestu
        parts.to_csv("N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility_2.csv")
        restoreHeaderInCSV(csvPath)

    for specType in boxesVehicleSpec:
        labelObject = gui.Label(text=f'{specType}')
        tableOfSpecTypes[specType] = createTable(specType, spec=True)

        rada1 = rada1 + (labelObject, 10,)
        rada2 = rada2 + (tableOfSpecTypes[specType], 10,)

    rada1 = rada1[:-1]
    rada2 = rada2[:-1]
    specTypeLabel = gui.Label(text=f'Vehicle Specification', font={'bold': True})
    VehicleSpecFrame = gui.VFrame(specTypeLabel, rada1, rada2)
    rada1 = ()
    rada2 = ()


    for parent in boxesParents:
        labelObject = gui.Label(text=f'{parent}')
        if parent not in getVehicleSpecTypes(hierarchyOfTypes):
            tableOfParents[parent] = createTable(parent)
        else:
            continue

        rada1 = rada1 + (labelObject, 10,)
        rada2 = rada2 + (tableOfParents[parent], 10,)

    rada1 = rada1[:-1]
    rada2 = rada2[:-1]
    superior_label = gui.Label(text=f'Superordinates', font={'bold': True})
    parentsFrame = gui.VFrame(superior_label, rada1, rada2, "<->")
    rada1 = ()
    rada2 = ()

    for subordinate in boxesSubordinants:
        labelObject = gui.Label(text=f'{subordinate}')
        tableOfSubordinants[subordinate] = createTable(subordinate)

        rada1 = rada1 + (labelObject, 10,)
        rada2 = rada2 + (tableOfSubordinants[subordinate], 10,)

    rada1 = rada1[:-1]
    rada2 = rada2[:-1]
    subordinatesLabel = gui.Label(text=f'Subordinates', font={'bold': True})
    subordinatesFrame = gui.VFrame(subordinatesLabel, rada1, rada2, "<->")
    rada1 = ()
    rada2 = ()

    global compatibilityGuiFrame

    cancel  = gui.Button('Cancel', command=onCancelCompatibilityGUI)


    print(f"initiator: {initiator.caption}")

    if initiator.caption == "Edit Part":
        confirm = gui.Button('Edit in DB', command=lambda event: editCompatibilityInDB(event, parts))
    elif initiator.caption == "Add Part":
        confirm = gui.Button('Add to DB', command=lambda event: addPartToDB(event, parts, partInfo))

    sepVertical = gui.Separator(orientation='vertical', spacing='20')
    sepHorizontal1 = gui.Separator(orientation='horizontal', spacing='2')
    sepHorizontal2 = gui.Separator(orientation='horizontal', spacing='3')

    print(partInfo)

    label_partName = gui.Label(text=f"{partInfo.get('partName', '---')} -", font={'bold': True})
    label_partType = gui.Label(text=partInfo.get("partType", "---"), font={'bold': True})
    label_os =       gui.Label(text=f"|  {os.path.basename(partInfo.get('optistruct') or '---')}")
    label_radioss =  gui.Label(text=f"|  {os.path.basename(partInfo.get('radioss') or '---')}")

    labelFrame = gui.HFrame(label_partName, label_partType, label_os, label_radioss, "<->")

    parentsAndSubordinatesFrame = gui.HFrame(parentsFrame, sepVertical, subordinatesFrame)
    compatibilityGuiFrame = gui.VFrame(labelFrame, sepHorizontal1, VehicleSpecFrame, sepHorizontal2, parentsAndSubordinatesFrame, (800, confirm, cancel))

    dialogSetCompatibility.recess().add(compatibilityGuiFrame)

    dialogSetCompatibility.setButtonVisibile('ok', False)
    dialogSetCompatibility.setButtonVisibile('cancel', False)
    dialogSetCompatibility.show(width=900, height=500)

def showCompatibilityGUI(initiator, typ, hierarchyOfTypes, parts, partInfo):
    global dialogSetCompatibility
    dialogSetCompatibility = gui.Dialog(caption="Set compatibility")
    SetCompatibilityGUI(initiator,typ, hierarchyOfTypes, parts, partInfo)