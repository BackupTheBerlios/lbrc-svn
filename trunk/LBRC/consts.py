
"""
@var input: Constants taken from input.h (see kernel source or in our doc dir)

             These constants are used to report input events to the kernel.
             
@var uinput: Constants taken from uinput.h (see kernel source or in our doc dir)

             These are needed for the creation of a userspace uinput driver
"""
input_def = {}
input_def['EV_SYN'] = 0x00
input_def['EV_KEY'] = 0x01
input_def['EV_REL'] = 0x02
input_def['EV_ABS'] = 0x03
input_def['EV_MSC'] = 0x04
input_def['EV_SW'] = 0x05
input_def['EV_LED'] = 0x11
input_def['EV_SND'] = 0x12
input_def['EV_REP'] = 0x14
input_def['EV_FF'] = 0x15
input_def['EV_PWR'] = 0x16
input_def['EV_FF_STATUS'] = 0x17
input_def['EV_MAX'] = 0x1f

# Synchronization events.

input_def['SYN_REPORT'] = 0
input_def['SYN_CONFIG'] = 1

# Keys and buttons

input_def['KEY_RESERVED'] = 0
input_def['KEY_ESC'] = 1
input_def['KEY_1'] = 2
input_def['KEY_2'] = 3
input_def['KEY_3'] = 4
input_def['KEY_4'] = 5
input_def['KEY_5'] = 6
input_def['KEY_6'] = 7
input_def['KEY_7'] = 8
input_def['KEY_8'] = 9
input_def['KEY_9'] = 10
input_def['KEY_0'] = 11
input_def['KEY_MINUS'] = 12
input_def['KEY_EQUAL'] = 13
input_def['KEY_BACKSPACE'] = 14
input_def['KEY_TAB'] = 15
input_def['KEY_Q'] = 16
input_def['KEY_W'] = 17
input_def['KEY_E'] = 18
input_def['KEY_R'] = 19
input_def['KEY_T'] = 20
input_def['KEY_Y'] = 21
input_def['KEY_U'] = 22
input_def['KEY_I'] = 23
input_def['KEY_O'] = 24
input_def['KEY_P'] = 25
input_def['KEY_LEFTBRACE'] = 26
input_def['KEY_RIGHTBRACE'] = 27
input_def['KEY_ENTER'] = 28
input_def['KEY_LEFTCTRL'] = 29
input_def['KEY_A'] = 30
input_def['KEY_S'] = 31
input_def['KEY_D'] = 32
input_def['KEY_F'] = 33
input_def['KEY_G'] = 34
input_def['KEY_H'] = 35
input_def['KEY_J'] = 36
input_def['KEY_K'] = 37
input_def['KEY_L'] = 38
input_def['KEY_SEMICOLON'] = 39
input_def['KEY_APOSTROPHE'] = 40
input_def['KEY_GRAVE'] = 41
input_def['KEY_LEFTSHIFT'] = 42
input_def['KEY_BACKSLASH'] = 43
input_def['KEY_Z'] = 44
input_def['KEY_X'] = 45
input_def['KEY_C'] = 46
input_def['KEY_V'] = 47
input_def['KEY_B'] = 48
input_def['KEY_N'] = 49
input_def['KEY_M'] = 50
input_def['KEY_COMMA'] = 51
input_def['KEY_DOT'] = 52
input_def['KEY_SLASH'] = 53
input_def['KEY_RIGHTSHIFT'] = 54
input_def['KEY_KPASTERISK'] = 55
input_def['KEY_LEFTALT'] = 56
input_def['KEY_SPACE'] = 57
input_def['KEY_CAPSLOCK'] = 58
input_def['KEY_F1'] = 59
input_def['KEY_F2'] = 60
input_def['KEY_F3'] = 61
input_def['KEY_F4'] = 62
input_def['KEY_F5'] = 63
input_def['KEY_F6'] = 64
input_def['KEY_F7'] = 65
input_def['KEY_F8'] = 66
input_def['KEY_F9'] = 67
input_def['KEY_F10'] = 68
input_def['KEY_NUMLOCK'] = 69
input_def['KEY_SCROLLLOCK'] = 70
input_def['KEY_KP7'] = 71
input_def['KEY_KP8'] = 72
input_def['KEY_KP9'] = 73
input_def['KEY_KPMINUS'] = 74
input_def['KEY_KP4'] = 75
input_def['KEY_KP5'] = 76
input_def['KEY_KP6'] = 77
input_def['KEY_KPPLUS'] = 78
input_def['KEY_KP1'] = 79
input_def['KEY_KP2'] = 80
input_def['KEY_KP3'] = 81
input_def['KEY_KP0'] = 82
input_def['KEY_KPDOT'] = 83

