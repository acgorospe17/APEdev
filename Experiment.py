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
import Procedures_Parses
import Executor
import XlineTPGen as TPGen
import FlexPrinterApparatus
from Procedure import procedure
import time

NEW_TRAY = True
LIGHT_SOURCE_POS = 'E30'
TRAY_NAME = 'tray'
SAMPLE_NAME = 'sample'

MyApparatus = Apparatus.apparatus()
MyExecutor = Executor.executor()
MyExecutor.debug = True

materials = [{'AgPMMA': 'ZZ1'}]

FlexPrinterApparatus.Build_FlexPrinter(materials, MyApparatus)

MyApparatus['devices']['nAgPMMA']['descriptors'].append('AgPMMA')
MyApparatus['devices']['nAgPMMA']['trace_height'] = 0.1
MyApparatus['devices']['nAgPMMA']['trace_width'] = 0.2
MyApparatus['devices']['aeropump0']['descriptors'].append('AgPMMA')
MyApparatus['devices']['gantry']['default']['speed'] = 40
MyApparatus['devices']['gantry']['nAgPMMA']['speed'] = 5  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['pumpon_time'] = 1  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['mid_time'] = 1
MyApparatus['devices']['aeropump0']['pumpoff_time'] = 0
MyApparatus['devices']['aeropump0']['pumpres_time'] = 0.3
MyApparatus['devices']['aeropump0']['pressure'] = 100
MyApparatus['devices']['pump0']['COM'] = 9

MyApparatus['devices']['TProbe'] = {'type':'Keyence_TouchProbe', 'addresstype':'pointer', 'A3200name': 'gantry', 'systemname': 'system', 'retract':True, 'zreturn':5}
MyApparatus['devices']['TProbe']['DOaxis'] = 'ZZ1'
MyApparatus['devices']['TProbe']['DObit'] = 0
MyApparatus['devices']['TProbe']['AIaxis'] = 'ZZ2'
MyApparatus['devices']['TProbe']['AIchannel'] = 0

MyApparatus['devices']['camera'] = {'type':'Ueye_Camera', 'addresstype':'pointer', 'settle_time':5}
MyApparatus['devices']['gantry']['TProbe'] = {'axismask': {'Z': 'ZZ2'}}
MyApparatus['information']['alignmentnames'].append('TProbe@mark')
MyApparatus['information']['alignments']['TProbe@mark'] = {'X': '', 'Y': '', 'ZZ2': ''}
MyApparatus['information']['alignments']['TProbe@TP_init'] = {'X': -200, 'Y': -250, 'ZZ2': -50}

MyApparatus['devices']['gantry']['camera'] = {'axismask': {'Z': 'ZZ4'}}
MyApparatus['information']['alignmentnames'].append('camera@mark')
MyApparatus['information']['alignments']['camera@mark'] = {'X': '', 'Y': '', 'ZZ4': ''}


MyApparatus['information']['materials']['AgPMMA']['density'] = 1.84
MyApparatus['information']['toolpaths'] = {}
MyApparatus['information']['toolpaths']['generator'] = TPGen.GenerateToolpath
MyApparatus['information']['toolpaths']['parameters'] = TPGen.Make_TPGen_Data('AgPMMA')
MyApparatus['information']['toolpaths']['toolpath'] = [0]

MyApparatus['information']['height_data'] = [0]

MyApparatus.Connect_All(MyExecutor, simulation=False)

# Create instances of the procedures that will be used
AlignPrinter = Procedures_Alignments.Align(MyApparatus, MyExecutor)
BuildGrid = Procedures_SampleTray.Setup_XYGridTray(MyApparatus, MyExecutor)
SampleGrid = Procedures_SampleTray.SampleTray(MyApparatus, MyExecutor)
initTouch = Procedures_TouchProbe.Initialize_TouchProbe(MyApparatus, MyExecutor)
calink = Procedures_InkCal.Calibrate(MyApparatus, MyExecutor)
config_camera = Procedures_Camera.Configure_Settings(MyApparatus, MyExecutor)
initHeightCor = Procedures_HeightCorrection.Initialize_SPHeightCorrect(MyApparatus, MyExecutor)
settings_mode = ['default', 'input', 'saved']
startpos = Procedures_Parses.Start(MyApparatus, MyExecutor)
# Create instances of elemental procedures
cam_connect = MyApparatus.GetEproc('camera', 'Connect')
cam_disconnect = MyApparatus.GetEproc('camera', 'Disconnect')

