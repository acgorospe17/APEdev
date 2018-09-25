from collections import OrderedDict
import ctypes as ct


# =============================================================================
# Global Variables
# =============================================================================
DLL_LOC = r"C:\Program Files (x86)\Aerotech\A3200\CLibrary\Bin64\A3200C64.dll"


# =============================================================================
# Global Enumerations
# =============================================================================
temp = ['TASKID_{:02d}'.format(i) for i in range(32)]
temp.insert(0, 'TASKID_Library')
temp = dict(enumerate(temp))
TASK_ID = OrderedDict({v: ct.c_int(k) for k, v in temp.items()})
temp = ['AXIS_INDEX_{:02d}'.format(i) for i in range(32)]
temp = dict(enumerate(temp))
AXIS_INDEX = OrderedDict({v: ct.c_int(k) for k, v in temp.items()})
temp = ['AXISMASK_{:02d}'.format(i) for i in range(32)]
temp = dict(enumerate(temp))
AXIS_MASK = OrderedDict()
AXIS_MASK['AXISMASK_None'] = ct.c_ulong(0)
AXIS_MASK.update({v: ct.c_ulong(1 << k) for k, v in temp.items()})
AXIS_MASK['AXISMASK_All'] = ct.c_ulong(0xffffffff)
del temp
TASK_MASK = {'TASK'+k[4:]: v for k, v in AXIS_MASK.items()}


# =============================================================================
# Exception Class
# =============================================================================
class A3200Error(Exception):
    def __init__(self, source, handle=None, task_id=None, controller=None):
        self.source = source
        self.handle = handle
        self.task_id = task_id

        bf = 100

        if not handle and not task_id:
            error_string = ct.create_string_buffer(bf)
            buffer_size = ct.c_int(bf)  # in bytes
            controller.dll.A3200GetLastErrorString(error_string, buffer_size)
            print(error_string.value.decode("utf-8"))
        else:
            error_string = ct.create_string_buffer(bf)
            buffer_size = ct.c_int(bf)  # in bytes
            controller.dll.A3200GetTaskErrorString(handle, task_id, error_string, buffer_size)
            print(error_string.value.decode("utf-8"))


# =============================================================================
# Main Class
# =============================================================================
class A3200:
    def __init__(self):
        self.dll = ct.WinDLL(DLL_LOC)

        while not self.is_initialized():
            self.handle = self.connect()

    def __del__(self):
        while self.is_initialized():
            self.handle = self.disconnect()

# =============================================================================
# Generic Commands
# =============================================================================
    def acknowledge_all(self, task_id):
        '''
        Not implemented.
        '''
        pass

    def command_execute(self, task_id, command, ret=False):
        pass

# =============================================================================
# Motion Commands
# =============================================================================
    def disable():
        '''
        Not implemented.
        '''
        pass

    def enable():
        '''
        Not implemented.
        '''
        pass

    def fault_ack():
        '''
        Not implemented.
        '''
        pass

    def home():
        '''
        Not implemented.
        '''
        pass

    def home_conditional():
        '''
        Not implemented.
        '''
        pass

    def linear():
        '''
        Not implemented.
        '''
        pass

    def linear_velocity():
        '''
        Not implemented.
        '''
        pass

    def rapid():
        '''
        Not implemented.
        '''
        pass

    def cw_axis_radius():
        '''
        Not implemented.
        '''
        pass

    def cw_axis_center():
        '''
        Not implemented.
        '''
        pass

    def ccw_axis_radius():
        '''
        Not implemented.
        '''
        pass

    def ccw_axis_center():
        '''
        Not implemented.
        '''
        pass

    def slave_offset():
        '''
        Not implemented.
        '''
        pass

    def freerun():
        '''
        Not implemented.
        '''
        pass

    def freerun_stop():
        '''
        Not implemented.
        '''
        pass

    def move_inc():
        '''
        Not implemented.
        '''
        pass

    def move_abs():
        '''
        Not implemented.
        '''
        pass

    def auto_focus():
        '''
        Not implemented.
        '''
        pass

    def safe_zone():
        '''
        Not implemented.
        '''
        pass

    def safe_zone_type():
        '''
        Not implemented.
        '''
        pass

    def safe_zone_set():
        '''
        Not implemented.
        '''
        pass

    def safe_zone_clear():
        '''
        Not implemented.
        '''
        pass

    def abort():
        '''
        Not implemented.
        '''
        pass

    def wait_for_motion_done():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Motion Setup Commands
