import pandas as pd
import yaml 
import functions as fc 
import fitz
import io
import numpy as np 

from datetime import datetime 

from flask import Flask, render_template, request
from waitress import serve

from tkinter import *
import customtkinter

from PIL import Image
import pytesseract #https://www.geeksforgeeks.org/python/introduction-to-python-pytesseract-package/





class Progression():
    def __init__(self):
        self.get_config()

    def get_config(self):
        self.config = fc.yamlOperator('config', 'progression.yaml')      


class Schematic():
    def __init__(self):
        self.get_config()
        self.order_id = self.tkinter(self.config['order_id_request_text'], 'int')

        self.curr_page = 0
        self.curr_kast = None 
        self.curr_eiland = None 

        self.pageMin = None 
        self.pageMax = None 

        self.page_X_pixels = None #horizontaal
        self.page_Y_pixels = None #verticaal 

        self.pageMinRange = None 
        self.pageMaxRange = None 

        self.export_rack        = None 
        self.export_io          = None 
        self.export_schematic   = None 


    def get_config(self):
        self.config = fc.yamlOperator('config', 'schematic.yaml')      
    
    def tkinter (self, text='', variable_type='str'):
        error = False 
        while True:
            customtkinter.set_appearance_mode('dark')
            customtkinter.set_default_color_theme('dark-blue')

            dialog = customtkinter.CTkInputDialog(text=text, title='IO Tester input command')
            user_input = dialog.get_input()

            try:
                if variable_type == 'int':
                    user_input = int(user_input)

            except:
                if not error:
                    text = 'Not of the correct type. Enter again: ' + text 
                    error = True 
                continue

            return user_input

    def get_imports(self, progress_path):
        elements_requested = {'order_id':self.order_id}
       
        for export in ['rack','io','schematic']:        
            key = 'export_' + export
            export = self.config[key]
           
            for request in export['elements_to_request']:
                if list(elements_requested.keys()).count(request['variable']) == 1:
                    continue

                elements_requested[request['variable']] = self.tkinter(request['text'], request['variable_type'])
        
            file_list = fc.fileOperator(export['path'], True)

            for file in file_list:
                correct_file_selected = True 

                for item in export['file_elements']:
                    if file.count(item) == 0:
                        correct_file_selected = False 
               
                for item in export['file_exclude_elements']:
                    if file.count(item) == 1:
                        correct_file_selected = False 

                for item in export['elements_to_request']:                 
                    item = elements_requested[item['variable']]
                    if file.count(str(item)) == 0:
                        correct_file_selected = False 

                if correct_file_selected:
                    if export['extension_type'] == '.xlsx':
                        self.__dict__[key] = pd.read_excel(export['path'] + '/' + file + '.xlsx')

                    elif export['extension_type'] == '.csv':
                        self.__dict__[key] = pd.read_csv(export['path'] + '/' + file + '.csv')

                    elif export['extension_type'] == '.pdf':
                        doc = fitz.open(export['path'] + '/' + file + '.pdf')

                        fc.dirOperator(progress_path + '/schematic_jpg')

                        for i, page in enumerate(doc):
                            pix = page.get_pixmap()

                            if self.page_X_pixels == None or self.page_Y_pixels == None:
                                rect = page.rect
                                self.page_X_pixels = rect.width
                                self.page_Y_pixels = rect.height
                            
         
                            box_page = self.config['box_page_nr']
  
                            image_bytes = pix.tobytes("ppm")
                            image = Image.open(io.BytesIO(image_bytes))
                            crop_rectangle = (box_page['Y_pos'], box_page['X_pos'], box_page['Y_pos'] + box_page['Y_length'], box_page['X_pos'] + box_page['X_length']) #(left, upper, right, lower)
                            cropped_im = image.crop(crop_rectangle)

                            cropped_im.show()
                            #pix.save(progress_path + '/schematic_jpg/E1_150_' + str(i) +'.jpg')
                            
                            text = pytesseract.image_to_string(cropped_im)

                            print(f'results: {text}')
                      

                    else:
                        print("error")

                    print(file)
            
            




        #filterd de imports rack opbouw en io lijst. 
        #convert schema pdf naar jpg bestand(en) 
        #per jpg een format maken met {kast, schema_pagina_Nr, pdf_pagina_Nr}





        
    
    def get_page_elements(self):
        #haal van de curr_page alle verwijzingen op naar een beckhoff kaart 
        pass 

    def set_selection_range(self):
        #set de range van de pagina`s wat te scrollen is. dit wordt bepaald door curr_kast / curr_eiland         
        pass 

    def decode_page_nr(self):
        #kijkt wat de pagina nummer is en welke kast de pagina is toegewezen 
        pass 


class Beckhoff():
    def __init__(self):
        self.get_config()

    def get_config(self):
        self.config = fc.yamlOperator('config', 'beckhoff.yaml')      


class IO_Tester():
    def __init__(self, schematic_class, beckhoff_class, progression_class):
        self.schematic      = schematic_class 
        self.beckhoff       = beckhoff_class 
        self.progression    = progression_class

        #file_list = fc.fileOperator('C:/Users/Hacker/OneDrive/Bureaublad/Ethercat I_O tester V2.0/export/schematic', True)
        #print(file_list)
        self.get_config()
        self.get_progress_id()
        self.schematic.get_imports(self.progress_path)



        #1. !!!
            #vragen naar de gegevens zoals {orderNr} 
            #controleren of de gegevens aanwezig zijn 

            #opbouwen van de html server 
            #QR code projecteren om te verbinden tablet 
            #vragen gegevens op main screen zoals {orderNr}


    def get_config(self):
        self.config = fc.yamlOperator('config', 'IOTester.yaml')      

    def get_progress_id(self):
        dir_list = fc.dirOperator('saved_progress', make=False, returnList=True)

        self.progress_id, resume_process = len(dir_list), False 

        for dir_ in dir_list:
            info = fc.yamlOperator('saved_progress' + '/' + dir_, 'info.yaml')  
            if info['order_id'] == self.schematic.order_id:
                self.progress_id = info['progress_id']
                resume_process = True 
                break 

        self.progress_path = 'saved_progress/progress' + str(self.progress_id)

        if not resume_process:            
            fc.dirOperator(self.progress_path)
            info = {'progress_id':self.progress_id, 'order_id':self.schematic.order_id, 'last_updated':datetime.now().strftime('%d/%m/%y')}
            fc.yamlOperator(self.progress_path, 'info.yaml', info)

        



if __name__ == '__main__':
    IO_Tester(Schematic(), Beckhoff(), Progression())    





