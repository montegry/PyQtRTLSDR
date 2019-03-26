import rtlsdr
from PyQt5 import QtWidgets
import sys

"""Server With PyQt gui. To create connection with RTLSDR"""

class MWindow (QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # Elements
        self.line = QtWidgets.QLineEdit("192.168.1.21")
        self.button = QtWidgets.QPushButton("Ok")
        self.form = QtWidgets.QFormLayout()
        self.hbox = QtWidgets.QHBoxLayout()

        # Connections
        self.button.clicked.connect(self.on_button_click)

        # Layout
        self.hbox.addWidget(self.line)
        self.hbox.addWidget(self.button)
        self.form.addRow(self.hbox)
        self.setLayout(self.form)

    def on_button_click(self):
        server = rtlsdr.RtlSdrTcpServer(hostname=self.line.text(), port=111)
        server.run_forever()


app = QtWidgets.QApplication(sys.argv)
mw = MWindow()
mw.show()
sys.exit(app.exec_())
