from psychopy import visual, core, event  # import some libraries from PsychoPy
from define_monitor import monitor_def

import numpy as np

mon = monitor_def()

#create a window
mywin = visual.Window([2400, 1200], monitor=mon)
#create some stimuli
grating = visual.GratingStim(win=mywin, mask="circle", units='cm', size=6, pos=[10,1], sf=3)

#draw the stimuli and update the window
while True: #this creates a never-ending loop
    grating.setPhase(0.05, '+')#advance phase by 0.05 of a cycle
    grating.setPos([np.random.randint(0, 5), np.random.randint(0, 5)])
    grating.draw()
    mywin.flip()

    if len(event.getKeys())>0:
        break
    event.clearEvents()

#pause, so you get a chance to see it!
core.wait(3.0)

