import numpy as np

from Utils import unit_converter

def loomer(wnd, params, screenMs):
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


def stim_calculator(wnd, params, screenMs):
    # Call subfunctions to generate the stimulus
    if 'loom' in params['type'].lower():
        stim_frames = loomer(wnd, params, screenMs)
    return stim_frames





