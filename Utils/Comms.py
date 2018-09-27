"""
CLASS TO HANDLE COMMS WITH MANTIS
"""


class MantisComms():
    def __init__(self, Main):
        """
        Set up server communication with mantis.

        :param Main reference to App_Main class
        """

        # Hardcoded information about the data received. Useful for
        # reconstructing sweeps from the data chunks
        # TODO: read this info from Mantis
        self.chunkSize = 50
        self.sweepSize = int(0.5 * 25000 / 10)
        self.sweepArray = np.zeros(self.sweepSize)
        self.sweepInfo = [self.chunkSize, self.sweepSize, self.sweepArray]
        self.chunkCounter = 0

        # Setup sockets
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost', 8079))
        self.server.listen(1)
        try:
            self.conn, self.addr = self.server.accept()  # use the same TCP/IP refnum for the experiment
        except:
            raise Warning('Could not establish communication with Mantis')

        # Reference the stim trigger function
        self.stim_trigger_func = App_UI.App_control.launch_stim
        # Referernce to Main App class instance for stim trigger
        self.app_main = Main

    def receive(self):
        # 1st TCP packet: The default 16byte Mantis header  ACTION/CHID/DATASIZE/ e.g @INIT@001@00353@
        cmnd = self.conn.recv(16)
        # convert 'command' type to a normal python string
        MantisHeader = str(cmnd)
        # all strings from Mantis are @ separated so we make it a list
        Header_list = MantisHeader.split('@')
        # delete first dummy element before first @ python autoappends characters here
        # Header_list.pop()
        # delete last dummy element after last @  python autoappends characters here too
        # Header_list.pop(0)
        # the first element is the action to be performed on the data
        action = Header_list[1]
        # the second element indicates the channel number that is transmitted
        ch_id = Header_list[2]
        # the third header element indicates the size of data for the next packet
        size = Header_list[3]
        size = float(size)
        size = int(size)
        # print(size)
        self.conn.sendall(b'size')

        # 2nd TCP packet: wait to read the exact length of data that the Mantis Header indicated
        cmnd = self.conn.recv(size)

        # actions
        # Do the initialization action by parsing the command send by Mantis each time an experiment starts
        if 'INIT' in str(action):

            # delete the 'INIT' tag from the list- this list contains all the initialization data
            # Header_list.pop(0)
            # assume the first element in the list is the sampling frequency and so on
            # fs=Header_list[0]
            # fs=float(fs)
            # print(fs)
            self.conn.sendall(b'INIT ok.')  # feedback to Mantis that the initialization was successful

        # Do the lay action
        elif 'PLAY' in str(cmnd):
            self.conn.sendall(cmnd)

        # Do the quit action
        elif 'QUIT' in str(cmnd):
            self.conn.sendall(b'QUIT ok.')

        # The data sent by Mantis in runtime has the prefix 'DATA'
        elif 'DATA' in str(action):
            MantisData = str(cmnd)
            Mantis_list = MantisData.split('@')
            # delete the 'DATA' prefix from the list to cast to nparray
            Mantis_list.pop(0)
            Mantis_list.pop()
            array = np.asarray(Mantis_list)
            # convert to float nparray for online analysis
            array = array.astype(np.float)

            # Keep track of chuncks received to build sweeps
            if self.chunkCounter < (self.sweepSize - self.chunkSize):
                self.chunkCounter += self.chunkSize
            else:
                self.chunkCounter = 0

            # call function for data processing
            self.stim_trigger_func(self.app_main)

            # TODO: Mantis currently needs to receive something back so we send this
            avg = sum(array) / len(array)
            # returns little endian DBL float 8 byte that Mantis can read and plot
            self.conn.sendall(avg)
