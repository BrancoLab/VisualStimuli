from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from App_funcs import *
from App_Main import App_control


####################################################################################################################
"""    DEFINE THE LAYOUT AND LOOKS OF THE GUI  """
####################################################################################################################

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


def define_layout(self):
    # Status label
    self.grid.addWidget(self.status_label, 16, 0, 1, 2)
    self.status_label.setObjectName('Status')
    self.status_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    # Available yml files
    self.grid.addWidget(self.params_files_label, 0, 0)

    self.grid.addWidget(self.param_files_list, 1, 0, 10, 1)

    # Loaded stims
    self.grid.addWidget(self.laoded_stims_label, 0, 1, )

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
        self.grid.addWidget(lbl, 1 + i, 2, 1, 1)
        self.grid.addWidget(entry, 1 + i, 3, 1, 1)

    # Bg Luminosity and delay
    self.grid.addWidget(self.bg_label, 1, 2)
    self.grid.addWidget(self.delay_label, 2, 2)
    self.grid.addWidget(self.bg_edit, 1, 3)
    self.grid.addWidget(self.delay_edit, 2, 3)

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
                        max-width: 250px;

                    }

                    QListWidget {
                        font-size: 14pt;
                        max-width: 500;
                        background-color: #c1c1c1;
                        border-radius: 4px;

                    }
                                   """)