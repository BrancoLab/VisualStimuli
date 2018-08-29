import numpy as np

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
    pos = unit_converter(wnd, pos[0], in_unit='px', out_unit=unit), unit_converter(wnd, pos[1], in_unit='px', out_unit=unit)

    # Prepare raddi steps
    numExpSteps = np.ceil(int(params['expand_time']) / screenMs) + 1
    if params['modality'] == 'linear':
        radii = np.linspace(float(params['start_size']),
                            float(params['end_size']), numExpSteps)
    elif params['modality'] == 'exponential':
        radii = np.geomspace(0.1, float(params['end_size']), numExpSteps)
    else:
        raise Warning('Couldnt compute loom parameters')
    return pos, radii

def grater(wnd, params, screenMs):
    """
    Calculates the data for generating a grating stimulus given some params
    same input as loomer
    """
    numExpSteps = np.ceil(int(params['duration']) / screenMs)+1
    x, y, width, height = get_position_in_px(wnd, 'top left', 0, return_scree_size=True)
    if params['units'] == 'cm':
        pos = (0, 0)
        screen_size = (width, height)
    else:
        pos = (0, 0)
        screen_size = (width*2, height*2)

    """
    The velocity is set by specifying the phase of the grating at each frame. 
    To do this: create an array that covers an entire phase cycle [0-1] and is 1/n frames long where n depends on the 
    velocity [i.e. phases per second]. The array is then repeat to be as long as the stimulus we are creating
    """
    frames_per_sec = np.ceil(1000 / screenMs)
    vel = float(params['velocity'])
    if vel > 0:
        phase = np.linspace(0, 2, frames_per_sec/vel)
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
    return pos, screen_size, phases


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