from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import os
import itertools
from functools import partial
import csv

def MyCustomGui():

        csv_file = 'N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv'

        # Method called on clicking 'Close'.
        def onClose(event):
                dialog.Hide ()

        def onRun(event):
                dialog.Hide ()
                postprocAuto(modelFile.value, resultFile.value, folderSel.value)
                gui2.tellUser('Done!')
                
        def onReset(event):
                vyber_rear_end.setValues(najdi_vsechny_daneho_typu("rear"))
                vyber_rear_end.set("---")
                vyber_middle_part.setValues(najdi_vsechny_daneho_typu("middle"))
                vyber_middle_part.set("---")
                vyber_front_end.setValues(najdi_vsechny_daneho_typu("front"))
                vyber_front_end.set("---")
                vyber_front_accessories.clear()
                updateLabelyCest()
                
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
                cesta_rear_end.text = vyber_rear_end.value
                cesta_middle_part.text = vyber_middle_part.value
                cesta_front_end.text = vyber_front_end.value
                
        def updateListFrontAccessories():
                print(vyber_front_end.value)
                print(najdiLabelPodleCesty(vyber_front_end.value))
                print(najdi_kompatibilni_radky(najdiLabelPodleCesty(vyber_front_end.value), "front_accessories", True))
                
                vyber_front_accessories.clear()
                vyber_front_accessories.append(najdi_kompatibilni_radky(najdiLabelPodleCesty(vyber_front_end.value), "front_accessories", True))
                
      
        
        def onSelectedMiddle(event):
                rear_value = vyber_rear_end.value
                vyber_rear_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "rear"))
                if rear_value in vyber_rear_end.values : vyber_rear_end.set(rear_value)
                front_value = vyber_front_end.value
                vyber_front_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "front"))
                if front_value in vyber_front_end.values : vyber_front_end.set(front_value)
                updateLabelyCest()
                updateListFrontAccessories()

                
        def onSelectedRear(event):
                middle_value = vyber_middle_part.value
                vyber_middle_part.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "middle"))
                if middle_value in vyber_middle_part.values : vyber_middle_part.set(middle_value)
                front_value = vyber_front_end.value
                vyber_front_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(vyber_middle_part.value), "front"))
                if front_value in vyber_front_end.values : vyber_front_end.set(front_value)
                updateLabelyCest()
                updateListFrontAccessories()
                
        def onSelectedFront(event):
                middle_value = vyber_middle_part.value
                vyber_middle_part.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "middle"))
                if middle_value in vyber_middle_part.values : vyber_middle_part.set(middle_value)
                rear_value = vyber_rear_end.value
                vyber_rear_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(vyber_middle_part.value), "rear"))
                if rear_value in vyber_rear_end.values : vyber_rear_end.set(rear_value)
                updateLabelyCest()
                updateListFrontAccessories()
                
                

        #rear_possibilities_1 =     (("rear11","rear11"), ("rear12","rear12"),("rear13","rear13"),("-empty-","-empty-"))
        #rear_possibilities_2 =     (("rear21","rear21"), ("rear22","rear22"),("rear23","rear23"),("-empty-","-empty-"))
        #middle_possibilities =     (("middle1","middle1"), ("middle2","middle2"),("middle3","middle3"),("-empty-","-empty-"))
        #front_possibilities =      (("front1","front1"), ("front3","front3"),("front3","front3"),("-empty-","-empty-"))
        na_strechu_possibilities = (("na strechu 1","na strechu 1"), ("na strechu 2","na strechu 2"),("-empty-","-empty-"))    

        label_na_strechu     = gui.Label(text='Na strechu')
        vyber_na_strechu     = gui2.ComboBox(na_strechu_possibilities)                
        label_rear_end       = gui.Label(text='Rear End')
        vyber_rear_end       = gui2.ComboBox(najdi_vsechny_daneho_typu("rear"), command=onSelectedRear)
        cesta_rear_end       = gui2.Label("---", font=dict(size=8, italic=True))
        label_middle_part    = gui.Label(text='Middle Part')
        vyber_middle_part    = gui2.ComboBox(najdi_vsechny_daneho_typu("middle"), command=onSelectedMiddle)
        cesta_middle_part    = gui2.Label("---", font=dict(size=8, italic=True))
        label_front_end      = gui.Label(text='Front End')
        vyber_front_end      = gui2.ComboBox(najdi_vsechny_daneho_typu("front"),command=onSelectedFront)
        cesta_front_end      = gui2.Label("---", font=dict(size=8, italic=True))
        obrazek              = gui.Label(icon='N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/bus.png')
        
        close  = gui.Button  ('Close', command=onClose)
        create = gui.Button  ('Run', command=onRun)
        reset  = gui.Button  ('Reset', command=onReset)
        
        label_front_accessories     = gui.Label(text='Front accessories')
        vyber_front_accessories     = gui2.ListBox(selectionMode="ExtendedSelection")


        mainFrame = gui.VFrame (
                (350, label_na_strechu, 350),
                (350, vyber_na_strechu, 350),
                (900, label_front_accessories),
                (150, obrazek, 10, vyber_front_accessories),
                (5),
                (label_rear_end, 10, label_middle_part, 10, label_front_end),
                (vyber_rear_end, 10, vyber_middle_part, 10, vyber_front_end),
                (cesta_rear_end, 10, cesta_middle_part, 10, cesta_front_end),
                (15),
                (500,create,reset,close)
        )

        dialog = gui.Dialog(caption  = "Bus configuration")
        dialog.recess().add(mainFrame)
        dialog.setButtonVisibile('ok',False)
        dialog.setButtonVisibile('cancel',False)
        dialog.show(width=1000, height=500)
        
        print(vyber_front_end.labels)
        
        

        



