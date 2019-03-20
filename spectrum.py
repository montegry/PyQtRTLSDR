from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavTool
from matplotlib.mlab import specgram
import rtlsdr
import sys
import queue


class QtMplPanel(FigureCanvas):
    def __init__(self, parent):
        self.fig = Figure()
        self. gs = self.fig.add_gridspec(3, 1)  # grid for Axes
        self.axe1 = self.fig.add_subplot(self.gs[0, 0])
        self.axe2 = self.fig.add_subplot(self.gs[1, 0])
        self.axe3 = self.fig.add_subplot(self.gs[2, 0])

        self.rtl = rtlsdr.RtlSdrTcpClient(hostname='192.168.1.21', port=111)  # Create a client to get data
        self.rtl.center_freq = 450e6
        self.rtl.rs = 2.4e6
        self.rtl.gain = 0

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.magnitude, self.power, self.phase = [], [], []
        self.data_queue = queue.Queue()
        self.fig.canvas.draw()

    def get_data_from_sdr(self):
        """Getting data from RTL-SDR and put it in Queue"""
        try:
            self.data_queue.put(self.rtl.read_samples(1024*4))
        except Exception as e:
            print(e)

    def get_data_from_file(self, filename):
        """Test function for reading from file"""
        try:
            self.data_queue.put(filename.read(1024*4))
            self.data_queue.put(filename.read(1024*4))
            self.data_queue.put(filename.read(1024*4))
        except Exception as e:
            print("File read error:", e)

    def update_plot(self):
        """Updating Axes with new data, redraw the plot"""
        if self.data_queue.not_empty:
            get_samples = self.data_queue.get()

            self.power, power_len, _ = specgram(list(get_samples), mode='magnitude')
            self.magnitude, magnitude_len, _ = specgram(list(get_samples), mode='psd')
            self.phase, phase_len, _ = specgram(list(get_samples), mode='phase')

            self.axe1.clear()
            self.axe2.clear()
            self.axe3.clear()
            self.axe1.plot(power_len, self.magnitude[:, 0])
            self.axe2.plot(magnitude_len, self.power[:, 0])
            self.axe3.plot(phase_len, self.phase[:, 0])
            self.fig.canvas.draw()


class AppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("SDR data show")
        self.main_widget = QtWidgets.QWidget(self)

        self.qmc = QtMplPanel(self.main_widget)

        ntb = NavTool(self.qmc, self.main_widget)

        but1 = QtWidgets.QPushButton("Hello")
        but1.clicked.connect(self.on_push_button)

        vbox = QtWidgets.QVBoxLayout(self.main_widget)
        vbox.addWidget(self.qmc)
        vbox.addWidget(ntb)
        vbox.addWidget(but1)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.file = open("data.wav", 'rb')
        self.file.read(32)
        self.timerEvent(None)
        self.timer = self.startTimer(500)

    def timerEvent(self, evt):
        """Timer event override. """
        self.qmc.get_data_from_sdr()
        self.qmc.update_plot()

    def on_push_button(self):
        """Stop the timer"""
        self.killTimer(self.timer)


qApp = QtWidgets.QApplication(sys.argv)
aw = AppWindow()
aw.show()
aw.qmc.rtl.close()
sys.exit(qApp.exec_())
