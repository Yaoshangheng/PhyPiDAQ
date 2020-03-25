#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
from __future__ import absolute_import

''' 
  GUI to control run_phipy.py 

    - select and edit configuration files 
    - select working direcotory
    - start data taking via execution of run_phypi.py
'''

import sys, os, time, yaml, subprocess

from PyQt5.QtWidgets import QMessageBox

from .phypiUi import * # imort code generated by designer-qt5

CONFIG_ENVIRONMENT_file = 'phypidaq.cfg'

# --> own implementation starts here --> 
class PhyPiUiInterface(Ui_PhyPiWindow):
    '''interface to class generated by designer-qt5
    '''   

    def __init__(self):
      # initialize configuration parameters  
      self.ConfDir = None 
      self.WDname = None  

    def MB_Question(self, Title, Text):
    # wrapper for QMessageBox Question yes/abort
      msg = QMessageBox()
      msg.setIcon(QMessageBox.Question)
      msg.setWindowTitle(Title)
      msg.setText(Text)       
      msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
      return msg.exec_()

    def MB_YesNo(self, Title, Text):
    # wrapper for QMessageBox Question yes/abort
      msg = QMessageBox()
      msg.setIcon(QMessageBox.Question)
      msg.setWindowTitle(Title)
      msg.setText(Text)       
      msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
      return msg.exec_()

    def MB_Info(self, Title, Text):
    # wrapper for QMessageBox Info
      msg = QMessageBox()
      msg.setIcon(QMessageBox.Information)
      msg.setWindowTitle(Title)
      msg.setText(Text)       
      msg.setStandardButtons(QMessageBox.Ok)
      return msg.exec_()

    def MB_Warning(self, Title, Text):
    # wrapper for QMessageBox Info
      msg = QMessageBox()
      msg.setIcon(QMessageBox.Warning)
      msg.setWindowTitle(Title)
      msg.setText(Text)       
      msg.setStandardButtons(QMessageBox.Ok)
      return msg.exec_()

    def init(self, Window, DAQconfFile, ConfDir= None, WDname = None):
# initialisation 
      super().setupUi(Window) # initialize base class
      self.Window = Window
      
# set display options, fonts etc.
      self.setOptions()

# set-up help 
      self.setHelp_EN()

# find user home directory and create directory 'PhyPi' 
      self.homedir = os.getenv('HOME')
      if ConfDir is not None:
        if ConfDir[0] != '/':    # relative path
          self.ConfDir = self.homedir + '/' + ConfDir
        else:                     # absolute path          
          self.ConfDir = ConfDir
      else:
        if self.ConfDir is None: self.ConfDir = self.homedir + '/PhyPi' 
      if not os.path.exists(self.ConfDir): 
        os.makedirs(self.ConfDir)

# set initial working Directory
      if WDname is not None:
        if WDname[0] != '/':    # relative path
          self.WDname = self.homedir + '/' + WDname          
        else:                   # absolute path
          self.WDname = WDname          
      else:
        if self.WDname is None: self.WDname = self.ConfDir
      if not os.path.exists(self.WDname): 
        os.makedirs(self.WDname)
        
      self.lE_WorkDir.setText(self.WDname)

# set iterable over Device Configs Tabs (max. of 3)
      self.tab_DeviceConfigs = [self.tab_DeviceConfig0, 
                                self.tab_DeviceConfig1,
                                self.tab_DeviceConfig2]
      self.pB_DeviceSelects = [self.pB_DeviceSelect0, 
                               self.pB_DeviceSelect1,  
                               self.pB_DeviceSelect2]  
      self.pTE_DeviceConfigs = [self.pTE_DeviceConfig0, 
                                self.pTE_DeviceConfig1,
                                self.pTE_DeviceConfig2]

