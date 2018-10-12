import Apparatus
import Procedures_Toolpath
import Procedures_Alignments
import Procedures_SampleTray
import Executor
import XlineTPGen as TPGen
import FlexPrinterApparatus
from Procedure import procedure

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


# Create procedure to do at each position in the sample grid
class Sample(procedure):
    def Prepare(self):
        self.name = 'Sample'
        self.gentp = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
        self.printtp = Procedures_Toolpath.Print_Toolpath(MyApparatus, MyExecutor)
    def Plan(self):
        # Renaming useful pieces of informaiton

        # Retreiving necessary device names

        # Retrieving information from apparatus

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        self.gentp.Do()
        self.printtp.Do({'toolpath': self.gentp.requirements['target']['value']})


sample = Sample(MyApparatus, MyExecutor)

# Do the experiment
AlignPrinter.Do({'primenoz': 'nstuff'})
BuildGrid.Do({'trayname': 'test_tray', 'samplename': 'bleh', 'xspacing': 1, 'xsamples': 2, 'yspacing': 1, 'ysamples': 3})
SampleGrid.Do({'trayname': 'test_tray', 'procedure': sample})
