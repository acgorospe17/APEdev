import Apparatus
import Procedures_Toolpath
import Procedures_Alignments
import Procedures_SampleTray
import Procedures_Planner
import Procedures_TouchProbe
import Procedures_Camera
import Procedures_InkCal
import Procedures_DataFiles
import Procedures_HeightCorrection
import Executor
import XlineTPGen as TPGen
import FlexPrinterApparatus
from Procedure import procedure
import time

MyApparatus = Apparatus.apparatus()
MyExecutor = Executor.executor()
MyExecutor.debug = True

materials = [{'stuff': 'ZZ1'}]

FlexPrinterApparatus.Build_FlexPrinter(materials, MyApparatus)

MyApparatus['devices']['nstuff']['descriptors'].append('stuff')
MyApparatus['devices']['nstuff']['trace_height'] = 0.8
MyApparatus['devices']['nstuff']['trace_width'] = 0.8
MyApparatus['devices']['aeropump0']['descriptors'].append('stuff')
MyApparatus['devices']['gantry']['default']['speed'] = 40
MyApparatus['devices']['gantry']['nstuff']['speed'] = 5  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['pumpon_time'] = 1  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['mid_time'] = 1
MyApparatus['devices']['aeropump0']['pumpoff_time'] = 0
MyApparatus['devices']['aeropump0']['pumpres_time'] = 0.3
MyApparatus['devices']['aeropump0']['pressure'] = 250
MyApparatus['devices']['pump0']['COM'] = 9

MyApparatus['devices']['TProbe'] = {'type':'Keyence_TouchProbe', 'addresstype':'pointer', 'A3200name': 'gantry', 'systemname': 'system', 'retract':True, 'zreturn':5}
MyApparatus['devices']['TProbe']['DOaxis'] = 'ZZ1'
MyApparatus['devices']['TProbe']['DObit'] = 0
MyApparatus['devices']['TProbe']['AIaxis'] = 'ZZ2'
MyApparatus['devices']['TProbe']['AIchannel'] = 0

MyApparatus['devices']['camera'] = {'type':'Ueye_Camera', 'addresstype':'pointer', 'settle_time':5}
MyApparatus['devices']['gantry']['TProbe'] = {'axismask': {'Z': 'ZZ3'}}
MyApparatus['information']['alignmentnames'].append('TProbe@mark')
MyApparatus['information']['alignments']['TProbe@mark'] = {'X': '', 'Y': '', 'ZZ3': ''}
MyApparatus['information']['alignments']['TProbe@TP_init'] = {'X': -200, 'Y': -250, 'ZZ3': -50}

MyApparatus['devices']['gantry']['camera'] = {'axismask': {'Z': 'ZZ4'}}
MyApparatus['information']['alignmentnames'].append('camera@mark')
MyApparatus['information']['alignments']['camera@mark'] = {'X': '', 'Y': '', 'ZZ4': ''}


MyApparatus['information']['materials']['stuff']['density'] = 1.13
MyApparatus['information']['toolpaths'] = {}
MyApparatus['information']['toolpaths']['generator'] = TPGen.GenerateToolpath
MyApparatus['information']['toolpaths']['parameters'] = TPGen.Make_TPGen_Data('stuff')
MyApparatus['information']['toolpaths']['toolpath'] = [0]

MyApparatus['information']['height_data'] = [0]

MyApparatus.Connect_All(MyExecutor, simulation=True)

# Create instances of the procedures that will be used
AlignPrinter = Procedures_Alignments.Align(MyApparatus, MyExecutor)
BuildGrid = Procedures_SampleTray.Setup_XYGridTray(MyApparatus, MyExecutor)
SampleGrid = Procedures_SampleTray.SampleTray(MyApparatus, MyExecutor)
initTouch = Procedures_TouchProbe.Initialize_TouchProbe(MyApparatus, MyExecutor)
calink = Procedures_InkCal.Calibrate(MyApparatus, MyExecutor)
configure_camera = Procedures_Camera.Configure_Settings(MyApparatus, MyExecutor)
initHeightCor = Procedures_HeightCorrection.Initialize_SPHeightCorrect(MyApparatus, MyExecutor)
settings_mode = ['default', 'input', 'saved']