# =============================================================================
    def ramp_type_axis():
        '''
        Not implemented.
        '''
        pass

    def ramp_mode_axis():
        '''
        Not implemented.
        '''
        pass

    def ramp_rate_axis():
        '''
        Not implemented.
        '''
        pass

    def ramp_rate_accel_axis():
        '''
        Not implemented.
        '''
        pass

    def ramp_rate_decel_axis():
        '''
        Not implemented.
        '''
        pass

    def ramp_time_axis():
        '''
        Not implemented.
        '''
        pass

    def ramp_time_accel_axis():
        '''
        Not implemented.
        '''
        pass

    def ramp_time_decel_axis():
        '''
        Not implemented.
        '''
        pass

    def pos_offset_set():
        '''
        Not implemented.
        '''
        pass

    def pos_offset_clear():
        '''
        Not implemented.
        '''
        pass

    def setup_scurve():
        '''
        Not implemented.
        '''
        pass

    def absolute():
        '''
        Not implemented.
        '''
        pass

    def incremental():
        '''
        Not implemented.
        '''
        pass

    def ramp_type_coordinated():
        '''
        Not implemented.
        '''
        pass

    def ramp_mode_coordinated():
        '''
        Not implemented.
        '''
        pass

    def ramp_rate_coordinated():
        '''
        Not implemented.
        '''
        pass

    def ramp_rate_accel_coordinated():
        '''
        Not implemented.
        '''
        pass

    def ramp_rate_decel_coordinated():
        '''
        Not implemented.
        '''
        pass

    def ramp_rate_dependent_accel():
        '''
        Not implemented.
        '''
        pass

    def ramp_rate_dependent_decel():
        '''
        Not implemented.
        '''
        pass

    def ramp_time_coordinated():
        '''
        Not implemented.
        '''
        pass

    def ramp_time_accel_coordinated():
        '''
        Not implemented.
        '''
        pass

    def ramp_time_decel_coordinated():
        '''
        Not implemented.
        '''
        pass

    def set_ext_pos():
        '''
        Not implemented.
        '''
        pass

    def servo():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Motion Advanced Commands
# =============================================================================
    def home_async():
        '''
        Not implemented.
        '''
        pass

    def home_async_conditional():
        '''
        Not implemented.
        '''
        pass

    def move_out_lim():
        '''
        Not implemented.
        '''
        pass

    def move_to_lim_cw():
        '''
        Not implemented.
        '''
        pass

    def move_to_lim_ccw():
        '''
        Not implemented.
        '''
        pass

    def move_slice():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# IO Commands
# =============================================================================
    def brake():
        '''
        Not implemented.
        '''
        pass

    def analog_input():
        '''
        Not implemented.
        '''
        pass

    def analog_ouput():
        '''
        Not implemented.
        '''
        pass

    def digital_input():
        '''
        Not implemented.
        '''
        pass

    def digital_output():
        '''
        Not implemented.
        '''
        pass

    def digital_input_bit():
        '''
        Not implemented.
        '''
        pass

    def digital_output_bit():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Motion Fiber Commands
# =============================================================================
    def centroid_1d():
        '''
        Not implemented.
        '''
        pass

    def centroid_1d_controller_variable():
        '''
        Not implemented.
        '''
        pass

    def centroid_2d():
        '''
        Not implemented.
        '''
        pass

    def centroid_2d_controller_variable():
        '''
        Not implemented.
        '''
        pass

    def centroid_3d():
        '''
        Not implemented.
        '''
        pass

    def centroid_3d_controller_variable():
        '''
        Not implemented.
        '''
        pass

    def fast_align_2d():
        '''
        Not implemented.
        '''
        pass

    def fast_align_3d():
        '''
        Not implemented.
        '''
        pass

    def fast_align_4d():
        '''
        Not implemented.
        '''
        pass

    def fast_align_5d():
        '''
        Not implemented.
        '''
        pass

    def fast_align_6d():
        '''
        Not implemented.
        '''
        pass

    def geo_center():
        '''
        Not implemented.
        '''
        pass

    def hill_climb():
        '''
        Not implemented.
        '''
        pass

    def spiral_rough():
        '''
        Not implemented.
        '''
        pass

    def spiral_fine():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Units Commands
