import sys
import logging 


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def log(msg, level='error'): 
    logging.__dict__[level](f' -- {datetime.now()} -- {msg}')

    if level == 'error':
        sys.exit("Stop het programma hier")
        
try:
    from imports import import_modules
except ImportError as e:
    log(f"Kon import_modules niet importeren uit imports.py error: {e}")

i, error = import_modules('main.py', ["pathlib","os","pandas","fitz","io","datetime","flask","waitress","tkinter","customtkinter","PIL","pytesseract","time","importlib","copy","subprocess","pysoem","functions"])

if error:
    log('check which imports are missing')

Path            = i['pathlib'].Path
os              = i['os']
pd              = i['pandas']
fitz            = i['fitz']
io              = i['io']
datetime        = i['datetime'].datetime
flask           = i['flask']
serve           = i['waitress'].serve
tkinter         = i['tkinter']
customtkinter   = i['customtkinter']
Image           = i['PIL'].Image
pytesseract     = i['pytesseract']
time            = i['time']
importlib       = i['importlib']
deepcopy        = i['copy'].deepcopy
subprocess      = i['subprocess']
pysoem          = i['pysoem']
fc              = i['functions']

render_template     = flask.render_template
send_from_directory = flask.send_from_directory


class Progression():
    def __init__(self, T):
        self.t = T
        self.get_config()

    def get_config(self):
        self.config = fc.yamlOperator('defauld/config', 'progression.yaml')      


