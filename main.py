import pandas as pd
import yaml 
import functions as fc 
import fitz
import io
import numpy as np 

from datetime import datetime 

from flask import Flask, render_template, send_from_directory, request
from waitress import serve

from tkinter import *
import customtkinter

from PIL import Image
import pytesseract #https://www.geeksforgeeks.org/python/introduction-to-python-pytesseract-package/

import logging
import time 
import sys
import importlib

#pip install qrcode


logging.basicConfig(filename='log.log', level=logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(message)s')


def log(msg, level='error'): 
        levels = ['error', 'info']

        if levels.count(level) != 1:
            logging.error(f" -- {datetime.now()} -- level: {level} don't exist")
            return 

        logging.__dict__[level](f' -- {datetime.now()} -- {msg}')

        if level == 'error':
            while True:
                time.sleep(2)
                print(f'Fix before restart Error: {msg}')


class Progression():
    def __init__(self):
        self.get_config()

    def get_config(self):
        self.config = fc.yamlOperator('config', 'progression.yaml')      


class Schematic():
    def __init__(self):
        self.get_config()
        self.order_id = 4553 #self.tkinter(self.config['order_id_request_text'], 'int')

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
       
        for export_id in ['rack','io','schematic']:        
            config = self.config['export_' + export_id]
           
            for request in config['elements_to_request']:
                if list(elements_requested.keys()).count(request['variable']) == 1:
                    continue

                elements_requested[request['variable']] = self.tkinter(request['text'], request['variable_type'])
        
            file_list = fc.fileOperator(config['path'], True)
            
            for file in file_list:
                correct_file_selected = True 

                for item in config['file_elements']:
                    if file.count(item) == 0:
                        correct_file_selected = False 
               
                for item in config['file_exclude_elements']:
                    if file.count(item) == 1:
                        correct_file_selected = False 

                for item in config['elements_to_request']:                 
                    item = elements_requested[item['variable']]
                    if file.count(str(item)) == 0:
                        correct_file_selected = False 

                if not correct_file_selected:
                    continue

                if export_id == 'schematic':
                    continue
                    if not config['extension_type'] == '.pdf':
                        log('extension_type .pdf is only supported for the schematic')
                    
                    doc = fitz.open(config['path'] + '/' + file + '.pdf')

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
                        page_nr_text = pytesseract.image_to_string(cropped_im)

                        exclude_jpg = False 
                        for item in self.config['export_jpg']['pages_to_exclude']:
                            if page_nr_text.lower().count(item.lower()) > 0:
                                exclude_jpg = True 
                            
                        if exclude_jpg:
                            continue

                        format_items = fc.formatOperator(self.config['page_nr']['format'], formatToDecrypt=page_nr_text)

                        if format_items is None:
                            continue
                        
                        jpg_name = fc.formatOperator(self.config['export_jpg']['format'], format_items)
                        pix.save(progress_path + '/schematic_jpg/' + jpg_name +'.jpg')


                else:
                    if not config['extension_type'] == '.xlsx' and not config['extension_type'] == '.csv':
                        log('extension_type .xlsx or .csv is only supported for the rack or io export')

                    data = pd.__dict__['read_' + 'excel' if config['extension_type'] == '.xlsx' else '.csv'](config['path'] + '/' + file + config['extension_type'])

                    if not len(data.columns) == len(config['columns']):
                        log(f'The collumns of Export {export_id} and the pre defined columns of export_{export_id} are not of the same length')
                 
                    data.columns = config['columns']
                    self.__dict__['export_'+ export_id] = data


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
        sys.path.append("beckhoff/cards")

        self.cards = []
        self.supported_cards = []

        for card in fc.fileOperator('beckhoff/cards', True, False):
            card, extention = card.split('.')

            if not extention == 'py':
                continue
            
            module = importlib.import_module(card)
            card = getattr(module, card)()

            self.supported_cards += card.supported
            self.cards.append(card)


    def get_config(self):
        self.config = fc.yamlOperator('config', 'beckhoff.yaml')      


class IO_Tester():
    def __init__(self, schematic_class, io_class, progression_class, name):
        
        self.schematic      = schematic_class 
        self.io             = io_class 
        self.progression    = progression_class

        self.app = Flask(name)

        self.get_config()
        self.get_progress_id()

        self.schematic.get_imports(self.progress_path)
        self.filter_exports()
        
        self.kast_list = ['E1','E2','E3','E4'] 
        self.page_list = ['201', '202', '203'] 
        self.background_jpg = "saved_progress/progress0/schematic_jpg/BHS_E3_56.jpg"  # of relatieve URL

        self.routing()
        self.app.run(debug=True)
        


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


    def filter_exports(self):
        
        export_rack = self.schematic.export_rack
        export_rack = export_rack[export_rack['kaart_type'].isin(self.io.supported_cards)]

        export_io = self.schematic.export_io
        export_io = export_io[export_io['kaart_id'].isin(export_rack['kaart_id'])]

        self.schematic.export_rack  = export_rack
        self.schematic.export_io    = export_io


    def routing(self):
        #home routs 
        @self.app.route("/")
        def home_page():
            progression_status = 'laag'
            return render_template('home_page.html', progression=(progression_status == "hoog"))

        @self.app.route("/resume")
        def resume_progression():
            print("Resuming progression...")
            
            return render_template('schematic_page.html', kast_list=self.kast_list, page_list=self.page_list, background_path=self.background_jpg)

        @self.app.route("/restart")
        def restart_progression():
            print("Progression restarted!")
            kast_picker = ['E1','E2','E3','E4'] 
            return render_template('schematic_page.html', kast_list=self.kast_list, page_list=self.page_list, background_path=self.background_jpg)
        
        #schematic routs
        @self.app.route("/next_page")
        def next_page():
            print("next_page")
            kast_picker = ['E1','E2','E3','E4'] 
            return render_template('schematic_page.html', kast_list=self.kast_list, page_list=self.page_list, background_path=self.background_jpg)
        
        @self.app.route("/previous_page")
        def previous_page():
            print("previous_page")

            kast_picker = ['E1','E2','E3','E4'] 
            return render_template('schematic_page.html', kast_list=self.kast_list, page_list=self.page_list, background_path=self.background_jpg)
        

        @self.app.route("/saved_progress/progress0/schematic_jpg/<filename>")
        def schematic_images(filename):
            return send_from_directory("saved_progress/progress0/schematic_jpg", filename)

if __name__ == '__main__':
    IO_Tester(Schematic(), Beckhoff(), Progression(), __name__)    





