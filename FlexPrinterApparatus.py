def Build_FlexPrinter(materials, apparatus):
    
    #General Printer settings
    devices = {}
    devices['gantry']={'type':'A3200Dev', 'model':'Flex Printer', 'descriptors':['motion'],'addresstype':'pointer'}
    devices['gantry']['default']={}
    devices['gantry']['default']['motion']={'speed':40, 'length_units':'mm', 'MotionRamp':1000, 'MaxAccel':1000, 'RelAbs':'Abs', 'LookAhead':True, 'mode':'loadrun', 'axismask':{}}
    apparatus['information']['materials']={}
    apparatus['information']['alignments']={}
    apparatus['information']['alignments']['initial']= {'X':'','Y':'', 'ZZ1':'', 'ZZ2':'', 'ZZ3':'', 'ZZ4':''}
    apparatus['information']['alignmentnames']=['initial']
    apparatus['information']['alignmentsfile']='alignments.json'
    apparatus['information']['calibrationfile']='cal.json'
    apparatus['information']['ink calibration']={}
    apparatus['information']['ink calibration']['time'] = 60
    
    primenozzle = True
    for materialx in materials:
        material = list(materialx)[0]
        zaxis = materialx[material]
        #nozzle devices
        devices['n'+ material]={'ID':'', 'OD':'', 'TraceHeight':'','TraceWidth':'', 'type':'','addresstype':'','descriptors':['nozzle',material]}
        devices['n' + material + 'slide']={'ID':'', 'OD':'', 'type':'','addresstype':'','descriptors':['nozzle',material+'slide']}        
        #motion details for nozzles
        devices['gantry']['n'+material] = {'axismask':{'Z':zaxis}}
        devices['gantry']['n'+material]['motion'] = {'speed':'',  'MotionRamp':devices['gantry']['default']['motion']['MotionRamp'], 'MaxAccel':devices['gantry']['default']['motion']['MaxAccel']}
        devices['gantry']['n'+material+'slide'] = {}
        devices['gantry']['n'+material+'slide']['axismask'] = devices['gantry']['n'+material]['axismask']
        devices['gantry']['n'+material+'slide']['motion']={'speed':devices['gantry']['default']['motion']['speed'],  'MotionRamp':1000, 'MaxAccel':1000}
        #information location for each material
        apparatus['information']['materials'][material]={}
        apparatus['information']['alignmentnames'].append('n'+material+'@mark')
        apparatus['information']['alignments']['n'+material+'@mark']= {'X':'','Y':'', zaxis:''}
        #treat first nozzle as prime nozzles
        if primenozzle:
            apparatus['information']['alignmentnames'].append('n'+material+'@start')
            apparatus['information']['alignments']['n'+material+'@start']= {'X':'','Y':'', zaxis:''}
            apparatus['information']['alignmentnames'].append('n'+material+'@cal')
            apparatus['information']['alignments']['n'+material+'@cal']= {'X':'','Y':'', zaxis:''}
            primenozzle = False
    
    #pumps
    n = 0
    for materialx in materials:
        devices['pump'+str(n)]={'type':'UltimusVDev', 'COM':'','pressure':0, 'vacuum':0, 'pumprestime':0,'pumpontime':0, 'pumpofftime':0, 'midtime':0, 'addresstype':'pointer','descriptors':[]}
        devices['aeropump'+str(n)]={'type':'UltimusVDev_A3200', 'pumpname':'pump'+str(n), 'A3200name':'gantry', 'IOaxis': 'ZZ1', 'IObit':2 ,'pressure':0, 'vacuum':0, 'pumprestime':0,'pumpontime':0, 'pumpofftime':0, 'midtime':0, 'addresstype':'pointer','descriptors':[]}
        n += 1
    #System
    devices['system'] = {'type':'System', 'addresstype':'pointer'}
    apparatus['devices']=devices
    
