from Procedure import procedure
import Procedures_Motion
import json
import time


class Align(procedure):
    def Prepare(self):
        self.name = 'Align'
        self.requirements['Measured_List']={'source':'apparatus', 'address':['information','alignmentnames'], 'value':'', 'desc':'parameters used to generate toolpath'}
        self.requirements['primenoz']={'source':'apparatus', 'address':'', 'value':'', 'desc':'prime material'}
        self.requirements['filename']={'source':'apparatus', 'address':'', 'value':'', 'desc':'name of alignmentfile'}
        self.requirements['filename']['address']=['information','alignmentsfile']
        self.updatealign = UpdateAlignment(self.apparatus, self.executor)
        self.derivealign = DeriveAlignments(self.apparatus, self.executor)
    
    def Plan(self):
        measuredlist = self.requirements['Measured_List']['value']
        primenoz = self.requirements['primenoz']['value']
        filename = self.requirements['filename']['value']
        
        #Doing stuff
        
        #Check for loading file
        alignmentscollected = False
        doalignment = input('Import alignments from file?([y]/n/filename)')
        if doalignment in ['y','Y','yes','Yes','YES', '']:
            afilename = input('What filename?([' + filename + '])')
            if afilename == '':
                afilename = filename
            try:
                print(filename)
                with open(filename, 'r') as TPjson:
                     self.apparatus['information']['alignments'] = json.load(TPjson)
                alignmentscollected = True
            except:
                print('No file loaded.  Possible error in ' + afilename)
        
        if not alignmentscollected:
            for alignment in measuredlist:
                self.updatealign.Do({'alignmentname':alignment})
            self.derivealign.Do({'Measured_List':measuredlist, 'primenoz':primenoz})

        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)

        with open('Logs/'+str(int(round(time.time(),0)))+filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)
            
class UpdateAlignment(procedure):
    def Prepare(self):
        self.name = 'GetAlignment'
        self.requirements['alignmentname']={'source':'apparatus', 'address':'', 'value':'', 'desc':'parameters used to generate toolpath'}

    
    def Plan(self):
        
        alignmentname = self.requirements['alignmentname']['value']
        alignment = self.apparatus['information']['alignments'][alignmentname]
        
        motionname = self.apparatus.findDevice({'descriptors':'motion'})
        
        getpostion = self.apparatus.GetEproc(motionname, 'getPosition')
        
        #Doing stuff
        input('Move to ' + alignmentname + ',and press ENTER when there.')
        dimlist = list(alignment)
        if self.apparatus.simulation:
            tempposition = input('What is the simulated value of the form ' + str(dimlist) + '?')
            tempposition = tempposition.replace('[','')
            tempposition = tempposition.replace(']','')
            tempposition = tempposition.split(',')
            tempposition = [float(x) for x in tempposition]   
        else:
            datavessel = [0]
            getpostion.Do({'addresstype':'pointer','address':datavessel, 'axislist':dimlist})
            tempposition = datavessel[0]

        n=0
        for dim in dimlist:
            alignment[dim] = tempposition[n]
            n += 1

