from re import split


gain_modes =   '''
#define IS_GET_MASTER_GAIN                  0x8000
#define IS_GET_RED_GAIN                     0x8001
#define IS_GET_GREEN_GAIN                   0x8002
#define IS_GET_BLUE_GAIN                    0x8003
#define IS_GET_DEFAULT_MASTER               0x8004
#define IS_GET_DEFAULT_RED                  0x8005
#define IS_GET_DEFAULT_GREEN                0x8006
#define IS_GET_DEFAULT_BLUE                 0x8007
#define IS_GET_GAINBOOST                    0x8008
#define IS_SET_GAINBOOST_ON                 0x0001
#define IS_SET_GAINBOOST_OFF                0x0000
#define IS_GET_SUPPORTED_GAINBOOST          0x0002
#define IS_MIN_GAIN                         0
#define IS_MAX_GAIN                         100
'''

color_modes = '''
/*! \brief Raw sensor data, occupies 8 bits */
#define IS_CM_SENSOR_RAW8           11

/*! \brief Raw sensor data, occupies 16 bits */
#define IS_CM_SENSOR_RAW10          33

/*! \brief Raw sensor data, occupies 16 bits */
#define IS_CM_SENSOR_RAW12          27

/*! \brief Raw sensor data, occupies 16 bits */
#define IS_CM_SENSOR_RAW16          29

/*! \brief Mono, occupies 8 bits */
#define IS_CM_MONO8                 6

/*! \brief Mono, occupies 16 bits */
#define IS_CM_MONO10                34

/*! \brief Mono, occupies 16 bits */
#define IS_CM_MONO12                26

/*! \brief Mono, occupies 16 bits */
#define IS_CM_MONO16                28

/*! \brief BGR (5 5 5 1), 1 bit not used, occupies 16 bits */
#define IS_CM_BGR5_PACKED           (3  | IS_CM_ORDER_BGR)

/*! \brief BGR (5 6 5), occupies 16 bits */
#define IS_CM_BGR565_PACKED         (2  | IS_CM_ORDER_BGR)

/*! \brief BGR and RGB (8 8 8), occupies 24 bits */
#define IS_CM_RGB8_PACKED           (1  | IS_CM_ORDER_RGB)
#define IS_CM_BGR8_PACKED           (1  | IS_CM_ORDER_BGR)

/*! \brief BGRA and RGBA (8 8 8 8), alpha not used, occupies 32 bits */
#define IS_CM_RGBA8_PACKED          (0  | IS_CM_ORDER_RGB)
#define IS_CM_BGRA8_PACKED          (0  | IS_CM_ORDER_BGR)

/*! \brief BGRY and RGBY (8 8 8 8), occupies 32 bits */
#define IS_CM_RGBY8_PACKED          (24 | IS_CM_ORDER_RGB)
#define IS_CM_BGRY8_PACKED          (24 | IS_CM_ORDER_BGR)

/*! \brief BGR and RGB (10 10 10 2), 2 bits not used, occupies 32 bits, debayering is done from 12 bit raw */
#define IS_CM_RGB10_PACKED          (25 | IS_CM_ORDER_RGB)
#define IS_CM_BGR10_PACKED          (25 | IS_CM_ORDER_BGR)

/*! \brief BGR and RGB (10(16) 10(16) 10(16)), 6 MSB bits not used respectively, occupies 48 bits */
#define IS_CM_RGB10_UNPACKED        (35 | IS_CM_ORDER_RGB)
#define IS_CM_BGR10_UNPACKED        (35 | IS_CM_ORDER_BGR)

/*! \brief BGR and RGB (12(16) 12(16) 12(16)), 4 MSB bits not used respectively, occupies 48 bits */
#define IS_CM_RGB12_UNPACKED        (30 | IS_CM_ORDER_RGB)
#define IS_CM_BGR12_UNPACKED        (30 | IS_CM_ORDER_BGR)

/*! \brief BGRA and RGBA (12(16) 12(16) 12(16) 16), 4 MSB bits not used respectively, alpha not used, occupies 64 bits */
#define IS_CM_RGBA12_UNPACKED       (31 | IS_CM_ORDER_RGB)
#define IS_CM_BGRA12_UNPACKED       (31 | IS_CM_ORDER_BGR)

#define IS_CM_JPEG                  32

/*! \brief YUV422 (8 8), occupies 16 bits */
#define IS_CM_UYVY_PACKED           12
#define IS_CM_UYVY_MONO_PACKED      13
#define IS_CM_UYVY_BAYER_PACKED     14

/*! \brief YCbCr422 (8 8), occupies 16 bits */
#define IS_CM_CBYCRY_PACKED         23

/*! \brief RGB planar (8 8 8), occupies 24 bits */
#define IS_CM_RGB8_PLANAR           (1 | IS_CM_ORDER_RGB | IS_CM_FORMAT_PLANAR)

#define IS_CM_ALL_POSSIBLE          0xFFFF
#define IS_CM_MODE_MASK             0x007F
'''

def get_codes(c_defines):
    codes_py = {}

    for line in split('\n', c_defines):
        temp = split('#define', line)
        if len(temp) > 1:
            temp2 = temp[1].split()
            try:
                if r'(' in temp2[1]:
                    codes_py[temp2[0]] = int(split('\(', temp2[1])[1])
                else:
                    codes_py[temp2[0]] = int(temp2[1])
            except ValueError:
                codes_py[temp2[0]] = int(temp2[1], 0)
    return codes_py

x = get_codes(color_modes)

print(x)