input_def['KEY_ZENKAKUHANKAKU'] = 85
input_def['KEY_102ND'] = 86
input_def['KEY_F11'] = 87
input_def['KEY_F12'] = 88
input_def['KEY_RO'] = 89
input_def['KEY_KATAKANA'] = 90
input_def['KEY_HIRAGANA'] = 91
input_def['KEY_HENKAN'] = 92
input_def['KEY_KATAKANAHIRAGANA'] = 93
input_def['KEY_MUHENKAN'] = 94
input_def['KEY_KPJPCOMMA'] = 95
input_def['KEY_KPENTER'] = 96
input_def['KEY_RIGHTCTRL'] = 97
input_def['KEY_KPSLASH'] = 98
input_def['KEY_SYSRQ'] = 99
input_def['KEY_RIGHTALT'] = 100
input_def['KEY_LINEFEED'] = 101
input_def['KEY_HOME'] = 102
input_def['KEY_UP'] = 103
input_def['KEY_PAGEUP'] = 104
input_def['KEY_LEFT'] = 105
input_def['KEY_RIGHT'] = 106
input_def['KEY_END'] = 107
input_def['KEY_DOWN'] = 108
input_def['KEY_PAGEDOWN'] = 109
input_def['KEY_INSERT'] = 110
input_def['KEY_DELETE'] = 111
input_def['KEY_MACRO'] = 112
input_def['KEY_MUTE'] = 113
input_def['KEY_VOLUMEDOWN'] = 114
input_def['KEY_VOLUMEUP'] = 115
input_def['KEY_POWER'] = 116
input_def['KEY_KPEQUAL'] = 117
input_def['KEY_KPPLUSMINUS'] = 118
input_def['KEY_PAUSE'] = 119

input_def['KEY_KPCOMMA'] = 121
input_def['KEY_HANGEUL'] = 122
input_def['KEY_HANGUEL'] = input_def['KEY_HANGEUL']
input_def['KEY_HANJA'] = 123
input_def['KEY_YEN'] = 124
input_def['KEY_LEFTMETA'] = 125
input_def['KEY_RIGHTMETA'] = 126
input_def['KEY_COMPOSE'] = 127

input_def['KEY_STOP'] = 128
input_def['KEY_AGAIN'] = 129
input_def['KEY_PROPS'] = 130
input_def['KEY_UNDO'] = 131
input_def['KEY_FRONT'] = 132
input_def['KEY_COPY'] = 133
input_def['KEY_OPEN'] = 134
input_def['KEY_PASTE'] = 135
input_def['KEY_FIND'] = 136
input_def['KEY_CUT'] = 137
input_def['KEY_HELP'] = 138
input_def['KEY_MENU'] = 139
input_def['KEY_CALC'] = 140
input_def['KEY_SETUP'] = 141
input_def['KEY_SLEEP'] = 142
input_def['KEY_WAKEUP'] = 143
input_def['KEY_FILE'] = 144
input_def['KEY_SENDFILE'] = 145
input_def['KEY_DELETEFILE'] = 146
input_def['KEY_XFER'] = 147
input_def['KEY_PROG1'] = 148
input_def['KEY_PROG2'] = 149
input_def['KEY_WWW'] = 150
input_def['KEY_MSDOS'] = 151
input_def['KEY_COFFEE'] = 152
input_def['KEY_DIRECTION'] = 153
input_def['KEY_CYCLEWINDOWS'] = 154
input_def['KEY_MAIL'] = 155
input_def['KEY_BOOKMARKS'] = 156
input_def['KEY_COMPUTER'] = 157
input_def['KEY_BACK'] = 158
input_def['KEY_FORWARD'] = 159
input_def['KEY_CLOSECD'] = 160
input_def['KEY_EJECTCD'] = 161
input_def['KEY_EJECTCLOSECD'] = 162
input_def['KEY_NEXTSONG'] = 163
input_def['KEY_PLAYPAUSE'] = 164
input_def['KEY_PREVIOUSSONG'] = 165
input_def['KEY_STOPCD'] = 166
input_def['KEY_RECORD'] = 167
input_def['KEY_REWIND'] = 168
input_def['KEY_PHONE'] = 169
input_def['KEY_ISO'] = 170
input_def['KEY_CONFIG'] = 171
input_def['KEY_HOMEPAGE'] = 172
input_def['KEY_REFRESH'] = 173
input_def['KEY_EXIT'] = 174
input_def['KEY_MOVE'] = 175
input_def['KEY_EDIT'] = 176
input_def['KEY_SCROLLUP'] = 177
input_def['KEY_SCROLLDOWN'] = 178
input_def['KEY_KPLEFTPAREN'] = 179
input_def['KEY_KPRIGHTPAREN'] = 180
input_def['KEY_NEW'] = 181
input_def['KEY_REDO'] = 182

