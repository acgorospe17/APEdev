import Procedure
import time
from Drivers import A3200
from Drivers import Ultimus_V as UltimusV

# Parent class of all devices bleh
class Device():
    def __init__(self, name):
        self.simulation = False
        self.connected = False
        self.name = name
        self.on = False
        self.descriptors = []
        self.driver_address = ''
        self.addresstype = 'pointer'
        self.procaddresstype = 'pointer'
        self.send_addresstype = 'direct'
        self.dependent_device = False
        self.requirements = {}
        self.log = ''

        # Description of methods that will be treated as elemental procedures
        self.requirements['On'] = {}
        self.requirements['Off'] = {}
        self.requirements['Set'] = {}
        self.requirements['Connect'] = {}
        self.requirements['Disconnect'] = {}

    def On(self):
        self.addlog(self.name + ' on')

        return self.returnlog()

    def Off(self):
        self.addlog(self.name + ' off')

        return self.returnlog()

    def Set(self):
        self.addlog(self.name + ' set')

        return self.returnlog()

    def CreateEprocs(self, apparatus, executor):
        for eleproc in self.requirements:
            eprocEntry = {'device': self.name,
                          'method': eleproc,
                          'handle': Procedure.eproc(apparatus, executor, self.name, eleproc, self.requirements[eleproc])}
            apparatus['eproclist'].append(eprocEntry)

    def returnlog(self):
        message = self.log
        self.log = ''

        return message

    def addlog(self, logstr):
        self.log += logstr + '\n'

    def ERegister(self, executer):
        executer.loadDevice(self.name, self, 'pointer')

    def Connect(self):
        self.addlog(self.name + ' is connected.')

        return self.returnlog()

    def Disconnect(self):
        self.addlog(self.name + ' is disconnected.')

        return self.returnlog()


class System(Device):
    def __init__(self, name):
        Device.__init__(self,name)

        self.descriptors.append('system')

        self.requirements['Dwell'] = {}
        self.requirements['Dwell']['dtime'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'time to wait in seconds'}

        self.requirements['Run'] = {}
        self.requirements['Run']['address'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'address of the program or pointer to it'}
        self.requirements['Run']['addresstype'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'type of address'}
        self.requirements['Run']['arguments'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'list of the arguments for the program in order. Will be decomposed with * operator'}

    def Set(self, pressure=''):
        self.pressure = pressure
        self.log = self.name + ' set to ' + self.pressure

        return self.returnlog()

    def Dwell(self, dtime=''):
        if not self.simulation and dtime != '':
            time.sleep(dtime)
        self.log = self.name + ' waited ' + str(dtime) + ' s.'

        return self.returnlog()

    def Run(self, address='', addresstype='pointer', arguments=[]):
        if addresstype == 'pointer':
            address(*arguments)
        self.log = self.name + ' ran a program'

        return self.returnlog()