class DeriveAlignments(procedure):
    def Prepare(self):
        self.name = 'DeriveAlignments'
        self.requirements['Measured_List']={'source':'apparatus', 'address':'', 'value':'', 'desc':'list of measurements'}
        self.requirements['primenoz']={'source':'apparatus', 'address':'', 'value':'', 'desc':'prime material'}
    
    def Plan(self):
        measuredlist = self.requirements['Measured_List']['value']
        primenoz = self.requirements['primenoz']['value']
        alignments = self.apparatus['information']['alignments']
        
        motionname = self.apparatus.findDevice({'descriptors':'motion'})
        
        toollist = [n.partition('@')[0] for n in measuredlist]
        
        #Doing stuff 
        alignments['safeZZ1'] = {'ZZ1':alignments['initial']['ZZ1']}
        alignments['safeZZ2'] = {'ZZ2':alignments['initial']['ZZ2']}
        alignments['safeZZ3'] = {'ZZ3':alignments['initial']['ZZ3']}
        alignments['safeZZ4'] = {'ZZ4':alignments['initial']['ZZ4']}
        
        toollist.remove('initial')
        
        paxismask = self.apparatus['devices'][motionname][primenoz]['axismask']
        pzaxis = 'Z'
        if 'Z' in paxismask:
            pzaxis =paxismask['Z']

        for tool in toollist:
            zaxis = 'Z'
            axismask = self.apparatus['devices'][motionname][tool]['axismask']
            if 'Z' in axismask:
                zaxis =axismask['Z']
            print(pzaxis)
            print(zaxis)
            for name in [tool+'@start',tool+'slide@start',tool+'@cal']:
                if name not in alignments:
                    alignments[name]={}
            alignments[tool+'@start']['X']=alignments[primenoz+'@start']['X'] -(alignments[primenoz+'@mark']['X'] - alignments[tool+'@mark']['X'])
            alignments[tool+'@start']['Y']=alignments[primenoz+'@start']['Y'] -(alignments[primenoz+'@mark']['Y'] - alignments[tool+'@mark']['Y'])
            alignments[tool+'@start'][zaxis]=alignments[primenoz+'@start'][pzaxis] -(alignments[primenoz+'@mark'][pzaxis] - alignments[tool+'@mark'][zaxis])
            alignments[tool+'slide@start'] = alignments[tool+'@start']
            alignments[tool+'@cal']['X']=alignments[primenoz+'@cal']['X'] -(alignments[primenoz+'@mark']['X'] - alignments[tool+'@mark']['X'])
            alignments[tool+'@cal']['Y']=alignments[primenoz+'@cal']['Y'] -(alignments[primenoz+'@mark']['Y'] - alignments[tool+'@mark']['Y'])
            alignments[tool+'@cal'][zaxis]=alignments[primenoz+'@cal'][pzaxis] -(alignments[primenoz+'@mark'][pzaxis] - alignments[tool+'@mark'][zaxis])
            
def mList(alignlist):
    #alignlist is the list of devices that need to be aligned
    alignable_names=[]
    if len(alignlist)>1:
        for alignable in alignlist:
            alignable_names.append('m'+alignable + '@mark')

def DoAlignments(alignmentnames, apparatus, filename='alignments.json'):
    alignments = dialogue_loadfromfile(filename)
    if alignments == {}:
        alignments = dialogue_newalign(alignmentnames, apparatus)
    SaveAlignments(alignments, filename)
    RedoAlignment(apparatus, alignmentnames, alignments, filename)
    return alignments

def RedoAlignment(apparatus, alignmentnames, alignments, filename):
    alignmentsOK = False
    while not alignmentsOK:
        redoalignments = input('Would you like to redo any alignments?(y/[n])')
        if redoalignments in ['n','N','no','No','NO','']:
            alignmentsOK = True
        else:
            namestring = ''
            for name in alignmentnames:
                namestring += name + ' '
                
            which_alignment = input('Which alignment would you like to redo? (pick from list below)\n'+namestring)
            alignments[which_alignment] = GetAlignment(apparatus, which_alignment)
        SaveAlignments(alignments, filename)
        

             
    

def Alignments_Measured2Req(apparatus, alignments, primemat, calibrate=True):
    motion = apparatus.findDevice({'type':'A3200Dev'})
    
    #handle the initials point
    alignments['initial'] = alignments['minitial']
    #handle the safe heights
    alignments['safeZZ1'] = {'ZZ1':alignments['minitial']['ZZ1']}
    alignments['safeZZ2'] = {'ZZ2':alignments['minitial']['ZZ2']}
    alignments['safeZZ3'] = {'ZZ3':alignments['minitial']['ZZ3']}
    alignments['safeZZ4'] = {'ZZ4':alignments['minitial']['ZZ4']}

    #handle the start positions of the materials
    for material in apparatus['information']['materials']:
        pmatzaxis = apparatus['devices'][motion]['n'+primemat]['Zaxis']
        matzaxis = apparatus['devices'][motion]['n'+material]['Zaxis']
        alignments['n'+material+'@start']={}
        alignments['n'+material+'@start']['X']=alignments['mn'+primemat+'@start']['X'] -(alignments['mn'+primemat+'@mark']['X'] - alignments['mn'+material+'@mark']['X'])
        alignments['n'+material+'@start']['Y']=alignments['mn'+primemat+'@start']['Y'] -(alignments['mn'+primemat+'@mark']['Y'] - alignments['mn'+material+'@mark']['Y'])
        alignments['n'+material+'@start'][matzaxis]=alignments['mn'+primemat+'@start'][pmatzaxis] -(alignments['mn'+primemat+'@mark'][pmatzaxis] - alignments['mn'+material+'@mark'][matzaxis])
        alignments['n'+material+'slide@start'] = alignments['n'+material+'@start']    
    
    #handle calibration positions
    if calibrate:
        for material in apparatus['information']['materials']:
            pmatzaxis = apparatus['devices'][motion]['n'+primemat]['Zaxis']
            matzaxis = apparatus['devices'][motion]['n'+material]['Zaxis']
            alignments['n'+material+'@cal']={}
            alignments['n'+material+'@cal']['X']=alignments['mn'+primemat+'@cal']['X'] -(alignments['mn'+primemat+'@mark']['X'] - alignments['mn'+material+'@mark']['X'])
            alignments['n'+material+'@cal']['Y']=alignments['mn'+primemat+'@cal']['Y'] -(alignments['mn'+primemat+'@mark']['Y'] - alignments['mn'+material+'@mark']['Y'])
            alignments['n'+material+'@cal'][matzaxis]=alignments['mn'+primemat+'@cal'][pmatzaxis] -(alignments['mn'+primemat+'@mark'][pmatzaxis] - alignments['mn'+material+'@mark'][matzaxis])


