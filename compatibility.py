import os
import sys
# Get path to currently running script
currentDir = os.path.dirname(os.path.realpath(__file__))
# Add path to sys.path
sys.path.append(currentDir)
import logger
import hwui
from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
from pprint import pprint
import pandas as pd

from common import findSubordinantFts, findSuperordinantFts, findAllOfType, getVehicleSpecTypes, getValuesForVehicleSpec, findCompatibility, setCompatibility, paths, restoreHeaderInCSV

logger.debug("Initiating Compatibility GUI...")

dialogSetCompatibility = gui.Dialog(caption="Set compatibility")

def SetCompatibilityGUI(initiator,typ, hierarchyOfTypes, parts, partInfo):
    global dialogSetCompatibility
    global compatibilityGuiFrame
    boxesParents = []
    boxesSubordinants = []
    boxesVehicleSpec = []
    rada1 = ()
    rada2 = ()
    tableOfSuperordinates = {}
    tableOfSubordinants = {}
    tableOfSpecTypes = {}
    button_0 = {}
    button_1 = {}

    logger.debug(parts)

    def onCancelCompatibilityGUI():
        dialogSetCompatibility.Hide()
        global tableOfSuperordinates
        global tableOfSubordinants
        global tableOfSpecTypes
        tableOfSuperordinates = {}
        tableOfSubordinants = {}
        tableOfSpecTypes = {}
        button_0 = {}
        button_1 = {}
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
                compatibilityValue = findCompatibility(parts, partInfo.get("oldName",partInfo["partName"]), part)
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
        # logger.debug(f"celldata: {table.model.model.root.celldata}")
        # logger.debug(table.model.model.root.getData())
        # logger.debug(f"len(celldata): {len(table.model.model.root.celldata)}")
        for row in table.model.model.root.celldata:
            # logger.debug(f"row: {row}")
            # logger.debug(f"len(row): {len(row)}")
            if len(row) > 0:
                compatibilityWith = row[0].get('value', None)
                newValue = row[1].get('value', None)
                logger.debug(f"compatibilityWith: {compatibilityWith}-{newValue}")
                parts = setCompatibility(parts, partName, compatibilityWith, newValue)
        return parts

    def forAllTables(parts, partName):
        for ft, table in tableOfSpecTypes.items():
            parts = goThruTable(table, parts, partName)

        for ft, table in tableOfSuperordinates.items():
            parts = goThruTable(table, parts, partName)

        for ft, table in tableOfSubordinants.items():
            parts = goThruTable(table, parts, partName)

        return parts

    def editCompatibilityInDB(event, parts, partInfo):

        # Edit index
        positionIndex = next((i for i, tup in enumerate(parts.index) if tup[1] == partInfo["oldName"]), None)
        new_index = (partInfo["partType"], partInfo["partName"], partInfo["optistruct"], partInfo["radioss"])
        index_tuples = parts.index.tolist()
        index_tuples[positionIndex] = new_index
        parts.index = pd.MultiIndex.from_tuples(index_tuples, names=parts.index.names)

        # Edit header
        positionHeader = next((i for i, col in enumerate(parts.columns) if col[2] == partInfo["oldName"]), None)
        new_header =("ft", partInfo["partType"], partInfo["partName"])
        columns_tuples = parts.columns.tolist()
        columns_tuples[positionHeader] = new_header
        logger.debug(f"columns_tuples: {columns_tuples}")
        logger.debug(f"parts.columns.names: {parts.columns.names}")
        parts.columns = pd.MultiIndex.from_tuples(columns_tuples, names=parts.columns.names)

        # Edit values
        parts = forAllTables(parts, partInfo["partName"])

        # Move row values to column
        logger.debug(f"positionIndex: {positionIndex}")
        logger.debug(f"positionHeader: {positionHeader}")
        row = parts.iloc[positionIndex]
        logger.debug(f"row.values: {row.values}")
        ft_columns = [col for col in parts.columns if col[0] == 'ft']
        logger.debug(f"ft_columns: {ft_columns}")
        row_ft = row[ft_columns]
        logger.debug(row_ft.values)
        logger.debug(parts.iloc[:, positionHeader].values)
        parts.iloc[:, positionHeader] = row_ft.values

        # Write down
        logger.debug(parts)
        parts.to_csv(paths["csv"])
        restoreHeaderInCSV(paths["csv"])

        dialogSetCompatibility.hide()
        gui2.tellUser("Successfully edited")


    def addPartToDB(event, parts, partInfo):
        logger.debug(f"parts in addPartToDB:{parts}")
        logger.debug(f"partInfo.values(): {partInfo.values()}")
        new_row_df = pd.DataFrame(pd.NA, index=[tuple(partInfo.values())], columns=parts.columns)
        logger.debug(f"new_row_df: {new_row_df}")
        parts = pd.concat([parts, new_row_df], axis=0)
        logger.debug(f"1:{parts}")
        parts = forAllTables(parts, partInfo.get("partName",""))
        logger.debug(f"2:{parts}")
        last_row = parts.iloc[-1]
        last_index = parts.index[-1]

        ft_columns = [col for col in parts.columns if col[0] == 'ft']
        last_row_ft = last_row[ft_columns]

        new_column_name = ("ft", last_index[0], last_index[1])

        # Přidání nového sloupce s daty z posledního řádku
        parts[new_column_name] = pd.NA
        logger.debug(f"3:{parts}")
        parts.iloc[:-1, parts.columns.get_loc(new_column_name)] = last_row_ft.values
        logger.debug(f"4:{parts}")
        logger.debug(parts)
        parts.to_csv(paths["csv"])
        restoreHeaderInCSV(paths["csv"])


        dialogSetCompatibility.hide()
        gui2.tellUser("Successfully added")

    def setValuesInTable(event, table, value):
        for row in table.model.model.root.celldata:
            if len(row) > 0:
                row[1]["value"] = value
        model = table.model.model
        model.DataChanged(model.Index(0, 0, hwui.uiModelIndex()), model.Index(table.numRows() -1, table.numCols() - 1,  hwui.uiModelIndex()))
        return



    for specType in boxesVehicleSpec:
        labelObject = gui.Label(text=f'{specType}')
        tableOfSpecTypes[specType] = createTable(specType, spec=True)

        button_0[specType] = gui.Button('0', maxwidth=20, command=lambda event, t=tableOfSpecTypes[specType], value=0: setValuesInTable(event, t, value))
        button_1[specType] = gui.Button('1', maxwidth=20, command=lambda event, t=tableOfSpecTypes[specType], value=1: setValuesInTable(event, t, value))

        labelAndButtonsObject = gui.HFrame(labelObject, "<->", button_0[specType], button_1[specType])

        rada1 = rada1 + (labelAndButtonsObject, 10,)
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
            tableOfSuperordinates[parent] = createTable(parent)
        else:
            continue

        button_0[parent] = gui.Button('0', maxwidth=20, command=lambda event, t=tableOfSuperordinates[parent], value=0: setValuesInTable(event, t, value))
        button_1[parent] = gui.Button('1', maxwidth=20, command=lambda event, t=tableOfSuperordinates[parent], value=1: setValuesInTable(event, t, value))

        labelAndButtonsObject = gui.HFrame(labelObject,"<->", button_0[parent], button_1[parent])

        rada1 = rada1 + (labelAndButtonsObject, 10,)
        rada2 = rada2 + (tableOfSuperordinates[parent], 10,)


    rada1 = rada1[:-1]
    rada2 = rada2[:-1]
    superior_label = gui.Label(text=f'Superordinates', font={'bold': True})
    parentsFrame = gui.VFrame(superior_label, rada1, rada2)
    rada1 = ()
    rada2 = ()

    for subordinate in boxesSubordinants:
        labelObject = gui.Label(text=f'{subordinate}')
        tableOfSubordinants[subordinate] = createTable(subordinate)

        button_0[subordinate] = gui.Button('0', maxwidth=20, command=lambda event, t=tableOfSubordinants[subordinate], value=0: setValuesInTable(event, t, value))
        button_1[subordinate] = gui.Button('1', maxwidth=20, command=lambda event, t=tableOfSubordinants[subordinate], value=1: setValuesInTable(event, t, value))

        labelAndButtonsObject = gui.HFrame(labelObject, "<->", button_0[subordinate], button_1[subordinate])

        rada1 = rada1 + (labelAndButtonsObject, 10,)
        rada2 = rada2 + (tableOfSubordinants[subordinate], 10,)

    rada1 = rada1[:-1]
    rada2 = rada2[:-1]
    subordinatesLabel = gui.Label(text=f'Subordinates', font={'bold': True})
    subordinatesFrame = gui.VFrame(subordinatesLabel, rada1, rada2)
    rada1 = ()
    rada2 = ()

    cancel  = gui.Button('Cancel', command=onCancelCompatibilityGUI)


    logger.debug(f"initiator: {initiator.caption}")

    if initiator.caption == "Edit Part":
        confirm = gui.Button('Edit in DB', command=lambda event: editCompatibilityInDB(event, parts, partInfo))
        addNew = gui.Button('Add as new', command=lambda event: addPartToDB(event, parts, partInfo))
    elif initiator.caption == "Add Part":
        confirm = gui.Button('Add to DB', command=lambda event: addPartToDB(event, parts, partInfo))
        addNew = "<->"

    sepVertical = gui.Separator(orientation='vertical', spacing='20')
    sepHorizontal1 = gui.Separator(orientation='horizontal', spacing='2')
    sepHorizontal2 = gui.Separator(orientation='horizontal', spacing='3')

    logger.debug(partInfo)

    label_partName = gui.Label(text=f"{partInfo.get('partName', '---')} -", font={'bold': True})
    label_partType = gui.Label(text=partInfo.get("partType", "---"), font={'bold': True})
    label_os =       gui.Label(text=f"|  {os.path.basename(partInfo.get('optistruct') or '---')}")
    label_radioss =  gui.Label(text=f"|  {os.path.basename(partInfo.get('radioss') or '---')}")

    labelFrame = gui.HFrame(label_partName, label_partType, label_os, label_radioss, "<->")

    parentsAndSubordinatesFrame = gui.HFrame(parentsFrame, sepVertical, subordinatesFrame)
    compatibilityGuiFrame = gui.VFrame(labelFrame, sepHorizontal1, VehicleSpecFrame, sepHorizontal2, parentsAndSubordinatesFrame, (800, confirm, 5, addNew, 5, cancel))

    dialogSetCompatibility.recess().add(compatibilityGuiFrame)

    dialogSetCompatibility.setButtonVisibile('ok', False)
    dialogSetCompatibility.setButtonVisibile('cancel', False)
    dialogSetCompatibility.show(width=900, height=800)

def showCompatibilityGUI(initiator, typ, hierarchyOfTypes, parts, partInfo):
    global dialogSetCompatibility
    dialogSetCompatibility = gui.Dialog(caption="Set compatibility")
    SetCompatibilityGUI(initiator,typ, hierarchyOfTypes, parts, partInfo)