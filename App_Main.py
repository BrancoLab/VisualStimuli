from PyQt5.QtWidgets import *

import time
import sys
from benchmark_results_analysis import *

from App_UI import App_layout, App_control
from Utils import *

####################################################################################################################
####################################################################################################################

class Main_UI(QWidget):
    def __init__(self):
        """
        Initialise variables to control GUI behaviour
        Initialise multi threading
        Call functions that create widgets and take care of the styling the GUI
        start MAIN loop
        """
        super().__init__()
        # Display silent exceptions that cause the gui to crash [Doesn't work all the time]
        sys._excepthook = sys.excepthook
        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback)
            sys.exit(1)
        sys.excepthook = exception_hook

        # ==============================================================================
        # ==============================================================================
        # Load parameters from config file
        config_path = '.\\GUI_cfg.yml'
        self.settings = load_yaml(config_path)

        # Initialise variables
        self.initialise_variables()

        # ==============================================================================
        # START MULTITHREDING - create a thread to handle psychopy stuff in parallel to gui thread
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        main_loop_worker = Worker(self.main_loop)
        self.threadpool.start(main_loop_worker)  # Now the mainloop will keep goin

        # Create GUI UI
        App_layout.create_widgets(self)
        App_layout.define_layout(self)
        App_layout.define_style_sheet(self)

        # Load parameters YAML files
        App_control.get_stims_yaml_files_from_folder(self)

    def initialise_variables(self):
        # Flag to signal when app is ready to launch a stim
        self.ready = False

        # Dictionary of preparred stimuli and name of thr currently displayed stimulus
        self.prepared_stimuli = {}
        self.current_stim_params_displayed = ''

        # Stim parameters that should not be desplayed in the GUI [by name]
        self.ignored_params = ['name', 'units', 'type', 'modality', 'Stim type']

        # Flags to handle stim generation
        """
        stim on            - stim currently being played
        stim               - reference to stimulus object
        stim_frames        - array of frames that are used to update stim
        stim_frame_number  - keep track of progess when looping through stim_frames
        """
        self.stim_on = False
        self.stim, self.stim_frames, self.stim_frame_number = None, False, False

        # Keep track of how long it takes to draw on the psyspy window
        self.last_draw, self.draws = 0, []

        # Flags to handle generation of "signal" square
        """
        A square can be drawn in a corner of the scren (above a LDR, light dependant resistor). The color changes
        when a stim is on so that stim onset and duration can be recorded with ms accuracy
        -square: reference to the square object
        - position: position on the screen (in cm)
        """
        self.square, self.square_pos = None, (0, 0)

        # Flags to control benchmarking (testing the GUI stimulus geneartion)
        """
        - benchmarking: has the benchmarking button been pressed
        -stim duration: keep track of how long each stimulus lasted for
        - benchmark_results: dictionary to store the results of the tests (e.g. stim on duration)
        - number_of_tests: number of stimuli to deliver as part of the test
        """
        self.benchmarking = False
        self.benchmark_results = {'Stim name': None,
                                  'Monitor name': None,
                                  'Stim duration': [],
                                  'Draw duration all': [],
                                  'Draw duration all auto': [],
                                  'Draw duration avg': [],
                                  'Draw duration std': [],
                                  'Number frames per stim': [],
                                  'Number dropped frames': []}
        self.tests_done, self.number_of_tests = 0, 50

    ####################################################################################################################
    """  PSYCHOPY functions  """
    ####################################################################################################################

    def start_psychopy(self):
        t = time.clock()
        from psychopy import visual, logging  # This needs to be here, it can't be outside the threat the window is created from
        print('First psychopy import took: {}'.format((time.clock()-t)*1000))

        # Create monitor object
        monitor, screen_number = monitor_def(self.settings)

        # Get params to create a window from settings
        size = self.settings['wnd_PxSize']  # Get size from the settings (specified in GUI_cfg.yml
        try:
            size = (size.split(', ')[0], size.split(', ')[1])
        except:
            size = (size.split(',')[0], size.split(',')[1])

        col = map_color_scale(int(self.settings['default_bg']))  # Get default background color and update bg widget
        self.params_widgets_dict['Background Luminosity']['Background Luminosity'][1].setText(
            str(int(map_color_scale(col, reversed=True))))  # Update the BG color widget

        # Create a window, get mseconds per screen refresh
        self.psypy_window = visual.Window([int(size[0]), int(size[1])], monitor=monitor, color=[col, col, col],
                                          screen=screen_number,
                                          fullscr=self.settings['fullscreen'], units=self.settings['unit'])
        avg, std, self.screenMs = self.psypy_window.getMsPerFrame(showVisual=True, msg='Testing refresh rate')

        self.psypy_window.refreshThreshold = self.screenMs + 5  # ms per screen + 5 is our threshold for dropped frames
        logging.console.setLevel(logging.WARNING)

        # Get position of the square stimulus [if on]
        if self.settings['square on']:
            self.square_pos = get_position_in_px(self.psypy_window, self.settings['square pos'],
                                                 self.settings['square width'])

        # Update status
        self.ready = 'Ready'

        # Print the results to the console
        print('\n========================================')
        print('''
        Initialised Psychopy window: {}
            with size: {}
        Using monitor: {}\n
        mS per frame: {} std {}\n
        '''.format(self.psypy_window.name, self.psypy_window.size, monitor.name, self.screenMs, std))
        print('\n========================================')

    def change_bg_lum(self):
        # Get bg luminosity and update widow
        lum = self.bg_luminosity
        if not lum:
            lum = 0
        elif int(lum) > 255:
            lum = 255
        else:
            lum = int(lum)
        # update the window color
        lum = map_color_scale(lum)
        prev_lum = self.psypy_window.color[0]
        if not prev_lum == lum:  # only update the background color if we actually changed it
            self.psypy_window.setColor([lum, lum, lum])

    def stim_creator(self):
        """
        Creates and initialises stimuli, including the LDR square
        """
        # Need to import from psychopy here or it gives an error. Takes <<1 ms
        from psychopy import visual

        # Create the visual stimuli
        if self.stim_on:
            params = self.prepared_stimuli[self.current_stim_params_displayed]

            # Create a LOOM
            if 'loom' in params['type'].lower():
                pos = self.stim_frames[0]
                radii = self.stim_frames[1]

                if self.stim is None:
                    self.stim = visual.Circle(self.psypy_window, radius=float(params['start_size']), edges=64,
                                              units=params['units'], pos=pos,
                                              lineColor='black', fillColor='black')
                self.stim.radius = radii[self.stim_frame_number]

            # Create a GRATING
            if 'grating' in params['Stim type'].lower():
                pos = self.stim_frames[0]
                size = self.stim_frames[1]
                phases = self.stim_frames[-1]
                ori = self.stim_frames[2]
                fg_col = self.stim_frames[3]
                if self.stim is None:
                    self.stim = visual.GratingStim(win=self.psypy_window, size=size, pos=pos, ori=ori, color=fg_col,
                                                   sf=params['spatial frequency'], units=params['units'], interpolate=True)
                self.stim.phase = phases[self.stim_frame_number]

        # Create the square for Light Dependant Resistors [change color depending of if other stims are on or not
        if self.settings['square on']:
            if self.stim_on:
                col = map_color_scale(self.settings['square default col'])
            else:
                col = -map_color_scale(self.settings['square default col'])

            if self.square is None:
                self.square = visual.Rect(self.psypy_window, width=self.settings['square width'],
                                      height=self.settings['square width'], pos=self.square_pos, units='cm',
                                      lineColor=[col, col, col], fillColor=[col, col, col])
            else:
                self.square.setFillColor([col, col, col])
            self.square.draw()

    def stim_manager(self):
        """
        When the launch button gets called:
        * The stimulus frames get calculated (e.g. for looms the number of frames it will take to expand and the radii at all steps)
        * This function creates the stimulus object
        * Everytime stim_manager is called it loops over the stimulus frames and updates it
        * When all frames have been played, the window is cleaned
        """
        if self.stim_on:
            if isinstance(self.stim_frames, bool):  # if it is we havent generated the stim frames yet
                # This is due to the fact that the frames are generated in another thread and the
                # that might have not been done by the time that stim_manager is called in the main loop
                return

            # If stim is just being created, start clock to time its duration
            if not self.stim_frame_number:
                self.psypy_window.recordFrameIntervals = True  # Record if we drop frames during stim generation

                self.ready = 'Busy'
                # Update status label
                App_control.update_status_label(self)

                self.stim_timer = time.clock()
                self.stim_creation_timer = time.clock()
                # Initialise variable to keep track of progress during stim update
                self.stim_frame_number = 0

            """
            Two options: create the stim one and then update it using stim_updater or crate a new stim everyframe.
            It looks like creating a new stim every frame [using stim_creator] results in more consistent time
            between frames
            """
            # Create the stimulus object
            self.stim_creator()

            # Keep track of our progress as we update the stim
            self.stim_frame_number += 1

            if self.stim_frame_number == len(self.stim_frames[-1]):  # the last elemnt in stim frames is as long as the duration of the stim
                if self.benchmarking:
                    self.psypy_window.flip()
                elapsed = time.clock() - self.stim_timer

                # We reached the end of the stim frames, keep the stim on for a number of ms and then clean up
                # Print time to last draw and from first draw to last
                print('     ... Last stim draw was {}ms ago\n     ... From stim creation to last draw: {}'.
                      format((time.clock()-self.last_draw)*1000, (self.last_draw - self.stim_timer)*1000))
                self.draws = np.array(self.draws)[1:]

                all_draws, avg_draw, std_draw = self.draws.copy(), np.mean(self.draws), np.std(self.draws)
                print('     ... avg time between draws: {}, std {}'.format(avg_draw, std_draw))

                self.draws = []
                # Print for how long the stimulus has been on
                print('     ... stim duration: {}'.format(elapsed * 1000))

                if self.benchmarking:
                    # Store results
                    print('----->>> {} frames where dropped'.format(self.psypy_window.nDroppedFrames))
                    self.benchmark_results['Stim name'] = self.current_stim_params_displayed
                    self.benchmark_results['Monitor name'] = self.psypy_window.monitor.name
                    self.benchmark_results['Number dropped frames'].append(self.psypy_window.nDroppedFrames)
                    self.benchmark_results['Ms per frame'] = self.screenMs
                    self.benchmark_results['Stim duration'].append(elapsed)
                    self.benchmark_results['Draw duration all'].append(all_draws)
                    self.benchmark_results['Draw duration all auto'].append(self.psypy_window.frameIntervals)
                    self.psypy_window.frameIntervals = []
                    self.benchmark_results['Draw duration avg'].append(avg_draw)
                    self.benchmark_results['Draw duration std'].append(std_draw)
                    self.benchmark_results['Number frames per stim'].append(len(self.stim_frames[-1])-1)
                    self.tests_done += 1

                # After everything is done, clean up
                self.stim = None
                self.stim_frames = False
                self.stim_frame_number = False
                self.stim_on = False

                self.ready = 'Ready'
                # Update status label
                App_control.update_status_label(self)

                print('     ... stim disappeared after {}\n'.format((time.clock()-self.stim_timer)*1000))
        else:
            # Call stim creator anyway so that we can update the color of the LDR sqare if one is present
            self.stim_creator()

    ####################################################################################################################
    """  NI BOARD functions  """
    ####################################################################################################################

    def setup_ni_communication(self):
        # import PyDAQmx as nidaq
        #
        # with nidaq.Task() as t:
        #     t.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        #     t.write(5.0)
        #     t.CreateAIVoltageChan("Dev1/ai0", None, nidaq.DAQmx_Val_Diff, 0, 10, nidaq.DAQmx_Val_Volts, None)
        #     t.CfgSampClkTiming("", 1000, nidaq.DAQmx_Val_Rising, nidaq.DAQmx_Val_FiniteSamps, 5000)
        #     t.StartTask()
        #
        #     t.read
     pass

    ####################################################################################################################
    """    MAIN LOOP  """
    ####################################################################################################################

    def main_loop(self):
        """
        The main loop runs in a separate thread from the GUI

        After initialisng the psychopy window it keeps looping in sync with the screen refresh rate (check out
        window.flip() docs in psychopy)

        At each loop the parameters of the currently loaded stim are checked, then the background is changed
        accordingly and finally the stimuli are managed
        """
        # Start psychopy window
        self.start_psychopy()
        # Update status label
        App_control.update_status_label(self)

        while True:  # Keep loopingn in synch with the screen refresh rate, check the params and update stuff
            if self.benchmarking:
                if self.ready == 'Ready':
                    if self.tests_done >= self.number_of_tests:
                        self.benchmarking = False
                        self.stim_on = False
                        plotting_worker = Worker(plot_benchmark_results, self.benchmark_results)
                        self.threadpool.start(plotting_worker)  # Now the mainloop will keep goin

                    else:
                        # self.stim_on = False
                        self.stim_creator()
                        self.psypy_window.flip()

                        print('\nTest {}'.format(self.tests_done))
                        time.sleep(np.random.randint(2))
                        App_control.launch_stim(self)

            # Update parameters
            if self.ready == 'Ready':
                App_control.read_from_params_widgets(self)

                # Update background
                self.change_bg_lum()

            # Generate, update and clean up stimuli
            self.stim_manager()

            # Update psychopy window
            try:
                if self.settings['square on'] and self.square is not None:
                    self.square.draw()

                if self.stim is not None:
                    self.stim.draw()
                    self.draws.append((time.clock()-self.last_draw)*1000)
                    self.last_draw = time.clock()

                self.psypy_window.flip()
            except:
                print('Didnt flip')

####################################################################################################################
####################################################################################################################
####################################################################################################################
####################################################################################################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Main_application = Main_UI()
    sys.exit(app.exec_())



