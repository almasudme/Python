###
import sys
from PyQt5 import QtWidgets,QtCore,QtGui
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE,getoutput,call
import os
import shutil
import re
# from subprocess import call,Popen

VALCR_XML_PATH="valcr.xml"

class Window(QtWidgets.QWidget):

    anchors = [' ', 'ELEM', 'FREQ', 'COMP_EIGEN', 'POINT', 'PANEL', 'LOADSTEP', 'TIME', 'GROUP'\
    , 'AML', 'RECORD', 'PGRID']
    at = [' ', 'element','ply', 'source', 'point', 'grid', 'fibd', 'ring']
    at1 = [' ', 'element','ply', 'source', 'point', 'grid', 'fibd', 'ring']
    at2 = [' ', 'element','point', 'grid', 'fibd', 'fibl', 'var', 'edge', 'fiber']
    at3 = [' ', 'edge']
    at4 = [' ', 'ft']
    

    def __init__(self):
        super().__init__()
        dict_valcr = self.loadXml(VALCR_XML_PATH)
        self.keys, self.complex , self.attrib = self.scanXml(dict_valcr)
        self.init_ui()
        self.show()

    def init_ui(self):
        '''
        The following part introduces/Initializes all the buttons and GUI objects. Needed for the GUI.
        We shall later add them to a Layout and place the layout in the window.
        '''

        self.criteria_string = 'VALUE['
        self.setWindowTitle('Validation Criteria')
        self.comboBoxHeader=QtWidgets.QComboBox(self)
        self.lBlock = QtWidgets.QLabel('Select your Block Header from the list above:')
        self.le = QtWidgets.QLineEdit('')
        self.b1 = QtWidgets.QPushButton('Start')
        self.b2 = QtWidgets.QPushButton('Clear')
        self.lCrit = QtWidgets.QLabel('Click \"Start\" to populate box below.')
        self.lwCrit = QtWidgets.QListWidget(self)
        self.lwCrit.setEnabled(False)
        self.lAnchor = QtWidgets.QLabel('Anchor :')
        self.cbAnchor = QtWidgets.QComboBox(self)
        self.leAnchor = QtWidgets.QLineEdit()
        self.leAnchor.setEnabled(False)
        self.leCritRe = QtWidgets.QLineEdit('Real Part')
        self.leCritRe.setEnabled(False)
        self.leCritIm = QtWidgets.QLineEdit('Imaginary Part')
        self.leCritIm.setEnabled(False)
        self.lEq = QtWidgets.QLabel('=')
        self.gb1 = QtWidgets.QGroupBox('Row/Grid point')
        self.gb2 = QtWidgets.QGroupBox('More specifications to locate the information:')
        self.lAt = QtWidgets.QLabel('at :')
        self.lGenerate = QtWidgets.QPushButton('Generate Criteria')
        self.leCriteria = QtWidgets.QLineEdit('Your Syntax here')
        self.leCriteria.setEnabled(False)
        self.btnClose = QtWidgets.QPushButton('close') 

        '''
        Palcing layouts. We plan on creating and populating all the horizontal layouts first.
        Then we place the horizontal layouts in a Virtical layout one after another.
        We shall include some widgets in between.
        '''
        header_box = QtWidgets.QHBoxLayout()
        header_box.addWidget(self.comboBoxHeader)
        aBlocks=list(self.keys.keys())
        for i in range(len(aBlocks)):
            self.comboBoxHeader.addItem(aBlocks[i])

        h1_box = QtWidgets.QHBoxLayout()
        h1_box.addWidget(self.le)
        h1_box.addWidget(self.b1)
        h1_box.addWidget(self.b2)

        self.b1.clicked.connect(self.bgetCode)
        self.b2.clicked.connect(self.clearBlock)
        self.lGenerate.clicked.connect(self.gen_click)
        self.btnClose.clicked.connect(self.click2close)

        h3_box = QtWidgets.QGridLayout()
        h3_box.addWidget(self.lAnchor,0,0)
        h3_box.addWidget(self.cbAnchor,0,1)
        h3_box.addWidget(self.leAnchor,0,2)

        for i in range(len(self.anchors)):
            self.cbAnchor.addItem(self.anchors[i])
        self.lSubcase = QtWidgets.QLabel('Subcase = ')
        self.sbSubcase = QtWidgets.QSpinBox(self)
        self.sbSubcase.setEnabled(False)

        h3_box.addWidget(self.lSubcase,0,3)
        h3_box.addWidget(self.sbSubcase,0,4)

        self.cbAt = QtWidgets.QComboBox(self)
        self.leAt = QtWidgets.QLineEdit()
        self.leAt.setEnabled(False)
        self.cbAt.resize(200, 30)
        self.leAt.resize(200, 30)
        self.lAt = QtWidgets.QLabel('at = ')
        h3_box.addWidget(self.lAt,1,0)
        h3_box.addWidget(self.cbAt,1,1)
        h3_box.addWidget(self.leAt,1,2)
        

        for i in range(len(self.at)):
            self.cbAt.addItem(self.at[i].upper())

        self.checkboxTol = QtWidgets.QCheckBox('Tolerance')
        self.leTol = QtWidgets.QLineEdit()
        self.leTol.setEnabled(False)
        self.lTol = QtWidgets.QLabel('%')
        h3_box.addWidget(self.checkboxTol,1,3)
        h3_box.addWidget(self.leTol,1,4)
        h3_box.addWidget(self.lTol,1,5)
        self.checkboxTol.stateChanged.connect(self.clickBox)

        #at1
        self.cbAt1 = QtWidgets.QComboBox(self)
        self.leAt1 = QtWidgets.QLineEdit()
        self.leAt1.setEnabled(False)
        h4_box = QtWidgets.QHBoxLayout()
        h4_box.addWidget(self.cbAt1)
        h4_box.addWidget(self.lEq)
        h4_box.addWidget(self.leAt1)
        #self.at2 = at2

        for i in range(len(self.at1)):
            self.cbAt1.addItem(self.at1[i].upper())
        #at2
        self.cbAt2 = QtWidgets.QComboBox(self)
        self.leAt2 = QtWidgets.QLineEdit()
        self.leAt2.setEnabled(False)
        
        h4_box.addWidget(self.cbAt2)
        h4_box.addWidget(self.lEq)
        h4_box.addWidget(self.leAt2)
        #self.at2 = at2

        for i in range(len(self.at2)):
            self.cbAt2.addItem(self.at2[i].upper())

        #at3
        h5_box = QtWidgets.QHBoxLayout()
        self.cbAt3 = QtWidgets.QComboBox(self)
        self.leAt3 = QtWidgets.QLineEdit()
        self.leAt3.setEnabled(False)

        
        h5_box.addWidget(self.cbAt3)
        h5_box.addWidget(self.lEq)
        h5_box.addWidget(self.leAt3)
        #self.at3 = at3

        for i in range(len(self.at3)):
            self.cbAt3.addItem(self.at3[i].upper())

        #at4
        self.cbAt4 = QtWidgets.QComboBox(self)
        self.leAt4 = QtWidgets.QLineEdit()
        self.leAt4.setEnabled(False)

        h5_box.addWidget(self.cbAt4)
        h5_box.addWidget(self.lEq)
        h5_box.addWidget(self.leAt4)
        #self.at4 = at4

        for i in range(len(self.at4)):
            self.cbAt4.addItem(self.at4[i].upper())

        h2_box = QtWidgets.QHBoxLayout()
        h2_box.addStretch()
        h2_box.addWidget(self.lwCrit)
        h2_box.addStretch()


        '''
        We shall put all the horizontal layouts now in a verical layout.
        '''
        
        v_box = QtWidgets.QVBoxLayout()
        v_box.addLayout(header_box)
        v_box.addWidget(self.lBlock)
        v_box.addLayout(h1_box)
        #v_box.addWidget(self.cbComplex)
        v_box.addWidget(self.lCrit)
        
        v_box.addLayout(h2_box)

        v_at_box = QtWidgets.QVBoxLayout()
        v1_box = QtWidgets.QVBoxLayout()
        v1_box.addLayout(h3_box)
        self.gb1.setLayout(v1_box)
        v_at_box.addWidget(self.gb1)
        

        v2_box = QtWidgets.QVBoxLayout()
        v2_box.addLayout(h4_box)
        v2_box.addLayout(h5_box)
        
        self.gb2.setLayout(v2_box)
        v_at_box.addWidget(self.gb2)

        '''
        The Expected value that needs to be checked
        '''
        hvaltype_box = QtWidgets.QHBoxLayout()
        self.radioBtnValue = QtWidgets.QRadioButton('Value')
        self.radioBtnAbsValue = QtWidgets.QRadioButton('Absolute Value')
        self.radioBtnMax = QtWidgets.QRadioButton('MAX')
        self.radioBtnConsistent = QtWidgets.QRadioButton('Consistent')
        self.radioBtnMsg = QtWidgets.QRadioButton('Warning Message')
        hvaltype_box.addWidget(self.radioBtnValue)
        self.radioBtnValue.setChecked(True)
        hvaltype_box.addWidget(self.radioBtnAbsValue)
        hvaltype_box.addWidget(self.radioBtnMax)
        hvaltype_box.addWidget(self.radioBtnConsistent)
        hvaltype_box.addWidget(self.radioBtnMsg)
        self.radioBtnMsg.setEnabled(False)

        hval_box = QtWidgets.QHBoxLayout()
        hval_box.addWidget(self.leCritRe)
        hval_box.addWidget(self.leCritIm)

        v_val_box = QtWidgets.QVBoxLayout()
        v_val_box.addLayout(hvaltype_box)
        v_val_box.addLayout(hval_box)
        self.gb3 = QtWidgets.QGroupBox('Criteria: Expected Value')
        self.gb3.setObjectName("ColoredGroupBox")  # Changed here...
        self.gb3.setStyleSheet("QGroupBox#ColoredGroupBox { border: 2px solid Black;}")  # ... and here
        #self.gb3.setFixedWidth(100)

        
        self.gb3.setLayout(v_val_box)
        v_at_box.addWidget(self.gb3)
        h2_box.addLayout(v_at_box)

        hg_box = QtWidgets.QHBoxLayout()
        hg_box.addStretch()
        hg_box.addWidget(self.lGenerate)

        v_box.addLayout(hg_box)

        v_box.addWidget(self.leCriteria)

        '''
        update deck
        '''
        hlayout_update_deck = QtWidgets.QHBoxLayout()
        self.btnUpdateDeck = QtWidgets.QPushButton('Update Deck: ')
        self.lineEditDeck = QtWidgets.QLineEdit('d:/workdir/valcr/Test/foo.dat')
        hlayout_update_deck.addWidget(self.btnUpdateDeck)
        hlayout_update_deck.addWidget(self.lineEditDeck)

        v_box.addLayout(hlayout_update_deck)
        

        self.btnUpdateDeck.clicked.connect(self.update_deck_tab1)

        '''
        Validate
        '''
        hlayout_validate = QtWidgets.QHBoxLayout()
        self.btnValidate = QtWidgets.QPushButton('Validate: ')
        self.lineEditValidate = QtWidgets.QLineEdit('d:/workdir/valcr/Test/foo')
        hlayout_validate.addWidget(self.btnValidate)
        hlayout_validate.addWidget(self.lineEditValidate)

        v_box.addLayout(hlayout_validate)

        self.btnValidate.clicked.connect(self.validate)

        '''
        Close button 
        '''
        close_box = QtWidgets.QHBoxLayout()
        close_box.addStretch()
        close_box.addWidget(self.btnClose)
        v_box.addLayout(close_box)

        '''
        Creating Tabs
        '''
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()	
        self.tab2 = QtWidgets.QWidget()

        self.tabs.addTab(self.tab1,"Add New Criteria")
        self.tabs.addTab(self.tab2,"Edit Old Criteria")
        self.tab1.setLayout(v_box)

        '''#==========================================
        Tab 2 items
        '''#==========================================
        self.input_deck = None
        self.criteria =None
        self.inView = False

        self.radBtnSource = QtWidgets.QRadioButton("SCM [doug] ")
        self.radBtnSource.setToolTip("A perforce view is already set up.")
        self.radBtnSource.toggled.connect(self.radBtnSourceChecked)
        self.radBtnDir = QtWidgets.QRadioButton("User defined Directory")
        self.radBtnDir.setToolTip("The F06 and dat file has to be in same location")
        self.lineEditDir = QtWidgets.QLineEdit("d:/workdir/valcr/Test")
        self.lineEditDir.setEnabled(False)
        self.radBtnDir.toggled.connect(self.radBtnDirChecked)

        
            
        self.lineEditDeck2 = QtWidgets.QLineEdit("cmpsld01.dat")
        self.btnStartDeck2 =QtWidgets.QPushButton("START")
        self.btnStartDeck2.clicked.connect(self.on_click_tab2_start)
        self.lblCurrentCr = QtWidgets.QLabel("Current Criteria") 
        self.lblCurrentVal = QtWidgets.QLabel("Current Status")        
        self.txtBrCurrentCr = QtWidgets.QTextBrowser()
        self.txtBrCurrentVal = QtWidgets.QTextBrowser()
        self.txtBrCurrentCr.setMaximumHeight(60)
        self.txtBrCurrentVal.setMaximumHeight(60)
        self.lblEditCriteria = QtWidgets.QLabel("Edit/ Modify Criteria")
        self.textEditCriteria = QtWidgets.QTextEdit()
        self.btnUpdateDeck = QtWidgets.QPushButton("update deck")
        self.btnUpdateDeck.setEnabled(self.radBtnSource.isChecked())
        self.btnUpdateDeck.clicked.connect(self.update_deck)
        self.btnSaveDeck = QtWidgets.QPushButton("save")
        self.btnSaveDeck.setEnabled(self.radBtnDir.isChecked())
        self.btnSaveDeck.clicked.connect(self.btnSaveDeckClicked)
        self.btnCloseTab2 = QtWidgets.QPushButton('close')
        self.btnCloseTab2.clicked.connect(self.click2close)
        

        #self.textEditCriteria.setMaximumHeight(60)


        layoutDeck2 = QtWidgets.QHBoxLayout()
        layoutDeck2.addWidget(self.radBtnSource)
        layoutDeck2.addWidget(self.radBtnDir)
        #layoutDeck2.addChildWidget(self)
        layoutDeck2.addWidget(self.lineEditDir)
        layoutDeck2.addWidget(self.lineEditDeck2)
        
        
        layoutDeck2.addWidget(self.btnStartDeck2)

        v_box2 = QtWidgets.QVBoxLayout()
        v_box2.addLayout(layoutDeck2)
        v_box2.addWidget(self.lblCurrentCr)
        v_box2.addWidget(self.txtBrCurrentCr)
        v_box2.addWidget(self.lblCurrentVal)
        v_box2.addWidget(self.txtBrCurrentVal)        
        v_box2.addWidget(self.lblEditCriteria)
        v_box2.addWidget(self.textEditCriteria)
        v_box2.addWidget(self.textEditCriteria)
        #v_box2.addWidget(self.btnUpdateDeck)

        #layout_vbtn = QtWidgets.QVBoxLayout()
        layout_hbtn = QtWidgets.QHBoxLayout()
        layout_hbtn.addWidget(self.btnSaveDeck)
        layout_hbtn.addWidget(self.btnUpdateDeck)
        layout_hbtn.addWidget(self.btnCloseTab2)
        # layout_hbtn.addLayout(layout_vbtn)


        v_box2.addLayout(layout_hbtn)

        self.tab2.setLayout(v_box2)
        self.layout =QtWidgets.QVBoxLayout(self)
        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        #self.setLayout(v_box)


    '''
    #============================================
    All helper functions here
    #============================================
    '''

    def bgetCode(self):
        sender = self.sender()  

        if sender.text() == 'Start':
            self.le.setText(self.comboBoxHeader.currentText())
            self.lwCrit.setEnabled(True)
            self.aBlockCodes = list(set(self.getBlockCodes(self.le.text(), self.keys)))
            self.viewBlockCodes(self.aBlockCodes)
            self.leCritRe.setEnabled(True)
            self.leCritIm.setEnabled(self.complex[self.le.text()])
            self.leAnchor.setEnabled(True)
            self.leAt.setEnabled(True)
            self.leAt1.setEnabled(True)
            self.leAt2.setEnabled(True)
            self.leAt3.setEnabled(True)
            self.leAt4.setEnabled(True)
            self.sbSubcase.setEnabled(True)
            
            
        else:
            self.le.clear()
            self.lwCrit.clear()
            print('Something is not right')

    def clearBlock(self):
        self.le.clear()
        self.lwCrit.clear()
        
    def viewBlockCodes(self,aBlockCodes):
        self.aBlockCodes = aBlockCodes
        self.lwCrit.clear()
        for i in range(len(self.aBlockCodes)):
            self.lwCrit.addItem(self.aBlockCodes[i])

    def loadXml(self, xmlFilePath):
        self.tree = ET.parse(xmlFilePath)
        self.root = self.tree.getroot()

        return self.root

    def scanXml(self,dict_xml):
        schema = dict()
        dict_complex = dict()
        dict_attrib=dict()
        '''
        As long as there is an element to add add it to an array, when there is none 
        name the array with the elements.
        '''
        for i in range(len(dict_xml)):
            if 'complex' in dict_xml[i].attrib:
                dict_complex[dict_xml[i][0].text] = True  
            else:
                dict_complex[dict_xml[i][0].text] = False   

            try:
                schema[dict_xml[i][0].text].append(dict_xml[i].attrib['id'])
            except:
                schema[dict_xml[i][0].text] = [dict_xml[i].attrib['id']]


            dict_attrib[dict_xml[i].attrib['id']] = list(dict_xml[i].attrib.keys())

        return schema,dict_complex, dict_attrib 

    def getBlockCodes(self,sBlockHeader, rSchema):
        self.schema = rSchema
        self.BlockHeader = sBlockHeader
        return self.schema[self.BlockHeader]

    def gen_click(self, item):
        self.anchorKey = str(self.cbAnchor.currentText())
        self.anchorValue = self.leAnchor.text()
        self.subcaseValue = str(self.sbSubcase.value())
        self.atKey = str(self.cbAt.currentText())
        self.atValue = self.leAt.text()
        self.at1Key = str(self.cbAt1.currentText())
        self.at1Value = self.leAt1.text()
        self.at2Key = str(self.cbAt2.currentText())
        self.at2Value = self.leAt2.text()
        self.at3Key = str(self.cbAt3.currentText())
        self.at3Value = self.leAt3.text()
        self.at4Key = str(self.cbAt4.currentText())
        self.at4Value = self.leAt4.text()
        self.critValueRe = self.leCritRe.text()        
        if self.complex[self.le.text()]:
            self.critValueIm = self.leCritIm.text()
        self.critKey = str(self.lwCrit.currentItem().text())

        #type_criteria = 'VALUE' # Default
        if self.radioBtnValue.isChecked():
            type_criteria = 'VALUE'
        if self.radioBtnAbsValue.isChecked():
            type_criteria = 'ABSVALUE'
        if self.radioBtnMax.isChecked():
            type_criteria = 'MAX'
        if self.radioBtnConsistent.isChecked():
            self.leAt.clear()
            self.atKey= ""
            self.atValue= ""
            type_criteria = 'CONSISTENT'
        if self.radioBtnMsg.isChecked():
            type_criteria = 'ISSUE'

        self.returnString = '$ CRITERIA    - '+type_criteria+'[' + self.critKey

        if len(self.anchorKey) > 1:
            self.returnString += ',ANCHOR_' + self.anchorKey + '=>' + self.anchorValue
        if int(self.subcaseValue) > 0:
            self.returnString += ',SUBCASE=>' + self.subcaseValue
        if len(self.atKey) > 1:
            self.returnString += ',' + self.atKey + '=>' + self.atValue
        if len(self.at1Key) > 1:
            self.returnString += ',' + self.at1Key + '=>' + self.at1Value
        if len(self.at2Key) > 1:
            self.returnString += ',' + self.at2Key + '=>' + self.at2Value
        if len(self.at3Key) > 1:
            self.returnString += ',' + self.at3Key + '=>' + self.at3Value
        if len(self.at4Key) > 1:
            self.returnString += ',' + self.at4Key + '=>' + self.at4Value
        self.returnString += ',' + self.critValueRe 
        if self.complex[self.le.text()]:
            self.returnString += '_' + self.critValueIm

        if self.checkboxTol.checkState():
            print("checked2");
            self.returnString += ',' + self.leTol.text()+ '%'

        self.returnString += ']'
        self.leCriteria.setText(self.returnString)
        self.leCriteria.setEnabled(True)
        
        print(self.returnString)
        
    def clickBox(self,state):          
        if state == QtCore.Qt.Checked:
            self.leTol.setEnabled(True)
            print('Tolerance Required now')
        else:
            print('Tolerance is not required now')
            self.leTol.setEnabled(False)

    def update_deck_tab1(self):
        deck = self.lineEditDeck.text()
        
        dir = os.path.dirname(deck)
        base_file = os.path.basename(deck)
        old_file = dir+"/old_"+base_file
        shutil.copy(deck,old_file)        
        
        with open(deck) as file:
            content = file.readlines()
        new_file = open(deck,"w+")
        new_file.write(self.returnString+"\n")
        for line in content:
            new_file.write(line)
        new_file.close
        QtWidgets.QMessageBox.question(self, "Message",deck +" updated.",QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
        
    
    def validate(self):
        test = self.lineEditValidate.text()
        output = getoutput(["perl" ,"//plm/cinas/cae_nxn/nastran_tools/bin/qa_valcr.pl", test])
        #print(output.shape())
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setWindowTitle("Validation Result...")
        self.textEdit.setText(output)
        self.textEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textEdit.setMinimumSize(600,20)
        self.textEdit.show()
    
    def extract_criteria(self,test):
        if '.dat' in test:  
            deck = test      
        else:
            deck = test+'.dat'
        if self.inView and os.environ['VIEW'] != 'none' :
            input_deck = getoutput("dt scm find "+deck+" -q")
            if input_deck:        
                self.input_deck = os.environ['VIEW']+'/'+input_deck
            print("Input Deck:" + self.input_deck)
            dt_load_cmd = 'dt load '+ self.input_deck
            dt_co_cmd = 'dt co '+self.input_deck
            os.system(dt_load_cmd)
            os.system(dt_co_cmd)            
        elif self.radBtnDir.isChecked():
            self.input_deck = self.lineEditDir.text()+'/'+deck
            #self.input_deck = 'd:/view/mir_13/nastran4/nxn/c/'+ deck
            #self.input_deck = '//plm/cinas/cae_nxn/nastran_tools/gb13/nxn/'+deck
            print(" No client set up.Input Deck:" + self.input_deck)
        else:
            QtWidgets.QMessageBox.about(self,"Failure!!!","Make sure you are in a client or check directory and try again.")  

        lCriteria = []
        bcrit=False
        with open(self.input_deck,'r') as f:
            for line in f:
                if re.search('^[\$#]\*?\s+VALIDATION\s+CRITERIA\s+\-?\s*(.*)\s+$',line) or re.search('^[\$#]\*?\s+CRITERIA\s+\-', line):
                    bcrit = True
                    lCriteria.append(line)
                if bcrit:
                    if ('VALUE' or 'ABSVALUE' or 'MAX') in line:
                        lCriteria.append(line)
       
        output = "".join(lCriteria)
        return output


    def on_click_tab2_start(self):        
        test = self.lineEditDeck2.text()
        self.criteria = self.extract_criteria(test)
        self.txtBrCurrentCr.setText(self.criteria)
        self.textEditCriteria.setText(self.criteria)
        output = getoutput(["perl" ,"//plm/cinas/cae_nxn/nastran_tools/bin/qa_valcr.pl", self.input_deck])
        self.txtBrCurrentVal.setText(output)
        
        print(output)

    def update_deck(self):
        deck = self.input_deck
        print(deck)
        self.new_criteria = self.textEditCriteria.toPlainText()
        print(self.new_criteria)
        aLines=[]
        bcrit=False

        with open(self.input_deck,'r') as f:
            for line in f:
                if re.search('^[\$#]\*?\s+VALIDATION\s+CRITERIA\s+\-?\s*(.*)\s+$',line) or re.search('^[\$#]\*?\s+CRITERIA\s+\-', line):
                    bcrit = True
                    aLines.append(self.new_criteria)
                    next
                elif bcrit  and  re.search('VALUE',line):
                        next
                else:
                    aLines.append(line)
        '''
        If source control is not active(not in a view). deck will be updated at a local directory
        '''
        if (os.environ['VIEW'] == 'none'):            
            new_input_deck = self.lineEditDir.text()+'/'+ self.lineEditDeck2.text()
            with open(new_input_deck,'w') as f2:
                for line in aLines:
                    f2.write(line)
                diff_cmd = 'wincmp3 '+ new_input_deck + ' ' + self.input_deck
                diff_cmd = diff_cmd.replace('/','\\')
                print(diff_cmd)
                try:
                    os.system(diff_cmd)
                    
                except:
                    print('wincmp3 not found! add path variable for compare it!')
                
        else:
            new_input_deck = self.input_deck
            with open(new_input_deck,'w') as f2:
                for line in aLines:
                    f2.write(line)

            diff_cmd = 'dt diff '+new_input_deck+' -L'
            print(diff_cmd)
            os.system(diff_cmd)

    def btnSaveDeckClicked(self):
        new_input_deck = self.lineEditDir.text()+'/'+ self.lineEditDeck2.text()
        with open(new_input_deck,'w') as f2:
            for line in aLines:
                f2.write(line)
            diff_cmd = 'wincmp3 '+ new_input_deck + ' ' + self.input_deck
            diff_cmd = diff_cmd.replace('/','\\')
            print(diff_cmd)
            try:
                os.system(diff_cmd)
                
            except:
                print('wincmp3 not found! add path variable for compare it!')


    def radBtnSourceChecked(self,enabled):
        if enabled:
            self.inView = True
            self.btnUpdateDeck.setEnabled(True)
        else:
            self.inView = False
            #self.btnUpdateDeck.setEnabled(True)
    def radBtnDirChecked(self,enabled):
        if enabled:
            self.lineEditDir.setEnabled(True)
            self.btnUpdateDeck.setEnabled(False)
            self.btnSaveDeck.setEnabled(True)
        else:
            self.lineEditDir.setEnabled(False)
            self.btnUpdateDeck.setEnabled(True)
            self.btnSaveDeck.setEnabled(False)
        
    def click2close(self):
        self.close()  

        
"""
Running the app
"""
app = QtWidgets.QApplication(sys.argv)
a_window = Window()
sys.exit(app.exec_())
