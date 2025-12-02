import pandas as pd
import yaml 
import functions as fc 
import fitz
import io
import numpy as np 

from datetime import datetime 

from flask import Flask, render_template, send_from_directory, jsonify, request
from waitress import serve

from tkinter import *
import customtkinter

from PIL import Image
import pytesseract #https://www.geeksforgeeks.org/python/introduction-to-python-pytesseract-package/

import logging
import time 
import sys
import importlib
from copy import deepcopy

#pip install qrcode
#Ctrl+Shift+P


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
    def __init__(self, T):
        self.t = T
        self.get_config()

    def get_config(self):
        self.config = fc.yamlOperator('config', 'progression.yaml')      


class Schematic():
    def __init__(self, T):
        self.t = T
        self.get_config()
        self.order_id = 4553 #self.tkinter(self.config['order_id_request_text'], 'int')

        self.curr_page = 0
        self.curr_background = None 
        self.curr_kast = None 
        self.curr_eiland = None 
        self.page_index = 0 

        self.curr_rack = None 
        self.curr_io = None 

        self.next_button = True 
        self.prev_button = True 

        self.page_X_pixels = 1200 #None #horizontaal
        self.page_Y_pixels = 800 #None #verticaal 

        self.page_min_range = None 
        self.page_max_range = None 

        self.export_rack        = None 
        self.export_io          = None 

        self.kast_list = [] 
        self.page_list = []         

        self.lamp_elements = []
        self.button_elements = []
        self.text_elements = []
        self.input_elements = []

    def to_percent(self, x, y):
        return round(x / self.page_X_pixels * 100, 2), round(y / self.page_Y_pixels * 100, 2)

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

    
    def dataframe_filter(df, ):
        pass
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


        self.export_rack = self.export_rack[self.export_rack['kaart_type'].isin(self.t.io.supported_cards)]
        self.export_io = self.export_io[self.export_io['kaart_id'].isin(self.export_rack['kaart_id'])]

        pattern = r'=(?P<machine_type>[^+]+)\+(?P<kast_nr>[^/]+)/(?P<pagina_nr>\d+)(?:\.(?P<pagina_section>\d+))?'

        self.export_io.loc[:, ['machine_type', 'kast_nr', 'pagina_nr', 'pagina_section']] = (self.export_io['pagina_nr'].str.extract(pattern))
        self.kast_list = self.export_rack['kast_nr'].unique().tolist()

    def set_page_elements(self):
        self.lamp_elements.clear()
        self.button_elements.clear()
        self.text_elements.clear()
        self.input_elements.clear()
        print('set_page_elements')

        df = self.curr_io[self.curr_io['pagina_nr'].isin([self.curr_page])]

        defauld_x = [100, 200, 300, 400, 500, 600, 700, 800] 
        defauld_y = 500

        for row in df.itertuples():
            card = self.t.io.configuration[self.curr_eiland][row.kaart_id]

            if card.is_defauld == True:
                continue
            
            x = defauld_x[int(row.pagina_section)]
            y = defauld_y     
            _id = card.element_type + str(len(self.__dict__[card.element_type +'_elements']))
    

            if card.element_type == 'lamp':
                self.lamp_elements.append({"id": _id, "label": "Lamp1", "x": x, "y": y, "color": "red"})
                print('lamp added')
            elif card.element_type == 'button':
                self.button_elements.append({"label": _id, "x": x, "y": y, "route": "dynamic_button", "param": "btn1"})
                print('button added')

            elif card.element_type == 'text':
                self.text_elements.append({"id": _id, "label": "Status: OK", "x": x, "y": y})
            elif card.element_type == 'input':
                self.input_elements.append({"label": _id, "x": x, "y": y, "route":"dynamic_input", "name": "username"})
            
 

    def set_page(self, page_correction= None, kast= None, eiland= None):
        render_columns = ['curr_background','curr_kast','curr_eiland','curr_page','page_min_range','page_max_range','kast_list','page_list','lamp_elements','button_elements','text_elements','input_elements'] 

        if self.curr_kast is None or not kast is None:
            self.curr_kast = self.kast_list[0] #moet ik nog aanpassen als kast niet none is 
            self.curr_eiland = 0

            self.curr_rack = self.export_rack[self.export_rack['kast_nr'].isin([self.curr_kast])]
            self.curr_io = self.export_io[self.export_io['kast_nr'].isin([self.curr_kast])]

            self.curr_rack = self.curr_rack.reset_index(drop=True)
            self.curr_io = self.curr_io.reset_index(drop=True)

            self.page_list = self.curr_io['pagina_nr'].unique().tolist()
            self.page_index = 0 
            self.page_min_range = 0  
            self.page_max_range = len(self.page_list)

            self.t.io.get_configuration(self.curr_rack)            

        if not page_correction is None:
            self.page_index += page_correction

        if not eiland is None:
            self.curr_eiland = eiland

        self.curr_page = self.page_list[self.page_index]
        self.set_page_elements()

        df = self.curr_io.iloc[self.page_index]
        format_elements = {'machine_type': df['machine_type'], 'kast_nr': df['kast_nr'], 'pagina_nr': df['pagina_nr']}
        self.curr_background = fc.formatOperator(self.config['export_schematic']['jpg_format'], format_elements) + ".jpg"  # "saved_progress/progress0/schematic_jpg/" +   #%machine_type%_%kast_nr%_%pagina_nr%'
        

        render = {}
        for key in render_columns:
            if not self.__dict__.get(key) is None:
                render[key] = self.__dict__[key]
            else:
                log('Missing key in set_page')

        
        return render 


