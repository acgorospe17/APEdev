from device import Device
import pyueye.ueye as pue


class Camera(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.descriptors.append('camera')
        self.requirements['Set']['color_mode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Camera color mode.'}

    def Set(self, color_mode=''):
        self.color_mode = color_mode
        self.addlog(self.name + ' set to ' + self.color_mode)

        return self.returnlog()


class UEye(Camera):
    def __init__(self, name):
        Camera.__init__(self, name)
        self.descriptors = [*self.descriptors,
                            *['IDS', 'uEye', 'camera']]


if __name__ == "__main__":
    camera = UEye()