# define actions
      self.pB_abort.clicked.connect(QtCore.QCoreApplication.instance().quit) 
      self.rB_EditMode.clicked.connect(self.actionEditConfig) 
      self.pB_reloadConfig.clicked.connect(self.readDeviceConfig)
      self.pB_SaveDefault.clicked.connect(self.saveDefaultConfig)
      self.pB_FileSelect.clicked.connect(self.selectConfigFile)
      self.pB_DeviceSelect0.clicked.connect(self.selectDeviceFile0)
      self.pB_DeviceSelect1.clicked.connect(self.selectDeviceFile1)
      self.pB_DeviceSelect2.clicked.connect(self.selectDeviceFile2)
      self.pB_WDselect.clicked.connect(self.selectWD)
      self.pB_Help.clicked.connect(self.setHelp_EN)
      self.pB_Hilfe.clicked.connect(self.setHelp_DE)
      self.pB_StartRun.clicked.connect(self.actionStartRun) 

# initialization dependent on DAQ config file
      self.initDAQ(DAQconfFile)

    def initDAQ(self, DAQconfFile):
# initialize DAQ from config files - need absolute path
      path = os.path.dirname(DAQconfFile)
      if path == '': path = '.'
      self.cwd = path

      try:
        with open(DAQconfFile, 'r') as f:
          DAQconf = f.read()
      except:
        print('     failed to read DAQ configuration file ' + DAQconfFile)
        exit(1)

      self.lE_DAQConfFile.setText(DAQconfFile)
      RunTag = os.path.split(DAQconfFile)[1].split('.')[0]
      self.lE_RunTag.setText(RunTag)
      
      print('   - PhyPi configuration from file ' + DAQconfFile)
   # display config data in GUI
      self.pTE_phypiConfig.setPlainText(DAQconf)

   # read device File(s) as specified in DAQConfFile
      self.DeviceFiles = 3*['']
      self.readDeviceConfig() 
# - end initDAQ

    def setOptions(self):
      # set font for plainTextEdit to monospace
      monofont = QtGui.QFont()
      monofont.setStyleHint(QtGui.QFont.TypeWriter)
      monofont.setFamily("unexistentfont")        
      self.pTE_phypiConfig.setFont(monofont)
      self.pTE_DeviceConfig0.setFont(monofont)
      self.pTE_DeviceConfig1.setFont(monofont)
      # no line wrap, horizontal scroll bar instead
      self.pTE_phypiConfig.setLineWrapMode(0)
      self.pTE_DeviceConfig0.setLineWrapMode(0)
      self.pTE_DeviceConfig1.setLineWrapMode(0)
      
    def setHelp_DE(self):
      self.TE_Help.setText(open('doc/Hilfe.html', 'r').read() ) 

    def setHelp_EN(self):
      self.TE_Help.setText(open('doc/help.html', 'r').read() )

    def setDevConfig_fromFile(self, i, fname):
      try:
        self.pTE_DeviceConfigs[i].setPlainText(open(fname).read() )
        print('   - Device configuration from file ' + fname)
      except:
        self.pTE_DeviceConfigs[i].setPlainText('# no config file ' + fname )

    def readDeviceConfig(self):
#   read Device Configuration as specified by actual phypi DAQ config
      phypiConfD=yaml.load(self.pTE_phypiConfig.toPlainText(),
                           Loader=yaml.Loader )
      # find the device configuration file
      if "DeviceFile" in phypiConfD: 
        DevFiles = phypiConfD["DeviceFile"]
      elif "DAQModule" in phypiConfD: 
        DevFiles = phypiConfD["DAQModule"] + '.yaml' 
      else:
        print('     no device configuration file given - exiting')
        exit(1)

# if not a list, make it one
      if type(DevFiles) != type([]):
        DevFiles = [DevFiles]
      self.NDeviceConfigs = len(DevFiles)
