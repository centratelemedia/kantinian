# desktop
import os, sys, glob, serial, threading, atexit, time
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import downloadimage

# java
import os.path, subprocess
from subprocess import STDOUT, PIPE

# selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException

class Communicate(QtCore.QObject):
    my_GuiSignal = QtCore.pyqtSignal(str)
    
def downloadImage(callbackFunc, comPort):
    mySrc = Communicate()
    mySrc.my_GuiSignal.connect(callbackFunc)
    thread = threading.current_thread()

    while getattr(thread, "do_run", True):
        try:   
            imgLoc = downloadimage.scan(comPort)    
        except Exception as e:
            imgLoc = None         
        
        mySrc.my_GuiSignal.emit(imgLoc)

class Dashboard(QMainWindow):
    log = None
    imageBox = None
    comboBox = None
    imgFinger = None
    scannedImageLocation = None
    downloadImageThread = None
    driver = None

    def openBrowser(self, new = True):
        # firefox-ESR
        # driver = webdriver.Firefox(executable_path = os.getcwd() + '/geckodriver')
        
        # Chromium-browser ; install chromedriver dulu "sudo apt install chromium-chromedriver"
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        options.binary_location = "/usr/bin/chromium-browser"
        # self.driver = webdriver.Chrome(chrome_options=options)
        self.driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver')
        
        # go to kantinian login page
        self.driver.maximize_window()
        if new:
            self.driver.get('http://kantinian.id/login/login.php') 
        
        # zoom chrome
        self.driver.execute_script("document.body.style.zoom='200%'")
        # zoom firefox-ESR not fixed yet
        # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.ADD).key_up(Keys.CONTROL).perform()
        # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.ADD).key_up(Keys.CONTROL).perform()
        # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.ADD).key_up(Keys.CONTROL).perform()
        # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.ADD).key_up(Keys.CONTROL).perform()
        # ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        # self.driver.find_element_by_tag_name("html").send_keys(Keys.CONTROL + 't')
        # self.driver.find_element_by_tag_name("html").send_keys(Keys.CONTROL + '+')
        # self.driver.find_element_by_tag_name("html").send_keys(Keys.CONTROL + '+')
        # To zoom in
        # self.driver.execute_script("document.body.style.transform='scale(2.5)'")
    
    def __init__(self, parent=None):
        super(Dashboard, self).__init__()
        self.openBrowser()
        
        self.createImageBox()
        self.createConnectionBox()
        self.createControlBox()
        self.createLogBox()
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.imageBox, 0, 0, 2, 0)
        mainLayout.addWidget(self.connectionBox, 0, 1)
        mainLayout.addWidget(self.controlBox, 1, 1)
        mainLayout.addWidget(self.logBox, 2, 0, 2, 2)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnMinimumWidth(0, self.imgFinger.width() + 5)
        
        window = QWidget()
        window.setLayout(mainLayout)
        
        self.setWindowTitle("Kantinian Console")
        self.setCentralWidget(window)
        self.scanPorts()
    
    def createImageBox(self):
        self.imgFinger = QPixmap(os.getcwd() + '/resources/default.png')
        self.imgFinger = self.imgFinger.scaledToHeight(100)
        
        self.imageBox = QLabel()
        self.imageBox.setPixmap(self.imgFinger)
        
    def createConnectionBox(self):
        self.connectionBox = QGroupBox("Connection Box")
        
        self.comboBox = QComboBox()
        self.btnRefresh = QPushButton("Refresh")
        self.btnRefresh.clicked.connect(self.scanPorts)
        
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.comboBox)
        horizontalLayout.addWidget(self.btnRefresh)
        
        self.connectionBox.setLayout(horizontalLayout)
        
    def createControlBox(self):
        self.controlBox = QGroupBox("Control Box")
        
        scanIcon = QPixmap(os.getcwd() + '/resources/scan.png')
        enrollIcon = QPixmap(os.getcwd() + '/resources/add.png')
        startIcon = QPixmap(os.getcwd() + '/resources/start.png')
        scanIcon = scanIcon.scaled(46,46)
        enrollIcon = enrollIcon.scaled(46,46)
        startIcon = startIcon.scaled(46,46)
        
        self.btnScan = QLabel()
        self.btnScan.setPixmap(scanIcon)
        self.btnScan.mousePressEvent = self.scan
        self.btnEnroll = QLabel()
        self.btnEnroll.setPixmap(enrollIcon)
        self.btnEnroll.mousePressEvent = self.enroll
        self.btnStart = QLabel()
        self.btnStart.setPixmap(startIcon)
        self.btnStart.mousePressEvent = self.start
        
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.btnScan)
        horizontalLayout.addWidget(self.btnEnroll)
        horizontalLayout.addWidget(self.btnStart)
        
        self.controlBox.setLayout(horizontalLayout)
        
    def createLogBox(self):
        self.logBox = QGroupBox("LOG")
        
        self.log = QListWidget()
        
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.log)
        
        self.logBox.setLayout(verticalLayout)
    
    def scan(self, event):
        if(self.downloadImageThread != None):
            self.downloadImageThread.do_run = False

        try:
            self.scannedImageLocation = downloadimage.scan(str(self.comboBox.currentText()))
            self.log.insertItem(0, "Success, imgloc: " + self.scannedImageLocation)
            self.imgFinger = QPixmap(self.scannedImageLocation)
            self.imgFinger = self.imgFinger.scaledToHeight(100)
            self.imageBox.setPixmap(self.imgFinger)
            self.execute_java('findMatch','fingerprint.bmp')
        except Exception as e:
            self.log.insertItem(0, "Check your connection")
        
    def enroll(self, event):
        if(self.downloadImageThread != None):
            self.downloadImageThread.do_run = False

        try:
            self.scannedImageLocation = downloadimage.scan(str(self.comboBox.currentText()))
            self.log.insertItem(0, "Success, imgloc: " + self.scannedImageLocation)
            
            self.imgFinger = QPixmap(self.scannedImageLocation)
            self.imgFinger = self.imgFinger.scaledToHeight(100)
            self.imageBox.setPixmap(self.imgFinger)
            result = self.execute_java('img2json','fingerprint.bmp')
            self.log.insertItem(0, "json file has created")
            if(len(result) <= 500):
                self.log.insertItem(0, "Please retry, finger not valid")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Please retry, finger not valid")
                msg.setWindowTitle("Kantinian alert")
                msg.setDetailedText("The details are as follows:")
                msg.exec()
                return

            if (self.driver == None):            
                self.openBrowser(False)
                # self.driver = webdriver.Firefox(executable_path = os.getcwd() + '/geckodriver')
                # To zoom in
                # driver.execute_script("document.body.style.transform='scale(2.5)'")
                # driver.execute_script("document.body.style.zoom='200%'")

            self.driver.get("http://kantinian.id/form/tambahcustomer.php?kartu")
            self.driver.implicitly_wait(5)
            self.driver.maximize_window()
            if(self.driver.current_url == "http://kantinian.id/form/tambahcustomer.php?kartu"):
                elem = self.driver.find_element_by_id("fileupload")
                elem.clear()
                elem.send_keys(os.getcwd() + "/ft.json")

        except:
            self.log.insertItem(0, "Can't connect, check your connection")
            
    def start(self, event):
        if(self.downloadImageThread != None):
            self.downloadImageThread.do_run = False

        if (self.driver == None):            
            self.openBrowser(False)
            # self.driver = webdriver.Firefox(executable_path = os.getcwd() + '/geckodriver')
            # self.driver.implicitly_wait(5)
            # self.driver.maximize_window()
            # self.driver.execute_script("document.body.style.transform='scale(2.5)'")
            # driver.execute_script("document.body.style.zoom='200%'")
            

        self.log.insertItem(0, "Thread started")
        self.downloadImageThread = threading.Thread(name = 'download Image Thread', target=downloadImage, args = (self.downloadImageCallback, str(self.comboBox.currentText())))
        self.downloadImageThread.start()

        self.driver.get("http://kantinian.id/laman/bayar.php?bayar")
        # self.downloadImageCallback("hahaha")

    def scanPorts(self):
        if(self.downloadImageThread != None):
            self.downloadImageThread.do_run = False

        for i in range(0, self.comboBox.count()-1):
            self.comboBox.removeItem(i)
            
        ports = glob.glob('/dev/tty[A-Za-z]*')
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.comboBox.addItem(port)
                self.log.insertItem(0, "detected port:" + port)
                print(port)
            except (OSError, serial.SerialException):
                pass
            
    def compile_java(self):
        subprocess.check_call(['javac','-cp','.:./libjava/*', 'com/company/Main.java'])

    def execute_java(self, *args):
        cmd = ['java','-cp','.:./libjava/*','com.company.Main', args[0], args[1]]
        proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        stdout, stderr = proc.communicate()
        return stdout.decode("utf-8")
    
    def downloadImageCallback(self, msg):
        self.scannedImageLocation = msg
        self.log.insertItem(0, "Success, imgloc: " + self.scannedImageLocation)
        self.imgFinger = QPixmap(self.scannedImageLocation)
        self.imgFinger = self.imgFinger.scaledToHeight(100)
        self.imageBox.setPixmap(self.imgFinger)
        result = self.execute_java('findMatch','fingerprint.bmp')

        if(result.__contains__('null')):
            self.log.insertItem(0, "User not found or try again")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("User not found or try again")
            msg.setWindowTitle("Kantinian alert")
            msg.setDetailedText("The details are as follows:")
            msg.exec()
        else:
            if (self.driver == None):
                self.openBrowser(False)            
                # self.driver = webdriver.Firefox(executable_path = os.getcwd() + '/geckodriver')
                # self.driver.implicitly_wait(5)
                # self.driver.maximize_window()
                # self.driver.execute_script("document.body.style.zoom='200%'")

            idx1 = result.index("\"")
            idx2 = result.index("\"", idx1+1)
            userid = result[idx1+1:idx2]
            print("userid: " + userid)

            if(self.driver.current_url.__contains__('http://kantinian.id/laman/bayar.php')):
                elem = self.driver.find_element_by_id("idcustomer")
                elem.clear()
                elem.send_keys(userid)
                elem = self.driver.find_element_by_id("submitdata")
                elem.click()

            if(self.driver.current_url.__contains__('http://kantinian.id/login/login.php')):
                elem = self.driver.find_element_by_id("login-username")
                elem.clear()
                elem.send_keys(userid)
                elem = self.driver.find_element_by_id("submitdata")
                elem.click()

    def onExit(self):
        self.driver.close()
        self.downloadImageThread.do_run = False
        self.downloadImageThread.join()

        self.log.insertItem(0, "Exitting")
        print("quit")
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Plastique'))
    dashboard = Dashboard()
    dashboard.show()
    atexit.register(dashboard.onExit)
    sys.exit(app.exec_())