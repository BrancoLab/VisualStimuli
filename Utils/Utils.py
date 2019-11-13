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
import random
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


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
        if 'loom' == params['type'].lower():
            self.stim_frames = self.loomer(wnd, params, screenMs)
        elif 'grating' in params['type'].lower():
            self.stim_frames = self.grater(wnd, params, screenMs)
        elif 'audio' in params['type'].lower():
            self.stim_frames = self.audio_generator(wnd, params, screenMs)
        elif 'delay' in params['type'].lower():
            self.stim_frames = self.delayer(wnd, params, screenMs)
        elif 'fearcond_copmlex' in params['type'].lower():
            # Define which aspects of the
            self.stim_frames = self.complex_fearcon_stim(wnd, params, screenMs, blackout=True, grating=True,
                                                            ultrasound=True, overlap=True)
        elif 'spot_loom' == params['type'].lower():
            self.stim_frames = self.spot_to_loomer(wnd, params, screenMs)

    def exponential_loom_calculator(self, params, wnd, screenMs):
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

        # keep the radius constant during on time
        numOnSteps = int(np.round(int(params['on_time']) / screenMs))
        on_radii = np.repeat(radii[-1], numOnSteps)

        # put everything together
        radii = np.append(radii, on_radii)

        return radii


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
            numExpSteps = int(np.round(int(params['expand_time']) / screenMs))
            numOnSteps = int(np.round(int(params['on_time']) / screenMs))

            # calculate loom radii during expansioin phase
            radii = np.linspace(float(params['start_size']),
                                float(params['end_size']), numExpSteps)

            # keep the radius constant during on time
            last_radius = radii[-1]
            on_radii = np.repeat(last_radius, numOnSteps)

            # put everything together
            radii = np.append(radii, on_radii)

            # Repeat the stimulus N times
            if int(params['repeats']) > 1:
                # Add  inter stimuli interval
                isi = int(params['off_time'])
                if isi > 0:
                    numOffSteps = int(np.round(isi / screenMs))
                    off_radii = np.zeros(numOffSteps)
                    radii = np.append(radii, off_radii)
                radii = np.tile(radii, int(params['repeats']))

        elif params['modality'] == 'exponential':
            radii = self.exponential_loom_calculator(params, wnd, screenMs)

            # Repeat the stimulus N times
            if int(params['repeats']) > 1:
                # Add  inter stimuli interval
                isi = int(params['off_time'])
                if isi > 0:
                    numOffSteps = int(np.round(isi / screenMs))
                    off_radii = np.zeros(numOffSteps)
                    radii = np.append(radii, off_radii)
                radii = np.tile(radii, int(params['repeats']))
        else:
            raise Warning('Couldnt compute loom parameters')

        return pos, radii

    def spot_to_loomer(self, wnd, params, screenMs):
        """
            This function calculates the frames for a spot to loom stimulus in which a spot appears on the screen, moves towards the center and turns into a loom.
            In practice this is just a psychopy circle whose position and size changes over the course of the stimulus.
        """
        # Convert spot start and end positions from user defined pixel values to cm
        positions = []
        for param_name in ['initial_pos', 'end_pos']:
            pos = int(params[param_name].split(', ')[0]), int(params[param_name].split(', ')[1])
            unit = params['units']
            pos = unit_converter(wnd, pos[0], in_unit='px', out_unit=unit), unit_converter(wnd, pos[1], in_unit='px', out_unit=unit)
            positions.append(pos)
        positions = tuple(positions)

        # If there are no repeats, the off time must be zero otherwise the LDR stays on too long
        if int(params['repeats']) <= 1:
            params['off_time'] = '0'
 
        # get total duration of the stimulus in number of frames [for different elements of the stimulus]
        if params['modality'].lower() == 'linear':
            tot_duration = int(params['duration']) + int(params['expand_time']) + int(params['on_time']) + int(params['off_time'])
            loom_expansion_steps = int(np.round(int(params['expand_time']) / screenMs))
        else:
            original_start_size = params['start_size']
            params['start_size'] = str(2*int(params['start_size'])) #  need to double it because it's halfed in the exponential_loom_calculator
            radii = self.exponential_loom_calculator(params, wnd, screenMs) # stores the radius of the spot during exponential expansion
            expansion_duration = int(np.round(len(radii) * screenMs)) # expansion duration in ms
            tot_duration = int(params['duration']) + expansion_duration + int(params['on_time']) + int(params['off_time'])
            loom_expansion_steps = len(radii)
            params['start_size'] = original_start_size #  go back to original radius

        tot_steps = int(np.round(tot_duration / screenMs))
        spot_steps = int(np.round(int(params['duration']) / screenMs))
        loom_on_steps = int(np.round(int(params['on_time']) / screenMs))

        frames = np.zeros((3, tot_steps))   # 2d array with x,y position and size of the circle at each frame -> to be filled in

        # define position of circle at all frames
        x_spot_position = np.linspace(positions[0][0], positions[1][0], spot_steps)
        y_spot_position = np.linspace(positions[0][1], positions[1][1], spot_steps)


        frames[0, :spot_steps] = x_spot_position
        frames[0, spot_steps:] = positions[1][0]  # the spot remains in place when it turns into a loom
        frames[1, :spot_steps] = y_spot_position
        frames[1, spot_steps:] = positions[1][1]  

        # define the size at each frame
        if params['modality'].lower() == 'linear':
            frames[2, :spot_steps] = int(params['size']) # constant during expansion
            frames[2, spot_steps:spot_steps+loom_expansion_steps] = np.linspace(int(params['size']), int(params['end_size']), loom_expansion_steps) # expands
        elif params['modality'].lower() == 'exponential':
            frames[2, :spot_steps] = int(params['start_size']) # constant during expansion
            frames[2, spot_steps:spot_steps+loom_expansion_steps] = radii
            params['end_size'] = radii[-1]
        else:
            raise ValueError("Parameter not valid (modality: {})".format(params['modality']))
        frames[2, spot_steps+loom_expansion_steps:spot_steps+loom_expansion_steps+loom_on_steps] =  int(params['end_size']) # constant during ON
        frames[2, spot_steps+loom_expansion_steps+loom_on_steps:] =  0 # no radius during OFF

        # repeat the stimulus N times
        if int(params['repeats']) > 1:
            frames = np.tile(frames, (1, int(params['repeats'])))

        return frames

    def grater(self, wnd, params, screenMs):
        """
        Calculates the data for generating a grating stimulus given some params
        same input as loomer
        """
        dur = int(params['duration'].split(',')[0])
        dur_range = int(params['duration'].split(',')[1])
        if dur_range:
            dur = random.randint(dur-dur_range, dur+dur_range+1)
        numExpSteps = int(np.round(dur / screenMs))
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
        frames_per_sec = round(1000 / screenMs)
        vel = float(params['velocity'])

        # Get phase shift
        if float(params['direction']) <= 0:
            phase_max = -1
        else:
            phase_max = 1
        phase_len = abs(frames_per_sec/vel)  # do a whole period in N frames depending on speed and framerate
        phase = np.linspace(0, phase_max, phase_len)  # with speed of 1 do 1 period per second

        repeats = int(numExpSteps // phase_len)  # repeat phase to get an array longer than the total number of frames
        step_size = np.diff(phase)[0]
        phases = phase.copy()
        for n in range(repeats+1):
            to_add = phases[-1]+step_size
            p = np.add(phase, to_add)
            phases = np.concatenate((phases, p))

        if len(phases) > numExpSteps:
            phases = phases[0:numExpSteps]

        # Get orientation
        orientation = int(params['orientation'])
        if vel < 0:
            orientation += 180  # make it go in the opposite direction

        # get colors
        fg = map_color_scale(int(params['fg color']))

        return pos, screen_size, orientation, fg, phases

    def audio_generator(self, wnd, params, screenMs):
        """ an audio stim is a series of 0 frames just so that we can avoid creating furter stims for the duration
         of the audio file. A -1 is appendend at the first frame to signal the start of the audiofile"""
        numExpSteps = int(np.round(int(params['duration']) / screenMs))
        frames = np.zeros(numExpSteps-1)
        np.insert(frames, 0, -1)
        return None, frames   # returning None so that the output is a tuple like other functions

    def delayer(self, wnd, params, screenMs):
        numExpSteps = int(np.round(int(params['duration']) / screenMs))
        frames = np.zeros(numExpSteps)
        return None, frames  # returning None so that the output is a tuple like other functions

    def complex_fearcon_stim(self, wnd: object, params, screenMs: float, blackout: int = False, grating: int = False,
                             ultrasound: int = False, overlap: int = False) -> object:
        """ Generate a more complex stimulus (combination of different things) specific to the fear-cond experiments
         This stimulus includes (optionally):
         * Blackout period before the proper stimulus onset
         * Grating with variable (optionally): duration, contrast, direction, orientation
         * Overlapping ultrasound stimulus"""



        x, y, width, height = get_position_in_px(wnd, 'top left', 0, return_scree_size=True)
        if params['units'] == 'cm':
            pos = (0, 0)
            screen_size = (width, width)
        else:
            pos = (0, 0)
            screen_size = (width * 2, width * 2)

        screenMs /= 1000

        # Get the total length of the stimulus (# frames) and initialise a pandas df
        if blackout: nframes_blackout = round(int(params['blackout'])/screenMs)
        else: nframes_blackout = 0

        if grating: nframes_grating = int(np.ceil(int(params['grating'])/screenMs))
        else: nframes_grating = 0

        if ultrasound:
            if overlap:
                nframes_overlap = round(int(params['overlap'])/screenMs)
                nframes_ultrasound = round(int(params['ultrasound'])/screenMs) - nframes_overlap
            else: nframes_ultrasound = round(int(params['ultrasound'])/screenMs)
        else: nframes_ultrasound = 0

        nframes_combined = nframes_blackout + nframes_grating + nframes_ultrasound
        features = ['blackout_on', 'grating_on', 'grating_orientation', 'grating_velocity', 'grating_contrast',
                    'grating_direction', 'ultrasound_on']
        framesdf = pd.DataFrame(0, index=np.arange(nframes_combined), columns=features)

        # Start folling in framesdf, start with blackout period
        last_frame = 0
        if blackout:
            framesdf.iloc[last_frame:nframes_blackout]['blackout_on'] = 1
            last_frame = nframes_blackout

        # now the grating
        if grating:
            framesdf[last_frame+1:last_frame+nframes_grating]['grating_on'] = 1
            last_frame = last_frame+nframes_grating

        # And then ultrasound
        if ultrasound:
            if overlap: last_frame -= nframes_overlap

            framesdf[last_frame:last_frame+nframes_ultrasound]['ultrasound_on'] = 1

        """ To display on_frames: 
            import matplotlib.pyplot as plt
            plt.figure()
            [plt.plot(framesdf[col]) for col in features if '_on' in col]
            plt.show()
        """

        # Now define varying grating frames
        """ The varying properties of the grating are passed as a dictionary were each property has the structure
        prop_name: ([x0, x1], s) where x0 and x1 outline the range of values and s the duration of the period in s
        
        if a prop is not specified in the dictionary, or if its value is 'default' the default value will be used   
        
        the dictionary is created based on user selected values in the GUI    
        """

        # Default grating variables and params
        grating_defaults = dict(Orientation=180, Direction=1, Contrast=255)
        grating_variable = {}
        period = int(params['period'])
        for prop in grating_defaults.keys():
            if params[prop] == 'True':
                lims = [int(s) for s in params['{}_lims'.format(prop)].split(' - ')]
                grating_variable[prop] =(lims, period)

        # Update dataframe
        if grating and grating_variable:

            for prop, default in grating_defaults.items():
                framesdf_column_name = [c for c in framesdf.columns if prop.lower() in c]
                if len(framesdf_column_name) > 1: raise Warning('Something went wrong')
                else: framesdf_column_name = framesdf_column_name[0]

                if prop in grating_variable.keys():
                    if isinstance(grating_variable[prop], str):
                        if 'default' == grating_variable[prop]:
                            framesdf.iloc[0:nframes_combined][framesdf_column_name] = default
                            continue
                        else:
                            raise ValueError('Wrong input to stimulus generator')

                    limits, period = grating_variable[prop]
                    nframes_period = np.ceil(period/screenMs)
                    n_periods = int(np.ceil(int(params['grating']) / period))
                    values = np.tile(np.linspace(limits[0], limits[1], nframes_period), n_periods)
                    values = np.concatenate((np.zeros(nframes_blackout), values))
                    values = np.concatenate((values, np.zeros(nframes_ultrasound)))

                    framesdf[framesdf_column_name] = values[:len(framesdf)]
                else:
                    framesdf.iloc[0:nframes_combined][framesdf_column_name] = default
            if params['flash_screen']:
                period = float(params['flash_screen_period'])
                nframes_period = int(np.ceil(period / screenMs))
                n_periods = int(np.ceil(int(params['grating']) / period)/2)

                on_off = np.concatenate((np.ones(nframes_period)*255, np.zeros(nframes_period)))
                values = np.tile(on_off, n_periods)
                values = np.concatenate((values, np.zeros(nframes_ultrasound)))

                blkout = framesdf['blackout_on'].values
                blkout[nframes_blackout:] = values[:len(blkout[nframes_blackout:])]
                framesdf['blackout_on'] = blkout[:len(framesdf)]

        return framesdf, pos, screen_size,  nframes_combined




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
        settings = yaml.load(f, Loader=yaml.FullLoader)
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
    print('Setting up monitor {}'.format(settings['Name']))
    filename =settings['Name']
    setupfile = None
    for f in os.listdir(".\\Screens"):
        if filename == f.split('.')[0]:
            setupfile = f
            break
    if setupfile is None: raise FileNotFoundError("Could not find monitor file with name matching: {}".format(settings['Name']))
    
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
