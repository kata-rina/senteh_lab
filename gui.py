#!/usr/bin/python3

import sys, re, uart, PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

stop_clicked=0
started=0

#-----------------------------------------------------------------------------------
def get_errorMess(nmr):

    message={
                1:"Pogreška prilikom otvaranja datoteka. Provjerite radni direktorij!",
                2:"Pogreška prilikom uspostavljanja serijske veze! Provjerite serijski priključak!",
                3:"Pogreška prilikom otvaranja datoteka. Provjerite radni direktorij!\nPogreška prilikom uspostavljanja serijske veze! Provjerite serijski priključak!",
                4:"Vrijednost duty cyclea ne smije biti veća od 26860!",
                5:"Pogreška prilikom otvaranja datoteka. Provjerite radni direktorij!\nVrijednost duty cyclea ne smije biti veća od 26860!",
                6:"Pogreška prilikom uspostavljanja serijske veze! Provjerite serijski priključak!\nVrijednost duty cyclea ne smije biti veća od 26860!",
                7:"Pogreška prilikom otvaranja datoteka. Provjerite radni direktorij!\nPogreška prilikom uspostavljanja serijske veze! Provjerite serijski priključak!\nVrijednost duty cyclea ne smije biti veća od 26860!"
    }
    return message.get(nmr)

#-----------------------------------------------------------------------------------
class BasicInfoWindow(QWidget):
    def __init__(self):

        QWidget.__init__(self)
        self.setup()
        self.center()

    def setup(self):

        self.setWindowTitle('Obavijest')
        self.setFixedSize(400, 90)

        layout=QVBoxLayout()
        row1=QHBoxLayout()
        row2=QHBoxLayout()

        ok_button=QPushButton("OK", self)
        ok_button.clicked.connect(self.close)

        second_info=QLabel()
        string='Pokrenuto je mjerenje, senzori su uključeni!'
        second_info.setText(string)

        row1.addWidget(second_info)
        row1.addStretch(1)
        row2.addStretch(1)
        row2.addWidget(ok_button)

        layout.addLayout(row1)
        layout.addLayout(row2)

        self.setLayout(layout)


    def center(self):

        qr=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