# =============================================================================
    def primary():
        '''
        Not implemented.
        '''
        pass

    def secondary():
        '''
        Not implemented.
        '''
        pass

    def minutes():
        '''
        Not implemented.
        '''
        pass

    def seconds():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Tuning Commands
# =============================================================================
    def loop_trans():
        '''
        Not implemented.
        '''
        pass

    def m_comm():
        '''
        Not implemented.
        '''
        pass

    def m_set():
        '''
        Not implemented.
        '''
        pass

    def oscillate():
        '''
        Not implemented.
        '''
        pass

    def set_gain():
        '''
        Not implemented.
        '''
        pass

    def set_gain_advanced():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Tasks Commands
# =============================================================================
    def mfo():
        '''
        Not implemented.
        '''
        pass

    def user_task_error():
        '''
        Not implemented.
        '''
        pass

    def user_task_warning():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Advanced Commands
# =============================================================================
    def check_password():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Advanced Analog Commands
# =============================================================================
    def track():
        '''
        Not implemented.
        '''
        pass

    def track_limit():
        '''
        Not implemented.
        '''
        pass

    def control_on():
        '''
        Not implemented.
        '''
        pass

    def control_on_speed():
        '''
        Not implemented.
        '''
        pass

    def control_off():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Advanced Commands
# =============================================================================
    def gear_setup():
        '''
        Not implemented.
        '''
        pass

    def gear_ratio():
        '''
        Not implemented.
        '''
        pass

    def gear_on():
        '''
        Not implemented.
        '''
        pass

    def gear_on_filtered():
        '''
        Not implemented.
        '''
        pass

    def gear_off():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Data Acquisition Commands
# =============================================================================
    def array_setup():
        '''
        Not implemented.
        '''
        pass

    def array_read():
        '''
        Not implemented.
        '''
        pass

    def array_read_fast():
        '''
        Not implemented.
        '''
        pass

    def dataacq_input():
        '''
        Not implemented.
        '''
        pass

    def dataacq_trigger():
        '''
        Not implemented.
        '''
        pass

    def dataacq_off():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Camming Commands
# =============================================================================
    def cam_sync():
        '''
        Not implemented.
        '''
        pass

    def load_cam_table():
        '''
        Not implemented.
        '''
        pass

    def load_cam_variables_units():
        '''
        Not implemented.
        '''
        pass

    def load_cam_variables_counts():
        '''
        Not implemented.
        '''
        pass

    def free_cam_table():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# PSO Commands
# =============================================================================
    def pso_array():
        '''
        Not implemented.
        '''
        pass

    def pso_control():
        '''
        Not implemented.
        '''
        pass

    def pso_distance_fixed():
        '''
        Not implemented.
        '''
        pass

    def pso_distance_array():
        '''
        Not implemented.
        '''
        pass

    def pso_distance_off():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_to_window_mask():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_bit_mask():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_bit_mask_ext_sync():
        '''
        Not implemented.
        '''
        pass

    def pso_output_toggle():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_laser_mask():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_laser_mask_ext_sync():
        '''
        Not implemented.
        '''
        pass

    def pso_output_window():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_window_mask():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_window_mask_hard():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_window_mask_ext_sync():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_window_mask_ext_sync_hard():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_window_bit_mask():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_window_bit_mask_ext_sync():
        '''
        Not implemented.
        '''
        pass

    def pso_output_control():
        '''
        Not implemented.
        '''
        pass

    def pso_output_bit_map():
        '''
        Not implemented.
        '''
        pass

    def pso_output_bit_map_mode():
        '''
        Not implemented.
        '''
        pass

    def pso_output_combine():
        '''
        Not implemented.
        '''
        pass

    def pso_output_pulse_ext_sync():
        '''
        Not implemented.
        '''
        pass

    def pso_pulse_cycles_only():
        '''
        Not implemented.
        '''
        pass

    def pso_pulse_delay_only():
        '''
        Not implemented.
        '''
        pass

    def pso_pulse_cycles_and_delay():
        '''
        Not implemented.
        '''
        pass

    def pso_track_input():
        '''
        Not implemented.
        '''
        pass

    def pso_track_input_input2():
        '''
        Not implemented.
        '''
        pass

    def pso_track_input_input2_input3():
        '''
        Not implemented.
        '''
        pass

    def pso_track_reset():
        '''
        Not implemented.
        '''
        pass

    def pso_track_scale():
        '''
        Not implemented.
        '''
        pass

    def pso_track_direction():
        '''
        Not implemented.
        '''
        pass

    def pso_window_on():
        '''
        Not implemented.
        '''
        pass

    def pso_window_on_invert():
        '''
        Not implemented.
        '''
        pass

    def pso_window_off():
        '''
        Not implemented.
        '''
        pass

    def pso_window_input():
        '''
        Not implemented.
        '''
        pass

    def pso_window_input_invert():
        '''
        Not implemented.
        '''
        pass

    def pso_window_reset():
        '''
        Not implemented.
        '''
        pass

    def pso_window_load():
        '''
        Not implemented.
        '''
        pass

    def pso_window_range_array():
        '''
        Not implemented.
        '''
        pass

    def pso_window_range():
        '''
        Not implemented.
        '''
        pass

    def pso_window_control():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# ModBus Commands
