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

from common import findSubordinantFts, findSuperordinantFts, findAllOfType, getVehicleSpecTypes, getValuesForVehicleSpec, findCompatibility

print("Initiating Compatibility GUI...")

dialogSetCompatibility = gui.Dialog(caption="Set compatibility")

def SetCompatibilityGUI(typ, hierarchyOfTypes, parts, partName=None):
    global dialogSetCompatibility
    boxesParents = []
    boxesSubordinants = []
    boxesVehicleSpec = []
    rada1 = ()
    rada2 = ()
    tableOfParents = {}
    tableOfSubordinants = {}
    tableOfSpecTypes = {}

    def onCancelCompatibilityGUI():
        dialogSetCompatibility.Hide()
        global tableOfParents
        global tableOfSubordinants
        tableOfParents = {}
        tableOfSubordinants = {}

    boxesVehicleSpec = getVehicleSpecTypes(hierarchyOfTypes)
    boxesParents = findSuperordinantFts(hierarchyOfTypes, typ, [])
    boxesSubordinants = findSubordinantFts(hierarchyOfTypes, typ, [])

    def createTable(type, spec=False):
        root = gui.TableCellData(headers=[{'text': 'Part'}, {'text': 'Position'}])
        row = 0
        partList = getValuesForVehicleSpec(parts, type, removeEmpty=True) if spec else findAllOfType(parts,None, type, removeEmpty=True)
        for part in partList:
            if partName:
                compatibilityValue = findCompatibility(parts, partName, part)
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
    confirm = gui.Button('Confirm')

    sepVertical = gui.Separator(orientation='vertical', spacing='20')
    sepHorizontal = gui.Separator(orientation='horizontal', spacing='3')

    upperFrame = gui.HFrame(parentsFrame, sepVertical, subordinatesFrame)
    compatibilityGuiFrame = gui.VFrame(VehicleSpecFrame, sepHorizontal, upperFrame, (800, confirm, cancel))

    dialogSetCompatibility.recess().add(compatibilityGuiFrame)

    dialogSetCompatibility.setButtonVisibile('ok', False)
    dialogSetCompatibility.setButtonVisibile('cancel', False)
    dialogSetCompatibility.show(width=900, height=500)

def showCompatibilityGUI(typ, hierarchyOfTypes, parts, partName=None):
    global dialogSetCompatibility
    dialogSetCompatibility = gui.Dialog(caption="Set compatibility")
    SetCompatibilityGUI(typ, hierarchyOfTypes, parts, partName)