#  enable Config Tabs if needed
      _translate = QtCore.QCoreApplication.translate
      for i in range(1, self.NDeviceConfigs):
        self.tab_DeviceConfigs[i].setEnabled(True)
        self.tabConfig.setTabText(self.tabConfig.indexOf(self.tab_DeviceConfigs[i]), 
                                  _translate("PhyPiWindow", "Device Config " + str(i+1)))            

      for i in range(self.NDeviceConfigs, len(self.tab_DeviceConfigs) ):
        self.tab_DeviceConfigs[i].setEnabled(False)
        self.tabConfig.setTabText(self.tabConfig.indexOf(self.tab_DeviceConfigs[i]), 
                                  _translate("PhyPiWindow", ""))            

           
      # (re-)read device config if file name in phypi Config changed
      for i, DevFnam in enumerate(DevFiles):
        if DevFnam != self.DeviceFiles[i]:
          fname = self.cwd + '/' + DevFnam
          self.setDevConfig_fromFile(i, fname)
          if self.DeviceFiles[i] != '':
            message = self.MB_Info('Info', 
             'Device Configuration re-read, please check')       
          self.DeviceFiles[i] = DevFiles[i]
 
    def selectConfigFile(self):
      path2File = QtWidgets.QFileDialog.getOpenFileName(None,
         'PhyPi config', self.ConfDir, 'DAQ(*.daq)')
      FileName = str(path2File[0]).strip()
      if FileName is not '' :
        # print('selected File ' + str(FileName) )
      # remember new config directory
        self.ConfDir = os.path.dirname(FileName)
        self.initDAQ(FileName)
        
    def selectDeviceFile0(self):
      path2File = QtWidgets.QFileDialog.getOpenFileName(None,
          'Device config', self.ConfDir, 'yaml(*.yaml)')
      FileName = str(path2File[0]).strip()
      if FileName is not '' :
        # print('selected File ' + str(FileName) )
        self.setDevConfig_fromFile(0, FileName)

    def selectDeviceFile1(self):
      path2File = QtWidgets.QFileDialog.getOpenFileName(None,
          'Device config', self.ConfDir, 'yaml(*.yaml)')
      FileName = str(path2File[0]).strip()
      if FileName is not '' :
        # print('selected File ' + str(FileName) )
        self.setDevConfig_fromFile(1, FileName)

    def selectDeviceFile2(self):
      path2File = QtWidgets.QFileDialog.getOpenFileName(None,
          'Device config', self.ConfDir, 'yaml(*.yaml)')
      FileName = str(path2File[0]).strip()
      if FileName is not '' :
        # print('selected File ' + str(FileName) )
        self.setDevConfig_fromFile(2, FileName)

    def selectWD(self):
      path2WD = QtWidgets.QFileDialog.getExistingDirectory(None, '~')
      WDname = str(path2WD).strip()
      if WDname is not '' :
        # print('selected Directory' + WDname )
         self.lE_WorkDir.setText(WDname)
         self.WDname = WDname

    def actionEditConfig(self):
        checked = self.rB_EditMode.isChecked()
        self.pTE_phypiConfig.setReadOnly(not checked)
        self.pB_reloadConfig.setEnabled(checked)
        self.pTE_DeviceConfig0.setReadOnly(not checked)
        self.pTE_DeviceConfig1.setReadOnly(not checked)
        self.pTE_DeviceConfig2.setReadOnly(not checked)

    def checkConfig(self, DAQconf):
      # check validity of configuration files for valid yaml syntax
      try:
        DAQconfdict=yaml.load(DAQconf, Loader=yaml.Loader)       
      except Exception as e: 
        self.MB_Warning('Warning', 
          'PhyPi Config is not valid yaml format \n' + str(e))       
        return 1

      DevConfs = []   
      for i in range(self.NDeviceConfigs):
        DevConfs.append(self.pTE_DeviceConfigs[i].toPlainText()) 
        try:
          _ =yaml.load(DevConfs[i], Loader=yaml.Loader)       
        except Exception as e: 
          self.MB_Warning('Warning', 
             'Device Config %i is not valid yaml format \n'%(i) + str(e) )
          return 1
      return 0
   
    def saveConfigs(self, confdir, DAQfile=None, verbose=0):
    # save all Config files to confdir

      # retrieve actual configuration from GUI
      DAQconf = self.pTE_phypiConfig.toPlainText()
      # check validity of configuration files for valid yaml syntax
      try:
        DAQconfdict=yaml.load(DAQconf, Loader=yaml.Loader)       
      except Exception as e: 
        self.MB_Warning('Warning', 
          'PhyPi Config is not valid yaml format \n' + str(e))       
        return 1

      DevConfs = []   
      for i in range(self.NDeviceConfigs):
        DevConfs.append(self.pTE_DeviceConfigs[i].toPlainText()) 
        try:
          _ =yaml.load(DevConfs[i], Loader=yaml.Loader)       
        except Exception as e: 
          self.MB_Warning('Warning', 
             'Device Config %i is not valid yaml format \n'%(i) + str(e) )
          return 1
      
      # name of DAQ configuration file in confdir
      if(DAQfile) is None: # derive from RunTag if not given
        DAQfile = str(self.lE_RunTag.text() ).replace(' ','') + '.daq'
      fullDAQfile = confdir + '/' + DAQfile

      if verbose:
        if self.MB_Question('Question', 
          'saving Config to file ' + fullDAQfile) == QMessageBox.Cancel:
          return 1
     
      DevFiles = DAQconfdict["DeviceFile"] 
      if type(DevFiles) != type([]):
        DevFiles = [DevFiles]
        
      # check for overwriting ...
      #   ... device config files
      for DevFile in DevFiles:
        fullDevFile = confdir + '/' + DevFile
        if os.path.isfile(fullDevFile):
          if self.MB_Question('Question', 
            'File '+fullDevFile+' exists - overwrite ?') == QMessageBox.Cancel:
            return 1
      #  ... DAQ file         
      if os.path.isfile(fullDAQfile):
        if self.MB_Question('Question', 
          'File '+fullDAQfile+' exists - overwrite ?') == QMessageBox.Cancel:
          return 1
    
      # if ok, write all files
      fDAQ = open(fullDAQfile, 'w')
      print(DAQconf, file = fDAQ )
      self.DAQfile = DAQfile
      fDAQ.close()
      print('   - saved PhyPy configuration to ' + fullDAQfile)

      for i, DevFile in enumerate(DevFiles):
        cdir, fnam = os.path.split(DevFile)
        # make sub-directory if needed and non-existent        
        if cdir != '':
          if not os.path.exists(confdir + '/' + cdir):
            os.makedirs(confdir + '/' + cdir) 
        fDev = open(confdir + '/' + DevFile, 'w')
        print(DevConfs[i], file = fDev )
        fDev.close()
        print('   - saved Device configuration to ' + fullDevFile)

      if verbose:
        message = self.MB_Info('Info', 
                        'saved PhyPi and Device Configuration')               
      return 0

    def saveDefaultConfig(self):
    # save configuration
      # propose name for DAQ configuration file from RunTag 
      _file = self.ConfDir + '/' + str(self.lE_RunTag.text() ).replace(' ','') + '.daq'
      # select file and direcotory 
      path2File = QtWidgets.QFileDialog.getSaveFileName(None,
         'save configuration as', _file, 'daq(*.daq)')
      fullDAQfile = str(path2File[0]).strip()
      if  fullDAQfile is not '' :
      # remember new config directory
        self.ConfDir = os.path.dirname(fullDAQfile)
        DAQfile = os.path.basename(fullDAQfile)
      else:
        return 1
      # set name and save all configs 
      self.lE_DAQConfFile.setText(fullDAQfile)
      return self.saveConfigs(self.ConfDir, DAQfile=DAQfile, verbose=0)

    def saveEnvironment(self):
      '''
        Save PhyPi configuration to file ~/CONFIG_ENVIRONMENT_file
      '''
      hd = os.getenv('HOME')
  # ... and find name of work directory
      cfgname = hd + '/' + CONFIG_ENVIRONMENT_file
      fcfg = open(cfgname, 'w')
      print('work_directory: ', self.WDname, file=fcfg)
      print('config_directory: ', self.ConfDir, file=fcfg)
      print('daq_file: ', os.path.basename(self.DAQfile), file=fcfg)
 
    def actionStartRun(self):
      # start script run_phipy in subdirectory

      # generate a dedicated subdirectory
      datetime=time.strftime('%y%m%d-%H%M', time.localtime())
      RunTag = ''.join(str(self.lE_RunTag.text() ).split() )
      self.runDir = (RunTag + '_' + datetime) # timestamp
      self.path_to_WD = self.WDname + '/' + self.runDir
      if not os.path.exists(self.path_to_WD): 
        os.makedirs(self.path_to_WD)

      if self.saveConfigs(self.path_to_WD): return
      print("   - files for this run stored in directory " + self.path_to_WD) 

    # save changes to phypidaq configuration
      self.saveEnvironment()
      
    # close GUI window and start runCosmo 
      print('\n*==* PhyPi Gui: closing window and starting run_phypi.py')
      self.Window.hide()

    # start script 
      self.start_runphypi()

    # exit or continue ? 
      if self.MB_YesNo('End Dialog','Exit phypi ? ') == QMessageBox.Yes:
        QtCore.QCoreApplication.instance().quit()
        print('*==* phypi: exit \n')
      else:
        self.Window.show()

    def start_runphypi(self):
      dir = os.getcwd()
      subprocess.call([dir + '/run_phypi.py ' + self.DAQfile],
                 cwd = self.path_to_WD, shell = True)

