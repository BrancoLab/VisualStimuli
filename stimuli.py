from psychopy import visual, core
import time
import yaml
from threading import Timer as tm

import numpy as np


def loomer(wnd, expand_time=5000, on_time=1000,  startsize=0.1, endsize=10, units='cm', pos=[0, 0],
           mod='linear', loadyaml=False, yaml_file=''):
    def expander(stepper):
        loom.radius = radiuses[stepper]


    if loadyaml:
        with open(yaml_file, 'r') as f:
            settings = yaml.load(f)
        units = settings['units']
        mod = settings['modality']
        on_time = settings['on_time']
        expand_time = settings['expand_time']
        endsize = settings['end_size']

    # Initialise the visual stimulus and screen info
    loom = visual.Circle(wnd, radius=startsize, edges=64, units=units, lineColor='black', fillColor='black')
    screenMs, _, _ = wnd.getMsPerFrame()

    # calculate loom expansion
    startTime = time.clock()
    numExpSteps = np.ceil(expand_time / screenMs)
    if mod == 'linear':
        radiuses = np.linspace(startsize, endsize, numExpSteps)
    elif mod == 'exponential':
        radiuses = np.geomspace(0.1, endsize, numExpSteps)

    # expand
    stepper = 0
    while True:
        if loom.radius < endsize:
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
    if on_time:
        on_startTime = time.clock()
        core.wait(on_time/1000)
        on_elapsedTime = (time.clock() - on_startTime)*1000
        print('On duration: {}'.format(on_elapsedTime))



