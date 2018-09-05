from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import  os

from Utils import Stimuli_calculator, get_files, get_list_widget_items, load_yaml, get_param_val, get_param_label

####################################################################################################################
"""    DEFINE THE LAYOUT AND LOOKS OF THE GUI  """
####################################################################################################################


class App_layout():
    @staticmethod
    def create_widgets(self):
        # Take care of the layout
        self.grid = QGridLayout()
        self.grid.setSpacing(25)

        # Status label
        self.status_label = QLabel('Loading...')

        # Available yml file
        self.params_files_label = QLabel('Parameter files')

        self.param_files_list = QListWidget()
        self.param_files_list.itemDoubleClicked.connect(lambda: App_control.load_stim_params_from_list_widget(self))

        # Loaded stims
        self.laoded_stims_label = QLabel('Loaded stims')

        self.loaded_stims_list = QListWidget()
        self.loaded_stims_list.currentItemChanged.connect(lambda: App_control.update_params_widgets)
        self.loaded_stims_list.itemDoubleClicked.connect(App_control.remove_loaded_stim_from_widget_list)

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
        self.launch_btn.clicked.connect(lambda: App_control.launch_stim(self))

        # Load and save btn
        self.load_btn = QPushButton(text='Load')
        self.load_btn.clicked.connect(lambda: App_control.load_stim_params_from_list_widget(self))

        self.remove_btn = QPushButton(text='Remove')
        self.remove_btn.clicked.connect(lambda: App_control.remove_loaded_stim_from_widget_list(self))

        self.save_btn = QPushButton(text='Save')
        self.save_btn.clicked.connect(lambda: App_control.save_params_yaml_file(self))

        # Benchmark btn
        self.bench_btn = QPushButton(text='Bench Mark')
        self.bench_btn.clicked.connect(lambda: App_control.launch_benchmark(self))

    @staticmethod
    def define_layout(self):
        # Status label
        self.grid.addWidget(self.status_label, 16, 0, 1, 2)
        self.status_label.setObjectName('Status')
        self.status_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # Available yml files
        self.grid.addWidget(self.params_files_label, 0, 0)

        self.grid.addWidget(self.param_files_list, 1, 0, 4, 5)

        # Loaded stims
        self.grid.addWidget(self.laoded_stims_label, 5, 0)

        self.grid.addWidget(self.loaded_stims_list, 6, 0, 3, 4)

        # Current open stim
        self.grid.addWidget(self.filename_edit, 0, 2, 1, 2)

        for i in range(10):

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
            self.grid.addWidget(lbl, 1 + i, 2, 1, 1)
            self.grid.addWidget(entry, 1 + i, 3, 1, 1)

        # Bg Luminosity and delay
        self.grid.addWidget(self.bg_label, 9, 0)
        self.grid.addWidget(self.delay_label, 10, 0)
        self.grid.addWidget(self.bg_edit, 9, 1)
        self.grid.addWidget(self.delay_edit, 10, 1)

        # Launch btn
        self.grid.addWidget(self.launch_btn, 14, 0, 1, 4)
        self.launch_btn.setObjectName('LaunchBtn')

        # Load and save btn
        self.grid.addWidget(self.load_btn, 13, 0, 1, 1)
        self.grid.addWidget(self.remove_btn, 13, 1, 1, 1)
        self.grid.addWidget(self.save_btn, 13, 2, 1, 2)

        # Finalise layout
        self.setLayout(self.grid)
        self.setContentsMargins(50, 10, 10, 25)
        self.setGeometry(int(self.settings['position'].split(', ')[0]), int(self.settings['position'].split(', ')[1]),
                         int(self.settings['width']), int(self.settings['height']))
        self.setWindowTitle('Review')

        # Benchamrk btn
        self.grid.addWidget(self.bench_btn, 15, 0, 1, 4)
        self.bench_btn.setObjectName('BennchBtn')

        self.show()

    @staticmethod
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

                        QLabel#Status {
                            color: #000000;
                            background-color: #b40505;
                            font-size: 14pt;
                            max-height: 40pt;
                            border-radius: 6px; 
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
                            max-width: 200px;

                        }

                        QListWidget {
                            font-size: 14pt;
                            max-width: 510px;
                            background-color: #c1c1c1;
                            border-radius: 4px;

                        }
                                       """)


class App_control():
    """
    Set of functions that contro (mainly) the behaviour of the widgets of Main_UI.
    They are placed in this sub class as static methots and passed Main_UI as param
    Main to separate all of these function from main body of code, to make it easier to work on them
    separately

    """
    # PARAMS and WIDGETS
    @staticmethod
    def update_status_label(main):
        if not main.ready:
            main.status_label.setText('Loading...')
            main.status_label.setStyleSheet('background-color: orange')
        else:
            try:
                if not main.benchmarking:
                    if main.ready == 'Ready':
                        main.status_label.setText('READY')
                        main.status_label.setStyleSheet('background-color: green')
                    else:
                        main.status_label.setText('Busy...')
                        main.status_label.setStyleSheet('background-color: gray')
            except:
                print('Couldnt update status label')

    @staticmethod
    def read_from_params_widgets(main):
        """
        Loops over the params widgets and reads their values.
        Stores the values in the dictionary of the currently displayed stimulus
        :return:
        """
        for param_name, param in main.params_widgets_dict.items():
            if param_name == 'Background Luminosity':
                main.bg_luminosity = get_param_val(param, string=True)

            elif param_name == 'Delay':
                main.stim_delay = get_param_val(param)

            else:
                if not main.current_stim_params_displayed is None:
                    label = get_param_label(param)
                    value = get_param_val(param, string=True)
                    if len(label) > 1 and main.current_stim_params_displayed:
                        main.prepared_stimuli[main.current_stim_params_displayed][label] = value

    @staticmethod
    def update_params_widgets(main, stim_name):
        """ Takes the parameters form one of the loaded stims [in the list widget] and updates the widgets to display
        the parameters values"""
        try:
            if not isinstance(stim_name, str):
                # if the function has been called by clicking on an item of the list widget "stim_name" will
                # be a handle to the event not to the item being clicked so we need to extract the name
                stim_name = stim_name.text()

            # Get the parameters for the selected stim
            if not stim_name in main.prepared_stimuli.keys():
                return
            params = main.prepared_stimuli[stim_name]

            # Keep track of which is the stimulus we are currently displaying
            main.current_stim_params_displayed = stim_name

            # Update params file name entry
            main.filename_edit.setText(stim_name)

            # Update stim type parameter widgets
            list(main.params_widgets_dict['Stim Type'].values())[0][0].setText('Stim type')
            list(main.params_widgets_dict['Stim Type'].values())[0][1].setText(params['type'])

            # Update the other parameters widgets
            params_names = sorted(params.keys())
            params_names = [x for x in params_names if x not in main.ignored_params]  # Don't display all parameters
            assigned = 0  # Keep track of how many parameters have been assigned to a widget
            for pnum in sorted(main.params_widgets_dict.keys()):
                if 'Param' in pnum:
                    label = get_param_label(main.params_widgets_dict[pnum], object=True)
                    value = get_param_val(main.params_widgets_dict[pnum], object=True)

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
            print('Couldnt load parameters from file {}'.format(stim_name))

    @staticmethod
    def load_stim_params_from_list_widget(main):
        """
        Get the selected file in the widget list of .yaml files and loads the data from it, then calls other
        functions to update class data and GUI widgets
        """
        if main.param_files_list.currentItem().text():
            # Get correct path to file
            file = main.param_files_list.currentItem().text()
            file_long = os.path.join(main.settings['stim_configs'], file)

            main.prepared_stimuli[file] = load_yaml(file_long)  # Load parameters from YAML files
            App_control.update_params_widgets(main, file)  # Update the widgets with new paramaters
            main.loaded_stims_list.addItem(file)  # Add the file to the widget list
            main.current_stim_params_displayed = file  # Set the currently displayed stim accordingly

    def remove_loaded_stim_from_widget_list(self):
        self.ready = 'Busy'
        try:
            if self.loaded_stims_list.count() >= 1:
                # Remove item from loaded stims dictionary
                if self.loaded_stims_list.currentItem() is None:
                    return

                sel = self.loaded_stims_list.currentItem().text()
                if sel in self.prepared_stimuli.keys():
                    del self.prepared_stimuli[sel]

                # Clean up widgets
                for param, wdgets in self.params_widgets_dict.items():
                    if param not in ['Background Luminosity', 'Delay']:
                        label = get_param_label(wdgets, object=True)
                        value = get_param_val(wdgets, object=True)
                        label.setText('')
                        value.setText('')

                # Remove item from list widget
                qIndex = self.loaded_stims_list.indexFromItem(self.loaded_stims_list.selectedItems()[0])
                if qIndex.row() > 0:
                    self.loaded_stims_list.model().removeRow(qIndex.row())
                    # Display the params of the item above in the list if there is any
                    items = get_list_widget_items(self.loaded_stims_list)  # items already in the list widget
                    if items:
                        # Load from the first item in the list
                        update_params_widgets(self, items[0])
                else:
                    self.loaded_stims_list.item(0).setText('deleted stim')
                    # I think that this is where the bug is
                    self.filename_edit.setText('No stim loaded')
                    self.current_stim_params_displayed = None

        except:
            raise Warning('Something went wrong...')

        self.ready = 'Ready'

    # FILES handling
    @staticmethod
    def get_stims_yaml_files_from_folder(main):
        # Get all YAML files in the folder
        files_folder = main.settings['stim_configs']
        params_files = get_files(files_folder)

        # Get list of files already in list widget
        files_in_list = get_list_widget_items(main.param_files_list)

        # If we loaded new files add them to the widget
        for short in sorted(params_files.keys()):
            if not short.split in files_in_list:
                main.param_files_list.addItem(short)

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
        App_control.get_stims_yaml_files_from_folder(self)

    # LAUNCH btn function
    @staticmethod
    def launch_stim(main):
        if main.ready == 'Ready':
            if main.current_stim_params_displayed:
                main.stim_on = True
                # get params and call stim generator to calculate stim frames
                params = main.prepared_stimuli[main.current_stim_params_displayed]
                calcuated_stim = Stimuli_calculator(main.psypy_window, params, main.screenMs)
                main.stim_frames = calcuated_stim.stim_frames

    @staticmethod
    def launch_benchmark(main):
        main.benchmarking = True
        main.setup_ni_communication()