class Motion(Device):
    def __init__(self, name):
        Device.__init__(self, name)

        self.descriptors.append('motion')

        self.commandlog = []
        self.motiontype = 'linear'
        self.motionmode = 'loadrun'
        self.axes = ['X', 'x', 'Y', 'y', 'Z', 'z']
        self.motionsetting = {}

        self.requirements['Move'] = {}
        self.requirements['Move']['point'] = {'value': '', 'source': 'apparatus', 'address': '',
                                              'desc': 'Dictionary with the motions sytem axes as keys and target values'}
        self.requirements['Move']['speed'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'speed of motion, typicaly in mm/s'}
        self.requirements['Move']['motiontype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'speed of motion, typicaly in mm/s'}
        self.requirements['Move']['motionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun'}

        self.requirements['Set_Motion'] = {}
        self.requirements['Set_Motion']['RelAbs'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Relative or Absolute motion'}
        self.requirements['Set_Motion']['dmotionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'default motion mode'}
        self.requirements['Set_Motion']['dmotiontype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'default motion type'}
        self.requirements['Set_Motion']['motionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun'}

    def Move(self, point={}, speed=0, motiontype='', motionmode=''):
        self.commandlog.append(self.MotionCMD(point, speed, motiontype))
        self.fRun(motionmode)

        return self.returnlog()

    def Set_Motion(self, RelAbs='', dmotionmode='', dmotiontype='', motionmode=''):
        if dmotionmode != '':
            self.motionmode = dmotionmode
            self.motionsettings['motionmode'] = dmotionmode

        if dmotiontype != '':
            self.motiontype = dmotiontype
            self.motionsettings['motiontype'] = dmotiontype

        if RelAbs != '':
            self.fSet_RelAbs(RelAbs, motionmode)

        return self.returnlog()

    def fSet_RelAbs(self, RelAbs, motionmode):
        if RelAbs == 'Rel':
            self.commandlog.append('G91 \n')

        if RelAbs == 'Abs':
            self.commandlog.append('G90 \n')

        self.motionsettings['RelAbs'] = RelAbs
        self.fRun(motionmode)

    def MotionCMD(self, point, speed, motiontype):
        if motiontype == '':
            motiontype = self.motiontype
        cmdline = ''
        if motiontype == 'linear':
            cmdline += 'G01 '
            for axis in self.axes:
                if axis in point:
                    cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' '
            cmdline += 'F ' + '{0:f}'.format(speed) + ' '
            cmdline += '\n'

        return cmdline

    def Run(self, motionmode=''):
        if motionmode == '':
            motionmode = 'cmd'
        self.fRun(motionmode)
        return self.returnlog()

    def fRun(self, motionmode):
        if motionmode == '':
            motionmode = self.motionmode
        if motionmode == 'loadrun':
            self.addlog('Commands Loaded')
        elif motionmode == 'cmd':
            cmdline = self.commandlog
            self.sendCommands(cmdline)
            self.commandlog = []

    def sendCommands(self, commands):
        message = ''

        for line in commands:
            message += line

        self.addlog(message)


class Sensor(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.eprocs = [*self.eprocs, *['Measure', 'Settings', 'Calibrate']]
        self.returnformat = ''
        self.result = ''

    def StoreMeasurement(self, address, addresstype, result):
        if addresstype == 'pointer':
            # this assumes that address=[0] exists when this method is used.
            address[0] = result

    def Measure(self, address='', addresstype=''):
        pass

    def Sensor_Calibrate():
        pass


class A3200Dev(Motion, Sensor):
    def __init__(self, name):
        Motion.__init__(self, name)

        self.descriptors = [*self.descriptors,
                            *['Aerotech', 'A3200', 'sensor']]

        self.tasklog = {'task1': [], 'task2': [], 'task3': [], 'task4': []}
        self.commandlog = []
        self.defaulttask = 1
        self.handle = ''

        # Possible modes are cmd and loadrun
        self.axes = ['X', 'x', 'Y', 'y',
                     'ZZ1', 'zz1', 'ZZ2', 'zz2', 'ZZ3', 'zz3', 'ZZ4', 'zz4',
                     'i', 'I', 'j', 'J', 'k', 'K']
        self.axismask = {}
        self.maxaxis = 4

        self.requirements['Set_Motion']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Set_Motion']['length_units'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'length units for motion'}
        self.requirements['Set_Motion']['MotionRamp'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Ramp rate for a set of coordinated motions'}
        self.requirements['Set_Motion']['MaxAccel'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Maximum acceleration during coordinated motion'}
        self.requirements['Set_Motion']['LookAhead'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Activate multi-command motion planning'}
        self.requirements['Set_Motion']['axismask'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'how to convert between target and machine dimensions'}
        self.requirements['Set_Motion']['dtask'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'default task'}

        self.requirements['Move'] = {}
        self.requirements['Move']['point'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Information about where to move to'}
        self.requirements['Move']['motiontype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'kind of path taken to point'}
        self.requirements['Move']['speed'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'speed of the motion'}
        self.requirements['Move']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Move']['motionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

        self.requirements['set_DO'] = {}
        self.requirements['set_DO']['axis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'IO axis'}
        self.requirements['set_DO']['bit'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'bit on IO axis'}
        self.requirements['set_DO']['value'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'value of that bit.  0 or 1'}

        self.requirements['Run'] = {}
        self.requirements['Run']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Which task buffer to run'}

        self.requirements['getPosition'] = {}
        self.requirements['getPosition']['address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Address of where to store result'}
        self.requirements['getPosition']['addresstype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Type of address'}
        self.requirements['getPosition']['axislist'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'List of axes that will be reported'}

        self.requirements['getAI'] = {}
        self.requirements['getAI']['address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Address of where to store result'}
        self.requirements['getAI']['addresstype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Type of address'}
        self.requirements['getAI']['axis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Axis of AI'}
        self.requirements['getAI']['channel'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Channel on that axis'}

        self.requirements['Load'] = {}
        self.requirements['Load']['cmstr'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'String of commands to load'}
        self.requirements['Load']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Load']['mode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

    def Connect(self):
        if not self.simulation:
            self.handle = A3200.A3200()
        self.addlog(self.name + ' is connected')

        return self.returnlog()

    def Disconnect(self):
        if not self.simulation:
            self.handle.disconnect()
        self.addlog(Device.Disconnect(self))

        return self.returnlog()

    def Set_Motion(self, dtask='', axismask='', length_units='', RelAbs='', MotionRamp='', MaxAccel='', LookAhead='', dmotionmode='', dmotiontype='', motionmode='', task=''):
        # These direct assignments are somewhat queue jumping at the moment
        if dtask != '':
            self.defaulttask = dtask

        if dmotiontype != '':
            self.motiontype = dmotiontype

        if dmotionmode != '':
            self.motionmode = dmotionmode

        if task == '':
            task = self.defaulttask

        if motionmode == '':
            motionmode = self.motiontype

        # These do not que jump
        if axismask != '':
            self.fSet_axismask(axismask, task, motionmode)

        if RelAbs != '':
            self.fSet_RelAbs(RelAbs, task, motionmode)

        if length_units != '':
            self.fSet_length_units(length_units, task, motionmode)

        if MotionRamp != '':
            self.fSet_MotionRamp(MotionRamp, task, motionmode)

        if MaxAccel != '':
            self.fSet_MaxAccel(MaxAccel, task, motionmode)

        if LookAhead != '':
            self.fSet_LookAhead(LookAhead, task, motionmode)

        return self.returnlog()

    def fSet_axismask(self, axismask, task, motionmode, update=False):
        if update:
            self.axismask = axismask
            self.addlog('Axis mask changed to ' + str(self.axismask))
        else:
            kwargs = {'axismask': axismask, 'task': task, 'motionmode': motionmode, 'update': True}
            self.tasklog['task' + str(task)].append({'function': self.fSet_axismask, 'args': kwargs})

        self.fRun(motionmode,task)

    def fSet_LookAhead(self, LookAhead, task, motionmode):
        if LookAhead:
            self.tasklog['task' + str(task)].append('VELOCITY ON \n')
        else:
            self.tasklog['task' + str(task)].append('VELOCITY OFF \n')
        self.motionsetting['LookAhead'] = LookAhead

        self.fRun(motionmode, task)

    def fSet_MaxAccel(self, MaxAccel, task, motionmode):
        self.tasklog['task' + str(task)].append('CoordinatedAccelLimit = ' + str(MaxAccel) + '\n')
        self.motionsetting['MaxAccel'] = MaxAccel
        self.fRun(motionmode, task)

    def fSet_RelAbs(self, RelAbs, task, motionmode):
        if RelAbs == 'Rel':
            self.tasklog['task' + str(task)].append('G91 \n')

        if RelAbs == 'Abs':
            self.tasklog['task' + str(task)].append('G90 \n')

        self.motionsetting['RelAbs'] = RelAbs
        self.fRun(motionmode, task)

    def fSet_MotionRamp(self, MotionRamp, task, motionmode):
        self.tasklog['task' + str(task)].append('RAMP RATE ' + str(MotionRamp) + '\n')

        self.motionsetting['MotionRamp'] = MotionRamp
        self.fRun(motionmode, task)

    def fSet_length_units(self, length_units, task, motionmode):
        if length_units == 'mm':
            self.tasklog['task' + str(task)].append('G71 \n')

        if length_units == 'inch':
            self.tasklog['task' + str(task)].append('G70 \n')

        self.motionsetting['length_units'] = length_units
        self.fRun(motionmode, task)

    def Set_DO(self, axis='', bit='', value='', task='', motionmode=''):
        if motionmode == '':
            motionmode = self.motionmode

        if task == '':
            task = self.defaulttask

        if not self.simulation:
            cmdstr = '$DO' + '['+str(bit)+'].' + axis + ' = ' + str(value) + ' \n'
            self.tasklog['task'+str(task)].append(cmdstr)
        self.addlog('Bit ' + str(bit) + ' on the ' + str(axis) + ' set to ' + str(value))

        self.fRun(motionmode, task)

        return self.returnlog()

    def Move(self, point='', motiontype='', speed='', task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append({'function': self.MotionCMD, 'args': [point, speed, motiontype]})

        self.fRun(motionmode, task)

        return self.returnlog()

    def MotionCMD(self, point, speed, motiontype):
        if motiontype == '':
            motiontype = self.motiontype
        cmdline = ''

        for dim in self.axismask:
            if dim in point:
                point[self.axismask[dim]] = point[dim]
                point.pop(dim, None)

        if motiontype == 'linear':
            axescount = 0
            cmdline += 'G01 '
            for axis in self.axes:
                if axis in point:
                    axescount += 1
                    if axescount > self.maxaxis:
                        print(cmdline)
                        raise Exception('Number of axes exceeds ITAR limit.')
                    cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' '
            cmdline += 'F ' + '{0:f}'.format(speed) + ' '
            cmdline += '\n'
        self.addlog(cmdline)

        return cmdline

    def Run(self, task=''):
        self.fRun('cmd', task)

        return self.returnlog()

    def fRun(self, motionmode, task):
        if task == '':
            task = self.defaulttask

        if motionmode == '':
            motionmode = self.motionmode
        if motionmode == 'loadrun':
            self.addlog('Commands Loaded')
        elif motionmode == 'cmd':
            self.commandlog = self.tasklog['task' + str(task)]
            self.tasklog['task' + str(task)] = []
            cmdline = self.commandlog
            self.sendCommands(cmdline, task)
            self.commandlog = []

    def getPosition(self, address='', addresstype='', axislist=''):
        # Get the postion from the driver
        if not self.simulation:
            result = self.handle.get_position(axislist)
        else:
            result = input('What are simulation values for ' + str(axislist) + '?')

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.log += (str(axislist) + ' measured to be ' + str(result))

        return self.returnlog()

    def getAI(self, address='', addresstype='', axis='', channel=''):
        # Get the postion from the driver
        if not self.simulation:
            result = self.handle.AI(axis, channel)
        else:
            rstring = input('What is the simulated value for ' + str(axis) + ' ' + str(channel) + '?')
            result = float(rstring)

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.log = ('AI Axis ' + str(axis) + ' channel ' + str(channel) + ' measured to be ' + str(result))

        return self.returnlog()

    def sendCommands(self, commands, task):

        cmdmessage = ''
        for line in commands:
            if type(line) == str:
                cmdmessage += line
                self.addlog(line)
            elif type(line) == dict and line['function'] == self.MotionCMD:
                cmdmessage += line['function'](*line['args'])
            elif type(line) == dict:
                line['function'](**line['args'])
        if not self.simulation:
            self.handle.cmd_exe(cmdmessage, task=task)


if __name__ == '__main__':
    testmotion = A3200Dev('testmotion')
    testmotion.simulation = True
    testmotion.Set_Motion(RelAbs='Abs', MotionRamp=1000, MaxAccel=2000, length_units='mm', LookAhead=True)
    testmotion.Move({'X': 1, 'Y': 2, 'Z': 3}, speed=5)
    testmotion.Move({'X': 1, 'Y': 2, 'Z': 3}, speed=5)
    print(testmotion.Run())


class Pump(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.descriptors.append('pump')
        self.requirements['Set']['pressure'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Pump pressure in kPa'}

    def Set(self, pressure=''):
        self.pressure = pressure
        self.addlog(self.name + ' set to ' + self.pressure)

        return self.returnlog()


class UltimusVDev(Pump):
    def __init__(self, name):
        Device.__init__(self, name)
        self.descriptors = [*self.descriptors,
                            *['pump', 'pressure', 'Nordson', 'Ultimus', 'UltimusV']]

        self.requirements['Connect']['COM'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Serial COM port to communcate through'}
        self.requirements['Set']['pressure'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pressure when the pump is ON'}
        self.requirements['Set']['vacuum'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'vacuum when the pump is OFF'}

        self.pressure = 0
        self.vacuum = 0
        self.pumphandle = ''

    def On(self):
        if not self.simulation:
            self.driver_address.startPump()
        self.on = True
        self.addlog(self.name + ' is on.')

        return self.returnlog()

    def Off(self):
        if not self.simulation:
            self.driver_address.stopPump()
        self.on = False
        self.addlog(self.name + ' is off.')

        return self.returnlog()

    def Connect(self, COM=''):
        if not self.simulation:
            self.driver_address = UltimusV.Ultimus_V_Pump(COM)

        self.addlog('Ultimus ' + self.name + ' is connected on port ' + str(COM))

        return self.returnlog()

    def Set(self, pressure='', vacuum=''):
        if pressure != '':
            if not self.simulation:
                self.driver_address.set_pressure(pressure)
            self.pressure = pressure
        if vacuum != '':
            if not self.simulation:
                self.driver_address.set_vacuum(vacuum)
            self.vacuum = vacuum
        self.addlog(self.name + ' is set to ' + str(pressure) + 'kPa pressure and ' + str(vacuum) + 'kPa vacuum.')

        return self.returnlog()

    def Disconnect(self):
        if not self.simulation:
            if self.pumphandle != '':
                self.pumphandle.disconnect()
            
        self.addlog(Pump.Disconnect(self))

        return self.returnlog()


class UltimusVDev_A3200(UltimusVDev):
    def __init__(self, name):
        UltimusVDev.__init__(self, name)

        self.descriptors.append('A3200')

        self.pressure = 0
        self.vacuum = 0
        self.pumphandle = ''
        self.A3200handle = ''
        self.IOaxis = ''
        self.IObit = ''
        self.dependent_device = True
        self.defaulttask = 1
        self.dependencies = ['pump', 'A3200']

        self.requirements['Connect']['pumpname'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'name of the pump being used'}
        self.requirements['Connect']['pumpaddress'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pointer to the pump device'}
        self.requirements['Connect']['A3200name'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'name of the A3200 controller being used'}
        self.requirements['Connect']['A3200address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pointer to the A3200 device'}
        self.requirements['Connect']['IOaxis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'IO axis on A3200'}
        self.requirements['Connect']['IObit'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'bit on the IO axis being used'}

        # This entry is removed because the pump should already be connected
        self.requirements['Connect'].pop('COM', None)

    def On(self, task='', mode='cmd'):
        self.log += self.A3200handle.Set_DO(axis=self.IOaxis, bit=self.IObit, value=1, task=task, motionmode=mode)
        self.on = True
        self.addlog(self.name + ' is on.')
        return self.returnlog()

    def Off(self, task='', mode='cmd'):
        self.fOff(task, mode)
        return self.returnlog()

    def Set(self, pressure='', vacuum=''):
        self.addlog(self.pumphandle.Set(pressure=pressure, vacuum=vacuum))
        return self.returnlog()

    def fOff(self, task, mode):
        self.log += self.A3200handle.Set_DO(axis=self.IOaxis, bit=self.IObit, value=0, task=task, motionmode=mode)
        self.on = False
        self.addlog(self.name + ' is off.')

    def Connect(self, pumpname='', A3200name='', pumpaddress='', A3200address='', IOaxis = '', IObit = ''):
        self.descriptors.append(pumpname)
        self.descriptors.append(A3200name)
        self.pumphandle = pumpaddress
        self.A3200handle = A3200address
        self.IOaxis = IOaxis
        self.IObit = IObit

        self.addlog('Ultimus/A3200 ' + pumpname +
                    '/' + A3200name +
                    ' ' + self.name +
                    ' is connected using ' + str(self.IOaxis) +
                    ' bit ' + str(self.IObit))
        self.fOff(self.defaulttask, 'cmd')

        return self.returnlog()
