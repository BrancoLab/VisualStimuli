import numpy as np

class Manager:
    def __init__(self, wnd, screenMs, params):
        self.wnd = wnd
        self.params = params
        self.screenMs = screenMs
        if 'loom' in params['Stim type'].lower():
            self.loomer()

    def loomer(self, run_stim=True):
        # Prepare raddi steps
        numExpSteps = np.ceil(int(self.params['expand_time']) / self.screenMs) + 1
        if self.params['modality'] == 'linear':
            radii = np.linspace(float(self.params['start_size']),
                                float(self.params['end_size']), numExpSteps)
        elif self.params['modality'] == 'exponential':
            radii = np.geomspace(0.1, float(self.params['end_size']), numExpSteps)
        else:
            radii = []
            raise Warning('Couldnt compute loom parameters')

        self.stim_frames = radii




