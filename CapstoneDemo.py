## This program is designed to streamline adding MIB files to a CSV file directory for the FAA under the guidence of the University of Oklahoma
##
##  Authors: J.Barrett Shannon - jbarrettshannon@gmail.com (UI, PyQT dev)
##           Anthony Immenschuh - anthonyimmen279@gmail.com (Parser Logic dev)
##           Stephen Song - stephensong210@gmail.com (Parser Logic dev)
##
## TODO Might change the way the button that adds a MIB into CSV to a series of switches in the accordion view
## TODO Check to make sure main menu has been close to force close all other windows
##


import sys
import csv
from os import path
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from parser import *

class Application(QMainWindow):
   def __init__(self, parent=None):
        super(Application, self).__init__(parent)

        #Set the dimensions of the window and give it a name
        self.setGeometry(300, 300, 800, 500)
        self.setWindowTitle("MIB to CSV Data Dictionary Converter")

        #this is the popup window
        self.w = None

        #main layout is comprised of two vertical boxes that will fit together side by side on the main canvas
        leftpanel = QVBoxLayout()
        rightpanel = QVBoxLayout()
        
        #This will be the main widget that looks like a CSV
        self.CSVView = QTableWidget()

		#creates widget for opening MIB and connnect it to functionality of fileExplorerMIB
        self.buttonOpenMIB2 = QPushButton("Open MIB")
        self.buttonOpenMIB2.clicked.connect(lambda:self.fileExplorerMIB(self.buttonOpenMIB2))
        #This label will be populated after the user selects a MIB
        self.MIBFileName = QLabel()

        #creates textbox in which MIB text will be displayed
        self.MIBView = QPlainTextEdit()
        self.MIBView.setReadOnly(True)

        #creates tab widget for ListView and and raw text view of MIB
        self.MIBTab = QTabWidget()
        
        #widget for only the text
        self.widgetMIBList = QWidget()
        
        #Add both widgets as tabs
        self.MIBTab.addTab(self.widgetMIBList, "List View")
        self.MIBTab.addTab(self.MIBView, "Raw MIB")


        #creates widget for button to add the select MIB portion to the CSV
        self.addToCSV = QPushButton("Manually Add to CSV Viewer")
        self.addToCSV.clicked.connect(lambda:self.MIBPopUpFunction(self.CSVView))
        
        #populate the leftpanel
        leftpanel.addWidget(self.buttonOpenMIB2)
        leftpanel.addWidget(self.MIBFileName)
        leftpanel.addWidget(self.MIBTab)
        leftpanel.addWidget(self.addToCSV)

        #creates button for opening CSV and connects it to the functionality of fileExplorerCSV
        self.buttonOpenCSV = QPushButton("Open CSV in Viewer")
        self.buttonOpenCSV.clicked.connect(lambda:self.fileExplorerCSV(self.buttonOpenCSV))
        
        #creates button for exporting the CSVView to a CSV
        self.buttonSaveCSV = QPushButton("Export to CSV")
        self.buttonSaveCSV.clicked.connect(lambda:self.saveToCSV(self.buttonSaveCSV))

        #create widget for the search box
        search = QLineEdit()
        search.setPlaceholderText("Search...")
        search.textChanged.connect(self.search)

        #populate the right panel
        rightpanel.addWidget(self.buttonOpenCSV)
        rightpanel.addWidget(search)
        rightpanel.addWidget(self.CSVView)
        rightpanel.addWidget(self.buttonSaveCSV)
        
        #Wrap the layouts into widget objects so that way the splitter can hold them,
        #NOTE: the splitter can ONLY hold widgets, not layouts
        widgetRight = QWidget()
        widgetRight.setLayout(leftpanel)
        widgetLeft = QWidget()
        widgetLeft.setLayout(rightpanel)

        #Add widgets to the splitter, this will allow the user to slide the center of the screen to focus on either
        #   side of the UI
        splitterMain = QSplitter(Qt.Horizontal)
        splitterMain.addWidget(widgetRight)
        splitterMain.addWidget(widgetLeft)

        #Make the splitter(which houses every layout/widget) the only display
        self.setCentralWidget(splitterMain)

	#This is all the functionality for when the user hit the button to load in a MIB
   def fileExplorerMIB(self, b):
        #prompt the use to find the file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileMIB, _ = QFileDialog.getOpenFileName(self,"Select .mib file or swap file type to .txt", "","MIB Files(*.mib);;Text Files(*.txt);;All Files (*)", options=options)

        #If the user cancels the selection process, catch that no info was given, 
        # otherwise the application will crash when it tries to open nothing
        if not fileMIB:
            return
        
        print(fileMIB)

        #openfile and set the earlier unused label to the file name
        MIBtext = open(fileMIB).read()
        self.MIBFileName.setText(path.basename(fileMIB))
        self.MIBView.setPlainText(MIBtext)
        print("file was successfully opened! (", fileMIB, ")" )

        #grab all the MIB objects using the parser
        oidstack = interpretFile(fileMIB)

        #container for the listView
        self.controls = QWidget()
        self.controlsLayout = QVBoxLayout()
        self.widgets = []

        print("CSV in fileExplorerMIB")

        #for every single oid object parsed
        for oid in oidstack:
            item = OIDWidget(oid, self.CSVView)
            self.controlsLayout.addWidget(item)
            self.widgets.append(item)

        #Create the listView for the OIDs
        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.controlsLayout.addItem(spacer)
        self.controls.setLayout(self.controlsLayout)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.controls)

        self.MIBTab.removeTab(0)
        self.MIBTab.insertTab(0, self.scroll, "List View")
        self.MIBTab.setCurrentIndex(0)
 

   #All the functionality for when the user to open a CSV
   def fileExplorerCSV(self,b):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileCSV, _ = QFileDialog.getOpenFileName(self,"Select .csv file or swap to .xlsx file", "","CSV Files(*.csv);;xlsx Files(*.xlsx);;(All Files(*)", options=options)

        #If the user cancels the selection process, catch that no info was given, 
        # otherwise the application will crash when it tries to open nothing
        if not fileCSV:
            return

        print("we tried to open CSV")

        #variable to store all data
        CSVData = []

        #open CSV and store all info in above list
        with open(fileCSV, 'r') as stream:
            for rowdata in csv.reader(stream):
                CSVData.append(rowdata)

        #record dimensions and names of columns
        self.CSVlabels = CSVData.pop(0)
        CSVrows = len(CSVData)
        CSVcols = len(CSVData[0])

        #set CSVView to above dimensions and give names to columns
        self.CSVView.setRowCount(CSVrows)
        self.CSVView.setColumnCount(CSVcols)
        self.CSVView.setHorizontalHeaderLabels(self.CSVlabels)

        #go through the entirety of the list and convert it for the CSV viewing widget
        for row in range (CSVrows):
            for col in range(CSVcols):
                item = QTableWidgetItem(str(CSVData[row][col]))
                #print("adding in: ", item)
                self.CSVView.setItem(row, col, item)

        #TODO Consider adding in the stretch view for the CSVViewer
        #self.CSVView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    #search function for the CSVViewer
   def search(self, s):
        items = self.CSVView.findItems(s, Qt.MatchContains)
        if items:  # we have found something
            item = items[0]  # take the first
            self.CSVView.setCurrentItem(item)

    #export function from the CSVView to an actual CSV
   def saveToCSV(self, b):
        
        #print(self.saveLocation)
        promptReturn = QFileDialog.getSaveFileName(self, 'Save File')

        print("Checking if user correctly filed out prompt: ", promptReturn)
        if promptReturn != ('', ''):
            fileRoot = promptReturn[0] + ".csv"
            print("fileroot valid")

            with open(fileRoot, 'w') as inputStream:
                print("opened file")

                rowdata = []
                writer = csv.writer(inputStream)

                for header in range(len(self.CSVlabels)):
                    rowdata.append(self.CSVlabels[header])
                
                writer.writerow(rowdata)

                for row in range(self.CSVView.rowCount()):
                    rowdata = []
                    for column in range(self.CSVView.columnCount()):
                        item = self.CSVView.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())

                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
        else:
            print("aborted Export process due to no fileLocation")

   ##Pop up functionality, this is needed to relay this Application class to the MIBPopUp Class
   def MIBPopUpFunction(self, CSVView):
        
        #This weird section of if/else statements is to catch if the popup has ever been generated
        #   If this condition is not properly checked with hasattr, it will hard crash the whole application
        #   because initially the popupwindow does not exist. MORE INFO at the bottom of the function
        if(hasattr(self, 'MIBWindow')):

            #Check if the window exists but was simply minimized
            if(self.MIBWindow.status == True):
                print("about to activate the popup")
                print(self.MIBWindow)
                self.MIBWindow.activateWindow()
                self.MIBWindow.raise_()
                print("We reappeared the window")

            #Otherwise, the initial popup was closed and we need to recreate it
            else:
                print("creating replacement window popup")
                self.MIBWindow = MIBPopUp(CSVView)
                self.MIBWindow.setGeometry(QRect(100, 100, 600, 200))
                self.MIBWindow.show()
                self.MIBWindow.move(500, 400)

        else:
            print("creating window popup")
            self.MIBWindow = MIBPopUp(CSVView)
            self.MIBWindow.setGeometry(QRect(100, 100, 600, 200))
            self.MIBWindow.show()
            self.MIBWindow.move(500, 400)
    # The reason this looks so ugly is because the popup window is not able to tell the parent window that it was closed
    #   and thus, it cannot tell the parent to delete the parents record of the childs existence.

