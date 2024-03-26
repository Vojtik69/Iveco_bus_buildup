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

        with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
            hierarchie_typu = yaml.safe_load(file)

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

        def extractAllNames(data):
            names = []
            for item in data:
                names.append([item['name'],item['multiselection']])
                if 'subordinates' in item:
                    names.extend(extractAllNames(item['subordinates']))
            return names

        def findParent(data, target_name, parent=None):
            for item in data:
                if item['name'] == target_name:
                    return parent
                elif 'subordinates' in item:
                    result = findParent(item['subordinates'], target_name, item)
                    if result is not None:
                        return result

        def getSubordinantsNames(hierarchie_typu, node_name, descendants=[]):
            node = najit_prvek_podle_hodnoty(hierarchie_typu, node_name)
            try:
                for subordinate in node['subordinates']:
                    descendants.append([subordinate['name'], subordinate['multiselection']])
                    if subordinate['skippable']:
                        getSubordinantsNames([subordinate], subordinate['name'],descendants)
            except Exception as e: print(e)
            return descendants

        # Method called on clicking 'Close'.
        def onClose(event):
                dialog.Hide ()

        def onRun(event):
                dialog.Hide ()
                gui2.tellUser('Done!')
                
        def onReset(event):
                for [typ,multiselection] in extractAllNames(hierarchie_typu):
                    if multiselection:
                        widgety[f'vyber_{typ}'].clear()
                    else:
                        widgety[f'vyber_{typ}'].setValues(najdi_vsechny_daneho_typu(typ))
                        widgety[f'vyber_{typ}'].value = "---"
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
            for [typ,multiselection] in extractAllNames(hierarchie_typu):
                try:
                    widgety[f'cesta_{typ}'].text = widgety[f'vyber_{typ}'].value
                except:
                    pass

        def onSelectedCombo(event):
            widgety[f'cesta_{event.widget.name}'].text = widgety[f'vyber_{event.widget.name}'].value
            subordinants = getSubordinantsNames(hierarchie_typu, event.widget.name,[])
            for [typ, multiselection] in subordinants:
                if widgety[f'vyber_{event.widget.name}'].value == "---":
                    if najit_prvek_podle_hodnoty(hierarchie_typu, event.widget.name).get("skippable",False):
                        parent = findParent(hierarchie_typu, event.widget.name)
                        if multiselection:
                            widgety["vyber_" + typ].clear()
                            widgety["vyber_" + typ].append(
                                najdi_kompatibilni_radky(najdiLabelPodleCesty(widgety[f'vyber_{parent["name"]}'].value),
                                                         typ),True)
                        else:
                            widgety["vyber_" + typ].setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(widgety[f'vyber_{parent["name"]}'].value), typ, True))
                    else:
                        if multiselection:
                            widgety["vyber_" + typ].clear()
                            widgety["vyber_" + typ].append(najdi_vsechny_daneho_typu(typ))
                        else:
                            widgety["vyber_" + typ].setValues(najdi_vsechny_daneho_typu(typ))
                else:
                    if multiselection:
                        widgety["vyber_" + typ].clear()
                        widgety["vyber_" + typ].append(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), typ, True))
                    else:
                        widgety["vyber_"+typ].setValues(najdi_kompatibilni_radky(najdiLabelPodleCesty(event.value), typ))
                        widgety[f'cesta_{typ}'].text = widgety[f'vyber_{typ}'].value

        obrazek              = gui.Label(icon='N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/bus.png')
        
        close  = gui.Button  ('Close', command=onClose)
        create = gui.Button  ('Run', command=onRun)
        reset  = gui.Button  ('Reset', command=onReset)

        # Slovník pro uchování vytvořených widgetů
        widgety = {}

        # Vytvoř widgety
        for [typ,multiselection] in extractAllNames(hierarchie_typu):
            if multiselection:
                label_objekt = gui.Label(text=f'{typ.capitalize()}')
                vyber_objekt = gui2.ListBox(selectionMode="ExtendedSelection", name=typ)

                # Uložení objektů do slovníku
                widgety[f'label_{typ}'] = label_objekt
                widgety[f'vyber_{typ}'] = vyber_objekt
            else:
                label_objekt = gui.Label(text=f'{typ.capitalize()}')
                vyber_objekt = gui2.ComboBox(najdi_vsechny_daneho_typu(typ), command=onSelectedCombo, name=typ)
                cesta_objekt = gui2.Label("---", font=dict(size=8, italic=True))

                # Uložení objektů do slovníku
                widgety[f'label_{typ}'] = label_objekt
                widgety[f'vyber_{typ}'] = vyber_objekt
                widgety[f'cesta_{typ}'] = cesta_objekt

        # Napolohuj Widgety
        mainFrame = gui.VFrame (
                    (350, widgety['label_na_strechu'], 350),
                    (350, widgety['vyber_na_strechu'], 350),
                    (900, widgety['label_front_accessories']),
                    (150, obrazek, 10, widgety['vyber_front_accessories']),
                    (5),
                    (widgety['label_rear'], 10, widgety['label_prodluzovaci'], 10, widgety['label_middle'], 10, widgety['label_front']),
                    (widgety['vyber_rear'], 10, widgety['vyber_prodluzovaci'], 10, widgety['vyber_middle'], 10, widgety['vyber_front']),
                    (widgety['cesta_rear'], 10, widgety['cesta_prodluzovaci'], 10, widgety['cesta_middle'], 10, widgety['cesta_front']),
                    (15),
                    (500,create,reset,close)
            )

        dialog = gui.Dialog(caption  = "Bus model buildup")
        dialog.recess().add(mainFrame)
        dialog.setButtonVisibile('ok',False)
        dialog.setButtonVisibile('cancel',False)
        dialog.show(width=1000, height=500)

        
        

        