# - end Class Ui_PhyPiWindow

def runPhyPiUi():    
  script = sys.argv[0]
  print('\n*==* ' + script + ' running')

  # get relevant paths ...
  path_to_PhyPi = os.path.dirname(script)
  homedir = os.getenv('HOME')
  # ... and find name of work directory
  cfgname = homedir + '/' + CONFIG_ENVIRONMENT_file
  try:
    with  open(cfgname) as cfg: 
      cfg_dict = yaml.load(cfg, Loader=yaml.Loader)
  except:
    cfgname = path_to_PhyPi + '/' + CONFIG_ENVIRONMENT_file
    try:
      with  open(cfgname) as cfg: 
        cfg_dict=yaml.load(cfg, Loader=yaml.Loader)      
    except:
      print(2*' ', ' !!! no valid file '
            + CONFIG_ENVIRONMENT_file + ' found - using defaults')
      cfg_dict = {}
      cfg_dict['work_directory'] = '~'
      cfg_dict['config_directory'] = ' '
      cfg_dict['daq_file'] = 'PhyPiDemo.daq'
      
  work_directory = cfg_dict['work_directory']
  if work_directory == '~':  work_directory = homedir
  if work_directory == '.':  work_directory = os.getcwd()
  conf_directory = cfg_dict['config_directory']
  if conf_directory == '~':  conf_directory = homedir
  if conf_directory == '.':  conf_directory = os.getcwd()
  if conf_directory == ' ':  conf_directory = path_to_PhyPi
  DAQconfFile = conf_directory + '/' + cfg_dict['daq_file']
      
  # check for/read command line arguments and get DAQ configuration file
  if len(sys.argv) == 2:
    DAQconfFile = os.path.abspath(sys.argv[1]) # with full path to file
    conf_directory = os.path.dirname(DAQconfFile) # config dir from file name
    
  # print config information 
  print(5*' ', 'work directory: ', work_directory)
  print(5*' ', 'configuration directory: ', conf_directory)
  print(5*' ', 'DAQ configuration file: ', DAQconfFile)

# start GUI
  if path_to_PhyPi != '':
    os.chdir(path_to_PhyPi) # change path to where PhyPi lives
  app = QtWidgets.QApplication(sys.argv)
  MainWindow = QtWidgets.QMainWindow()

# call custom implementation
  ui= PhyPiUiInterface()
  ui.init( MainWindow, DAQconfFile,
           ConfDir = conf_directory, WDname = work_directory)

# start pyqt event loop
  MainWindow.show()
  sys.exit(app.exec_())

if __name__ == "__main__": # - - - - - - - - - - - - - - - - - - - -
  runPhyPiUi()
