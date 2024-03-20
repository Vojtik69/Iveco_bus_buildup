from hw import *
from hw.hv import *
from hwx.xmlui import gui
from hwx import gui as gui2
import os
import itertools
from functools import partial
import csv

def MyCustomGui():

        # Method called on clicking 'Close'.
        def onClose(event):
                dialog.Hide ()

        def onRun(event):
                dialog.Hide ()
                postprocAuto(modelFile.value, resultFile.value, folderSel.value)
                gui2.tellUser('Done!')
                
        def LoadCompatibility(file, row_name):
                with open(file, 'r', newline='') as file:
                    reader = csv.reader(file, delimiter=';')
                    matrix = list(reader)
                    
                    headers = matrix[0]  # Predpokládáme, že první rádek obsahuje hlavicky sloupcu
                    
                    # Najít index rádku se zadaným názvem
                    row_index = None
                    for i, row in enumerate(matrix):
                        if i != 0 and row[0] == row_name:
                            row_index = i
                            break
                    
                    if row_index is None:
                        return []  # Pokud rádek není nalezen, vrátit prázdný seznam
                    
                    row = matrix[row_index]
                    
                    nonzero_columns = ()  # Inicializovat n-tici
                    for i in range(1, len(row)):  # Zacít indexování od 1
                        if row[i] != '0':  # Zkontrolovat, zda hodnota není '0'
                            nonzero_columns += (headers[i],)  # Pridat název sloupce do n-tice
                    nonzero_columns += ("-empty-",)

                    return nonzero_columns
        
        
        def onSelectedMiddle(event):
                vyber_rear_end.setValues(MiddleFrontCompatibility('C:/Users/Vojtech Rulc/Desktop/middle-rear.csv',event.value))
                vyber_front_end.setValues(MiddleFrontCompatibility('C:/Users/Vojtech Rulc/Desktop/middle-front.csv',event.value))
                

        #rear_possibilities_1 =     (("rear11","rear11"), ("rear12","rear12"),("rear13","rear13"),("-empty-","-empty-"))
        #rear_possibilities_2 =     (("rear21","rear21"), ("rear22","rear22"),("rear23","rear23"),("-empty-","-empty-"))
        middle_possibilities =     (("middle1","middle1"), ("middle2","middle2"),("middle3","middle3"),("-empty-","-empty-"))
        #front_possibilities =      (("front1","front1"), ("front3","front3"),("front3","front3"),("-empty-","-empty-"))
        na_strechu_possibilities = (("na strechu 1","na strechu 1"), ("na strechu 2","na strechu 2"),("-empty-","-empty-"))    

        label_na_strechu     = gui.Label(text='Na strechu')
        vyber_na_strechu     = gui2.ComboBox(na_strechu_possibilities)                
        label_rear_end       = gui.Label(text='Rear End')
        vyber_rear_end       = gui2.ComboBox()
        label_middle_part    = gui.Label(text='Middle Part')
        vyber_middle_part    = gui2.ComboBox(middle_possibilities, command=onSelectedMiddle)
        label_front_end      = gui.Label(text='Front End')
        vyber_front_end      = gui2.ComboBox()

        close  = gui.Button  ('Close', command=onClose)
        create = gui.Button  ('Run', command=onRun)


        mainFrame = gui.VFrame (
                (350, label_na_strechu, 350),
                (350, vyber_na_strechu, 350),
                (label_rear_end, 10, label_middle_part, 10, label_front_end),
                (vyber_rear_end, 10, vyber_middle_part, 10, vyber_front_end),
                (15),
                (create,close)
        )

        dialog = gui.Dialog(caption  = "Bus configuration")
        dialog.recess().add(mainFrame)
        dialog.setButtonVisibile('ok',False)
        dialog.setButtonVisibile('cancel',False)
        dialog.show(width=1000, height=100)