#This is used by the MIBListView, each row in the list will use this class
class OIDWidget(QWidget):
    def __init__(self, oid, CSVView):
        super(OIDWidget, self).__init__()
        self.CSVView = CSVView
        self.name = oid.oid_name # Name of widget used for searching.

        
        self.label = QLabel(oid.subr_name)    #  The widget label
        self.infoButton = QPushButton("Info")     # The Info button
        self.infoButton.clicked.connect(lambda:self.infoTrigger(oid))
        self.addButton = QPushButton("Add")   # The Add button
        self.addButton.clicked.connect(lambda:self.saveTrigger(oid, CSVView))

        self.hbox = QHBoxLayout()       # A horizontal layout to encapsulate the above
        self.hbox.addWidget(self.label)   # Add the label to the layout
        self.hbox.addWidget(self.infoButton)    # Add the ON button to the layout
        self.hbox.addWidget(self.addButton)   # Add the OFF button to the layout
        self.setLayout(self.hbox)

    #This allows the buttons within this object to communicate with others
    def infoTrigger(self, oid):
        self.infoWindow = InfoPopUp(oid)
        print("infoWindow trigger activated")

    #This allows the buttons within this object to communicate with others
    def saveTrigger(self, oid, CSVView):
        print("attempting to save")
        print("we are waiting for window to close")

        print("CSVView in saveTrigger1 is")
        print(CSVView)
        self.saveWindow = SavePopUp(oid, CSVView)
        print("window is finished")


    #This allow the MIB side of the program to append to the CSVView
    def saveToCSV(self, oid, CSVView):
        print("CSVView is ")
        print(CSVView)
        CSVAppendingRow = CSVView.rowCount()
        CSVView.insertRow(CSVAppendingRow)

        oid.container = []
        oid.fitToContainer()
        print(oid.container)

        #go through the entirety of the list and convert it for the CSV viewing widget
        #for row in range (CSVrows):
        for col in range(CSVView.columnCount()):
            item = QTableWidgetItem(str(oid.container[col]))
            CSVView.setItem(CSVAppendingRow, col, item)