# =============================================================================
    def mb_register_int16_write():
        '''
        Not implemented.
        '''
        pass

    def mb_register_int16_read():
        '''
        Not implemented.
        '''
        pass

    def mb_register_int16_write_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_register_int16_read_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_register_int32_write():
        '''
        Not implemented.
        '''
        pass

    def mb_register_int32_read():
        '''
        Not implemented.
        '''
        pass

    def mb_register_int32_write_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_register_int32_read_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_register_float_write():
        '''
        Not implemented.
        '''
        pass

    def mb_register_float_read():
        '''
        Not implemented.
        '''
        pass

    def mb_register_float_write_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_register_float_read_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_register_double_write():
        '''
        Not implemented.
        '''
        pass

    def mb_register_double_read():
        '''
        Not implemented.
        '''
        pass

    def mb_register_double_write_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_register_double_read_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_bit_write():
        '''
        Not implemented.
        '''
        pass

    def mb_bit_read():
        '''
        Not implemented.
        '''
        pass

    def mb_bit_write_drive():
        '''
        Not implemented.
        '''
        pass

    def mb_bit_read_drive():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Generic Callback Methods
# =============================================================================
    def cb_registration_add():
        '''
        Not implemented.
        '''
        pass

    def cb_registration_remove():
        '''
        Not implemented.
        '''
        pass

    def cb_wait():
        '''
        Not implemented.
        '''
        pass

    def cb_wait_cancel():
        '''
        Not implemented.
        '''
        pass

    def cb_args_get_count():
        '''
        Not implemented.
        '''
        pass

    def cb_args_get_type():
        '''
        Not implemented.
        '''
        pass

    def cb_args_get_integer():
        '''
        Not implemented.
        '''
        pass

    def cb_args_get_double():
        '''
        Not implemented.
        '''
        pass

    def cb_args_get_string():
        '''
        Not implemented.
        '''
        pass

    def cb_ret_void():
        '''
        Not implemented.
        '''
        pass

    def cb_ret_double():
        '''
        Not implemented.
        '''
        pass

    def cb_ret_string():
        '''
        Not implemented.
        '''
        pass

    def cb_args_make_string():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Configuration Methods
# =============================================================================
    def config_open():
        '''
        Not implemented.
        '''
        pass

    def config_save():
        '''
        Not implemented.
        '''
        pass

    def config_close():
        '''
        Not implemented.
        '''
        pass

    def config_param_file_set():
        '''
        Not implemented.
        '''
        pass

    def config_param_file_get():
        '''
        Not implemented.
        '''
        pass

    def config_dist_logging_file_set():
        '''
        Not implemented.
        '''
        pass

    def config_dist_logging_file_get():
        '''
        Not implemented.
        '''
        pass

    def config_compiler_output_dir_set():
        '''
        Not implemented.
        '''
        pass

    def config_compiler_output_dir_get():
        '''
        Not implemented.
        '''
        pass

    def config_calibration_file_set():
        '''
        Not implemented.
        '''
        pass

    def config_calibration_file_get():
        '''
        Not implemented.
        '''
        pass

    def config_calibration_gcal_get_count():
        '''
        Not implemented.
        '''
        pass

    def config_calibration_gcal_set():
        '''
        Not implemented.
        '''
        pass

    def config_calibration_gcal_get():
        '''
        Not implemented.
        '''
        pass

    def config_calibration_gcal_add():
        '''
        Not implemented.
        '''
        pass

    def config_calibration_gcal_remove():
        '''
        Not implemented.
        '''
        pass

    def config_prgm_automation_get_count():
        '''
        Not implemented.
        '''
        pass

    def config_prgm_automation_set():
        '''
        Not implemented.
        '''
        pass

    def config_prgm_automation_get():
        '''
        Not implemented.
        '''
        pass

    def config_prgm_automation_add():
        '''
        Not implemented.
        '''
        pass

    def config_prgm_automation_remove():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Connection Methods
