from psychopy import monitors


def monitor_def():
    my_monitor = monitors.Monitor(name='Dell P2715Q')
    my_monitor.setSizePix((3840, 2160))
    my_monitor.setWidth(60)
    my_monitor.setDistance(40)
    my_monitor.saveMon()
    return my_monitor