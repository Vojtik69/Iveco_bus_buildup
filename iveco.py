from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import os
import itertools
from functools import partial
import csv
import yaml

def MyCustomGui():

        csv_file = 'N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv'
        typy_combo = ["rear", "prodluzovaci", "middle", "front", "na_strechu", ]
        typy_list = ["front_accessories", ]

        with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
            hierarchie_typu = yaml.safe_load(file)

        def najdi_potomky_prvni_generace(hierarchie, rodic):
            return hierarchie.get(rodic, [])

        print(najdi_potomky_prvni_generace(hierarchie_typu, 'middle'))

        # Method called on clicking 'Close'.
        def onClose(event):
                dialog.Hide ()

        def onRun(event):
                dialog.Hide ()
                gui2.tellUser('Done!')
                
        def onReset(event):
                # vyber_rear_end.setValues(najdi_vsechny_daneho_typu("rear"))
                # vyber_rear_end.set("---")
                # vyber_middle_part.setValues(najdi_vsechny_daneho_typu("middle"))
                # vyber_middle_part.set("---")
                # vyber_front_end.setValues(najdi_vsechny_daneho_typu("front"))
                # vyber_front_end.set("---")
                # vyber_front_accessories.clear()
                # updateLabelyCest()
                pass
                
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
                # cesta_rear_end.text = vyber_rear_end.value
                # cesta_middle_part.text = vyber_middle_part.value
                # cesta_front_end.text = vyber_front_end.value
                pass
                
        def updateListFrontAccessories():
                # print(vyber_front_end.value)
                # print(najdiLabelPodleCesty(vyber_front_end.value))
                # print(najdi_kompatibilni_radky(najdiLabelPodleCesty(vyber_front_end.value), "front_accessories", True))
                #
                # vyber_front_accessories.clear()
                # vyber_front_accessories.append(najdi_kompatibilni_radky(najdiLabelPodleCesty(vyber_front_end.value), "front_accessories", True))
                pass
      
        
        # def onSelectedMiddle(event):
        #         rear_value = vyber_rear_end.value
        #         vyber_rear_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "rear"))
        #         if rear_value in vyber_rear_end.values : vyber_rear_end.set(rear_value)
        #         front_value = vyber_front_end.value
        #         vyber_front_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "front"))
        #         if front_value in vyber_front_end.values : vyber_front_end.set(front_value)
        #         updateLabelyCest()
        #         updateListFrontAccessories()
        #
        #
        # def onSelectedRear(event):
        #         middle_value = vyber_middle_part.value
        #         vyber_middle_part.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "middle"))
        #         if middle_value in vyber_middle_part.values : vyber_middle_part.set(middle_value)
        #         front_value = vyber_front_end.value
        #         vyber_front_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(vyber_middle_part.value), "front"))
        #         if front_value in vyber_front_end.values : vyber_front_end.set(front_value)
        #         updateLabelyCest()
        #         updateListFrontAccessories()
        #
        # def onSelectedFront(event):
        #         print(event.widget.name)
        #         middle_value = vyber_middle_part.value
        #         vyber_middle_part.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "middle"))
        #         if middle_value in vyber_middle_part.values : vyber_middle_part.set(middle_value)
        #         rear_value = vyber_rear_end.value
        #         vyber_rear_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(vyber_middle_part.value), "rear"))
        #         if rear_value in vyber_rear_end.values : vyber_rear_end.set(rear_value)
        #         updateLabelyCest()
        #         updateListFrontAccessories()

        def onSelectedCombo(event):

                # event.widget.name
                # rear_value = vyber_rear_end.value
                # vyber_rear_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "rear"))
                # if rear_value in vyber_rear_end.values : vyber_rear_end.set(rear_value)
                # front_value = vyber_front_end.value
                # vyber_front_end.setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), "front"))
                # if front_value in vyber_front_end.values : vyber_front_end.set(front_value)
                # updateLabelyCest()
                # updateListFrontAccessories()
                pass
                
        obrazek              = gui.Label(icon='N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/bus.png')
        
        close  = gui.Button  ('Close', command=onClose)
        create = gui.Button  ('Run', command=onRun)
        reset  = gui.Button  ('Reset', command=onReset)

        # Slovník pro uchování vytvořených widgetů
        widgety = {}

        # Vytvoř widgety
        for typ in typy_combo:
            label_objekt = gui.Label(text=f'{typ.capitalize()}')
            vyber_objekt = gui2.ComboBox(najdi_vsechny_daneho_typu(typ), command=onSelectedCombo, name=typ)
            cesta_objekt = gui2.Label("---", font=dict(size=8, italic=True))

            # Uložení objektů do slovníku
            widgety[f'label_{typ}'] = label_objekt
            widgety[f'vyber_{typ}'] = vyber_objekt
            widgety[f'cesta_{typ}'] = cesta_objekt

        for typ in typy_list:
            label_objekt = gui.Label(text=f'{typ.capitalize()}')
            vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=typ)

            # Uložení objektů do slovníku
            widgety[f'label_{typ}'] = label_objekt
            widgety[f'vyber_{typ}'] = vyber_objekt

        # Napolohuj Widgety
        mainFrame = gui.VFrame (
                    (350, widgety['label_na_strechu'], 350),
                    (350, widgety['vyber_na_strechu'], 350),
                    (900, widgety['label_front_accessories']),
                    (150, obrazek, 10, widgety['vyber_front_accessories']),
                    (5),
                    (widgety['label_rear'], 10, widgety['label_middle'], 10, widgety['label_front']),
                    (widgety['vyber_rear'], 10, widgety['vyber_middle'], 10, widgety['vyber_front']),
                    (widgety['cesta_rear'], 10, widgety['cesta_middle'], 10, widgety['cesta_front']),
                    (15),
                    (500,create,reset,close)
            )

        dialog = gui.Dialog(caption  = "Bus model buildup")
        dialog.recess().add(mainFrame)
        dialog.setButtonVisibile('ok',False)
        dialog.setButtonVisibile('cancel',False)
        dialog.show(width=1000, height=500)

        
        

        