#This is the display when the user wants to look at the specific info of the OID object
class InfoPopUp(QWidget):
    def __init__(self, oid):
        QWidget.__init__(self)
        self.setWindowTitle("Info window")

        infoWindowLayout = QVBoxLayout()
        infoColumn1 = QVBoxLayout()
        infoColumn2 = QVBoxLayout()
        infoColumn3 = QVBoxLayout()
        infoColumnGroup = QHBoxLayout()

        standardCharacterWidth = 200

        self.selectedLabelResrc = QLabel("Resource Name")
        self.selectedLabelOid_name = QLabel("Oid name")
        self.selectedLabelnumber = QLabel("Oid Number")
        self.selectedLabelSubr_pfx = QLabel("Subr pref")
        self.selectedLabelSubr_name = QLabel("Subr Name")
        self.selectedLabelParam_name = QLabel("Param Name")
        self.selectedLabelTrap = QLabel("Trap")
        self.selectedLabelAlarm = QLabel("Alarm")
        self.selectedLabelModal_type = QLabel("Modal Type")
        self.selectedLabelModal_ctrl1 = QLabel("Modal ctrl 1")
        self.selectedLabelModal_ctrl2 = QLabel("Modal ctrl 2")
        self.selectedLabelStatus = QLabel("Status")
        self.selectedLabelImplemented = QLabel("Implemented")

        self.selectedLineEditResrc = QLineEdit()
        self.selectedLineEditResrc.setText(oid.resrc)
        self.selectedLineEditResrc.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditResrc.setReadOnly(True)
        #self.tempResrc.setPlaceholderText("Enter the Resource be required")
        self.selectedLineEditOid_name = QLineEdit()
        self.selectedLineEditOid_name.setText(oid.oid_name)
        self.selectedLineEditOid_name.setFixedWidth(600)
        self.selectedLineEditOid_name.setReadOnly(True)
        #self.tempOid_name.setPlaceholderText("Enter the OID name to be required")
        self.selectedLineEditnumber = QLineEdit()
        self.selectedLineEditnumber.setText(oid.number)
        self.selectedLineEditnumber.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditnumber.setReadOnly(True)
        #self.tempnumber.setPlaceholderText("Enter the OID number to be required")
        self.selectedLineEditSubr_pfx = QLineEdit()
        self.selectedLineEditSubr_pfx.setText(oid.subr_pfx)
        self.selectedLineEditSubr_pfx.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditSubr_pfx.setReadOnly(True)
        #self.tempSubr_pfx.setPlaceholderText("Enter the subresource prefix to be required")
        self.selectedLineEditSubr_name = QLineEdit()
        self.selectedLineEditSubr_name.setText(oid.subr_name)
        self.selectedLineEditSubr_name.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditSubr_name.setReadOnly(True)
        #self.tempSubr_name.setPlaceholderText("Enter the subresource name to be required")
        self.selectedLineEditParam_name = QLineEdit()
        self.selectedLineEditParam_name.setText(oid.param_name)
        self.selectedLineEditParam_name.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditParam_name.setReadOnly(True)
        #self.tempParam_name.setPlaceholderText("Enter the parameter name to be required")
        self.selectedLineEditTrap = QLineEdit()
        self.selectedLineEditTrap.setText(oid.trap)
        self.selectedLineEditTrap.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditTrap.setReadOnly(True)
        #self.tempTrap.setPlaceholderText("Enter the trap name to be required")
        self.selectedLineEditAlarm = QLineEdit()
        self.selectedLineEditAlarm.setText(oid.alarm)
        self.selectedLineEditAlarm.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditAlarm.setReadOnly(True)

        self.selectedLineEditModal_type = QLineEdit()
        self.selectedLineEditModal_type.setText(oid.modal_type)
        self.selectedLineEditModal_type.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditModal_type.setReadOnly(True)
        
        self.selectedLineEditModal_ctrl1  = QLineEdit()
        self.selectedLineEditModal_ctrl1.setText(oid.modal_ctrl1)
        self.selectedLineEditModal_ctrl1.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditModal_ctrl1.setReadOnly(True)
        
        self.selectedLineEditModal_ctrl2 = QLineEdit()
        self.selectedLineEditModal_ctrl2.setText(oid.modal_ctrl2)
        self.selectedLineEditModal_ctrl2.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditModal_ctrl2.setReadOnly(True)

        self.selectedLineEditStatus = QLineEdit()
        self.selectedLineEditStatus.setText(oid.status)
        self.selectedLineEditStatus.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditStatus.setReadOnly(True)

        self.selectedLineEditImplemented = QLineEdit()
        self.selectedLineEditImplemented.setText(oid.implemented)
        self.selectedLineEditImplemented.setFixedWidth(standardCharacterWidth)
        self.selectedLineEditImplemented.setReadOnly(True)
        
        nameBox = QVBoxLayout()

        nameBox.addWidget(self.selectedLabelOid_name)
        nameBox.addWidget(self.selectedLineEditOid_name)
       
        infoColumn1.addWidget(self.selectedLabelnumber)
        infoColumn1.addWidget(self.selectedLineEditnumber)
        infoColumn1.addWidget(self.selectedLabelResrc)
        infoColumn1.addWidget(self.selectedLineEditResrc)
        infoColumn1.addWidget(self.selectedLabelSubr_name)
        infoColumn1.addWidget(self.selectedLineEditSubr_name)
        infoColumn1.addWidget(self.selectedLabelSubr_pfx)
        infoColumn1.addWidget(self.selectedLineEditSubr_pfx)

        infoColumn2.addWidget(self.selectedLabelStatus)
        infoColumn2.addWidget(self.selectedLineEditStatus)
        infoColumn2.addWidget(self.selectedLabelParam_name)
        infoColumn2.addWidget(self.selectedLineEditParam_name)
        infoColumn2.addWidget(self.selectedLabelTrap)
        infoColumn2.addWidget(self.selectedLineEditTrap)
        infoColumn2.addWidget(self.selectedLabelAlarm)
        infoColumn2.addWidget(self.selectedLineEditAlarm)

        infoColumn3.addWidget(self.selectedLabelModal_type)
        infoColumn3.addWidget(self.selectedLineEditModal_type)
        infoColumn3.addWidget(self.selectedLabelModal_ctrl1)
        infoColumn3.addWidget(self.selectedLineEditModal_ctrl1)
        infoColumn3.addWidget(self.selectedLabelModal_ctrl2)
        infoColumn3.addWidget(self.selectedLineEditModal_ctrl2)
        infoColumn3.addWidget(self.selectedLabelImplemented)
        infoColumn3.addWidget(self.selectedLineEditImplemented)

        infoColumnGroup.addLayout(infoColumn1)
        infoColumnGroup.addLayout(infoColumn3)
        infoColumnGroup.addLayout(infoColumn2)

        infoWindowLayout.addLayout(nameBox)
        infoWindowLayout.addLayout(infoColumnGroup)

        self.setLayout(infoWindowLayout)
        
        
        self.setGeometry(QRect(100, 100, 600, 200))
        self.move(500, 400)
        self.show()
        self.setWindowTitle("Info window")
        print("we tried to open the info window")  

