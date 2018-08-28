from tkinter import *
import os
import yaml
from stimuli import loomer
from Utils import monitor_def
from psychopy import visual
import time
import numpy as np
import matplotlib.pyplot as plt

# Create psychopy window
mon = monitor_def()
# create a window, get mseconds per refresg
mywin = visual.Window([2400, 1200], monitor=mon, color=[1, 1, 1], fullscr=False, units='cm')
screenMs, _, _ = mywin.getMsPerFrame()

# Our GUI is going to be made into a class. If you're writing something simpler you can
# do without the class structure.
class App:
    def __init__(self):
        self.basefld = "C:\\Users\\Federico\\Documents\\GitHub\\VisualStimuli\\stim_setups"
        self.stim_params_widgets = {}
        self.params_topass = {'wnd':mywin, 'screenMs':screenMs}

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

        self.files_list = Listbox(fileUI, height=5)
        self.files_list.grid(column=0, row=1, sticky=(N,W,E,S), columnspan=10, padx=10, pady=10)
        self.files_list.bind('<Double-Button-1>', self.params_file_selected)
        s = Scrollbar(fileUI, orient=VERTICAL, command=self.files_list.yview)
        s.grid(column=10, row=1, sticky=(N, S))
        self.files_list['yscrollcommand'] = s.set

        loadbtn = Button(fileUI, text="Load", command=lambda:self.load_params(self.files_list))
        loadbtn.grid(row=3, column=0, columnspan=6)

        savebtn = Button(fileUI, text="Save")
        savebtn.grid(row=3, column=4, columnspan=6)

        # Create widgets for the run Frame
        launchBtn = Button(runFrm, text="Launch!", foreground='white', background='red',
                           command=lambda:self.launch_stim())
        launchBtn.grid(row=0, column=0, columnspan=10, rowspan=10)

        # Load files for fileUI
        for filename in self.get_params_files():
            self.files_list.insert(END, filename)

        # start the loop
        self.root.mainloop()

    def params_file_selected(self, event):
        self.load_params(self.files_list)

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
                e = Entry(self.stimUI, )
                e.grid(row=idx, column=1)
                e.insert(0, string=str(v))
                e.bind('<Key-Return>', self.entryUpdated)
                self.stim_params_widgets[k] = e
        self.get_stim_params()

    def entryUpdated(self, event):
        self.get_stim_params()

    def get_stim_params(self, load=True):
        if not load:
            return
        for parname, wdgt in self.stim_params_widgets.items():
            self.params_topass[parname] = wdgt.get()

    def prep_stim(self):
        numExpSteps = np.ceil(int(self.params_topass['expand_time']) / self.params_topass['screenMs'])+1
        if self.params_topass['modality'] == 'linear':
            radii = np.linspace(float(self.params_topass['start_size']),
                                   float(self.params_topass['end_size']), numExpSteps)
        elif self.params_topass['modality'] == 'exponential':
            radii = np.geomspace(0.1, float(self.params_topass['end_size']), numExpSteps)

        self.params_topass['radii'] = radii

    def launch_stim(self):
        print('\n\n==================\n==================\n')
        print('Launch Pressed at {}'.format(time.clock()))

        stim_preps, durations, frames = [], [], []

        # self.get_stim_params()
        # self.prep_stim()
        # loomer(self.params_topass, run_stim=False)

        iteration = 0
        while True:

            print('\n\n Iter {}'.format(iteration))
            # Prep stim
            start_prep = time.clock()
            self.get_stim_params()
            self.prep_stim()
            prep = time.clock()-start_prep
            stim_preps.append(prep)
            print('Stim prep: ', prep)

            dur, fr = loomer(self.params_topass)
            durations.append(dur)
            frames.append(fr)
            iteration += 1

            mywin.flip()
            time.sleep(np.random.randint(0, 30)/100)

            if iteration == 100:
                break

        plt.figure()
        plt.hist(durations)

        f, axarr = plt.subplots(3,1)
        axarr[0].plot(durations)
        axarr[0].set(title='mean duration: {}, sdev: {}'.format(round(np.mean(durations), 2),
                                                                round(np.std(durations), 2)))
        axarr[0].axhline(500)

        axarr[1].plot(stim_preps)
        axarr[1].set(title='mean duration: {}, sdev: {}'.format(round(np.mean(start_prep), 2),
                                                                round(np.std(start_prep), 2)))
        axarr[2].plot(frames)
        plt.show()


# Calling the class will execute our GUI.
App()