input_def['KEY_F13'] = 183
input_def['KEY_F14'] = 184
input_def['KEY_F15'] = 185
input_def['KEY_F16'] = 186
input_def['KEY_F17'] = 187
input_def['KEY_F18'] = 188
input_def['KEY_F19'] = 189
input_def['KEY_F20'] = 190
input_def['KEY_F21'] = 191
input_def['KEY_F22'] = 192
input_def['KEY_F23'] = 193
input_def['KEY_F24'] = 194

input_def['KEY_PLAYCD'] = 200
input_def['KEY_PAUSECD'] = 201
input_def['KEY_PROG3'] = 202
input_def['KEY_PROG4'] = 203
input_def['KEY_SUSPEND'] = 205
input_def['KEY_CLOSE'] = 206
input_def['KEY_PLAY'] = 207
input_def['KEY_FASTFORWARD'] = 208
input_def['KEY_BASSBOOST'] = 209
input_def['KEY_PRINT'] = 210
input_def['KEY_HP'] = 211
input_def['KEY_CAMERA'] = 212
input_def['KEY_SOUND'] = 213
input_def['KEY_QUESTION'] = 214
input_def['KEY_EMAIL'] = 215
input_def['KEY_CHAT'] = 216
input_def['KEY_SEARCH'] = 217
input_def['KEY_CONNECT'] = 218
input_def['KEY_FINANCE'] = 219
input_def['KEY_SPORT'] = 220
input_def['KEY_SHOP'] = 221
input_def['KEY_ALTERASE'] = 222
input_def['KEY_CANCEL'] = 223
input_def['KEY_BRIGHTNESSDOWN'] = 224
input_def['KEY_BRIGHTNESSUP'] = 225
input_def['KEY_MEDIA'] = 226

input_def['KEY_SWITCHVIDEOMODE'] = 227
input_def['KEY_KBDILLUMTOGGLE'] = 228
input_def['KEY_KBDILLUMDOWN'] = 229
input_def['KEY_KBDILLUMUP'] = 230

input_def['KEY_SEND'] = 231
input_def['KEY_REPLY'] = 232
input_def['KEY_FORWARDMAIL'] = 233
input_def['KEY_SAVE'] = 234
input_def['KEY_DOCUMENTS'] = 235

input_def['KEY_BATTERY'] = 236

input_def['KEY_BLUETOOTH'] = 237
input_def['KEY_WLAN'] = 238

input_def['KEY_UNKNOWN'] = 240

input_def['BTN_MISC'] = 0x100
input_def['BTN_0'] = 0x100
input_def['BTN_1'] = 0x101
input_def['BTN_2'] = 0x102
input_def['BTN_3'] = 0x103
input_def['BTN_4'] = 0x104
input_def['BTN_5'] = 0x105
input_def['BTN_6'] = 0x106
input_def['BTN_7'] = 0x107
input_def['BTN_8'] = 0x108
input_def['BTN_9'] = 0x109

input_def['BTN_MOUSE'] = 0x110
input_def['BTN_LEFT'] = 0x110
input_def['BTN_RIGHT'] = 0x111
input_def['BTN_MIDDLE'] = 0x112
input_def['BTN_SIDE'] = 0x113
input_def['BTN_EXTRA'] = 0x114
input_def['BTN_FORWARD'] = 0x115
input_def['BTN_BACK'] = 0x116
input_def['BTN_TASK'] = 0x117

