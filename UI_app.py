from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import traceback, sys
import os
import yaml
import time
import numpy as np

from Utils import *
from Visual_stimuli import stim_calculator


####################################################################################################################
####################################################################################################################

class Main_UI(QWidget):
    def __init__(self):
        """
        Initialise variables to control GUI behaviour
        Initialise multi threading
        Call functions that create widgets and take care of the styling the GUI
        start MAIN loop
        """
        super().__init__()
        # Display silent exceptions that cause the gui to crash [Doesn't work all the time]
        sys._excepthook = sys.excepthook
        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback)
            sys.exit(1)
        sys.excepthook = exception_hook
        # ==============================================================================
        # ==============================================================================
        # Load parameters from config file
        config_path = 'C:\\Users\\Federico\\Documents\\GitHub\\VisualStimuli\\GUI_cfg.yml'
        self.settings = load_yaml(config_path)

        # Initialise variables
        self.prepared_stimuli = {}
        self.current_stim_params_displayed = None
        self.ignored_params = ['name', 'units', 'type', 'modality', 'Stim type']  # Stim parameters with these will not be displayed
        # in the gui, they will have to be edited in the yaml files

        # Flags to handle stim generation
        """
        stim on            - stim currently being played
        stim               - reference to stimulus object
        stim_frames        - array of frames that are used to update stim
        stim_frame_number  - keep track of progess when looping through stim_frames
        """
        self.stim_on = False
        self.stim, self.stim_frames, self.stim_frame_number = None, False, False

        # ==============================================================================
        # START MULTITHREDING
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # Create GUI UI
        self.create_widgets()
        self.define_layout()
        self.define_style_sheet()

        # Call Main Loop - on a separate thread
        # Start a thread that continously checks the parameters and refreshes the window
        main_loop_worker = Worker(self.main_loop)
        self.threadpool.start(main_loop_worker)

        # Load parameters YAML files
        self.get_stims_yaml_files_from_folder()

    ####################################################################################################################
    """    DEFINE THE LAYOUT AND LOOKS OF THE GUI  """
    ####################################################################################################################

    def create_widgets(self):
        # Take care of the layout
        self.grid = QGridLayout()
        self.grid.setSpacing(25)

        # Available yml file
        self.params_files_label = QLabel('Parameter files')

        self.param_files_list = QListWidget()
        self.param_files_list.itemDoubleClicked.connect(self.load_stim_params_from_list_widget)

        # Loaded stims
        self.laoded_stims_label = QLabel('Loaded stims')

        self.loaded_stims_list = QListWidget()
        self.loaded_stims_list.currentItemChanged.connect(self.update_params_widgets)
        self.loaded_stims_list.itemDoubleClicked.connect(self.remove_loaded_stim_from_widget_list)

        # current open stim
        self.filename_edit = QLineEdit('Params file - not loaded -')

        # Dictionary with handles to parameters widgets - the widgets are created in self.define_layout()
        self.params_widgets_dict = {}

        # Bg Luminosity and delay
        self.bg_label = QLabel('Background Luminosity')
        self.bg_label.setObjectName('BaseParam')
        self.bg_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.bg_edit = QLineEdit('255')
        self.bg_edit.setObjectName('BaseParam')
        self.bg_luminosity = 255

        self.delay_label = QLabel('Delay')
        self.delay_label.setObjectName('BaseParam')
        self.delay_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.delay_edit = QLineEdit('0')
        self.delay_edit.setObjectName('BaseParam')

        # Append bg and delay stuff to parameters dictionary
        param = {self.bg_label.text(): [self.bg_label, self.bg_edit]}
        self.params_widgets_dict[self.bg_label.text()] = param
        param = {self.delay_label.text(): [self.delay_label, self.delay_edit]}
        self.params_widgets_dict[self.delay_label.text()] = param

        # Launch btn
        self.launch_btn = QPushButton(text='Launch')
        self.launch_btn.clicked.connect(self.launch_stim)

        # Load and save btn
        self.load_btn = QPushButton(text='Load')
        self.load_btn.clicked.connect(self.load_stim_params_from_list_widget)

        self.remove_btn = QPushButton(text='Remove')
        self.remove_btn.clicked.connect(self.remove_loaded_stim_from_widget_list)

        self.save_btn = QPushButton(text='Save')
        self.save_btn.clicked.connect(self.save_params_yaml_file)

        # Benchmark btn
        self.bench_btn = QPushButton(text='Bench Mark')
        self.bench_btn.clicked.connect(self.nofunc)

    def define_layout(self):
        # Available yml files
        self.grid.addWidget(self.params_files_label, 0, 0)

        self.grid.addWidget(self.param_files_list, 1, 0, 10, 1)

        # Loaded stims
        self.grid.addWidget(self.laoded_stims_label, 0, 1,)

        self.grid.addWidget(self.loaded_stims_list, 1, 1, 10, 1)

        # Current open stim
        self.grid.addWidget(self.filename_edit, 0, 2, 1, 2)

        for i in range(10):
            if i < 2:
                continue
            # Create empty parameter fields
            lbl = QLabel('Empty param')
            lbl.setObjectName('ParamName')
            lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            entry = QLineEdit('Empty edit')
            entry.setObjectName('ParamValue')
            entry.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # Add them to the dictionary
            param = {lbl.text(): [lbl, entry]}
            if i == 2:
                self.params_widgets_dict['Stim Type'] = param
            else:
                self.params_widgets_dict['Param {}'.format(i)] = param

            # Set their location
            self.grid.addWidget(lbl, 1+i, 2, 1 , 1)
            self.grid.addWidget(entry, 1+i, 3, 1 , 1)

        # Bg Luminosity and delay
        self.grid.addWidget(self.bg_label, 1, 2)
        self.grid.addWidget(self.delay_label, 2, 2)
        self.grid.addWidget(self.bg_edit, 1, 3)
        self.grid.addWidget(self.delay_edit, 2, 3)

        # Launch btn
        self.grid.addWidget(self.launch_btn, 14, 0, 1 ,4)
        self.launch_btn.setObjectName('LaunchBtn')

        # Load and save btn
        self.grid.addWidget(self.load_btn, 13, 0, 1, 1)
        self.grid.addWidget(self.remove_btn, 13, 1, 1, 1)
        self.grid.addWidget(self.save_btn, 13, 2, 1, 2)

        # Finalise layout
        self.setLayout(self.grid)
        self.setContentsMargins(50, 10, 10, 25)
        self.setGeometry(100, 100, 1000, 1800)
        self.setWindowTitle('Review')

        # Benchamrk btn
        self.grid.addWidget(self.bench_btn, 15, 0, 1 ,4)
        self.bench_btn.setObjectName('BennchBtn')


        self.show()

    def define_style_sheet(self):
        # Main window color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(40, 40, 40, 255))
        self.setPalette(p)

        # Widgets style sheet
        self.setStyleSheet("""
                    QPushButton {
                        color: #ffffff;
                        background-color: #565656;
                        border: 2px solid #8f8f91;
                        border-radius: 6px;
                        min-width: 80px;
                        min-height: 40px;
                    }
                    
                    QPushButton#LaunchBtn {
                        color: #000000;
                        font-size: 18pt;
                        background-color: #ce0404;
                        border: 2px solid #000000;
                        min-height: 80px;
                    }
                    
                    QPushButton#BennchBtn {
                        color: #000000;
                        font-size: 18pt;
                        background-color: #df972a;
                        min-height: 60px;
                    }
                    
                    QLabel {
                        color: #ffffff;
                        
                        font-size: 16pt;
                        
                        min-width: 80px;
                        min-height: 40px;
                    }
                    
                    QLabel#ParamName {
                        color: #202223;
                        font-size: 12pt;
                        background-color: #A0ADAF;
                        border-radius: 6px;
                        max-width: 300px;
                        min-width: 80px;
                        min-height: 40px;
                    }
                    
                    QLabel#BaseParam {
                        color: #ffffff;
                        font-size: 14pt;

                        max-width: 400px;
                    }
                    
                    QLineEdit {
                        color: #202223;
                        font-size: 10pt;
                        background-color: #c1c1c1;
                        border-radius: 4px;

                        min-width: 80px;
                        min-height: 40px;
                    }
                    
                    QLineEdit#ParamValue {

                        min-width: 80px;
                        max-width: 250px;

                    } 
                    
                    QLineEdit#BaseParam {
                        font-size: 14pt;
                        max-width: 250px;

                    }
                    
                    QListWidget {
                        font-size: 14pt;
                        max-width: 500;
                        background-color: #c1c1c1;
                        border-radius: 4px;

                    }
                                   """)

    ####################################################################################################################
    """  PSYCHOPY functions  """
    ####################################################################################################################

    def start_psychopy(self):
        t = time.clock()
        from psychopy import visual, core  # This needs to be here, it can't be outside the threat the window is created from
        print('First psychopy import took: {}'.format((time.clock()-t)*1000))

        # Create monitor object
        mon = monitor_def(self.settings)

        # Get params to create a window from settings
        size = self.settings['wnd_PxSize']  # Get size from the settings (specified in GUI_cfg.yml
        try:
            size = (size.split(', ')[0], size.split(', ')[1])
        except:
            size = (size.split(',')[0], size.split(',')[1])

        col = map_color_scale(int(self.settings['default_bg']))  # Get default background color and update bg widget
        self.params_widgets_dict['Background Luminosity']['Background Luminosity'][1].setText(
            str(int(map_color_scale(col, reversed=True))))  # Update the BG color widget

        # Create a window, get mseconds per screen refresh
        self.psypy_window = visual.Window([int(size[0]), int(size[1])], monitor=mon, color=[col, col, col],
                                          fullscr=self.settings['fullscreen'], units=self.settings['unit'])
        self.screenMs, _, _ = self.psypy_window.getMsPerFrame()

        # Print the results to the consol
        print('\n========================================')
        print('''
        Initialised Psychopy window: {}
            with size: {}
                 fps: {}\n
        Using monitor: {}\n
        mS per frame: {}\n
        '''.format(self.psypy_window.name, self.psypy_window.size, self.psypy_window.fps(), mon.name, self.screenMs))
        print('\n========================================')

    def change_bg_lum(self):
        # Get bg luminosity and update widow
        lum = self.bg_luminosity
        if not lum:
            lum = 0
        elif int(lum) > 255:
            lum = 255
        else:
            lum = int(lum)
        # update the window color
        lum = map_color_scale(lum)
        self.psypy_window.setColor([lum, lum, lum])

    def stim_creator(self):
        """
        Creates and initialises stimuli
        """
        # TODO non linear looms and gratings
        params = self.prepared_stimuli[self.current_stim_params_displayed]

        if 'loom' in params['Stim type'].lower():
            self.stim = visual.Circle(self.psypy_window, radius=float(params['start_size']), edges=64,
                                      units=params['units'],
                                      lineColor='white', fillColor='black')
            self.stim.radius = self.stim_frames[self.stim_frame_number]
            self.stim.draw()

        # Print how long it took to create the stim
        print('Stim generation took: {}'.format((time.clock()-self.stim_creation_timer)*1000))

    def stim_destroyer(self):
        """
        Cleans up the psychopy window after the stimulus ended and it re-initialises the variabels
        """
        params = self.prepared_stimuli[self.current_stim_params_displayed]

        # Clean up stimuli
        if 'loom' in params['Stim type'].lower():
            # Cant find a better way to remove looms than making them super tiny
            self.stim.radius = 0.001
            self.stim.draw()

        # Clean up variables
        self.stim_frames = False
        self.stim_frame_number = False
        self.stim_on = False

    def stim_manager(self):
        """
        When the launch button gets called:
        * The stimulus frames get calculated (e.g. for looms the number of frames it will take to expand and the radii at all steps)
        * This function creates the stimulus object
        * Everytime stim_manager is called it loops over the stimulus frames and updates it
        * When all frames have been played, the window is cleaned

        :return:
        """
        if self.stim_on:
            # Need to import from psychopy here or it gives an error. Takes <<1 ms
            from psychopy import visual

            # If stim is just being created, start clock to time its duration
            if not self.stim_frame_number:
                self.stim_timer = time.clock()
                self.stim_creation_timer = time.clock()
                # Initialise variable to keep track of progress during stim update
                self.stim_frame_number = 0

            # Create the stimulus object
            self.stim_creator()

            # Keep track of our progress as we update the loom
            self.stim_frame_number += 1

            if self.stim_frame_number == len(self.stim_frames):
                # We reached the end of the stim frames, keep the stim on for a number of ms and then clean up
                # Print for how long the stimulus has been on
                elapsed = time.clock() - self.stim_timer
                print('Stim duration: {}'.format(elapsed * 1000))

                # Get for how long the stimulus should be left on, and time it
                params = self.prepared_stimuli[self.current_stim_params_displayed]
                ontimer = time.clock()
                time.sleep(int(int(params['on_time'])/1000))
                print('ON time {}'.format((time.clock()-ontimer))*1000)

                # After everything is done, clean up
                self.stim_frames = False
                self.stim_frame_number = False
                self.stim_on = False



    ####################################################################################################################
    """  FUNCTIONS  """
    ####################################################################################################################
    # PARAMS handling
    def read_from_params_widgets(self):  # <--- !!!
        """
        Loops over the params widgets and reads their values.
        Stores the values in the dictionary of the currently displayed stimulus
        :return:
        """
        for param_name, param in self.params_widgets_dict.items():
            if param_name == 'Background Luminosity':
                self.bg_luminosity = get_param_val(param, string=True)

            elif param_name =='Delay':
                self.stim_delay = get_param_val(param)

            else:
                if not self.current_stim_params_displayed is None:
                    label = get_param_label(param)
                    value = get_param_val(param, string=True)
                    if label.text():
                        self.prepared_stimuli[self.current_stim_params_displayed][label.text()] = value

    def update_params_widgets(self, stim_name):
        """ Takes the parameters form one of the loaded stims [in the list widget] and updates the widgets to display
        the parameters values"""
        try:
            if not isinstance(stim_name, str):
                # if the function has been called by clicking on an item of the list widget "stim_name" will
                # be a handle to the event not to the item being clicked so we need to extract the name
                stim_name = stim_name.text()

            # Get the parameters for the selected stim
            params = self.prepared_stimuli[stim_name]

            # Keep track of which is the stimulus we are currently displaying
            self.current_stim_params_displayed = stim_name

            # Update params file name entry
            self.filename_edit.setText(stim_name)

            # Update stim type parameter widgets
            list(self.params_widgets_dict['Stim Type'].values())[0][0].setText('Stim type')
            list(self.params_widgets_dict['Stim Type'].values())[0][1].setText(params['type'])

            # Update the other parameters widgets
            params_names = sorted(params.keys())
            params_names = [x for x in params_names if x not in self.ignored_params]  # Don't display all parameters
            assigned = 0  # Keep track of how many parameters have been assigned to a widget
            for pnum in sorted(self.params_widgets_dict.keys()):
                if 'Param' in pnum:
                    label = get_param_label(self.params_widgets_dict[pnum])
                    value = get_param_val(self.params_widgets_dict[pnum])

                    if assigned >= len(params_names):
                        # Additional widgets should be empty
                        label.setText('')
                        value.setText(str(''))
                    else:
                        # Set the widgets texts
                        par = params_names[assigned]
                        label.setText(par)
                        value.setText(str(params[par]))
                    assigned += 1

            if assigned < len(params_names):  # Too many params to display for the number of widgets in the GUI
                print(' Couldnt display all params, need more widgets')
        except:
            # TODO: this seems to result in the application crashing if something went wrong
            raise Warning('Couldnt load parameters from file {}'.format(stim_name + '.yml'))

    def load_stim_params_from_list_widget(self):
        """
        Get the selected file in the widget list of .yaml files and loads the data from it, then calls other
        functions to update class data and GUI widgets
        """
        if self.param_files_list.currentItem().text():
            # Get correct path to file
            file = self.param_files_list.currentItem().text()
            file_long = os.path.join(self.settings['stim_configs'], file)

            self.prepared_stimuli[file] = load_yaml(file_long)  # Load parameters from YAML files
            self.update_params_widgets(file)  # Update the widgets with new paramaters
            self.loaded_stims_list.addItem(file)  # Add the file to the widget list
            self.current_stim_params_displayed = file  # Set the currently displayed stim accordingly

    def remove_loaded_stim_from_widget_list(self):
        # TODO --  this seems to be buggy
        try:
            if self.loaded_stims_list.count() >= 1:
                # Remove item from loaded stims dictionary
                sel = self.loaded_stims_list.currentItem().text()
                del self.prepared_stimuli[sel]

                # Clean up widgets
                for param, wdgets in self.params_widgets_dict.items():
                    if param not in ['Background Luminosity', 'Delay']:
                        label = get_param_label(wdgets)
                        value = get_param_val(wdgets)
                        label.setText('')
                        value.setText('')

                # Remove item from list widget
                qIndex = self.loaded_stims_list.indexFromItem(self.loaded_stims_list.selectedItems()[0])
                self.loaded_stims_list.model().removeRow(qIndex.row())

                # Display the params of the item above in the list if there is any
                items = get_list_widget_items(self.loaded_stims_list.count())  # items already in the list widget
                if items:
                    # Load from the first item in the list
                    self.update_params_widgets(items[0])
                else:
                    # I think that this is where the bug is
                    self.filename_edit.setText('No stim loaded')
                    self.current_stim_params_displayed = None
        except:
            raise Warning('Something went wrong...')

    # FILES handling
    def get_stims_yaml_files_from_folder(self):
        # Get all YAML files in the folder
        files_folder = self.settings['stim_configs']
        params_files = get_files(files_folder)

        # Get list of files already in list widget
        files_in_list = get_list_widget_items(self.param_files)

        # If we loaded new files add them to the widget
        for short in sorted(params_files.keys()):
            if not short.split in files_in_list:
                self.param_files_list.addItem(short)

    def save_params_yaml_file(self):
        # Save file
        if self.current_stim_params_displayed and self.prepared_stimuli:
            params = self.prepared_stimuli[self.current_stim_params_displayed]
            fname = self.filename_edit.text()
            path = self.settings['stim_configs']

            if fname in self.prepared_stimuli.keys():
                print('Trying to overwrite a parameters file !!!! <---------')
                # TODO handle this better ?

            print('Saving parameters to: {}'.format(os.path.join(path, fname)))
            with open(os.path.join(path, fname), 'w') as outfile:
                yaml.dump(params, outfile, default_flow_style=True)

        # Update files list widget
        self.get_stims_yaml_files_from_folder()

    # LAUNCH btn function
    def launch_stim(self):
        if self.current_stim_params_displayed:
            self.stim_on = True
            # get params and call stim generator to calculate stim frames
            params = self.prepared_stimuli[self.current_stim_params_displayed]
            self.stim_frames = stim_calculator(self.screenMs, params)


    ####################################################################################################################
    """    MAIN LOOP  """
    ####################################################################################################################

    def main_loop(self):
        """
        The main loop runs in a separate thread from the GUI

        After initialisng the psychopy window it keeps looping in sync with the screen refresh rate (check out
        window.flip() docs in psychopy)

        At each loop the parameters of the currently loaded stim are checked, then the background is changed
        accordingly and finally the stimuli are managed
        """
        # Start psychopy window
        self.start_psychopy()

        while True:  # Keep loopingnin synch with the screen refresh rate, check the params and update stuff
            # Update parameters
            self.read_from_params_widgets()

            # Update background
            self.change_bg_lum()

            # Generate, update and clean up stimuli
            self.stim_manager()

            if isinstance(self.stim_frames, bool):
                try:
                    self.stim.radius=0
                except:
                    pass

            # Update psychopy window
            try:
                self.psypy_window.flip()
            except:
                print('Didnt flip')

    ####################################################################################################################
    ####################################################################################################################

    def nofunc(self):
        # Decoy function to set up empty buttons during GUI design
        pass

####################################################################################################################
####################################################################################################################
####################################################################################################################
####################################################################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main_UI()
    sys.exit(app.exec_())



