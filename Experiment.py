import Apparatus
import Procedures_Toolpath
import Procedures_Alignments
import Executor
import EmbeddedHelixTPgen as TPGen
import FlexPrinterApparatus

MyApparatus = Apparatus.apparatus()
MyExecutor = Executor.executor()
MyExecutor.debug = True

materials = [{'PDMS': 'ZZ1'}, {'PDMSred': 'ZZ2'}]

FlexPrinterApparatus.Build_FlexPrinter(materials, MyApparatus)

MyApparatus['devices']['nPDMS']['descriptors'].append('PDMS')
MyApparatus['devices']['nPDMS']['trace_height'] = 0.8
MyApparatus['devices']['nPDMS']['trace_width'] = 0.8
MyApparatus['devices']['aeropump0']['descriptors'].append('PDMS')
MyApparatus['devices']['nPDMSred']['descriptors'].append('PDMSred')
MyApparatus['devices']['nPDMSred']['trace_height'] = 0.3
MyApparatus['devices']['nPDMSred']['trace_width'] = 0.4
MyApparatus['devices']['pump1']['descriptors'].append('PDMSred')
MyApparatus['devices']['gantry']['default']['speed'] = 40
MyApparatus['devices']['gantry']['nPDMS']['speed'] = 5  # Calibration is on so this is overwritten
MyApparatus['devices']['gantry']['nPDMSred']['speed'] = 7  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['pumpon_time'] = 1  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['mid_time'] = 1
MyApparatus['devices']['aeropump0']['pumpoff_time'] = 0
MyApparatus['devices']['aeropump0']['pumpres_time'] = 0.3
MyApparatus['devices']['aeropump0']['pressure'] = 250
MyApparatus['devices']['pump0']['COM'] = 9
MyApparatus['devices']['pump1']['COM'] = 4
MyApparatus['devices']['pump1']['pumpon_time'] = 1  # Calibration is on so this is overwritten
MyApparatus['devices']['pump1']['mid_time'] = 1
MyApparatus['devices']['pump1']['pumpoff_time'] = 0
MyApparatus['devices']['pump1']['pumpres_time'] = 0.2
MyApparatus['devices']['pump1']['pressure'] = 200

MyApparatus.Connect_All(MyExecutor, simulation=False)


AlignPrinter = Procedures_Alignments.Align(MyApparatus, MyExecutor)
GenerateToolpath = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
PrintToolpath = Procedures_Toolpath.Print_Toolpath(MyApparatus, MyExecutor)

AlignPrinter.Do({'primenoz':'nPDMS'})
MyApparatus['information']['materials']['PDMS']['density'] = 1.13
MyApparatus['information']['materials']['PDMSred']['density'] = 1.13
MyApparatus['information']['toolpaths']={}
MyApparatus['information']['toolpaths']['generator']=TPGen.GenerateToolpath
MyApparatus['information']['toolpaths']['parameters']=TPGen.Make_TPGen_Data('PDMS', 'PDMSred')
MyApparatus['information']['toolpaths']['parameters']['zlayers']=3
MyApparatus['information']['toolpaths']['toolpath']=[0]

GenerateToolpath.Do()
PrintToolpath.Do({'toolpath':GenerateToolpath.requirements['target']['value']})

proclist = MyApparatus.proclog