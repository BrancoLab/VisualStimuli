from psychopy import visual, core
import time


def loomer(params, run_stim=True):
    wnd = params['wnd']
    radii = params['radii']

    # Initialise the visual stimulus and screen info


    if not run_stim:
        loom = visual.Circle(wnd, radius=float(params['start_size']), edges=64, units=params['units'],
                             lineColor='white', fillColor='white')
    else:
        loom = visual.Circle(wnd, radius=float(params['start_size']), edges=64, units=params['units'],
                             lineColor='black', fillColor='black')
    loom.setAutoDraw(True)
    loom.setAutoLog(True)
    # Kee track of duration
    startTime = time.clock()

    # Loop over radii and update stim
    iter_count = 0
    for rad in radii:
        iter_count += 1
        loom.radius = rad
        wnd.flip()

    # Get elapsed time
    elapsedTime = (time.clock() - startTime) * 1000
    print('Start time: {}\nEnd time: {}\nElapsed time: {}'.format(startTime, time.clock(), elapsedTime))

    # let stim on for determined amount of time
    if int(params['on_time']):
        on_startTime = time.clock()
        core.wait(int(params['on_time'])/1000)
        on_elapsedTime = (time.clock() - on_startTime)*1000
        loom.setAutoDraw(False)
        wnd.flip()
        print('On duration: {}'.format(on_elapsedTime))

    del loom
    return elapsedTime, iter_count