# =============================================================================
    def connect(self):
        '''
        Connects to the A3200.

        This function will either connect to an already running A3200, or will
        initialize an A3200 if it is not already running. In either case, the
        handle to a running A3200 will be returned. Initialization involves
        sending parameters, calibration files, program automation, and other
        things.
        '''
        handle = ct.c_void_p()
        try:
            self.dll.A3200Connect(ct.byref(handle))
            return handle
        except A3200Error:
            raise A3200Error(source='A3200->connect', controller=self)
            return None

    def disconnect(self):
        '''
        Disconnects from the A3200.

        This disconnects from the A3200. The A3200 will keep running after this
        call.
        '''
        try:
            self.dll.A3200Connect(self.handle)
        except A3200Error:
            raise A3200Error(source='A3200->disconnect', controller=self)

    def reset(self):
        '''
        Resets the A3200.

        This resets the A3200 system. Calibration, program automation, etc.
        will be reinitialized after this call.
        '''
        try:
            self.dll.A3200Reset(self.handle)
        except A3200Error:
            raise A3200Error(source='A3200->reset', controller=self)

    def is_initialized(self):
        '''
        Checks if the A3200 system is initialized.

        This checks to see if the A3200 system has been fully initialized. If
        the system is not initialized, a call to A3200Connect() will perform
        the initialization.
        '''
        return self.dll.A3200IsInitialized(self.handle)

# =============================================================================
# Data Collection Methods
# =============================================================================
    def dc_config_create():
        '''
        Not implemented.
        '''
        pass

    def dc_config_free():
        '''
        Not implemented.
        '''
        pass

    def dc_config_set_samples():
        '''
        Not implemented.
        '''
        pass

    def dc_config_set_period():
        '''
        Not implemented.
        '''
        pass

    def dc_config_set_sample_trigger():
        '''
        Not implemented.
        '''
        pass

    def dc_config_add_signal():
        '''
        Not implemented.
        '''
        pass

    def dc_config_get_signal_count():
        '''
        Not implemented.
        '''
        pass

    def dc_config_remove_signal_all():
        '''
        Not implemented.
        '''
        pass

    def dc_config_apply():
        '''
        Not implemented.
        '''
        pass

    def dc_config_start():
        '''
        Not implemented.
        '''
        pass

    def dc_config_start_continuous():
        '''
        Not implemented.
        '''
        pass

    def dc_config_stop():
        '''
        Not implemented.
        '''
        pass

    def dc_config_get_status():
        '''
        Not implemented.
        '''
        pass

    def dc_config_data_retrieve():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Parameter Methods
# =============================================================================
    def param_get_value():
        '''
        Not implemented.
        '''
        pass

    def param_get_value_string():
        '''
        Not implemented.
        '''
        pass

    def param_set_value():
        '''
        Not implemented.
        '''
        pass

    def param_set_value_string():
        '''
        Not implemented.
        '''
        pass

    def param_file_get_defaults():
        '''
        Not implemented.
        '''
        pass

    def param_file_open():
        '''
        Not implemented.
        '''
        pass

    def param_file_close():
        '''
        Not implemented.
        '''
        pass

    def param_file_save():
        '''
        Not implemented.
        '''
        pass

    def param_file_get_value_string():
        '''
        Not implemented.
        '''
        pass

    def param_file_get_value():
        '''
        Not implemented.
        '''
        pass

    def param_file_set_value_string():
        '''
        Not implemented.
        '''
        pass

    def param_file_set_value():
        '''
        Not implemented.
        '''
        pass

    def param_file_get_data():
        '''
        Not implemented.
        '''
        pass

    def param_file_set_data():
        '''
        Not implemented.
        '''
        pass

    def param_file_get_axis_mask():
        '''
        Not implemented.
        '''
        pass

    def param_file_set_axis_mask():
        '''
        Not implemented.
        '''
        pass

    def param_retrieve_from_controller():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Program/Task Control Methods
