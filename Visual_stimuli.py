import numpy as np


def loomer(params, screenMs):
    # Prepare raddi steps
    numExpSteps = np.ceil(int(params['expand_time']) / screenMs)
    if params['modality'] == 'linear':
        radii = np.linspace(float(params['start_size']),
                            float(params['end_size']), numExpSteps)
    elif params['modality'] == 'exponential':
        radii = np.geomspace(0.1, float(params['end_size']), numExpSteps)
    else:
        radii = []
        raise Warning('Couldnt compute loom parameters')

    return radii


def stim_calculator(params, screenMs):
    # Call subfunctions to generate the stimulus
    if 'loom' in params['Stim type'].lower():
        stim_frames = loomer(params, screenMs)
    return stim_frames





