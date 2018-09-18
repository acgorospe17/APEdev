import ctypes as ct
from enum import Enum
from collections import Iterable
from multiprocessing import Value


NUM_TASKS = 4
DLL_LOC = r"C:\Program Files (x86)\Aerotech\A3200\CLibrary\Bin64\A3200C64.dll"


class A3200Error(Exception):
    def __init__(self, source, message, level, controller=None):
        self.source = source
        self.message = message
        self.level = level

        if controller is not None:
            error_msg = ct.create_string_buffer(100)
            buffer = ct.c_int(100)
            controller.dll.A3200GetLastErrorString(error_msg, buffer)
            print(error_msg.value)


class AxisMask(Enum):
    Y   = (1 << 0),  # 1
    YY  = (1 << 1),  # 2
    X   = (1 << 2),  # 4
    ZZ1 = (1 << 6),  # 64
    ZZ2 = (1 << 7),  # 128
    ZZ3 = (1 << 8),  # 256
    ZZ4 = (1 << 9),  # 512

    AXISMASK_None = 0,
    AXISMASK_All = 0xffffffff

    @classmethod
    def get_mask(cls, axes):
        '''
        Returns the sum of Axes masks for a given list of axes.
        '''
        try:
            if isinstance(axes, Iterable) and type(axes) is not str:
                mask = sum(cls[ax].value[0] for ax in axes)
                return ct.c_ulong(mask)
            else:
                return ct.c_ulong(cls[axes].value[0])
        except KeyError:
            print("Invalid axis: {}".format(axes))
            return 0


class A3200():
    def __init__(self, handle=None, default_task=1, debug=False):
        if handle is None:
            self.connect()
        else:
            self.is_open = True
            self.handle = handle
            self.dll = ct.WinDLL(DLL_LOC)

        self.task = default_task
        self.debug = debug
        self.default_speed = 10
        self.queue_status = [Value('i', 0) for _ in range(NUM_TASKS)]

    # -------------------------------------------------------------------------
    # Control Methods
    # -------------------------------------------------------------------------

    def connect(self):
        '''
        Connect to the A3200.
        '''
        if not self.is_open:
            self.handle = ct.c_void_p()
            try:
                self.dll.A3200Connect(ct.byref(self.handle))
                self.is_open = True
            except A3200Error('A3200->connect', 'Failed to connect', 'estop'):
                self.is_open = False
                self.handle = None

    def disconnect(self):
        '''
        Disconnect from the A3200.
        '''
        if self.is_open:
            try:
                self.dll.A3200Disconnect(self.handle)
                self.is_open = False
            except A3200Error('A3200->disconnect', 'Failed to disconnect', 'estop'):
                pass

    def enable(self, axes, task=-1):
        '''
        Enable the axes specified in axes.
        '''
        if self.is_open:
            ax_mask = AxisMask.get_mask(axes)
            if task < 0:
                self.dll.A3200MotionEnable(self.handle, self.task, ax_mask)
            else:
                self.dll.A3200MotionEnable(self.handle, task, ax_mask)

    def disable(self, axes, task=-1):
        '''
        Disable the axes specified in axes.
        '''
        if self.is_open:
            ax_mask = AxisMask.get_mask(axes)
            if task < 0:
                self.dll.A3200MotionDisable(self.handle, self.task, ax_mask)
            else:
                self.dll.A3200MotionDisable(self.handle, task, ax_mask)

    def cmd_exe(self, command, task=-1, ret=False):
        '''
        Execute an aerobasic command.
        '''
        if self.is_open:
            cmd = ct.create_unicode_buffer(command)
            if task < 0:
                self.dll.A3200CommandExecute(self.handle, self.task, cmd, None)
            else:
                self.dll.A3200CommandExecute(self.handle, task, cmd, None)

    # -------------------------------------------------------------------------
    # I/O Methods
    # -------------------------------------------------------------------------

    def analog_input(self, axis, channel, task=-1):
        '''
        Returns the value of analog input channel on axis
        '''


    def analog_output(self, axis, channel, value, task=-1):
        pass

    def digital_input(self, axis, bit, task=-1):
        pass

    def digital_output(self, axis, bit, value, task=-1):
        pass

    # -------------------------------------------------------------------------
    # Queue Methods
    # -------------------------------------------------------------------------

    def enable_queue_mode(self, task = -1):
        pass

    def disable_queue_mode(self, task = -1, wait_til_empty=True):
        pass

    def get_queue_depth(self, task=-1):
        pass

    def put_command(self, command, args, task=-1):
        pass

    def simple_queue_manager(self, task=-1, wait_mode='pause', loop_delay=0.025):
        pass

    def program_start(self, task=-1):
        pass

    def program_pause(self, task=-1):
        pass

    # -------------------------------------------------------------------------
    # Status Methods
    # -------------------------------------------------------------------------

    def get_position(self, axes, return_type=list):
        pass

    def is_move_done(self, axis, mode='done'):
        pass

    def set_absolute(self, task=-1):
        pass

    def set_incremental(self, task=-1):
        pass

    def get_task_variable(self, index, count=1, task=-1):
        pass

    def set_task_variable(self, index, variables, task=-1):
        pass

    def get_global_variable(self, index, count=1):
        pass

    def set_global_variable(self, index, variables, count=1):
        pass

    def get_task_string(self, index, length=50, task=-1):
        pass

    def set_task_string(self, index, string, task=-1):
        pass

    def get_global_string(self, index, length=50):
        pass

    def set_global_string(self, index, string):
        pass

    def setup_functions(self):
        pass

    # -------------------------------------------------------------------------
    # Motion Methods
    # -------------------------------------------------------------------------

    def home(self, axes, task=-1):
        '''
        Homes the axes specified in axes.
        '''
        if self.is_open:
            ax_mask = AxisMask.get_mask(axes)
            if task < 0:
                self.A3200Lib.A3200MotionHome(self.handle, self.task, ax_mask)
            else:
                self.A3200Lib.A3200MotionHome(self.handle, task, ax_mask)

    def abort(self, axes):
        '''
        Aborts the motion on the specified axes.
        '''
        if self.is_open:
            ax_mask = AxisMask.get_mask(axes)
            self.A3200Lib.A3200MotionAbort(self.handle, ax_mask)

    def rapid(self, axes, distance, speed=None, task=-1):
        '''
        Make a linearly coordinated point-to-point motion on axes for a
        specifed distance.

        Note: will fail (not execute) if more than four axes are specified and
        ITAR controls are enabled.
        '''
        pass

    def linear(self, axes, distance, task=-1):
        pass

    def linear_velocity(self, axes, distance, speed, task=-1):
        pass

    def begin_freerun(self, axis, speed, task=-1):
        pass

    def stop_freerun(self, axis, task=-1):
        pass

    def absolute_move(self, axes, distance=None, speed=None, task=-1, block_til_done=True):
        pass

    def incremental_move(self, axes, distance=None, speed=None, task=-1, block_til_done=True):
        pass

    def wait_for_move_done(self, axes, mode='move_done', timeout=-1):
        pass