#This is the pop up that is called from the trigger activated when the user is trying to add a OID from the ListView
class SavePopUp(QWidget):
    def __init__(self, oid, CSVView):
        QWidget.__init__(self)
        self.setWindowTitle("Info window")

        self.frequency = QLineEdit()
        self.frequency.setPlaceholderText("Enter the frequency (polling rate)")
        self.resrc = QLineEdit()
        self.resrc.setPlaceholderText("Enter the resource name")
        self.comments = QPlainTextEdit()
        self.comments.setPlaceholderText("Add additional comments")
        self.buttonSave = QPushButton("Add")
        self.implemented = QCheckBox()
        self.implemented.setText("Has this been implemented?")

        self.buttonSave.clicked.connect(lambda:self.saveTriggerPop( oid=oid, CSVView=CSVView))

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.resrc)
        self.layout.addWidget(self.frequency)
        self.layout.addWidget(self.implemented)
        self.layout.addWidget(self.comments)
        self.layout.addWidget(self.buttonSave)

        self.setLayout(self.layout)

        self.setGeometry(QRect(100, 100, 600, 200))
        self.move(500, 400)
        self.show()
        self.setWindowTitle("Save window")
        print("we tried to open the save window")
    
    #This is the trgger that is activate once the user has confirmed their additions onto the OID they want to add
    def saveTriggerPop(self, oid, CSVView):
        
        oid.poll_freq = self.frequency.text()
        oid.resrc = self.resrc.text()
        oid.comments = self.comments.toPlainText() + "\n" + oid.comments

        if self.implemented.isChecked():
            oid.implemented = "yes"
        else:
            oid.implemented = "no"

        print("freq")
        print(oid.poll_freq)
        print("resource name")
        print(oid.resrc)
        print("comments")
        print(oid.comments)

        print("CSVView in saveTrigger2 is")
        print(CSVView)
        OIDWidget.saveToCSV(self, oid, CSVView)
        self.close()




