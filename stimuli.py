from psychopy import visual, core
import time
from threading import Timer as tm

import numpy as np


def loomer(wnd, expand_time=5000, on_time=1000,  startsize=0, endsize=10, units='cm', pos=[0, 0]):
    def expander(stepper):
        loom.radius = radiuses[stepper]

    # Initialise the visual stimulus and screen info
    loom = visual.Circle(wnd, radius=startsize, edges=64, units=units, lineColor='black', fillColor='black')
    screenMs, _, _ = wnd.getMsPerFrame()

    # calculate loom expansion
    startTime = time.clock()
    numExpSteps = np.ceil(expand_time / screenMs)
    radiuses = np.linspace(startsize, endsize, numExpSteps)

    # expand
    stepper = 0
    while True:
        elapsedTime = (time.clock() - startTime)*1000

        # if elapsedTime > expand_time:
        #     print('Radius: {}\n',format(loom.radius))
        #     print('Start time: {}\nEnd time: {}\nElapsed time: {}'.format(startTime, time.clock(),
        #                                                                   elapsedTime))
        #
        #
        #     if loom.radius < endsize:
        #         print('didnt reach target size')
        #     break

        if loom.radius < endsize:
            tm(screenMs, expander(stepper))
            stepper += 1

        else:
            print('reached max size')
            print('Radius: {}\n', format(loom.radius))
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



