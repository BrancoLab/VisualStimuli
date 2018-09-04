import numpy as np
import math
from Utils import *


def loomer(wnd, params, screenMs):
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
        numExpSteps = np.ceil(int(params['expand_time']) / screenMs) + 1

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


def grater(wnd, params, screenMs):
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


def stim_calculator(wnd, params, screenMs):
    """
    Gets called by UI_app Main() when a stimulus needs to be generated and calls the right subfuction to calculate
    the stimulus parameters

    :param wnd: psychopy window
    :param params:  stimulus parameters, dict. Loaded from YAML file
    :param screenMs:  ms per screeen refresch
    :return:
    """
    # Call subfunctions to generate the stimulus
    if 'loom' in params['type'].lower():
        stim_frames = loomer(wnd, params, screenMs)

    if 'grating' in params['type'].lower():
        stim_frames = grater(wnd, params, screenMs)

    return stim_frames





