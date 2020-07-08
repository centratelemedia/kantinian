#desktop
#install chromedriver: sudo apt install chromium-chromedriver
#install selenium: python3 -m pip install selenium
#install PyQt4: sudo apt install python3-pyqt4

import os, sys, glob, serial, threading, atexit, time
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import adaptor

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException

class Dashboard(QMainWindow):
    log = None
    imageBox = None
    comboBox = None
    imgFinger = None
    scannedImageLocation = None
    driver = None

    url = 'http://192.168.43.193/absensitelkom/finger.php'
    urlAbsen = 'http://192.168.43.193/absensitelkom/api/absen.php?id='

    def __init__(self, parent=None):
        super(Dashboard, self).__init__()

        self.createImageBox()
        self.createControlBox()
        self.createLogBox()
        self.createNumBox()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.imageBox,0,0)        
        mainLayout.addWidget(self.logBox,0,1)
        mainLayout.addWidget(self.controlBox,1,0,1,2)
        mainLayout.addWidget(self.numBox,0,2,2,1)
        
        mainLayout.setColumnStretch(0,1)
        mainLayout.setColumnMinimumWidth(0,self.imgFinger.width()+5)

        window = QWidget()
        window.setLayout(mainLayout)

        self.setWindowTitle('Absensi')
        self.setCentralWidget(window)
        adaptor.loadFromDatabase()
        self.log.insertItem(0, 'registered finger: ' + str(adaptor.f.getTemplateCount()))

    def createImageBox(self):
        self.imgFinger = QPixmap(os.getcwd() + '/resources/default.png')
        self.imgFinger = self.imgFinger.scaledToHeight(100)

        self.imageBox = QLabel()
        self.imageBox.setPixmap(self.imgFinger)
        self.imageBox.mousePressEvent = self.showImage

    def createLogBox(self):
        self.logBox = QGroupBox('Log')
        
        self.log = QListWidget()
        self.log.setMaximumHeight(100)
        
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.log)
        
        self.logBox.setLayout(verticalLayout)
        
    def createControlBox(self):
        self.controlBox = QWidget()
        
        scanIcon = QPixmap(os.getcwd() + '/resources/scan.png')
        enrollIcon = QPixmap(os.getcwd() + '/resources/add.png')
        scanIcon = scanIcon.scaled(46,46)
        enrollIcon = enrollIcon.scaled(46,46)
        
        self.btnScan = QLabel()
        self.btnScan.setPixmap(scanIcon)
        self.btnScan.mousePressEvent = self.scan

        lblUsername = QLabel('NIM: ')
        self.txtUsername = QLineEdit()
        self.btnEnroll = QLabel()
        vEnrollLayout = QVBoxLayout()
        vEnrollLayout.addWidget(lblUsername)
        vEnrollLayout.addWidget(self.txtUsername)
        enrollWidget = QWidget()
        enrollWidget.setMaximumWidth(150)
        enrollWidget.setLayout(vEnrollLayout)
        self.btnEnroll.setPixmap(enrollIcon)
        self.btnEnroll.mousePressEvent = self.enroll

        scanLayout = QHBoxLayout()
        scanLayout.addWidget(self.btnScan)
        scanLayout.setAlignment(Qt.AlignCenter)
        scanContainer = QGroupBox('Scan')
        scanContainer.setMinimumWidth(100)
        scanContainer.setLayout(scanLayout)

        enrollLayout = QHBoxLayout()
        enrollLayout.addWidget(enrollWidget)
        enrollLayout.setAlignment(Qt.AlignCenter)
        enrollLayout.addWidget(self.btnEnroll)
        enrollContainer = QGroupBox('Enroll')
        enrollContainer.setLayout(enrollLayout)

        controlBoxLayout = QHBoxLayout()
        controlBoxLayout.addWidget(scanContainer)
        controlBoxLayout.addWidget(enrollContainer)
        self.controlBox.setLayout(controlBoxLayout)

    def createNumBox(self):
        self.numBox = QGroupBox('Numpad')

        self.b1 = QPushButton('1')
        self.b1.clicked.connect(self.addNum('1'))
        self.b2 = QPushButton('2')
        self.b2.clicked.connect(self.addNum('2'))
        self.b3 = QPushButton('3')
        self.b3.clicked.connect(self.addNum('3'))
        self.b4 = QPushButton('4')
        self.b4.clicked.connect(self.addNum('4'))
        self.b5 = QPushButton('5')
        self.b5.clicked.connect(self.addNum('5'))
        self.b6 = QPushButton('6')
        self.b6.clicked.connect(self.addNum('6'))
        self.b7 = QPushButton('7')
        self.b7.clicked.connect(self.addNum('7'))
        self.b8 = QPushButton('8')
        self.b8.clicked.connect(self.addNum('8'))
        self.b9 = QPushButton('9')
        self.b9.clicked.connect(self.addNum('9'))
        self.b0 = QPushButton('0')
        self.b0.clicked.connect(self.addNum('0'))
        self.bPoint = QPushButton('.')
        self.bPoint.clicked.connect(self.addNum('.'))
        self.bClear = QPushButton('Clear')
        self.bClear.clicked.connect(self.addNum('x'))

        numBoxLayout = QGridLayout()
        numBoxLayout.addWidget(self.b1,1,1)
        numBoxLayout.addWidget(self.b2,1,2)
        numBoxLayout.addWidget(self.b3,1,3)
        numBoxLayout.addWidget(self.b4,2,1)
        numBoxLayout.addWidget(self.b5,2,2)
        numBoxLayout.addWidget(self.b6,2,3)
        numBoxLayout.addWidget(self.b7,3,1)
        numBoxLayout.addWidget(self.b8,3,2)
        numBoxLayout.addWidget(self.b9,3,3)
        numBoxLayout.addWidget(self.b0,4,1)
        numBoxLayout.addWidget(self.bPoint,4,2)
        numBoxLayout.addWidget(self.bClear,4,3)

        self.numBox.setLayout(numBoxLayout)

    def addNum(self, c):
        def clear():
            self.txtUsername.setText('')
                
        def call():
            self.txtUsername.setText(self.txtUsername.text() + c)

        if(c == 'x'): return clear
        else: return call
    
    def openBrowser(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #self.driver = webdriver.Chrome(chrome_options=options)
        self.driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver')
        self.driver.maximize_window()
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 50).until(ec.alert_is_present(), 'timeout')
            alert = self.driver.switch_to.alert
            alert.accept()
            self.driver.close()
        except Exception as ex:
            self.log.insertItem(0, str(ex))

    def showImage(self, event):
            self.scannedImageLocation = adaptor.getImage()
            self.log.insertItem(0, "Success, imgloc: " + self.scannedImageLocation)
            
            self.imgFinger = QPixmap(self.scannedImageLocation)
            self.imgFinger = self.imgFinger.scaledToHeight(100)
            self.imageBox.setPixmap(self.imgFinger)
        
    def scan(self, event):
        try:
            [id, q] = adaptor.searchFinger()
            if(id < 0):
                self.log.insertItem(0, 'Finger Not Found!')
                return
            else:
                self.log.insertItem(0, 'Founded, opening web page')
                self.openBrowser(self.urlAbsen + str(id))
        except Exception as ex:
            print(ex)

    def enroll(self, event):
        try:
            if(self.txtUsername.text().strip() == ''):
                self.log.insertItem(0, 'NIM Cannot empty!')
                return
            
            self.log.insertItem(0, 'Registering NIM: ' + self.txtUsername.text())
            if(adaptor.enroll(str(self.txtUsername.text()))):
                adaptor.loadFromDatabase()
                self.log.insertItem(0, self.txtUsername.text() + ' Registered')
                self.txtUsername.setText('')
            else:
                self.log.insertItem(0, self.txtUsername.text() + ' Not Found')
        except Exception as ex:
            print(ex)

    def onExit(self):
        self.driver.close()
        self.log.insertItem(0, 'Exitting')

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Plastique'))
    dashboard = Dashboard()
    dashboard.show()
    atexit.register(dashboard.onExit)
    sys.exit(app.exec_())