# =============================================================================
    def prgm_run():
        '''
        Not implemented.
        '''
        pass

    def prgm_buffered_run():
        '''
        Not implemented.
        '''
        pass

    def prgm_load():
        '''
        Not implemented.
        '''
        pass

    def prgm_associate():
        '''
        Not implemented.
        '''
        pass

    def prgm_add():
        '''
        Not implemented.
        '''
        pass

    def prgm_remove():
        '''
        Not implemented.
        '''
        pass

    def prgm_start():
        '''
        Not implemented.
        '''
        pass

    def prgm_stop():
        '''
        Not implemented.
        '''
        pass

    def prgm_stop_and_wait():
        '''
        Not implemented.
        '''
        pass

    def prgm_pause():
        '''
        Not implemented.
        '''
        pass

    def prgm_pause_and_wait():
        '''
        Not implemented.
        '''
        pass

    def prgm_stop():
        '''
        Not implemented.
        '''
        pass

    def prgm_step_into():
        '''
        Not implemented.
        '''
        pass

    def prgm_step_over():
        '''
        Not implemented.
        '''
        pass

    def prgm_retrace():
        '''
        Not implemented.
        '''
        pass

    def prgm_get_task_state():
        '''
        Not implemented.
        '''
        pass

    def prgm_get_task_state_string():
        '''
        Not implemented.
        '''
        pass

    def prgm_feedhold():
        '''
        Not implemented.
        '''
        pass

    def prgm_set_line_number():
        '''
        Not implemented.
        '''
        pass

    def prgm_init_queue():
        '''
        Not implemented.
        '''
        pass

    def prgm_get_added_prgm_ct():
        '''
        Not implemented.
        '''
        pass

    def prgm_get_added_prgms():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Status Methods
# =============================================================================
    def status_get_items():
        '''
        Not implemented.
        '''
        pass

    def status_get_item():
        '''
        Not implemented.
        '''
        pass

# =============================================================================
# Variable Methods
# =============================================================================
    def var_get_global_double():
        '''
        Not implemented.
        '''
        pass

    def var_get_global_doubles():
        '''
        Not implemented.
        '''
        pass

    def var_get_global_string():
        '''
        Not implemented.
        '''
        pass

    def var_set_global_double():
        '''
        Not implemented.
        '''
        pass

    def var_set_global_doubles():
        '''
        Not implemented.
        '''
        pass

    def var_set_global_string():
        '''
        Not implemented.
        '''
        pass

    def var_get_task_double():
        '''
        Not implemented.
        '''
        pass

    def var_get_task_doubles():
        '''
        Not implemented.
        '''
        pass

    def var_get_task_string():
        '''
        Not implemented.
        '''
        pass

    def var_set_task_double():
        '''
        Not implemented.
        '''
        pass

    def var_set_task_doubles():
        '''
        Not implemented.
        '''
        pass

    def var_set_task_string():
        '''
        Not implemented.
        '''
        pass

    def var_get_value_string_by_name():
        '''
        Not implemented.
        '''
        pass

    def var_set_value_string_by_name():
        '''
        Not implemented.
        '''
        pass

    def var_get_value_by_name():
        '''
        Not implemented.
        '''
        pass

    def var_set_value_by_name():
        '''
        Not implemented.
        '''
        pass


if __name__ == '__main__':
    show_enums = True
    test_connect = False

    if show_enums:
        print('GLOBAL ENUMERATIONS:\n')
        for each in [TASK_ID, AXIS_INDEX, AXIS_MASK, TASK_MASK]:
            for k,v in each.items():
                print(k, '\t', v)
            print()

    if test_connect:
        controller = A3200()

        if controller.is_initialized():
            print('connect success')
        else:
            print('connect fail')

        del controller
        if not controller.is_initialized():
            print('disconnect success')
        else:
            print('disconnect fail')
