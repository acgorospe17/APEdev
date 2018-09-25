import Apparatus
import Procedures_Toolpath
import Procedures_Alignments
import Executor
import XlineTPGen as TPGen
import FlexPrinterApparatus

MyApparatus = Apparatus.apparatus()
MyExecutor = Executor.executor()
MyExecutor.debug = True

materials = [{'PDMS': 'ZZ1'}, {'AgTPU': 'ZZ2'}]

FlexPrinterApparatus.Build_FlexPrinter(materials, MyApparatus)

MyApparatus['devices']['nPDMS']['descriptors'].append('PDMS')
MyApparatus['devices']['nPDMS']['trace_height'] = 0.2
MyApparatus['devices']['nPDMS']['trace_width'] = 0.8
MyApparatus['devices']['aeropump0']['descriptors'].append('PDMS')
MyApparatus['devices']['nAgTPU']['descriptors'].append('AgTPU')
MyApparatus['devices']['nAgTPU']['trace_height'] = 0.1
MyApparatus['devices']['nAgTPU']['trace_width'] = 0.1
MyApparatus['devices']['pump1']['descriptors'].append('AgTPU')
MyApparatus['devices']['gantry']['default']['speed'] = 40
MyApparatus['devices']['gantry']['nPDMS']['speed'] = 5
MyApparatus['devices']['gantry']['nAgTPU']['speed'] = 7
MyApparatus['devices']['aeropump0']['pumpon_time'] = 1
MyApparatus['devices']['aeropump0']['mid_time'] = 2
MyApparatus['devices']['aeropump0']['pumpoff_time'] = 3
MyApparatus['devices']['aeropump0']['pumpres_time'] = 0.2
MyApparatus['devices']['pump0']['COM'] = 3
MyApparatus['devices']['pump1']['COM'] = 5
MyApparatus['devices']['pump1']['pumpon_time'] = 2
MyApparatus['devices']['pump1']['mid_time'] = 3
MyApparatus['devices']['pump1']['pumpoff_time'] = 4


MyApparatus.Connect_All(MyExecutor, simulation=True)


AlignPrinter = Procedures_Alignments.Align(MyApparatus, MyExecutor)
GenerateToolpath = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
PrintToolpath = Procedures_Toolpath.Print_Toolpath(MyApparatus, MyExecutor)

AlignPrinter.Do({'primenoz':'nPDMS'})
MyApparatus['information']['materials']['PDMS']['density'] = 1.1
MyApparatus['information']['materials']['AgTPU']['density'] = 3
MyApparatus['information']['toolpaths']={}
MyApparatus['information']['toolpaths']['generator']=TPGen.GenerateToolpath
MyApparatus['information']['toolpaths']['parameters']=TPGen.Make_TPGen_Data('PDMS')
MyApparatus['information']['toolpaths']['toolpath']=[0]

GenerateToolpath.Do()
PrintToolpath.Do({'toolpath':GenerateToolpath.requirements['target']['value']})
procedure_log=MyApparatus.proclog