#This is the functionality of the MIB Pop Up window when you try and manually add to the CSV
class MIBPopUp(QWidget):
    def __init__(self, CSVView):
        QWidget.__init__(self)

        self.setWindowTitle("Choose Severity and Frequency")
        self.status = True
        windowLayout = QHBoxLayout()

        #These window names are no longer accurate, my b
        leftWindow = QVBoxLayout()
        centerWindow = QVBoxLayout()
        rightWindow = QVBoxLayout()

        #The FAA requested they have these 3 fields manually filed out
        #Its possible that severity and frequency need to be set as selectable thresholds not manually entered as strings
        self.frequency = QLineEdit()
        self.frequency.setPlaceholderText("Enter the frequency (polling rate)")
        self.oid_name = QLineEdit()
        self.oid_name.setPlaceholderText("Enter the name of the  to be required")
        self.comments = QPlainTextEdit()
        self.comments.setPlaceholderText("Add additional comments")

        #Create the button and connect to functionality to add selected MIB info to CSV Viewer
        self.buttonAddtoCSV = QPushButton("Add to CSV")

        #Create wdigets for all OID values
        self.tempResrc = QLineEdit()
        self.tempResrc.setPlaceholderText("Resource")
        self.tempOid_name = QLineEdit()
        self.tempOid_name.setPlaceholderText("OID name")
        self.tempnumber = QLineEdit()
        self.tempnumber.setPlaceholderText("OID number")
        self.tempSubr_pfx = QLineEdit()
        self.tempSubr_pfx.setPlaceholderText("subresource prefix")
        self.tempSubr_name = QLineEdit()
        self.tempSubr_name.setPlaceholderText("subresource name")
        self.tempParam_name = QLineEdit()
        self.tempParam_name.setPlaceholderText("parameter name")
        self.tempTrap = QLineEdit()
        self.tempTrap.setPlaceholderText("trap name")
        self.tempAlarm = QLineEdit()
        self.tempAlarm.setPlaceholderText("alarm name")
        self.tempModal_type = QLineEdit()
        self.tempModal_type.setPlaceholderText("modal type")
        self.tempModal_ctrl1 = QLineEdit()
        self.tempModal_ctrl1.setPlaceholderText("modal control 1")
        self.tempModal_ctrl2 = QLineEdit()
        self.tempModal_ctrl2.setPlaceholderText("modal control 2 ")
        self.tempStatus = QLineEdit()
        self.tempStatus.setPlaceholderText("status ")
        self.tempImplemented = QLineEdit()
        self.tempImplemented.setPlaceholderText("implemented (yes/no)")

        self.buttonAddtoCSV.clicked.connect(lambda:self.addTrigger(self, CSVView))

        leftWindow.addWidget(self.frequency)
        leftWindow.addWidget(self.comments)
        leftWindow.addWidget(self.buttonAddtoCSV)

        centerWindow.addWidget(self.tempImplemented)
        centerWindow.addWidget(self.tempResrc)
        centerWindow.addWidget(self.tempOid_name)
        centerWindow.addWidget(self.tempnumber)
        centerWindow.addWidget(self.tempParam_name)
        centerWindow.addWidget(self.tempSubr_name)
        rightWindow.addWidget(self.tempTrap)
        rightWindow.addWidget(self.tempAlarm)
        rightWindow.addWidget(self.tempModal_type)
        rightWindow.addWidget(self.tempModal_ctrl1)
        rightWindow.addWidget(self.tempModal_ctrl2)
        rightWindow.addWidget(self.tempStatus)
        

        #Add both window panes into the windowlayout
        windowLayout.addLayout(rightWindow)
        windowLayout.addLayout(centerWindow)
        windowLayout.addLayout(leftWindow)

        #push the layout onto the canvas
        self.setLayout(windowLayout)


    #This is the trigger for when the user has confirmed all entries for the 
    def addTrigger(self, b, CSVView):

        tempOid = oid()


        tempOid.resrc = self.tempResrc.text()
        tempOid.oid_name = self.tempOid_name.text()
        tempOid.number = self.tempnumber.text()
        tempOid.poll_freq = self.frequency.text()
        tempOid.subr_pfx = self.tempSubr_pfx.text()
        tempOid.subr_name = self.tempSubr_name.text()
        tempOid.param_name = self.tempParam_name.text()
        tempOid.trap = self.tempTrap.text()
        tempOid.alarm = self.tempAlarm.text()
        tempOid.modal_type = self.tempModal_type.text()
        tempOid.modal_ctrl1 = self.tempModal_ctrl1.text()
        tempOid.modal_ctrl2 = self.tempModal_ctrl2.text()
        tempOid.status = self.tempStatus.text()
        tempOid.implemented = self.tempImplemented.text()
        tempOid.comments = self.comments.toPlainText()

        print("freq")
        print(tempOid.poll_freq)
        print("severity")
        print(tempOid.severity)
        print("comments")
        print(tempOid.comments)

        self.saveToCSV(self, oid=tempOid, CSVView=CSVView)
        self.close()


    def saveToCSV(self, b, oid, CSVView):

        CSVAppendingRow = CSVView.rowCount()
        CSVView.insertRow(CSVAppendingRow)

        print("oid in Save")
        print(oid)

        oid.container = []
        oid.fitToContainer()
        print(oid.container)

        #go through the entirety of the list and convert it for the CSV viewing widget
        #for row in range (CSVrows):
        for col in range(CSVView.columnCount()):
            item = QTableWidgetItem(str(oid.container[col]))
            CSVView.setItem(CSVAppendingRow, col, item)

    def closeEvent(self, event):
        # do stuff
        self.status = False
        print("we tried to delete the window")
        event.accept()

