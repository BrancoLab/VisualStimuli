from tkinter import *
import os
import yaml
from stimuli import loomer
from define_monitor import monitor_def
from psychopy import visual
import time

# Create psychopy window
mon = monitor_def()

# create a window
mywin = visual.Window([2400, 1200], monitor=mon, color=[1, 1, 1], fullscr=False, units='cm')

# Our GUI is going to be made into a class. If you're writing something simpler you can
# do without the class structure.
class App:
    def __init__(self):
        self.basefld = "C:\\Users\\Federico\\Documents\\GitHub\\VisualStimuli\\stim_setups"
        self.stim_params_widgets = {}

        # This first line initializes our GUI.
        self.root = Tk()

        # This line will force our window on top of all other windows and remain there.
        self.root.call('wm', 'attributes', '.', '-topmost', True)

        # The title in our title bar.
        self.root.title("Stim selector")

        # Define bg color and window geometry
        bgColor = "#708090"
        self.root.configure(bg=bgColor)
        self.root.geometry('750x300+0+0')

        # Define frames to organise content
        fileUI = Frame(self.root)
        fileUI.grid(row=0, column=0, sticky=(N,W,S), padx=60, pady=60)

        self.stimUI = Frame(self.root)
        self.stimUI.grid(row=0, column=1, sticky=(N,E,S), padx=10, pady=60)

        runFrm = Frame(self.root)
        runFrm.grid(row=0, column=2, rowspan=10, sticky=(N,E,S), padx=10, pady=60)

        # Create widgets for fileUI
        Label(fileUI, text="Select file").grid(row=0, sticky=W)

        files_list = Listbox(fileUI, height=5)
        files_list.grid(column=0, row=1, sticky=(N,W,E,S), columnspan=10, padx=10, pady=10)
        s = Scrollbar(fileUI, orient=VERTICAL, command=files_list.yview)
        s.grid(column=10, row=1, sticky=(N, S))
        files_list['yscrollcommand'] = s.set

        loadbtn = Button(fileUI, text="Load", command=lambda:self.load_params(files_list))
        loadbtn.grid(row=3, column=0, columnspan=6)

        savebtn = Button(fileUI, text="Save")
        savebtn.grid(row=3, column=4, columnspan=6)

        # Create widgets for the run Frame
        launchBtn = Button(runFrm, text="Launch!", foreground='white', background='red',
                           command=lambda:self.launch_stim())
        launchBtn.grid(row=0, column=0, columnspan=10, rowspan=10)

        # Load files for fileUI
        for filename in self.get_params_files():
            files_list.insert(END, filename)

        # start the loop
        self.root.mainloop()

    def get_params_files(self):
        allfiles = os.listdir(self.basefld)
        param_files = []

        for f in allfiles:
            if ".yml" in f:
                param_files.append(f)

        return param_files

    def load_params(self, flist):
        sel_file = flist.get(ACTIVE)
        if sel_file:
            with open(os.path.join(self.basefld, sel_file), 'r') as f:
                settings = yaml.load(f)

            for idx, (k,v) in enumerate(settings.items()):
                Label(self.stimUI, text=k).grid(row=idx, sticky=W)
                e = Entry(self.stimUI)
                e.grid(row=idx, column=1)
                e.insert(0, string=str(v))
                self.stim_params_widgets[k] = e

    def launch_stim(self):
        print('Launch Pressed at {}'.format(time.clock()))
        params_topass = {}
        for parname, wdgt in self.stim_params_widgets.items():
            params_topass[parname] = wdgt.get()

        loomer(mywin, params_topass)

# Calling the class will execute our GUI.
App()