class Schematic():
    def __init__(self, T):
        self.t = T
        self.get_config()
        self.order_id = 4553 #self.tkinter(self.config['order_id_request_text'], 'int')

        self.curr_page = 0
        self.curr_background = None 
        self.curr_kast = None 
        self.curr_eiland = None 
        self.curr_machine_type = None 

        self.page_index = 0 

        self.curr_rack = None 
        self.curr_io = None 

        self.next_button = True 
        self.prev_button = True       

        self.jpg_X_pixels = 1197.2099 #None #horizontaal
        self.jpg_Y_pixels = 882.567 #None #verticaal 
        self.zoom_ratio = 1

        self.sections = [] 

        self.page_X_pixels = None  #None #horizontaal
        self.page_Y_pixels = None  #None #verticaal 
    
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
        self.alignment_elements = [] 

    def to_percent(self, x, y):
        return round(x / self.page_X_pixels * 100, 2), round(y / self.page_Y_pixels * 100, 2)

    def get_config(self):
        self.config = fc.yamlOperator('defauld/config', 'schematic.yaml')      
    
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


        self.export_rack = self.export_rack[self.export_rack['kaart_type'].isin(self.t.io.supported_cards)]
        self.export_io = self.export_io[self.export_io['kaart_id'].isin(self.export_rack['kaart_id'])]

        pattern = r'=(?P<machine_type>[^+]+)\+(?P<kast_nr>[^/]+)/(?P<pagina_nr>\d+)(?:\.(?P<pagina_section>\d+))?'

        self.export_io.loc[:, ['machine_type', 'kast_nr', 'pagina_nr', 'pagina_section']] = (self.export_io['pagina_nr'].str.extract(pattern))
        self.export_io.loc[:, 'pagina_nr'] = self.export_io['pagina_nr'].astype('int64')
        self.export_io.loc[:, 'pagina_section'] = self.export_io['pagina_section'].astype('int64')

        self.kast_list = self.export_rack['kast_nr'].unique().tolist()

        x_pos = self.config['page_section']['X_pos']
        max_steps = sum(x_pos)
        pix_step = self.jpg_X_pixels / max_steps
        pix_count = 0 
        
        for i in range(len(x_pos)):
            pix_count += x_pos[i] * pix_step

            pix_begin = 0 if i == 0 else self.sections[-1]['end']
            pix_end = pix_count 
            self.sections.append({'begin':pix_begin, 'end':pix_end})


    def set_page_elements(self):
        self.lamp_elements.clear()
        self.button_elements.clear()
        self.text_elements.clear()
        self.input_elements.clear()

        df = self.curr_io[self.curr_io['pagina_nr'].isin([self.curr_page])]
        elemens_added = [0] * len(self.sections)

        for row in df.itertuples():
            card = self.t.io.configuration[self.curr_eiland][row.kaart_id]

            if card.is_defauld == True:
                continue
            
            section_index = row.pagina_section
            section_separations = (df['pagina_section'] == section_index).sum() + 1 
            section = self.sections[section_index]
            elemens_added[section_index] += 1 

            x = (section['begin'] + (((section['end'] - section['begin']) / section_separations) * elemens_added[section_index])) * self.zoom_ratio
            y = self.config['page_section']['Y_pos'] * self.zoom_ratio

            _id = card.element_type + str(len(self.__dict__[card.element_type +'_elements']) ) 

            if card.element_type == 'lamp':
                self.lamp_elements.append({"id": _id, "label": "Lamp1 "+ str(section_index), "x": x, "y": y, "color": "red"})

            elif card.element_type == 'button':
                self.button_elements.append({"label": str(section_index), "x": x, "y": y, "param": "btn1"}) 

            elif card.element_type == 'text':
                self.text_elements.append({"id": _id, "label": "Status: OK", "x": x, "y": y})

            elif card.element_type == 'input':
                self.input_elements.append({"label": _id, "x": x, "y": y, "name": "username"}) 
            


    def set_page(self, set_new_kast= False, eiland= None):
        render_columns = ['curr_background', 'page_X_pixels', 'page_Y_pixels','curr_kast','curr_eiland','curr_page','kast_list','page_list','lamp_elements','next_button','prev_button','button_elements','text_elements','input_elements'] 
        
        if self.curr_kast == None:
                self.curr_kast = self.kast_list[0]
                set_new_kast = True  

        if set_new_kast:
            self.curr_eiland = 0

            self.curr_rack = self.export_rack[self.export_rack['kast_nr'].isin([self.curr_kast])]
            self.curr_io = self.export_io[self.export_io['kast_nr'].isin([self.curr_kast])]

            self.curr_rack = self.curr_rack.reset_index(drop=True)
            self.curr_io = self.curr_io.reset_index(drop=True)

            self.page_list = self.curr_io['pagina_nr'].unique().tolist()
            self.page_list.sort()

            self.curr_machine_type = self.curr_rack.at[0, 'machine_type']

            self.page_index = 0 
            self.prev_button = False 
        
            self.page_min_range = 0  
            self.page_max_range = len(self.page_list)

            self.t.io.get_configuration(self.curr_rack)            


        if not eiland is None:
            self.curr_eiland = eiland

        self.curr_page = self.page_list[self.page_index]
        self.set_page_elements()

        format_elements = {'machine_type': self.curr_machine_type, 'kast_nr': self.curr_kast, 'pagina_nr': self.page_list[self.page_index]}
        self.curr_background = fc.formatOperator(self.config['export_schematic']['jpg_format'], format_elements) + ".jpg"  

        render = {}
        for key in render_columns:
            if not self.__dict__.get(key) is None:
                render[key] = self.__dict__[key]
            else:
                log('Missing key in set_page key: ', key)

        return render 


class Beckhoff():
    def __init__(self, T):
        self.t = T
        self.get_config()
        sys.path.append("beckhoff/cards")

        self.master = pysoem.Master()

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
        self.config = fc.yamlOperator('defauld/config', 'beckhoff.yaml')      

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
    
    def get_adapters(self, busid=None, search_term="Ethernet"):
        """
        Attach een USB device aan WSL via usbipd.
        - busid: direct het busid opgeven (bijv. '2-3')
        - search_term: zoekterm om automatisch busid te vinden
        """
        try:
            
            # Zoek automatisch naar het busid via usbipd list
            cmd_list = [
                "powershell.exe",
                "-Command",
                "usbipd list | Select-String '{}'".format(search_term)    
            ]

            result = subprocess.run(cmd_list, capture_output=True, text=True)

            if result.returncode != 0 or not result.stdout.strip():
                print("Geen USB device gevonden met zoekterm:", search_term)
                return False
            
            # Eerste kolom is het busid
            busid = result.stdout.strip().split()[0]

            # Attach uitvoeren
            cmd_attach = [
                "powershell.exe",
                "-Command",
                f"usbipd bind --busid {busid}"
            ]#f"usbipd attach --wsl --busid {busid}"
            
            result = subprocess.run(cmd_attach, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"USB device {busid} gekoppeld aan WSL.")
                return True
            else:
                print("Fout bij koppelen:", result.stderr)
                return False

        except Exception as e:
            print("Error:", e)
            return False