#---------------------------------------------------------------------------------
class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.serial = uart.TimerThread()
        self.serial.daemon = True
        self.initUI()

    def initUI(self):

        self.resize(400, 300)
        self.grid=QGridLayout()                                                 # grid manager, rows and columns
        self.setLayout(self.grid)

        self.settings()                                                         # add menu
        self.center()                                                           # center the window on the screen
        self.setWindowTitle('Mjerenje temperature')
        self.show()


    def settings(self):

        settings_box = QGroupBox("Postavke")
        settings_box.setFixedSize(400,285)

        portname_label = QLabel()
        file_dir_label = QLabel()
        mode_label = QLabel()
        duty_label = QLabel()

        self.portname=QLineEdit()                                               # enter serial port
        self.portname.setFixedWidth(250)
        self.portname.setAlignment(Qt.AlignRight)
        self.portname.setText('/dev/ttyACM0')

        self.dir_pick = QLineEdit()                                          # enter working directory
        self.dir_pick.setFixedWidth(250)
        self.dir_pick.setAlignment(Qt.AlignRight)
        file_dir_label.setText("Radni direktorij:")

        portname_label.setText("Serijski priključak:")
        mode_label.setText("Način rada:")
        duty_label.setText('Duty cycle:')

        self.mode_pick = QComboBox()                                            # choose working mode for peltier
        self.mode_pick.setFixedWidth(160)
        self.mode_pick.addItems(['Isključeno', 'Grijanje', 'Hlađenje'])

        self.duty = QLineEdit()
        self.duty.setFixedWidth(160)
        self.duty.setAlignment(Qt.AlignRight)

        self.ok_button = QPushButton("Pokreni", self)                           # start measuring button
        self.ok_button.clicked.connect(self.startMeasuring)

        self.stop_button = QPushButton("Zaustavi", self)                        # stop measuring button
        self.stop_button.clicked.connect(self.stopMeasuring)
        self.stop_button.setEnabled(False)

        self.send_new_duty_button = QPushButton("Pošalji ponovno", self)        # change duty cycle and continue measuring
        self.send_new_duty_button.clicked.connect(self.sendDuty)
        self.send_new_duty_button.setEnabled(False)

        vbox_settings = QVBoxLayout()                                           # add widgets to grid

        hbox_port = QHBoxLayout()
        hbox_dir = QHBoxLayout()
        hbox_mode = QHBoxLayout()
        hbox_duty = QHBoxLayout()
        hbox_button = QHBoxLayout()

        hbox_port.addWidget(portname_label)
        hbox_port.addWidget(self.portname)

        hbox_dir.addWidget(file_dir_label)
        hbox_dir.addWidget(self.dir_pick)

        hbox_mode.addWidget(mode_label)
        hbox_mode.addWidget(self.mode_pick)

        hbox_duty.addWidget(duty_label)
        hbox_duty.addWidget(self.duty)

        hbox_button.addWidget(self.ok_button)
        hbox_button.addWidget(self.send_new_duty_button)
        hbox_button.addWidget(self.stop_button)

        vbox_settings.addLayout(hbox_port)
        vbox_settings.addLayout(hbox_dir)
        vbox_settings.addLayout(hbox_mode)
        vbox_settings.addLayout(hbox_duty)

        vbox_settings.addStretch(2)
        vbox_settings.addLayout(hbox_button)
        settings_box.setLayout(vbox_settings)

        self.grid.addWidget(settings_box)

    def center(self):                                                           # centering the window

        qr=self.frameGeometry()                                                 # get application window dimensions
        cp=QDesktopWidget().availableGeometry().center()                        # get monitor resolution
        qr.moveCenter(cp)                                                       # center the window on the screen
        self.move(qr.topLeft())

    def closeEvent(self, event):                                                # closing the app

        reply=QMessageBox.question(self, 'Doviđenja',
            "Izlazak iz aplikacije?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:                                            # if users wants to close app
            self.serial.pause()                                                 # stop serial communication

            uart.end_communication()
            event.accept()                                                      # close app
        else:                                                                   # else ignore
            event.ignore()

    def startMeasuring(self):                       # start communication with stm32 and open files

        for i in range(7):                          # initialize timer for each sensor
            uart.time_control[i]=0

        p = self.portname.text()                    # read serial port input
        path = self.dir_pick.text()                 # read parent directory for files

        if re.search(r"\s$", path):                 # if it ends with \s (tab, blank space)
            path = re.sub(r"\s$", "", path)         # remove \s

        if not re.search(r"/$",path):               # add / at the end of the path (linux os)
            path = path + '/'

        m = self.mode_pick.currentText()            # read working mode for peltier's element

        if m == 'Hlađenje':                         # if cooling
            m = '-'
        else:                                       # if heating
            m = '+'

        dc = self.duty.text()                       # read duty cycle (max 26860)

        errors = 0                                  # check input, errors set to zero

        if uart.set_configuration(p,115200) == 0:  # open serial port
            errors += 2

        # if uart.open_files(path):                   # open files to save data
        #     errors += 1

        if (int(dc) > 26860):
            errors += 4

        # if duty cycle is OK and serial port opened
        if errors == 0:
            if uart.open_files(path):                   # open files to save data
                errors += 1


        if errors != 0:                             # report errors
            err_msg = QMessageBox.warning(self, 'Pogreška',
                                get_errorMess(errors), QMessageBox.Ok)

        # if there wasn't any errors
        else:
            self.message=BasicInfoWindow()          # report
            self.message.show()
            # uart.open_files(path)

            if m == 'Isključeno':                       # if mode == power off => send + and zeros for duty cycle
                uart.send_duty_cycle('00000', '+')
            else:                                       # else start cooling or heating
                uart.send_duty_cycle(dc, m)

            self.ok_button.setEnabled(False)            # enable or disable buttons
            self.stop_button.setEnabled(True)
            self.send_new_duty_button.setEnabled(True)

            if self.serial.is_alive():                  # if serial communication was established but paused, resume reading from serial port
                self.serial.resume()

            else:                                       # else start serial communication

                self.serial.start()
                self.serial.resume()

    def sendDuty(self):                                 # change working mode for peltier but do not open new files

        m = self.mode_pick.currentText()                # read working mode

        if m == 'Hlađenje':
            m = '-'
        else:
            m = '+'

        dc = self.duty.text()                           # read duty cycle

        if (int(dc) > 26860):
            err_msg = QMessageBox.warning(self, 'Pogreška',
                                get_errorMess(errors), QMessageBox.Ok)

        else:
            if m == 'Isključeno':                           # if mode == power off, send zeros and +
                uart.send_duty_cycle('00000', '+')
            else:                                           # else send duty
                uart.send_duty_cycle(dc, m)

    def stopMeasuring(self):                            # power off and end communication with stm32

        stop_clicked = 1
        uart.send_duty_cycle('00000', '0')              # stop measuring

        self.ok_button.setEnabled(True)
        self.send_new_duty_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        uart.bytes_to_data(uart.packets)                # convert stored bytes to data
        uart.packets = []                               # clear buffer

        for i in range(7):                              # reset timers for sensors
            uart.time_control[i] = 0

        uart.close_files()                              # close opened files
        self.serial.pause()                             # pause serial communication thread


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
