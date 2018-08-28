from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import traceback, sys
import os
import yaml

from utils import *

####################################################################################################################
####################################################################################################################
"""    WORKER CLASSES FOR MULTI THREADING   """
####################################################################################################################
####################################################################################################################


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    '''
    Worker thread
    multi threading: https://www.replrebl.com/article/multithreading-pyqt-applications-with-qthreadpool/

    :param args: Arguments to make available to the run code
    :param kwargs: Keywords arguments to make available to the run code

    '''

    def __init__(self, fn, *args, **kwargs):
        """
        Take a function and its parameters as input, then when RUN is executed call the function and pass the params
        """

        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(
                *self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

####################################################################################################################
####################################################################################################################
"""    MAIN GUI CLASS   """
####################################################################################################################
####################################################################################################################

class Main_UI(QWidget):
    """
    multi threading: https://www.replrebl.com/article/multithreading-pyqt-applications-with-qthreadpool/
    """
    def __init__(self):
        """
        Initialise variables to control GUI behaviour
        Initialise multi threading
        Call functions that create widgets and take care of the styling the GUI
        start MAIN loop
        """
        super().__init__()
        # Display silent exceptions that cause the gui to crash
        sys._excepthook = sys.excepthook
        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback)
            sys.exit(1)
        sys.excepthook = exception_hook
        # ==============================================================================
        # Load parameters from config file
        config_path = 'C:\\Users\\Federico\\Documents\\GitHub\\VisualStimuli\\GUI_cfg.yml'
        self.settings = load_yaml(config_path)

        # Initialise variables
        self.loaded_stims = {}
        self.current_stim_displayed = None
        self.ignored_params = ['name', 'units', 'type', 'modality']  # Stim parameters with these will not be displayed
        # in the gui, they will have to be edited in the yaml files


        # ==============================================================================
        # START MULTITHREDING
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # Create GUI
        self.create_widgets()
        self.define_layout()
        self.define_style_sheet()

        # Call Main Loop - on a separate thread
        # Start a thread that continously checks the parameters and refreshes the window
        main_loop_worker = Worker(self.main_loop)
        self.threadpool.start(main_loop_worker)

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
        self.param_files_list.itemDoubleClicked.connect(self.nofunc)

        # Loaded stims
        self.laoded_stims_label = QLabel('Loaded stims')

        self.loaded_stims_list = QListWidget()

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

        # Append bg and delay stiff to parameters dictionary
        param = {self.bg_label.text(): [self.bg_label, self.bg_edit]}
        self.params_widgets_dict[self.bg_label.text()] = param
        param = {self.delay_label.text(): [self.delay_label, self.delay_edit]}
        self.params_widgets_dict[self.delay_label.text()] = param


        # Launch btn
        self.launch_btn = QPushButton(text='Launch')
        self.launch_btn.clicked.connect(self.nofunc)

        # Load and save btn
        self.load_btn = QPushButton(text='Load')
        self.load_btn.clicked.connect(self.load_stim_params)

        self.remove_btn = QPushButton(text='Remove')
        self.remove_btn.clicked.connect(self.remove_loaded_stim)

        self.save_btn = QPushButton(text='Save')
        self.save_btn.clicked.connect(self.save_param_file)

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
        self.setGeometry(100, 100, 2500, 1800)
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
    """    INITIALISE PSYCHOPY  """
    ####################################################################################################################

    def start_psychopy(self):
        from psychopy import visual  # This needs to be here, it can't be outside the threat the window is created from

        mon = monitor_def(self.settings)
        # create a window, get mseconds per refresh
        size = self.settings['wnd_PxSize']
        try:
            size = (size.split(', ')[0], size.split(', ')[1])
        except:
            size = (size.split(',')[0], size.split(',')[1])
        col = map_color_scale(int(self.settings['default_bg']))
        self.params_widgets_dict['Background Luminosity']['Background Luminosity'][1].setText(
            str(int(map_color_scale(col, reversed=True))))  # Update the BG color widget

        self.psypy_window = visual.Window([int(size[0]), int(size[1])], monitor=mon, color=[col, col, col],
                                          fullscr=self.settings['fullscreen'], units=self.settings['unit'])
        self.screenMs, _, _ = self.psypy_window.getMsPerFrame()
        print('\n========================================')
        print('''
        Initialised Psychopy window: {}
            with size: {}
                 fps: {}\n
        Using monitor: {}\n
        mS per frame: {}\n
        '''.format(self.psypy_window.name, self.psypy_window.size, self.psypy_window.fps(), mon.name, self.screenMs))
        print('\n========================================')

    ####################################################################################################################
    """    FUNCTIONS  """
    ####################################################################################################################
    def change_bg_lum(self, lum):
        # Get bg luminosity and update widow
        if not lum:
            lum = 0
        elif int(lum) > 255:
            lum = 255
        else:
            lum = int(lum)

        lum = map_color_scale(lum)
        self.psypy_window.setColor([lum, lum, lum])

    def get_param_val(self, param):
        val = list(param.values())[0][1].text()
        if not val:
            val = 0
        return int(val)

    def update_params(self):  # <--- !!!
        for param_name, param in self.params_widgets_dict.items():
            if param_name == 'Background Luminosity':
                self.change_bg_lum(list(param.values())[0][1].text())
            elif param_name =='Delay':
                self.stim_delay = self.get_param_val(param)
            else:
                # TODO read params and prep them for stimulus generation
                pass

    def get_stims_param_files(self):
        files_folder = self.settings['stim_configs']
        self.params_files = get_files(files_folder)

        items = []  # items already in the list widget
        for index in range(self.param_files_list.count()):
            items.append(self.param_files_list.item(index).text())

        # If we loaded new files add them to the widget
        for short in sorted(self.params_files.keys()):
            if not short.split('.')[0] in items:
                self.param_files_list.addItem(short.split('.')[0])


    ####################################################################################################################
    """    MAIN LOOP  """
    ####################################################################################################################

    def main_loop(self):
        # Start psychopy window
        self.start_psychopy()

        # Get parameters files
        self.get_stims_param_files()

        while True:
            # Update parameters
            self.update_params()

            # Update the window
            try:
                self.psypy_window.flip()
            except:
                print('Didnt flip')

    ####################################################################################################################
    """    BUTTONS FUNCTIONS  """
    ####################################################################################################################

    def nofunc(self):
        pass

    def update_params_widgets(self, stim_name):
        """ Takes the parameters form one of the loaded stims and updates the widgets to display
        the parameters """
        try:
            try:
                params = self.loaded_stims[stim_name]
            except:
                params = self.loaded_stims[stim_name+'.yml']

            # Update params file name entry
            self.filename_edit.setText(stim_name.split('.')[0])

            # Update stim type parameter
            list(self.params_widgets_dict['Stim Type'].values())[0][0].setText('Stim type')
            list(self.params_widgets_dict['Stim Type'].values())[0][1].setText(params['type'])

            # Update the other parameters
            params_names = sorted(params.keys())
            params_names = [x for x in params_names if x not in self.ignored_params]
            assigned = 0
            for pnum in sorted(self.params_widgets_dict.keys()):
                if 'Param' in pnum:
                    label = list(self.params_widgets_dict[pnum].values())[0][0]
                    value = list(self.params_widgets_dict[pnum].values())[0][1]
                    if assigned >= len(params_names):
                        label.setText('')
                        value.setText(str(''))
                    else:
                        par = params_names[assigned]
                        label.setText(par)
                        value.setText(str(params[par]))
                    assigned += 1
            if assigned < len(params_names):
                print(' Couldnt display all params, need more widgets')
        except:
            raise Warning('Couldnt load parameters from file {}'.format(stim_name+'.yml'))

    def load_stim_params(self):
        if self.param_files_list.currentItem().text():
            # Get correct path to file
            file = self.param_files_list.currentItem().text()+'.yml'
            file_long = os.path.join(self.settings['stim_configs'], file)

            # Load file parametrs, store them in dictionary and update widgets
            self.loaded_stims[file] = load_yaml(file_long)
            self.update_params_widgets(file)
            self.loaded_stims_list.addItem(file.split('.')[0])
            self.current_stim_displayed = file.split('.')[0]

    def remove_loaded_stim(self):
        # TODO --  when item removed display stuff from the sitm above it in the list
        try:
            if self.loaded_stims_list.count()>=1:
                # Remove item from loaded stims dictionary
                sel = self.loaded_stims_list.currentItem().text()
                del self.loaded_stims[sel+'.yml']

                # Clean up widgets
                for param, wdgets in self.params_widgets_dict.items():
                    if param not in ['Background Luminosity', 'Delay']:
                        label = list(wdgets.values())[0][0]
                        value = list(wdgets.values())[0][1]
                        label.setText('')
                        value.setText('')

                # Remove item from list widget
                qIndex = self.loaded_stims_list.indexFromItem(self.loaded_stims_list.selectedItems()[0])
                self.loaded_stims_list.model().removeRow(qIndex.row())

                # Display the params of the item above in the list if there is any
                items = []  # items already in the list widget
                for index in range(self.loaded_stims_list.count()):
                    items.append(self.loaded_stims_list.item(index).text())

                if items:
                    item_name = items[0]
                    self.update_params_widgets(item_name)


        except:
            pass

    def save_param_file(self):
        # Save file
        if self.current_stim_displayed and self.loaded_stims:
            params = self.loaded_stims[self.current_stim_displayed+'.yml']
            fname = self.filename_edit.text()+'.yml'
            path = self.settings['stim_configs']

            if fname in self.loaded_stims.keys():
                print('Trying to overwrite a parameters file !!!! <---------')

            print('Saving parameters to: {}'.format(os.path.join(path, fname)))
            with open(os.path.join(path, fname), 'w') as outfile:
                yaml.dump(params, outfile, default_flow_style=True)

        # Update files list widget
        self.get_stims_param_files()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main_UI()
    sys.exit(app.exec_())