def derive_alignments(alignments):
    #Direct assignments
    alignments['initial'] = alignments['Initial']   
    alignments['safeZZ1'] = {'ZZ1':alignments['Initial']['ZZ1']}
    alignments['safeZZ2'] = {'ZZ2':alignments['Initial']['ZZ2']}
    alignments['safeZZ3'] = {'ZZ3':alignments['Initial']['ZZ3']}
    alignments['safeZZ4'] = {'ZZ4':alignments['Initial']['ZZ4']}
    alignments['nPDMS@start'] = {'X':alignments['Mat1 at Start']['X'], 'Y':alignments['Mat1 at Start']['Y'], 'ZZ1':alignments['Mat1 at Start']['ZZ1']}
    alignments['nPDMSslide@start'] = alignments['nPDMS@start']
    alignments['PDMScal']= {'X':alignments['Mat1 at Cal']['X'],'Y':alignments['Mat1 at Cal']['Y'],'ZZ1':alignments['Mat1 at Cal']['ZZ1']}
    
    #Calculated
    alignments['nAgTPU@start']={}
    alignments['nAgTPU@start']['X']=alignments['Mat1 at Start']['X'] -(alignments['Mat1 at corner']['X'] - alignments['Mat2 at corner']['X'])
    alignments['nAgTPU@start']['Y']=alignments['Mat1 at Start']['Y'] -(alignments['Mat1 at corner']['Y'] - alignments['Mat2 at corner']['Y'])
    alignments['nAgTPU@start']['ZZ2']=alignments['Mat1 at Start']['ZZ1'] -(alignments['Mat1 at corner']['ZZ1'] - alignments['Mat2 at corner']['ZZ2'])
    alignments['nAgTPUslide@start'] = alignments['nAgTPU@start']
    alignments['AgTPUcal'] = {}
    alignments['AgTPUcal']['X']=alignments['Mat1 at Cal']['X'] -(alignments['Mat1 at corner']['X'] - alignments['Mat2 at corner']['X'])
    alignments['AgTPUcal']['Y']=alignments['Mat1 at Cal']['Y'] -(alignments['Mat1 at corner']['Y'] - alignments['Mat2 at corner']['Y'])
    alignments['AgTPUcal']['ZZ2']=alignments['Mat1 at Cal']['ZZ1'] -(alignments['Mat1 at corner']['ZZ1'] - alignments['Mat2 at corner']['ZZ2'])

            


def SaveAlignments(alignments, filename):
    with open(filename, 'w') as TPjson:
        json.dump(alignments, TPjson)

def PrintAlignments(alignments):
    printstr = ''
    alignlist = list(alignments.keys())
    for alignment in alignlist:
        printstr = printstr + alignment + '\n'+ ' '
        dimlist = list(alignments[alignment].keys())
        for dim in dimlist:
            printstr += dim + ' ' + str(alignments[alignment][dim])
        printstr += '\n\n'
    print(printstr)
        


