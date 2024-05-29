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

from common import findPathToIncludeFile, getWidgetStructure, \
    getWidgetVehicleSpecStructure, saveSetup, loadSetup, resetModelEdit, importParts, hierarchyOfTypes, tclPath, \
    findCompatibleParts, findAllOfType, getValuesForVehicleSpec, findTypeOfPart

print("Initiating...")

parts = importParts()

# Slovník pro uchování vytvořených widgetů
widgetyModelEdit = {}

dialogModelEdit = gui.Dialog(caption="Bus model edit")


selectedSolver = 2 #2-optistruct, 3-radioss - it corresponds to column in csv, where first is index, second is type but it s columnt No. 0, then is OptiStruct as No.1,...
solverInterface = ['"OptiStruct" {}', '"RadiossBlock" "Radioss2023"']

columnWidth = 230

# TODO: Move include after import

def modelEditGui():
    global dialogModelEdit
    global selectedSolver

    # Method called on clicking 'Close'.
    def onCloseModelBuildup(event):
        dialogModelEdit.hide()


    # Method called on clicking 'Build-up'.
    def onEditModel(event):
        # TODO upravit pro edit
        # TODO myslet na to, že se musí porovnávat nově vybrané položky proti listu existujícíchc includů a pokud něco přebývá, tak nahrát, pokud něco chybí, tak smazat

        global selectedSolver
        print(f"BuildUp")
        print(f"selectedSolver: {selectedSolver}")
        print(f"solverInterface: {solverInterface[selectedSolver - 2]}")
        # Using "changing_interface_finished; vwait global_variable" is necessary because of bug in HyperMesh which continues in next Tcl commands before the Solver Interface is completely changed
        hw.evalTcl(f'source "{tclPath}"; set change_finished false; ::UserProfiles::LoadUserProfile {solverInterface[selectedSolver - 2]} changing_interface_finished; vwait change_finished')
        hw.evalTcl(f'*start_batch_import 2')

        print("ending batch import")
        hw.evalTcl(f'puts "Going to end batch import"')
        hw.evalTcl(f'*end_batch_import')
        print("realizing connectors")
        hw.evalTcl(f'source "{tclPath}"; realize_connectors')
        onCloseModelBuildup(None)
        gui2.tellUser('Model build-up has finished!')
        dialogModelEdit = gui.Dialog(caption="Bus model edit")

    # Method called on clicking 'Reset'.
    def onResetModelBuildup(event):
        global selectedSolver
        resetModelEdit(event, widgetyModelEdit, selectedSolver, parts)
        return

    def loadCurrentIncludes():
        listOfIncludes = hw.evalTcl(f"hm_getincludes -byshortname").split()
        for include in listOfIncludes:
            partType = findTypeOfPart(parts, include)
            print(f"include-type: {include}-{partType}")
            try:
                widgetyModelEdit[f'vyber_{partType}'].set(include)
            #     TODO zohlednit i multiselect
            except:
                print(f"{partType} nenalezen")
                pass


        return

    close = gui.Button('Close', command=onCloseModelBuildup)
    buildup = gui.Button('Edit model', command=lambda event: onEditModel(event))
    reset = gui.Button('Reset', command=onResetModelBuildup)


    vehicleSpecFrame = gui.HFrame(
        getWidgetVehicleSpecStructure(hierarchyOfTypes["groups"]["vehicle_spec"], hierarchyOfTypes, parts,
                                      widgetyModelEdit, selectedSolver), container=True, maxwidth=500)

    widgetStructure, columns = getWidgetStructure(hierarchyOfTypes["groups"]["FT groups"], hierarchyOfTypes, parts, selectedSolver,
                                                  widgetyModelEdit)

    loadCurrentIncludes()

    widgetFrame = gui.HFrame(widgetStructure, container=True, )
    widgetFrame.maxheight = widgetFrame.reqheight

    mainFrame = gui.VFrame(
        vehicleSpecFrame,
        15,
        widgetFrame,
        15,
        ("<->", buildup, reset, close)
    )


    dialogModelEdit.recess().add(mainFrame)

    dialogModelEdit.setButtonVisibile('ok', False)
    dialogModelEdit.setButtonVisibile('cancel', False)

    # mainFrame.move(x = 1, y = 1)

    width = columns * columnWidth
    height = widgetFrame.maxheight + 100

    return width, height

width, height = modelEditGui()
def mainFunc(*args, **kwargs):
    global dialogModelEdit
    dialogModelEdit.show(width=width, height=height)
    print("Initiated...")

if __name__ == "__main__":
    mainFunc()
