from psychopy import monitors
import yaml
import os


def load_yaml(fpath):
    with open(fpath, 'r') as f:
        settings = yaml.load(f)
    return settings


def get_files(fld):
    files = os.listdir(fld)
    files_output = {}
    for f in files:
        if 'yml' in f.split('.')[-1]:
            files_output[f] = os.path.join(fld, f)
    return files_output


def monitor_def(settings):
    my_monitor = monitors.Monitor(name=settings['Name'])
    size = settings['PxSize']
    try:
        my_monitor.setSizePix((int(size.split(', ')[0]), int(size.split(', ')[1])))
    except:
        my_monitor.setSizePix((int(size.split(',')[0]), int(size.split(',')[1])))

    my_monitor.setWidth(int(settings['Width']))
    my_monitor.setDistance(int(settings['Distance']))
    my_monitor.saveMon()
    return my_monitor


def map_color_scale(value, leftMin=0, leftMax=255, rightMin=-1, rightMax=1, reversed=False):
    """
    Psychopy colora work on a scale that ranges from -1 to 1
    The UI allows user to imput colors in a range from 0 to 255
    This functions maps the values from the user input to the psychopy scale
    """
    if reversed:
        # Mapping from PsychoPy colors to 255 RBG values
        leftMin, leftMax, rightMin, rightMax = -1, 1, 0, 255

    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