input_def['BTN_JOYSTICK'] = 0x120
input_def['BTN_TRIGGER'] = 0x120
input_def['BTN_THUMB'] = 0x121
input_def['BTN_THUMB2'] = 0x122
input_def['BTN_TOP'] = 0x123
input_def['BTN_TOP2'] = 0x124
input_def['BTN_PINKIE'] = 0x125
input_def['BTN_BASE'] = 0x126
input_def['BTN_BASE2'] = 0x127
input_def['BTN_BASE3'] = 0x128
input_def['BTN_BASE4'] = 0x129
input_def['BTN_BASE5'] = 0x12a
input_def['BTN_BASE6'] = 0x12b
input_def['BTN_DEAD'] = 0x12f

input_def['BTN_GAMEPAD'] = 0x130
input_def['BTN_A'] = 0x130
input_def['BTN_B'] = 0x131
input_def['BTN_C'] = 0x132
input_def['BTN_X'] = 0x133
input_def['BTN_Y'] = 0x134
input_def['BTN_Z'] = 0x135
input_def['BTN_TL'] = 0x136
input_def['BTN_TR'] = 0x137
input_def['BTN_TL2'] = 0x138
input_def['BTN_TR2'] = 0x139
input_def['BTN_SELECT'] = 0x13a
input_def['BTN_START'] = 0x13b
input_def['BTN_MODE'] = 0x13c
input_def['BTN_THUMBL'] = 0x13d
input_def['BTN_THUMBR'] = 0x13e

input_def['BTN_DIGI'] = 0x140
input_def['BTN_TOOL_PEN'] = 0x140
input_def['BTN_TOOL_RUBBER'] = 0x141
input_def['BTN_TOOL_BRUSH'] = 0x142
input_def['BTN_TOOL_PENCIL'] = 0x143
input_def['BTN_TOOL_AIRBRUSH'] = 0x144
input_def['BTN_TOOL_FINGER'] = 0x145
input_def['BTN_TOOL_MOUSE'] = 0x146
input_def['BTN_TOOL_LENS'] = 0x147
input_def['BTN_TOUCH'] = 0x14a
input_def['BTN_STYLUS'] = 0x14b
input_def['BTN_STYLUS2'] = 0x14c
input_def['BTN_TOOL_DOUBLETAP'] = 0x14d
input_def['BTN_TOOL_TRIPLETAP'] = 0x14e

input_def['BTN_WHEEL'] = 0x150
input_def['BTN_GEAR_DOWN'] = 0x150
input_def['BTN_GEAR_UP'] = 0x151

input_def['KEY_OK'] = 0x160
input_def['KEY_SELECT'] = 0x161
input_def['KEY_GOTO'] = 0x162
input_def['KEY_CLEAR'] = 0x163
input_def['KEY_POWER2'] = 0x164
input_def['KEY_OPTION'] = 0x165
input_def['KEY_INFO'] = 0x166
input_def['KEY_TIME'] = 0x167
input_def['KEY_VENDOR'] = 0x168
input_def['KEY_ARCHIVE'] = 0x169
input_def['KEY_PROGRAM'] = 0x16a
input_def['KEY_CHANNEL'] = 0x16b
input_def['KEY_FAVORITES'] = 0x16c
input_def['KEY_EPG'] = 0x16d
input_def['KEY_PVR'] = 0x16e
input_def['KEY_MHP'] = 0x16f
input_def['KEY_LANGUAGE'] = 0x170
input_def['KEY_TITLE'] = 0x171
input_def['KEY_SUBTITLE'] = 0x172
input_def['KEY_ANGLE'] = 0x173
input_def['KEY_ZOOM'] = 0x174
input_def['KEY_MODE'] = 0x175
input_def['KEY_KEYBOARD'] = 0x176
input_def['KEY_SCREEN'] = 0x177
input_def['KEY_PC'] = 0x178
input_def['KEY_TV'] = 0x179
input_def['KEY_TV2'] = 0x17a
input_def['KEY_VCR'] = 0x17b
input_def['KEY_VCR2'] = 0x17c
input_def['KEY_SAT'] = 0x17d
input_def['KEY_SAT2'] = 0x17e
input_def['KEY_CD'] = 0x17f
input_def['KEY_TAPE'] = 0x180
input_def['KEY_RADIO'] = 0x181
input_def['KEY_TUNER'] = 0x182
input_def['KEY_PLAYER'] = 0x183
input_def['KEY_TEXT'] = 0x184
input_def['KEY_DVD'] = 0x185
input_def['KEY_AUX'] = 0x186
input_def['KEY_MP3'] = 0x187
input_def['KEY_AUDIO'] = 0x188
input_def['KEY_VIDEO'] = 0x189
input_def['KEY_DIRECTORY'] = 0x18a
input_def['KEY_LIST'] = 0x18b
input_def['KEY_MEMO'] = 0x18c
input_def['KEY_CALENDAR'] = 0x18d
input_def['KEY_RED'] = 0x18e
input_def['KEY_GREEN'] = 0x18f
input_def['KEY_YELLOW'] = 0x190
input_def['KEY_BLUE'] = 0x191
input_def['KEY_CHANNELUP'] = 0x192
input_def['KEY_CHANNELDOWN'] = 0x193
input_def['KEY_FIRST'] = 0x194
input_def['KEY_LAST'] = 0x195
input_def['KEY_AB'] = 0x196
input_def['KEY_NEXT'] = 0x197
input_def['KEY_RESTART'] = 0x198
input_def['KEY_SLOW'] = 0x199
input_def['KEY_SHUFFLE'] = 0x19a
input_def['KEY_BREAK'] = 0x19b
input_def['KEY_PREVIOUS'] = 0x19c
input_def['KEY_DIGITS'] = 0x19d
input_def['KEY_TEEN'] = 0x19e
input_def['KEY_TWEN'] = 0x19f