class Beckhoff():
    def __init__(self, T):
        self.t = T
        self.get_config()
        sys.path.append("beckhoff/cards")

        self.cards = []
        self.supported_cards = []
        self.configuration = [] 

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

    def get_configuration(self, curr_rack):
        self.configuration.clear()
        self.identifier = [] 

        for row in curr_rack.itertuples():
            page = row.kaart_id.split('A')[0]
            identifier = page[0]

            if self.identifier.count(identifier) == 0:
                self.identifier.append(identifier)
                self.configuration.append({})

            index = self.identifier.index(identifier)
            if self.supported_cards.count(row.kaart_type) > 0:
                for card in self.cards:
                    if card.supported.count(row.kaart_type) > 0:
                        self.configuration[index][row.kaart_id] = deepcopy(card)
            else:
                class NotSupported:
                    def __init__(self):
                        self.is_defauld = True 
                self.configuration[index][row.kaart_id] = NotSupported()


class IO_Tester():
    def __init__(self, name):
        
        self.sch    = Schematic(self)
        self.io     = Beckhoff(self)
        self.pro    = Progression(self)
        self.app    = Flask(name)

        self.get_config()
        self.get_progress_id()

        self.sch.get_imports(self.progress_path)

        self.routing()
        self.app.run(debug=True)
        

    def get_config(self):
        self.config = fc.yamlOperator('config', 'IOTester.yaml')      


    def get_progress_id(self):
        dir_list = fc.dirOperator('saved_progress', make=False, returnList=True)

        self.progress_id, resume_process = len(dir_list), False 

        for dir_ in dir_list:
            info = fc.yamlOperator('saved_progress' + '/' + dir_, 'info.yaml')  
            if info['order_id'] == self.sch.order_id:
                self.progress_id = info['progress_id']
                resume_process = True 
                break 

        self.progress_path = 'saved_progress/progress' + str(self.progress_id)

        if not resume_process:            
            fc.dirOperator(self.progress_path)
            info = {'progress_id':self.progress_id, 'order_id':self.sch.order_id, 'last_updated':datetime.now().strftime('%d/%m/%y')}
            fc.yamlOperator(self.progress_path, 'info.yaml', info)


    def routing(self):

        @self.app.route("/")
        def home_page():
            progression_status = 'laag'
            return render_template('home_page.html', progression=(progression_status == "hoog"))

        @self.app.route("/resume")
        def resume_progression():
            render = self.sch.set_page()
            return render_template('schematic_page.html', **render) 

        @self.app.route("/restart")
        def restart_progression():
            render = self.sch.set_page()
            return render_template('schematic_page.html', **render) 
        
        @self.app.route("/next_page")
        def next_page():
            render = self.sch.set_page(page_correction= 1)
            return render_template('schematic_page.html', **render) 
        
        @self.app.route("/prev_page")
        def prev_page():
            print('prev_page')
            render = self.sch.set_page(page_correction= -1)
            return render_template('schematic_page.html', **render) 
        
        @self.app.route("/link")
        def link():
            render = self.sch.set_page()
            return render_template('schematic_page.html', **render)
        
        @self.app.route("/save_progression")
        def save_progression():
            render = self.sch.set_page(page_correction= -1)
            return render_template('schematic_page.html', **render)
        
        @self.app.route("/saved_progress/progress0/schematic_jpg/<filename>")
        def schematic_images(filename):
            return send_from_directory("saved_progress/progress0/schematic_jpg", filename)
        
        @self.app.route("/dynamic_button/<name>")
        def dynamic_button(name):
            render = self.sch.set_page()
            return render_template('schematic_page.html', **render)

        @self.app.route("/dynamic_input/<name>", methods=["POST"])
        def dynamic_input(name):
            text = request.form.get(name)
            render = self.sch.set_page()
            return render_template('schematic_page.html', **render)
        
        @self.app.route("/dynamic_update")
        def dynamic_update():
            lamps = [
                {"id": "lamp0", "color": "red"}
            ]
            texts = [
                {"id": "text0", "value": "System OK"}
            ]
            return jsonify({"lamps": lamps, "texts": texts})
        
if __name__ == '__main__':
    IO_Tester(__name__)    