#There is an oid parser that has the same object, but I'm scared what breaks if I take this out
class oid:

    #def init(self):
    def __init__(self):

        self.container = []

        self.resrc = None
        #self.oid_name = 'oid name'
        self.oid_name = None
        self.number = None
        self.poll_freq = None
        self.subr_pfx = None
        self.subr_name = 'subr Name'
        self.param_name = None
        self.trap = None
        self.alarm = None
        self.modal_type = None
        self.modal_ctrl1 = None
        self.modal_ctrl2 = None
        self.status = None
        self.implemented = None
        self.severity = ""
        self.comments = None

    def fitToContainer(self):
        self.container.append(self.resrc)
        self.container.append(self.oid_name)
        self.container.append(self.number)
        self.container.append(self.poll_freq)
        self.container.append(self.subr_pfx)
        self.container.append(self.subr_name)
        self.container.append(self.param_name)
        self.container.append(self.trap)
        self.container.append(self.alarm)
        self.container.append(self.modal_type)
        self.container.append(self.modal_ctrl1)
        self.container.append(self.modal_ctrl2)
        self.container.append(self.status)
        self.container.append(self.implemented)
        self.container.append(self.comments)



def main():
   app = QApplication(sys.argv)
   #app.setApplicationName("MIB to CSV Data Dictionary Converter")
   ex = Application()
   ex.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()