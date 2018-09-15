'''
These procedures are related to calibrating the ink extrusion rate and the
pump timing using a fairly simple and robust conversion from mass extrution
rate to volumetric extrusion rate to speed from target trace geometry.

'''

from Procedure import procedure
import time
import json
import Procedures_Motion
import Procedures_Pumps


class Calibrate(procedure):
    def Prepare(self):
        self.name = 'Calibrate'
        self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of alignmentfile'}
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.cal_calculation = Cal_Calulation(self.apparatus, self.executor)
        self.cal_measurement = Cal_Measurement(self.apparatus, self.executor)

    def Plan(self):
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']

        # Do stuff
        # Handle the first call of a calibration on a particular material
        # This involves choosing to calibrate or not and whether to make a new file
        if not self.apparatus['information']['materials'][material]['calibrated']:
            usecal = input('Would you like to use ink calibraton for ' + material + '?([y],n)')
            if usecal in ['Y', 'y', 'yes', 'Yes', '']:
                self.apparatus['information']['materials'][material]['calibrated'] = True
                newfile = input('Would you like to make a new file for ' + material + '?(y,[n])')
                if newfile in ['Y', 'y', 'yes', 'Yes']:
                    # Clear existing file
                    cfilename = material + filename
                    tempfile = open(cfilename, mode='w')
                    tempfile.close()
                    self.cal_measurement.Do({'material': material})
                else:
                    newdata = input('Would you like to make new measurement of ' + material + '?(y,[n])')
                    if newdata in ['Y', 'y', 'yes', 'Yes']:
                        self.cal_measurement.Do({'material': material})
                    else:
                        self.cal_calculation.Do({'material': material})

        else:
            self.cal_measurement.Do({'material': material})

        # Save a copy of the alignments to the main folder and to the log folder
        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)

        with open('Logs/'+str(int(round(time.time(), 0)))+filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)


class Cal_Measurement(procedure):
    def Prepare(self):
        self.name = 'Cal_Measurement'
        self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of alignmentfile'}
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.pmotion = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.pumpon = Procedures_Pumps.PumpOn(self.apparatus, self.executor)
        self.pumpoff = Procedures_Pumps.PumpOff(self.apparatus, self.executor)

    def Plan(self):
        # Reassignments for convienence
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']

        # FIND devices needed for procedure
        motion = self.apparatus.findDevice({'descriptors': ['motion']})
        system = self.apparatus.findDevice({'descriptors': ['system']})
        nozzle = self.apparatus.findDevice({'descriptors': ['nozzle', material]})
        pump = self.apparatus.findDevice({'descriptors': ['pump', material]})

        #Find elemental procedures
        run = self.apparatus.GetEproc(motion, 'Run')
        dwell = self.apparatus.GetEproc(system, 'Dwell')
        
        self.pmotion.requirements['axismask']['address'] = ['devices', motion, 'n'+material, 'axismask']
        self.pmotion.requirements['refpoint']['address'] = ['information', 'alignments', 'n'+material+'@cal']
        self.pmotion.requirements['speed']['address'] = ['devices', motion, 'default', 'speed']

        # Do stuff
        # Go to calibration position
        self.pmotion.Do({'priority': [['Z'], ['X', 'Y']]})
        run.Do()

        #Get intial information
        initialweightok = False
        while not initialweightok:
            initialweightstr = input('What is the initial weight of the slide in grams?')
            try:
                initialweight = float(initialweightstr)
                qtext = 'Is ' + initialweightstr + 'g the correct value?(y/n)'
                confirmation = input(qtext)
                if confirmation == 'y':
                    initialweightok = True
            except:
                print('That is not a number.  Try again.')
        input('Put slide in place and press ENTER.')
        
        #turn pumps on and off
        ptime =self.apparatus['information']['ink calibration']['time']
        
        self.pumpon.Do({'name': pump})
        dwell.Do({'dtime': ptime})
        self.pumpoff.Do({'name': pump})
        
        finalweightok = False
        while not finalweightok:
            finalweight = input('What is the final weight of the slide in grams?')
            try:
                dataline['finalweight'] = float(finalweight)
                qtext = 'Is ' + str( dataline['finalweight']) + 'g the correct value?(y/n)'
                confirmation = input(qtext)
                if confirmation == 'y':
                    finalweightok = True
            except:
                print('That is not a number.  Try again.')
        # Save a copy of the alignments to the main folder and to the log folder
        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)

        with open('Logs/'+str(int(round(time.time(), 0)))+filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)
            



