from psychopy import visual, core
import time
from threading import Timer as tm
import numpy as np

def loomer(params):
    def expander(stepper):
        if stepper == 0:
            print('First expansion step at {}'.format(time.clock()))
        loom.radius = radiuses[stepper]


    wnd = params['wnd']
    radiuses = params['radiuses']

    # Initialise the visual stimulus and screen info
    loom = visual.Circle(wnd, radius=float(params['start_size']), edges=64, units=params['units'],
                         lineColor='black', fillColor='black')

    # calculate loom expansion
    startTime = time.clock()

    # expand
    stepper = 0
    while True:
        if loom.radius < float(params['end_size']):
            tm(params['screenMs'], expander(stepper))
            stepper += 1

        else:
            elapsedTime = (time.clock() - startTime) * 1000
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