# Create procedures to do at each position in the sample grid
class ProbeSample(procedure):
    def Prepare(self):
        self.name = 'ProbeSample'
        self.requirements['samplename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of this sample for logging purposes'}
        self.gentp = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
        self.measureTouch = Procedures_TouchProbe.Measure_TouchProbeXY(self.apparatus, self.executor)
        self.planner = Procedures_Planner.Combinatorial_Planner(self.apparatus, self.executor)
        self.heightlog = Procedures_DataFiles.DataListJSON_Store(self.apparatus, self.executor)
        self.heightcor = Procedures_HeightCorrection.SPHeightCorrect(self.apparatus, self.executor)
        
        if 'DD_SPHeightCorrect' not in self.apparatus['information']:
            self.apparatus['information']['DD_SPHeightCorrect']={}

    def Plan(self):
        # Renaming useful pieces of informaiton
        samplename = self.requirements['samplename']['value']

        # Retrieving information from apparatus
        linelength = self.apparatus['information']['toolpaths']['parameters']['length']

        # Doing stuff
        # Update Plan
        space = {'tiph': [0.01*n for n in range(8)]}
        space['trace_height'] = [0.1 * n for n in range(1, 6)]
        addresses = {'tiph': ['information', 'toolpaths', 'parameters', 'tiph']}
        addresses['trace_height'] = ['devices', 'nAgPMMA', 'trace_height']
        priority = ['tiph', 'trace_height']
        file = 'Data//planner.json'
        self.planner.Do({'space': space, 'Apparatus_Addresses': addresses, 'file': file, 'priority': priority})
        # Generate Toolpath
        self.gentp.Do()
        
        # Measure center point
        heightlist = []
        self.heightcor.Do({'point': {'X': linelength / 2, 'Y': 0}})
        height = self.apparatus.getValue(['information', 'height_data'])[0]
        heightlist.append(height)
        self.apparatus['information']['DD_SPHeightCorrect'][samplename]=height
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
        self.heightlog.Do({'filename': 'Data//heights.json', 'label': samplename, 'value': heightlist, 'newentry': True})
        

