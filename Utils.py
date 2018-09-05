from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from psychopy import monitors, tools
import yaml
import os
import traceback
import sys
import numpy as np
import math



"""
CLASS TO CALCULATE THE STIMULI FRAMES FOR DIFFERENT TYPES OF STIMULI
"""


class Stimuli_calculator():
    def __init__(self, wnd, params, screenMs):
        """
            Gets called by UI_app Main() when a stimulus needs to be generated and calls the right subfuction to calculate
            the stimulus parameters

            :param wnd: psychopy window
            :param params:  stimulus parameters, dict. Loaded from YAML file
            :param screenMs:  ms per screeen refresch
            :return:
            """
        self.stim_frames = None  # Initialise variable to avoid problems

        # Call subfunctions to generate the stimulus
        if 'loom' in params['type'].lower():
            self.stim_frames = self.loomer(wnd, params, screenMs)

        if 'grating' in params['type'].lower():
            self.stim_frames = self.grater(wnd, params, screenMs)

    def loomer(self, wnd, params, screenMs):
        """
        Calculates the position of the loom, for how many screen frames it will stay on and what the radius will be
        at each frame

        :param wnd:  psychopy window
        :param params:   stim params [from YAML file]
        :param screenMs:  Ms for each screen refresh
        :return: position of the centre of the loom, radii steps
        """
        # get position of centre of loom. The user selects it in pixels so we need to convert it to whatver the
        # unit that is being used for the loom
        pos = int(params['pos'].split(', ')[0]), int(params['pos'].split(', ')[1])
        unit = params['units']
        pos = unit_converter(wnd, pos[0], in_unit='px', out_unit=unit), unit_converter(wnd, pos[1],
                                                                                       in_unit='px', out_unit=unit)

        # Prepare radii steps
        if params['modality'] == 'linear':
            numExpSteps = np.ceil(int(params['expand_time']) / screenMs) +1

            radii = np.linspace(float(params['start_size']),
                                float(params['end_size']), numExpSteps)
        elif params['modality'] == 'exponential':
            # Get the parameters to calculate the loom expansion steps
            speed = int(params['LV speed'])/1000
            if params['units'] == 'degs' or params['units'] == 'deg':
                tangent = math.tan(math.radians(float(params['start_size'])/2))
            elif params['units'] == 'cm':
                size = unit_converter(wnd, float(params['start_size']), in_unit='cm', out_unit='deg')
                tangent = math.degrees(math.tan(float(size)))
            mouse_distance = wnd.monitor.getDistance()  # distance of mouse from screen in cm

            # Calc expansions steps  [based on Matlab code for exponential looms]
            time_to_collision = round(float(100*speed/tangent),2)/100 # time to collision IN SECONDS
            num_steps = np.ceil(time_to_collision/(1/60))
            time_array = np.linspace(-time_to_collision, 0, num_steps)

            conv_factor = speed/abs(time_array[0:-1])
            radii = conv_factor * mouse_distance  # Radii in cm

            # Convert the radii in degres if the stim is being defined in degrees
            if params['units']  == 'deg' or params['units'] == 'degs':
                converted_radii = []
                for rad in radii:
                    converted_radii.append(unit_converter(wnd, rad, in_unit='cm', out_unit='deg'))
                radii = np.array(converted_radii)

            # Cut of radii that exceed user selected value
            radii[np.where(radii>int(params['max radius']))] = int(params['max radius'])

            # TODO find a way to make the loom last a pre-determined ammount of time

        else:
            raise Warning('Couldnt compute loom parameters')

        return pos, radii


    def grater(self, wnd, params, screenMs):
        """
        Calculates the data for generating a grating stimulus given some params
        same input as loomer
        """
        numExpSteps = np.ceil(int(params['duration']) / screenMs)+2
        x, y, width, height = get_position_in_px(wnd, 'top left', 0, return_scree_size=True)
        if params['units'] == 'cm':
            pos = (0, 0)
            screen_size = (width, width)
        else:
            pos = (0, 0)
            screen_size = (width*2, width*2)

        """
        The velocity is set by specifying the phase of the grating at each frame. 
        To do this: create an array that covers an entire phase cycle [0-1] and is 1/n frames long where n depends on the 
        velocity [i.e. phases per second]. The array is then repeat to be as long as the stimulus we are creating.
        The sign of the phases depends on the direction of movement 
        """
        frames_per_sec = np.ceil(1000 / screenMs)
        vel = float(params['velocity'])
        if float(params['direction']) <= 0:
            phase_max = -2
        else:
            phase_max = 2

        if vel > 0:
            phase = np.linspace(0, phase_max, frames_per_sec/vel)
            if len(phase) == 0:
                pass
            repeats = int(numExpSteps)/len(phase)
            if repeats >= 1:
                phases = np.tile(phase, int(repeats))
            else:
                phases = np.tile(phase, np.ceil(repeats))
                phases = phases[0:int(numExpSteps)]
            if abs(len(phases)-int(numExpSteps))>2:
                a = 1
        else:
            phases = np.ones((int(numExpSteps), 1))

        # Get orientation
        orientation = int(params['orientation'])

        # get colors
        fg = map_color_scale(int(params['fg color']))
        #
        # if params['bg color'] == 'wnd':
        #     bg = wnd.color[0]
        # else:
        #     bg = map_color_scale(int(params['bg color']))

        return pos, screen_size, orientation, fg, phases




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
    if isinstance(list_wdg.count(), int):
        if not list_wdg.item(0) is None:
            items.append(list_wdg.item(0).text())
    else:
        for index in range(list_wdg.count()):
            items.append(list_wdg.item(index).text())
    return items

####################################################################################################################
####################################################################################################################
"""    FUNCTIONS FOR PSYCHOPY   """
####################################################################################################################
####################################################################################################################


def monitor_def(settings):
    print('Setting up monitor')
    filename =settings['Name']
    for f in os.listdir(".\\Screens"):
        if filename == f.split('.')[0]:
            setupfile = f
            break

    screen_params = load_yaml(".\\Screens\\{}".format(setupfile))

    my_monitor = monitors.Monitor(screen_params['Name'])
    size = screen_params['PxSize']
    try:
        my_monitor.setSizePix((int(size.split(', ')[0]), int(size.split(', ')[1])))
    except:
        my_monitor.setSizePix((int(size.split(',')[0]), int(size.split(',')[1])))

    my_monitor.setWidth(int(screen_params['Width']))
    my_monitor.setDistance(int(screen_params['Distance']))
    my_monitor.saveMon()
    return my_monitor, screen_params['Screen number']


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
        if out_unit == 'deg' or out_unit == 'degs':
            conv_fact = tools.monitorunittools._deg2pix(1, 0, wnd)*cm_per_px
            out = data*(1/conv_fact)
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
