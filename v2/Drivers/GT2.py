'''
Functions and class for controlling a Keyence GT2 sensor mounted on an aerotech A3200 motion controlled stage.

Alexander Cook
Created 2017-06-21

'''

from errors import print_error, print_message
import time
from math import sqrt
import A3200 as a32

class GT2():
    def __init__(self, A3200, **kwargs):
        '''
        Set up the touch probe for measurement.
        
        Input:
            A3200: the A3200 instance to address movement, DO and AI commands to
            KWARGS:
                axis: the axis the GT2 is mounted upon
                    
        '''
        self.debug = True
        
        self.A3200 = A3200
        self.num_samples = 5
        self.int_time = 0.1 #seconds
        self.call_limit = 25
        self.floor = -135
        self.speed = 15
        self.retract_voltage = 5
        self.extend_voltage = 1
        
        self.lower_voltage_limit = 0.15
        self.upper_voltage_limit = 0.85
        
        
        #set the default task to the default task on the A3200
        self.task = self.A3200.task
        
        #set the axis the GT2 is mounted upon
        if 'axis' in kwargs:
            self.axis = kwargs['axis']
        else:
            self.axis = 'ZZ3'
        if 'home' in kwargs:
            if kwargs['home']:
                A3200.home(self.axis)
        if 'min_z' in kwargs:
            if kwargs['min_z'] < 0:            
                self.min_z = kwargs['min_z']
            else:
                self.min_z = - kwargs['min_z']
        
        #the DO address is the DO bit which controls the pnuematic actuation
        if 'DO_address' in kwargs:
            self.do_axis = kwargs['DO_address']['axis']
            self.do_bit = kwargs['DO_address']['bit']
        else:
            self.do_axis = 'ZZ1'
            self.do_bit = 0
        #the AI address is where the voltage signal is read
        if 'AI_address' in kwargs:
            self.ai_axis = kwargs['ai_address']['axis']
            self.ai_bit = kwargs['ai_address']['bit']
        else:
            self.ai_axis = 'ZZ2'
            self.ai_bit = 0
        if 'reset' in kwargs:
            if kwargs['reset']:
                self.initialize(**kwargs)
        else:
            #set defaults
            pass
    
    def initialize(self, **kwargs):
        '''
        Initializes 
        '''
        if 'ref_position' in kwargs:
            try:
                items = kwargs['ref_position']
                #break up into xy and z axes
                z_axes = []
                z_dist = []
                xy_axes = []
                xy_dist = []
                for k in items.keys():
                    if 'Z' in k:
                        z_axes.append(k)
                        z_dist.append(items[k])
                    else:
                        if 'X' in k or 'Y' in k:
                            xy_axes.append(k)
                            xy_dist.append(items[k])
                current_pos = self.A3200.get_position(z_axes, dict)
                current_pos.update(self.A3200.get_position(xy_axes, dict))
                motion_mode = self.A3200.motion_mode
                if 'relative' in kwargs:
                    if kwargs['relative']:
                        self.A3200.incremental(self.task)
                    else:
                        self.A3200.absolute(self.task)
                else:
                    self.A3200.absolute(self.task)
                self.A3200.rapid(z_axes, z_dist, None, self.task)  
                self.A3200.rapid(xy_axes, xy_dist, None, self.task)
                #run set_ref routine
                pre_ref_pos = round(self.A3200.get_position(self.axis), 3)
                print(pre_ref_pos)
                self.A3200.home(self.axis)
                #self.set_reference()
                reference_pos = self.A3200.get_position(z_axes, dict)
                reference_pos.update(self.A3200.get_position(xy_axes, dict))
                self.A3200.rapid(self.axis, pre_ref_pos, None, self.task)  
                #go back
                self.A3200.absolute(self.task)
                z_axes = []
                z_dist = []
                xy_axes = []
                xy_dist = []
                for k in current_pos.keys():
                    if 'Z' in k:
                        z_axes.append(k)
                        z_dist.append(current_pos[k])
                    else:
                        if 'X' in k or 'Y' in k:
                            xy_axes.append(k)
                            xy_dist.append(current_pos[k])
                self.A3200.rapid(xy_axes, xy_dist, None, self.task)
                self.A3200.rapid(z_axes, z_dist, None, self.task)  
                if motion_mode == 'incremental':
                    self.A3200.incremental(self.task)    
            except KeyError:
                print_error("GT2 initialize failed: improper or missing axis", True)
        else:
            self.A3200.home(self.axis)
            self.set_reference()
    
    def set_reference(self):
        #need to find the voltages of an extended and retracted probe first
        self.retract() #just in case
        self.retract_voltage = self.sample(error_limit = 0.1)
        self.extend()
        time.sleep(1)
        self.extend_voltage = self.sample(error_limit = 0.1)
        if self.debug:
            print_message("RV: {:0.4}, EV: {:0.4}".format(self.retract_voltage, self.extend_voltage))
        #find a point in the lower range
        lower_voltage = self.find_surface(limits = (0.1, 0.2))
        lower_pos = self.A3200.get_position(self.axis, dict)
        if self.debug:
            #print(lower_voltage, lower_pos)
            print_message("LV: {:0.4}, LP: {:0.4}".format(lower_voltage, lower_pos))
        #go to the uppoer range
        upper_voltage = self.find_surface(limits = (0.8, 0.9), speed = 2)
        upper_pos = self.A3200.get_position(self.axis, dict)
        if self.debug:
            #print(upper_voltage, upper_pos)
            print_message("UV: {:0.4}, UP: {:0.4}".format(upper_voltage, upper_pos))
        self.retract()
        self.conversion_factor = (upper_pos - lower_pos) / (upper_voltage - lower_voltage)            
        self.ref_z = lower_pos - self.conversion_factor * lower_voltage
        self.ref_xy = self.A3200.get_position(['X', 'Y'], dict)
        if self.debug:
            print_message("Set Ref: Conversion Factor: {:0.4}".format(self.conversion_factor))
	     
    def extend(self, check_air = False):
        if self.A3200.DO(self.do_axis, self.do_bit, 1) == 1:
            #bit change went fine, check extention
            if check_air:
                time.sleep(1)
                if self.A3200.AI(self.ai_axis, self.ai_bit) > 2:
                    #didn't extend, throw error and stop
                    print_error('The GT2 did not extend, check the Nitrogen pressure', True)
        else:
        #something went wrong, throw an error and stop
            print_error('The GT2 did not extend, there was a failure to communicated with the A3200', True)
    
    def retract(self, check_air = False):
        if self.A3200.DO(self.do_axis, self.do_bit, 0) == 1:
            #bit change went fine, check extention
            if check_air:
                time.sleep(1)
                if self.A3200.AI(self.ai_axis, self.ai_bit) < 2:
                    #didn't extend, throw error and stop
                    print_error('The GT2 did not retract, check the motion', True)
        else:
        #something went wrong, throw an error and stop
            print_error('The GT2 did not extend, there was a failure to communicated with the A3200', True)
    
    def measure(self, **kwargs):
        self.extend()
        time.sleep(0.25)
        voltage = self.find_surface(**kwargs)
        position = self.A3200.get_position(self.axis)[0]
        z = voltage * self.coversion_factor + position
        if 'opt_axes' in kwargs:
            pos_axes = self.A3200.get_position(kwargs['opt_axes'], dict)
            return {'Z': z}.update(pos_axes)
        else:
            return z
    
    def find_surface(self, call = 0, **kwargs):
        if 'speed' in kwargs:
            speed = kwargs['speed']
        else:
            speed = self.speed
        if 'limits' in kwargs:
            lvl = min(kwargs['limits']) * (self.retract_voltage - self.extend_voltage) + self.extend_voltage
            uvl = max(kwargs['limits']) * (self.retract_voltage - self.extend_voltage) + self.extend_voltage
        else:
            lvl = self.lower_voltage_limit * (self.retract_voltage - self.extend_voltage) + self.extend_voltage
            uvl = self.upper_voltage_limit * (self.retract_voltage - self.extend_voltage) + self.extend_voltage
        if self.debug:
            print_message('lvl: {}, uvl: {}'.format(lvl, uvl))
        #check to make sure we aren't already in contact
        voltage = self.sample()
        if voltage < lvl:
            self.A3200.freerun(self.axis, -speed, self.task)
            while self.A3200.AI(self.ai_axis, self.ai_bit, self.task)[1] < lvl:
                time.sleep(0.025)
            self.A3200.stop_freerun(self.axis, self.task)
        else:
            #are we above the voltage window, ie too far down?
            if voltage > uvl:
                self.A3200.freerun(self.axis, speed, self.task)
                while self.A3200.AI(self.ai_axis, self.ai_bit, self.task)[1] > uvl:
                    time.sleep(0.025)
                self.A3200.stop_freerun(self.axis, self.task)
        success = self.A3200.wait_for_move_done(self.axis, 'move_done', 1000)
        time.sleep(0.5)
        voltage = self.sample(error_limit = 0.01)
        #check if in the voltage window
        if voltage > lvl and voltage < uvl:
            return self.sample(**kwargs)
        else:
            if 'call_limit' in kwargs:
                call_limit = kwargs['call_limit']
            else:
                call_limit = self.call_limit
            if call < call_limit:
                if speed > 0.5:
                    kwargs['speed'] = speed / 2
                return self.find_surface(call + 1, **kwargs)
            else:
                print_error("hit call limit when trying to find the surface", False)
                return voltage
    
    def sample(self, call = 0, **kwargs):
        if 'num_samples' in kwargs:
            num = kwargs['num_samples']
        else:
            num = self.num_samples
        if 'int_time' in kwargs:
            int_time = kwargs['int_time']
        else:
            int_time = self.int_time
        
        samples = []
        for i in range(num):
            m = self.A3200.AI(self.ai_axis, self.ai_bit, self.task)
            if m[0] > 0:
                samples.append(m[1])
            time.sleep(int_time)
        
        avg = sum(samples)/num
        
        #optional error checking / settling routine
        if 'error_limit' in kwargs:
            error = sqrt(sum([(s - avg)**2 for s in samples])/num)/sqrt(num)
            if kwargs['error_limit'] < error:
                if 'call_limit' in kwargs:
                    if call < kwargs['call_limit']:
                        return self.sample(call + 1, **kwargs)
                    else:
                        print_error('Call limit exceeded prior to error reducing below limit.', False)
                        return avg
                else: 
                    if call < self.call_limit:
                        return self.sample(call + 1, **kwargs)
                    else:
                        print_error('Call limit exceeded prior to error reducing below limit.', False)
                        return avg
            else:
                #error is less than limit, return
                return avg
        else:
            #no specified error limit, return
            return avg
            
if __name__ == '__main__':
    '''
    Test code
    '''
    controller = a32.A3200()
    controller.incremental()
    gt2 = GT2(controller)
    gt2.initialize(ref_position = {'X': -50, 'Y': -50, 'ZZ2' : -20, 'ZZ3': -20})
    controller.disconnect()
    