class ImageSample(procedure):
    def Prepare(self):
        self.name = 'ImageSample'
        self.requirements['samplename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of this sample for logging purposes'}
        self.gentp = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
        self.measureTouch = Procedures_TouchProbe.Measure_TouchProbeXY(self.apparatus, self.executor)
        self.capture_image = Procedures_Camera.Capture_ImageXY(self.apparatus, self.executor)
        self.planner = Procedures_Planner.Combinatorial_Planner(self.apparatus, self.executor)
        self.heightcor = Procedures_HeightCorrection.DD_SPHeightCorrect(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        samplename = self.requirements['samplename']['value']

        # Retrieving information from apparatus
        linelength = self.apparatus['information']['toolpaths']['parameters']['length']
        
        if NEW_TRAY:
            self.heightcor.Do({'height': self.apparatus['information']['DD_SPHeightCorrect'][samplename]})
        
        # Update Plan
        space = {'tiph': [0.01*n for n in range(8)]}
        space['trace_height'] = [0.1 * n for n in range(1, 6)]
        addresses = {'tiph': ['information', 'toolpaths', 'parameters', 'tiph']}
        addresses['trace_height'] = ['devices', 'nAgPMMA', 'trace_height']
        priority = ['tiph', 'trace_height']
        file = 'Data//planner.json'
        self.planner.Do({'space': space, 'Apparatus_Addresses': addresses, 'file': file, 'priority': priority})
        # Generate Toolpath
        self.gentp.Do()
        
        # Take picture
        filename = 'Data\\' + samplename + LIGHT_SOURCE_POS + '.tif'
        self.capture_image.Do({'point': {'X': linelength / 2, 'Y': 0}, 'file': filename, 'camera_name': 'camera'})
        

class PrintSample(procedure):
    def Prepare(self):
        self.name = 'PrintSample'
        self.requirements['samplename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of this sample for logging purposes'}
        self.gentp = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
        self.printtp = Procedures_Toolpath.Print_Toolpath(MyApparatus, MyExecutor)
        self.measureTouch = Procedures_TouchProbe.Measure_TouchProbeXY(self.apparatus, self.executor)
        self.capture_image = Procedures_Camera.Capture_ImageXY(self.apparatus, self.executor)
        self.planner = Procedures_Planner.Combinatorial_Planner(self.apparatus, self.executor)
        self.heightlog = Procedures_DataFiles.DataListJSON_Store(self.apparatus, self.executor)
        self.heightcor = Procedures_HeightCorrection.DD_SPHeightCorrect(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        samplename = self.requirements['samplename']['value']
        
        self.heightcor.Do({'height': self.apparatus['information']['DD_SPHeightCorrect'][samplename]})
        
        # Update Plan
        space = {'tiph': [0.01*n for n in range(8)]}
        space['trace_height'] = [0.1 * n for n in range(1, 6)]
        addresses = {'tiph': ['information', 'toolpaths', 'parameters', 'tiph']}
        addresses['trace_height'] = ['devices', 'nAgPMMA', 'trace_height']
        priority = ['tiph', 'trace_height']
        file = 'Data//planner.json'
        self.planner.Do({'space': space, 'Apparatus_Addresses': addresses, 'file': file, 'priority': priority})
        
        # Generate Toolpath
        self.gentp.Do()

        self.printtp.Do({'toolpath': self.gentp.requirements['target']['value']})


# Do the experiment
cam_disconnect.Do()
AlignPrinter.Do({'primenoz': 'nAgPMMA'})
cam_connect.Do()

startpos.Do()
initTouch.Do()
calink.Do({'material': 'AgPMMA'})
initHeightCor.Do()

BuildGrid.Do({'trayname': TRAY_NAME, 'samplename': SAMPLE_NAME, 'xtray': 60, 'xsamples': 7, 'ytray': 35, 'ysamples': 5})

myProcedure = procedure(MyApparatus, MyExecutor)
wait = MyApparatus.GetEproc(MyApparatus.findDevice({'descriptors': 'system'}), 'Dwell')
 
for light_pos in ['E30', 'E45', 'E60', 'W30', 'W45', 'W60']:
    input('Move light source to position and press ENTER when ready.')
    
    # configure camera based off light source angle
    if '30' in light_pos:
        config_camera.Do({'camera_name':'camera', 'gain':[0,55,20,90]})
    elif '45' in light_pos:
        config_camera.Do({'camera_name':'camera', 'gain':[50,25,0,45]})
    elif '60' in light_pos:
        config_camera.Do({'camera_name':'camera', 'gain':[100,35,2,70]})
    else:
        print('camera not configured')

    if light_pos == 'E30' and NEW_TRAY:
        # touch probe the background
        SampleGrid.Do({'trayname': TRAY_NAME, 'procedure': ProbeSample(MyApparatus, MyExecutor)})
        
        # image capture the background
        LIGHT_SOURCE_POS = 'Initial@' + light_pos
        SampleGrid.Do({'trayname': TRAY_NAME, 'procedure': ImageSample(MyApparatus, MyExecutor)})
        
        # print the samples
        input('Press ENTER when ready to print.')
        SampleGrid.Do({'trayname': TRAY_NAME, 'procedure': PrintSample(MyApparatus, MyExecutor)})
        wait.Do({'dtime':300})
        
        # touch probe the samples
        SampleGrid.Do({'trayname': TRAY_NAME, 'procedure': ProbeSample(MyApparatus, MyExecutor)})
          
    # image capture the samples
    LIGHT_SOURCE_POS = light_pos
    SampleGrid.Do({'trayname': TRAY_NAME, 'procedure': ImageSample(MyApparatus, MyExecutor)})
        
print('Finished experiment.')
cam_disconnect.Do()