def fproc_ProcessData(apparatus, material, dataline):
    eproclines =[]
    nozzle = apparatus.findDevice({'descriptors':['nozzle',material]})
    
    density = apparatus['information']['materials'][material]['density']
    width = apparatus['devices'][nozzle]['TraceWidth']
    height = apparatus['devices'][nozzle]['TraceHeight']
    
    details = {}
    details['programaddress']=prog_ProcessData
    details['addresstype']='pointer'
    details['arguments']=[dataline, density, width, height]
    eproclines.append([{'devices':'system', 'procedure':'Run', 'details':details}])
    
    return eproclines

def prog_ProcessData(dataline, density, width, height):
    
        
    dweight = dataline['finalweight'] - dataline['initialweight'] #g
    exvolume = dweight/density*1000 #mm^3
    vexrate = exvolume / (60) #mm^3/s
    target_width = width #mm
    crossarea = target_width * height #mm^2
    targetspeed = vexrate/crossarea #m/s
    
    dataline['speed'] = targetspeed 

def fproc_SaveCalData(material, dataline):
    eproclines =[]
    
    details = {}
    details['programaddress']=prog_SaveCalData
    details['addresstype']='pointer'
    details['arguments']=[material, dataline]
    eproclines.append([{'devices':'system', 'procedure':'Run', 'details':details}])
    
    return eproclines

def prog_SaveCalData( material, dataline):
    filename = material + 'log.json'
    timevalue = time.time()
    dataline['time'] = timevalue
    try:
        prevdata=LoadInkCal(material)
    except:
        prevdata = []
        
    prevdata.append(dataline)
    
    with open(filename, 'w') as TPjson:
        json.dump(prevdata, TPjson) 

    
def LoadInkCal(material):
    filename = material + 'log.json' 
    with open(filename, 'r') as caljson:
        data = json.load(caljson)
    
    return data   

def fproc_UpdateInk(apparatus, material):
    eproclines =[]
    nozzle = apparatus.findDevice({'descriptors':['nozzle',material]})

    density = apparatus['information']['materials'][material]['density']
    width = apparatus['devices'][nozzle]['TraceWidth']
    height = apparatus['devices'][nozzle]['TraceHeight']
        
    details = {}
    details['programaddress']=prog_UpdateInk
    details['addresstype']='pointer'
    details['arguments']=[apparatus, material, density, width, height]
    
    if 'UpdateSpeed' in apparatus['information']['materials'][material]:
        details['arguments'].append(apparatus['information']['materials'][material]['UpdateSpeed'])
    else:
        details['arguments'].append(True)
    
    if 'UpdatePumpOn' in apparatus['information']['materials'][material]:
        details['arguments'].append(apparatus['information']['materials'][material]['UpdatePumpOn'])
    else:
        details['arguments'].append(True)
    
    eproclines.append([{'devices':'system', 'procedure':'Run', 'details':details}])
    
    return eproclines

def prog_UpdateInk(apparatus, material, density, width, height, UpdateSpeed, UpdatePumpOn):
    #Get the associated devices
    motion = apparatus.findDevice({'descriptors':['motion']})
    nozzle = apparatus.findDevice({'descriptors':['nozzle', material]})
    pump = apparatus.findDevice({'descriptors':['pump', material]})
    
    #Load information for specific ink
    data=LoadInkCal(material)
    
    if UpdateSpeed:
        #Calculate and Update Speed
        if len(data)==1:
            dataline = data[0]
            prog_ProcessData(dataline, density, width, height)
            apparatus['devices'][motion][nozzle]['motion']['speed'] = dataline['speed']
        else: #assume linear drift
            pdataline = data[len(data)-2]
            prog_ProcessData(pdataline, density, width, height)
            dataline = data[len(data)-1]
            prog_ProcessData(dataline, density, width, height)
            current_time = time.time()
            deltat = float(dataline['time'])-float(pdataline['time'])
            deltas = float(dataline['speed'])-float(pdataline['speed'])
            apparatus['devices'][motion][nozzle]['motion']['speed'] = float(dataline['speed']) + deltas/deltat * (current_time-dataline['time'])
    
    if UpdatePumpOn:    
        #Calculate and Update Pumpontimes
        apparatus['devices'][pump]['pumpontime']=apparatus['devices'][pump]['pumprestime']+1.5*apparatus['devices'][nozzle]['TraceHeight']/apparatus['devices'][motion][nozzle]['motion']['speed']
        
def fproc_UpdateCalStatus(apparatus, material):
    eproclines =[]
    
    details = {}
    details['programaddress']=prog_UpdateCalStatus
    details['addresstype']='pointer'
    details['arguments']=[apparatus, material]
    eproclines.append([{'devices':'system', 'procedure':'Run', 'details':details}])
    
    return eproclines

def prog_UpdateCalStatus(apparatus, material):
    apparatus['information']['materials'][material]['calibrated'] = True



