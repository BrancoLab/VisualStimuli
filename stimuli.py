from psychopy import visual, core
import time
import yaml
from threading import Timer as tm

import numpy as np


def loomer(wnd, params):
    def expander(stepper):
        print('Expansion step at {}'.format(time.clock()))
        loom.radius = radiuses[stepper]

    # Initialise the visual stimulus and screen info
    loom = visual.Circle(wnd, radius=float(params['start_size']), edges=64, units=params['units'],
                         lineColor='black', fillColor='black')
    screenMs, _, _ = wnd.getMsPerFrame()

    # calculate loom expansion
    startTime = time.clock()
    numExpSteps = np.ceil(int(params['expand_time']) / screenMs)
    if params['modality'] == 'linear':
        radiuses = np.linspace(float(params['start_size']), float(params['end_size']), numExpSteps)
    elif params['modality'] == 'exponential':
        radiuses = np.geomspace(0.1,  float(params['end_size']), numExpSteps)

    # expand
    stepper = 0
    while True:
        if loom.radius < float(params['end_size']):
            tm(screenMs, expander(stepper))
            stepper += 1

        else:
            elapsedTime = (time.clock() - startTime) * 1000
            print('reached max size')
            print('Radius: {}'.format(loom.radius))
            print('Start time: {}\nEnd time: {}\nElapsed time: {}'.format(startTime, time.clock(),
                                                                          elapsedTime))
            break

        loom.draw()
        wnd.flip()

    if int(params['on_time']):
        on_startTime = time.clock()
        core.wait(int(params['on_time'])/1000)
        on_elapsedTime = (time.clock() - on_startTime)*1000
        loom.radius=0.00001
        loom.draw()
        wnd.flip()
        print('On duration: {}'.format(on_elapsedTime))