input_def['KEY_DEL_EOL'] = 0x1c0
input_def['KEY_DEL_EOS'] = 0x1c1
input_def['KEY_INS_LINE'] = 0x1c2
input_def['KEY_DEL_LINE'] = 0x1c3

input_def['KEY_FN'] = 0x1d0
input_def['KEY_FN_ESC'] = 0x1d1
input_def['KEY_FN_F1'] = 0x1d2
input_def['KEY_FN_F2'] = 0x1d3
input_def['KEY_FN_F3'] = 0x1d4
input_def['KEY_FN_F4'] = 0x1d5
input_def['KEY_FN_F5'] = 0x1d6
input_def['KEY_FN_F6'] = 0x1d7
input_def['KEY_FN_F7'] = 0x1d8
input_def['KEY_FN_F8'] = 0x1d9
input_def['KEY_FN_F9'] = 0x1da
input_def['KEY_FN_F10'] = 0x1db
input_def['KEY_FN_F11'] = 0x1dc
input_def['KEY_FN_F12'] = 0x1dd
input_def['KEY_FN_1'] = 0x1de
input_def['KEY_FN_2'] = 0x1df
input_def['KEY_FN_D'] = 0x1e0
input_def['KEY_FN_E'] = 0x1e1
input_def['KEY_FN_F'] = 0x1e2
input_def['KEY_FN_S'] = 0x1e3
input_def['KEY_FN_B'] = 0x1e4

input_def['KEY_BRL_DOT1'] = 0x1f1
input_def['KEY_BRL_DOT2'] = 0x1f2
input_def['KEY_BRL_DOT3'] = 0x1f3
input_def['KEY_BRL_DOT4'] = 0x1f4
input_def['KEY_BRL_DOT5'] = 0x1f5
input_def['KEY_BRL_DOT6'] = 0x1f6
input_def['KEY_BRL_DOT7'] = 0x1f7
input_def['KEY_BRL_DOT8'] = 0x1f8

# Relative axes

input_def['REL_X'] = 0x00
input_def['REL_Y'] = 0x01
input_def['REL_Z'] = 0x02
input_def['REL_RX'] = 0x03
input_def['REL_RY'] = 0x04
input_def['REL_RZ'] = 0x05
input_def['REL_HWHEEL'] = 0x06
input_def['REL_DIAL'] = 0x07
input_def['REL_WHEEL'] = 0x08
input_def['REL_MISC'] = 0x09
input_def['REL_MAX'] = 0x0f

# Absolute axes

