from psychopy import visual, core, event  # import some libraries from PsychoPy
from define_monitor import monitor_def
from stimuli import loomer

# create a monitor
mon = monitor_def()

# create a window
mywin = visual.Window([2400, 1200], monitor=mon, color=[1, 1, 1], fullscr=True, units='cm')

# loom
print('\n\n500')
loomer(mywin, expand_time=500)
print('\n\n2000')
loomer(mywin, expand_time=2000)
print('\n\n200')
loomer(mywin, expand_time=200)


core.wait(2)

# cleanup
mywin.close()
core.quit()