# Create procedure to do at each position in the sample grid
class ProbeImagePrintImage(procedure):
    def Prepare(self):
        self.name = 'ProbeImagePrintImage'
        self.requirements['samplename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of this sample for logging purposes'}
        self.gentp = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
        self.printtp = Procedures_Toolpath.Print_Toolpath(MyApparatus, MyExecutor)
        self.measureTouch = Procedures_TouchProbe.Measure_TouchProbeXY(self.apparatus, self.executor)
        self.capture_image = Procedures_Camera.Capture_ImageXY(self.apparatus, self.executor)
        self.planner = Procedures_Planner.Combinatorial_Planner(self.apparatus, self.executor)
        self.heightlog = Procedures_DataFiles.DataListJSON_Store(self.apparatus, self.executor)
        self.heightcor = Procedures_HeightCorrection.SPHeightCorrect(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        samplename = self.requirements['samplename']['value']

        # Retreiving necessary device names

        # Retrieving information from apparatus
        linelength = self.apparatus['information']['toolpaths']['parameters']['length']

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        # Update Plan
        space = {'tiph': [0.1*n for n in range(10)]}
        space['trace_height'] = [0.1 * n for n in range(1, 6)]
        addresses = {'tiph': ['information', 'toolpaths', 'parameters', 'tiph']}
        addresses['trace_height'] = ['devices', 'nstuff', 'trace_height']
        priority = ['tiph', 'trace_height']
        file = 'Data//planner.json'
        self.planner.Do({'space': space, 'Apparatus_Addresses': addresses, 'file': file, 'priority': priority})
        # Generate Toolpath
        self.gentp.Do()
        # Measure center point
        heightlist = []
        self.heightcor.Do({'point': {'X': linelength / 2, 'Y': 0}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        # Update start heights accordingly
        # Do remaining height measurements for 3x3 grid
        self.measureTouch.Do({'point': {'X': 0, 'Y': 0}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        self.measureTouch.Do({'point': {'X': linelength, 'Y': 0}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        self.measureTouch.Do({'point': {'X': 0, 'Y': 2}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        self.measureTouch.Do({'point': {'X': linelength / 2, 'Y': 2}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        self.measureTouch.Do({'point': {'X': linelength, 'Y': 2}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        self.measureTouch.Do({'point': {'X': 0, 'Y': -2}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        self.measureTouch.Do({'point': {'X': linelength / 2, 'Y': -2}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        self.measureTouch.Do({'point': {'X': linelength, 'Y': -2}})
        heightlist.append(self.apparatus.getValue(['information', 'height_data'])[0])
        self.heightlog.Do({'filename': 'Data//heights.json', 'label': samplename + ' initial', 'value': heightlist, 'newentry': True})
        # Take initial picture
        filename = 'Data\\' + samplename + 'aE60' +'Initial.tif'
        self.capture_image.Do({'point': {'X': linelength / 2, 'Y': 0}, 'file': filename, 'camera_name': 'camera'})
        self.printtp.Do({'toolpath': self.gentp.requirements['target']['value']})
        # Take first of final pictures
        filename = 'Data\\' + samplename + 'aE60' + '.tif'
        self.capture_image.Do({'point': {'X': linelength / 2, 'Y': 0}, 'file': filename, 'camera_name': 'camera'})

sample = ProbeImagePrintImage(MyApparatus, MyExecutor)

# Do the experiment
AlignPrinter.Do({'primenoz': 'nstuff'})
initTouch.Do()
calink.Do({'material': 'stuff'})
initHeightCor.Do()
BuildGrid.Do({'trayname': 'test_tray', 'samplename': 'bleh', 'xspacing': 1, 'xsamples': 2, 'yspacing': 1, 'ysamples': 1})
SampleGrid.Do({'trayname': 'test_tray', 'procedure': sample})
