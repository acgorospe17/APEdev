from ...APEDev import Procedure

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
