from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from psychopy import monitors, tools
import yaml
import os


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
"""    FILES INPUT  OUTPUT   """
####################################################################################################################
####################################################################################################################


def load_yaml(fpath):
    # Load data from a YAML file
    with open(fpath, 'r') as f:
        settings = yaml.load(f)
    return settings


def get_files(fld, ending='yml'):
    # Get all files in a directory and return a dictionary with all those with a specific ending
    # Keys of the dict are files names, entries are the complete file path
    files = os.listdir(fld)
    files_output = {}
    for f in files:
        if ending in f.split('.')[-1]:
            files_output[f] = os.path.join(fld, f)
    return files_output

####################################################################################################################
####################################################################################################################
"""    PYQT FUNCTIONS TO HADNLE WIDGET DATA   """
####################################################################################################################
####################################################################################################################


def get_param_label(param, object=False):
    """
    Given a param object returns its label text as a string or as the widget object itsels
    """
    if not object:
        return list(param.values())[0][0].text()
    else:
        return list(param.values())[0][0]


def get_param_val(param, string=False, object=False):
    """
    Given a param object returns its value as a string or int or as the widget object itsels
    """
    if not object:
        val = list(param.values())[0][1].text()
        if not string:
            if not val:
                val = 0

            return int(val)
        else:
            return val
    else:
        return list(param.values())[0][1]


def get_list_widget_items(list_wdg):
    # Give a PyQt list widget return a list of all items in it
    items = []  # items already in the list widget
    for index in range(list_wdg.count()):
        items.append(list_wdg.item(index).text())
    return items

####################################################################################################################
####################################################################################################################
"""    FUNCTIONS FOR PSYCHOPY   """
####################################################################################################################
####################################################################################################################


def monitor_def(settings):
    my_monitor = monitors.Monitor(name=settings['Name'])
    size = settings['PxSize']
    try:
        my_monitor.setSizePix((int(size.split(', ')[0]), int(size.split(', ')[1])))
    except:
        my_monitor.setSizePix((int(size.split(',')[0]), int(size.split(',')[1])))

    my_monitor.setWidth(int(settings['Width']))
    my_monitor.setDistance(int(settings['Distance']))
    my_monitor.saveMon()
    return my_monitor


def map_color_scale(value, leftMin=0, leftMax=255, rightMin=-1, rightMax=1, reversed=False):
    """
    Psychopy colora work on a scale that ranges from -1 to 1
    The UI allows user to imput colors in a range from 0 to 255
    This functions maps the values from the user input to the psychopy scale
    """
    if reversed:
        # Mapping from PsychoPy colors to 255 RBG values
        leftMin, leftMax, rightMin, rightMax = -1, 1, 0, 255

    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def get_position_in_px(wnd, location, square_side, return_scree_size=False):
    """
    In psychopy the centre of the window is pos 0,0. For us is more convenient if the top left corner is 0, 0
    so we need to map from our coordinate space to psychopys one

    :param wnd: psychopy window

    :param location: which corner of the screen are we interested in
    :return:
    """
    screen_size_px = wnd.monitor.getSizePix()
    screen_width_cm = wnd.monitor.getWidth()
    half_width_cm = screen_width_cm/2

    screen_height_cm = (screen_width_cm/screen_size_px[0])*screen_size_px[1]
    half_height_cm = screen_height_cm/2

    half_side_cm = int(square_side/2)

    x_translate, y_translate = -half_width_cm+half_side_cm, half_height_cm-half_side_cm

    # Go from our mapping to psychopy location
    if location == 'top left':
        mappedloc = (x_translate, y_translate)
    elif location == 'top right':
        mappedloc = (-x_translate, y_translate)
    elif location == 'bottom right':
        mappedloc = (-x_translate, -y_translate)
    else:  # location == 'bottom left'
        mappedloc = (x_translate, -y_translate)

    if not return_scree_size:
        return int(mappedloc[0]), int(mappedloc[1])
    else:
        return int(mappedloc[0]), int(mappedloc[1]), screen_width_cm, screen_height_cm


def unit_converter(wnd, data, in_unit='cm', out_unit='px'):
    """
    Map between different units for psychopy. Most commonly used to convert a measure from pixels to degrees
    """
    cm_per_px = wnd.monitor.getWidth() / wnd.monitor.getSizePix()[0]
    out = 0
    if in_unit == 'cm':
        if out_unit == 'px':
            out = tools.monitorunittools._cm2pix(data, 0, wnd)
    if in_unit == 'deg' or in_unit == 'degs':
        if out_unit == 'px':
            out = tools.monitorunittools._deg2pix(data, 0, wnd)
        else:  # out cm
            out = tools.monitorunittools._deg2pix(data, 0, wnd)
            out *= cm_per_px
    if in_unit == 'px' or in_unit == 'pix':
        if out_unit == 'deg' or out_unit == 'degs':
            px_per_deg = tools.monitorunittools._deg2pix(1, 0, wnd)
            out = data / px_per_deg
        else:  #out in cm
            out = data * cm_per_px
    return out