class IO_Tester():
    def __init__(self, name, debug_mode= False):
        self.system_oke = False 
        self.system_default = True 
        self.system_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = None 

        if hasattr(sys, "_MEIPASS"):
            self.resource_path = Path(sys._MEIPASS)
        else:
            self.resource_path = self.system_path

        self.check_system()

        #self.sch    = Schematic(self)
        #self.io     = Beckhoff(self)
        #self.pro    = Progression(self)
        #self.app    = flask.Flask(name)

        #self.get_config()

        #self.io.get_adapters(search_term="Realtek USB GbE Family Controller #3")
         #--disable exports--
        #self.get_progress_id()
        #self.sch.get_imports(self.progress_path)

        #--disable server--
        #self.routing()
        #self.app.run(debug=debug_mode)
    
    def check_system(self):
        system_folders = ({'beckhoff/cards': ['EL1xxx.py','EL2xxx.py'],
                           'default/config': ['beckhoff.yaml','IOTester.yaml','progression.yaml','schematic.yaml'],
                           'default/export/excel': ['V4553  IO lijst.xlsx','V4553  Rack opbouw.xlsx'],
                           'default/export/schematic': ['V4553 00.1.pdf'],

                           'static/css': ['end_page.css','home_page.css','schematic_page.css'],
                           'static/js': ['home_page.js','schematic_page.js'],
                           'templates': ['end_page.html','home_page.html','schematic_page.html'],
                            })
        config_folders = ({'config': ['beckhoff.yaml','IOTester.yaml','progression.yaml','schematic.yaml']})


        system_oke = fc.check_folders(self.resource_path, system_folders)

        if not system_oke:
            log('Het systeem is niet oke. Check logs')

        self.system_default = fc.check_folders(self.system_path, system_folders)
        
        if not self.system_default:
            log('System is running in defauld', level='info')


        
    


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
        
        @self.app.route("/progression/<name>")
        def progression(name):
            if name == 'save':
                return render_template('home_page.html') 

            render = self.sch.set_page()
            return render_template('schematic_page.html', **render) 
        
        @self.app.route("/page_correction/<correction>")
        def page_correction(correction):
            self.sch.page_index += int(correction)  
            self.sch.next_button = True if self.sch.page_index < (len(self.sch.page_list) -1) else False  
            self.sch.prev_button = True if self.sch.page_index > 0 else False      
    
            render = self.sch.set_page() #page_correction=int(correction)
            return render_template('schematic_page.html', **render) 
        
        @self.app.route("/zoom/<ratio>")
        def zoom(ratio):
            self.sch.zoom_ratio += float(ratio)
            self.sch.page_X_pixels = self.sch.jpg_X_pixels * self.sch.zoom_ratio
            self.sch.page_Y_pixels = self.sch.jpg_Y_pixels * self.sch.zoom_ratio
            render = self.sch.set_page()
            return render_template('schematic_page.html', **render) 
        
        @self.app.route("/link")
        def link():
            render = self.sch.set_page()
            return render_template('schematic_page.html', **render)
        
        @self.app.route("/defauld/saved_progress/progress0/schematic_jpg/<filename>")
        def schematic_images(filename):
            return send_from_directory("defauld/saved_progress/progress0/schematic_jpg", filename)
        
        @self.app.route("/dynamic_button/<name>")
        def dynamic_button(name):
            render = self.sch.set_page()
            return render_template('schematic_page.html', **render)

        @self.app.route("/dynamic_input/<name>", methods=["POST"])
        def dynamic_input(name):
            text = flask.request.form.get(name)
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
            return flask.jsonify({"lamps": lamps, "texts": texts})
        
        @self.app.route("/list_picker/<name>")
        def list_picker(name):
            render, new_item = None, flask.request.args.get("value")
    
            if name == 'kast':
                self.sch.curr_kast = new_item
                print('kast: ', self.sch.curr_kast)
                render = self.sch.set_page(set_new_kast=True)

            elif name == 'page':
                self.sch.page_index = self.sch.page_list.index(int(new_item))
                render = self.sch.set_page()
    
            return render_template('schematic_page.html', **render)
        
if __name__ == '__main__':
    IO_Tester(__name__)    