input_def['ABS_X'] = 0x00
input_def['ABS_Y'] = 0x01
input_def['ABS_Z'] = 0x02
input_def['ABS_RX'] = 0x03
input_def['ABS_RY'] = 0x04
input_def['ABS_RZ'] = 0x05
input_def['ABS_THROTTLE'] = 0x06
input_def['ABS_RUDDER'] = 0x07
input_def['ABS_WHEEL'] = 0x08
input_def['ABS_GAS'] = 0x09
input_def['ABS_BRAKE'] = 0x0a
input_def['ABS_HAT0X'] = 0x10
input_def['ABS_HAT0Y'] = 0x11
input_def['ABS_HAT1X'] = 0x12
input_def['ABS_HAT1Y'] = 0x13
input_def['ABS_HAT2X'] = 0x14
input_def['ABS_HAT2Y'] = 0x15
input_def['ABS_HAT3X'] = 0x16
input_def['ABS_HAT3Y'] = 0x17
input_def['ABS_PRESSURE'] = 0x18
input_def['ABS_DISTANCE'] = 0x19
input_def['ABS_TILT_X'] = 0x1a
input_def['ABS_TILT_Y'] = 0x1b
input_def['ABS_TOOL_WIDTH'] = 0x1c
input_def['ABS_VOLUME'] = 0x20
input_def['ABS_MISC'] = 0x28
input_def['ABS_MAX'] = 0x3f

# Switch events

input_def['SW_LID'] = 0x00               # set = lid shut */
input_def['SW_TABLET_MODE'] = 0x01       # set = tablet mode */
input_def['SW_HEADPHONE_INSERT'] = 0x02  # set = inserted */
input_def['SW_MAX'] = 0x0f

# Misc events

input_def['MSC_SERIAL'] = 0x00
input_def['MSC_PULSELED'] = 0x01
input_def['MSC_GESTURE'] = 0x02
input_def['MSC_RAW'] = 0x03
input_def['MSC_SCAN'] = 0x04
input_def['MSC_MAX'] = 0x07

# LEDs

input_def['LED_NUML'] = 0x00
input_def['LED_CAPSL'] = 0x01
input_def['LED_SCROLLL'] = 0x02
input_def['LED_COMPOSE'] = 0x03
input_def['LED_KANA'] = 0x04
input_def['LED_SLEEP'] = 0x05
input_def['LED_SUSPEND'] = 0x06
input_def['LED_MUTE'] = 0x07
input_def['LED_MISC'] = 0x08
input_def['LED_MAIL'] = 0x09
input_def['LED_CHARGING'] = 0x0a
input_def['LED_MAX'] = 0x0f

# Autorepeat values

input_def['REP_DELAY'] = 0x00
input_def['REP_PERIOD'] = 0x01
input_def['REP_MAX'] = 0x01

# Sounds

input_def['SND_CLICK'] = 0x00
input_def['SND_BELL'] = 0x01
input_def['SND_TONE'] = 0x02
input_def['SND_MAX'] = 0x07

# IDs.

input_def['ID_BUS'] = 0
input_def['ID_VENDOR'] = 1
input_def['ID_PRODUCT'] = 2
input_def['ID_VERSION'] = 3

input_def['BUS_PCI'] = 0x01
input_def['BUS_ISAPNP'] = 0x02
input_def['BUS_USB'] = 0x03
input_def['BUS_HIL'] = 0x04
input_def['BUS_BLUETOOTH'] = 0x05
input_def['BUS_VIRTUAL'] = 0x06

input_def['BUS_ISA'] = 0x10
input_def['BUS_I8042'] = 0x11
input_def['BUS_XTKBD'] = 0x12
input_def['BUS_RS232'] = 0x13
input_def['BUS_GAMEPORT'] = 0x14
input_def['BUS_PARPORT'] = 0x15
input_def['BUS_AMIGA'] = 0x16
input_def['BUS_ADB'] = 0x17
input_def['BUS_I2C'] = 0x18
input_def['BUS_HOST'] = 0x19
input_def['BUS_GSC'] = 0x1A


uinput = {}
uinput['UI_DEV_CREATE'] = 0x5501
uinput['UI_DEV_DESTROY'] = 0x5502
uinput['UI_SET_EVBIT'] = 0x40045564
uinput['UI_SET_KEYBIT'] = 0x40045565
uinput['UI_SET_RELBIT'] = 0x40045566
uinput['UI_SET_ABSBIT'] = 0x40045567
uinput['UI_SET_MSCBIT'] = 0x40045568
uinput['UI_SET_LEDBIT'] = 0x40045569
uinput['UI_SET_SNDBIT'] = 0x4004556A
uinput['UI_SET_FFBIT'] = 0x4004556B
uinput['UI_SET_PHYS'] = 0x4004556C
uinput['UI_SET_SWBIT'] = 0x4004556D

