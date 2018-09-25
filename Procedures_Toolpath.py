from Procedure import procedure
import Procedures_Motion
import Procedures_Parses

class Generate_Toolpath(procedure):
    def Prepare(self):
        self.name = 'Generate_Toolpath'
        self.requirements['parameters']={'source':'apparatus', 'address':'', 'value':'', 'desc':'parameters used to generate toolpath'}
        self.requirements['generator']={'source':'apparatus', 'address':'', 'value':'', 'desc':'pointer to generator'}
        self.requirements['target']={'source':'apparatus', 'address':'', 'value':'', 'desc':'where to store the toolpath'}
        self.requirements['parameters']['address']=['information','toolpaths','parameters']
        self.requirements['generator']['address']=['information','toolpaths','generator']
        self.requirements['target']['address']=['information','toolpaths','toolpath']
    
    def Plan(self):
        parameters = self.requirements['parameters']['value']
        generator = self.requirements['generator']['value']
        target = self.requirements['target']['value']        
        
        systemname = self.apparatus.findDevice({'descriptors':'system'})
        
        runprog = self.apparatus.GetEproc(systemname, 'Run')
        
        runprog.Do({'address':generator, 'addresstype':'pointer', 'arguments':[parameters, target]})

class Print_Toolpath(procedure):
  
    def Prepare(self):
        self.name = 'Print_Toolpath'
        self.requirements['toolpath'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'toolpath to be printed'}
        self.move = Procedures_Motion.RefRelLinearMotion(self.apparatus, self.executor)
        self.start = Procedures_Parses.Start(self.apparatus, self.executor)
        self.startmotion = Procedures_Parses.StartofMotion(self.apparatus, self.executor)
        self.endmotion = Procedures_Parses.EndofMotion(self.apparatus, self.executor)
        self.changemat = Procedures_Parses.ChangeMat(self.apparatus, self.executor)
        self.endoflayer = Procedures_Parses.EndofLayer(self.apparatus, self.executor)

          
    
    def Plan(self):
        #Renaming useful pieces of informaiton
        toolpath = self.requirements['toolpath']['value'][0]

        #Retreiving necessary device names
        
        #Getting necessary eprocs
        
        #Assign apparatus addresses to procedures
        
        #Doing stuff
        for line in toolpath:
            if 'parse' in line:
                if line['parse']=='start':
                    self.start.Do()
                if line['parse']=='startofmotion':
                    self.startmotion.Do({'motion':line['motion']})
                if line['parse']=='endofmotion':
                    self.endmotion.Do({'motion':line['motion']})
                if line['parse']=='changemat':
                    self.changemat.Do({'startmotion':line['startmotion'],'endmotion':line['endmotion']})
                if line['parse']=='endoflayer':
                    self.endoflayer.Do({'layernumber':line['number']})
            else:
                motionname = self.apparatus.findDevice({'descriptors': 'motion' })
                nozzlename = self.apparatus.findDevice({'descriptors':['nozzle', line['material']] })
                refpoint = self.apparatus['information']['alignments'][nozzlename+'@start']
                speed = self.apparatus['devices'][motionname][nozzlename]['speed']
                axismask = self.apparatus['devices'][motionname][nozzlename]['axismask']
                self.move.Do({'refpoint':refpoint,'relpoint':line['endpoint'], 'speed':speed, 'axismask':axismask})

