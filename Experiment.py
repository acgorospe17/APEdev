import Apparatus
import Procedures_Toolpath
import Procedures_Alignments
import Executor
import XlineTPGen as TPGen
import FlexPrinterApparatus

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

MyApparatus.Connect_All(MyExecutor, simulation=False)


AlignPrinter = Procedures_Alignments.Align(MyApparatus, MyExecutor)
GenerateToolpath = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
PrintToolpath = Procedures_Toolpath.Print_Toolpath(MyApparatus, MyExecutor)

MyApparatus['devices']['gantry']['TProbe']={'axismask': {'Z': 'ZZ3'}}
MyApparatus['information']['alignmentnames'].append('TProbe@mark')
MyApparatus['information']['alignments']['TProbe@mark'] = {'X': '', 'Y': '', 'ZZ3': ''}
MyApparatus['information']['alignments']['TProbe@TP_init'] = {'X': -200, 'Y': -250, 'ZZ3': -50}

AlignPrinter.Do({'primenoz':'nstuff'})
MyApparatus['information']['materials']['stuff']['density'] = 1.13
MyApparatus['information']['toolpaths']={}
MyApparatus['information']['toolpaths']['generator']=TPGen.GenerateToolpath
MyApparatus['information']['toolpaths']['parameters']=TPGen.Make_TPGen_Data('stuff')
MyApparatus['information']['toolpaths']['toolpath']=[0]

MyApparatus['information']['height_data']=[0]

GenerateToolpath.Do()
PrintToolpath.Do({'toolpath':GenerateToolpath.requirements['target']['value']})

