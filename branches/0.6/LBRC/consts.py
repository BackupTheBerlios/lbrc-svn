
"""
@var input: Constants taken from input.h (see kernel source or in our doc dir)

             These constants are used to report input events to the kernel.
             
@var uinput: Constants taken from uinput.h (see kernel source or in our doc dir)

             These are needed for the creation of a userspace uinput driver
"""
input = {}
input['EV_SYN'] = 0x00
input['EV_KEY'] = 0x01
input['EV_REL'] = 0x02
input['EV_ABS'] = 0x03
input['EV_MSC'] = 0x04
input['EV_SW'] = 0x05
input['EV_LED'] = 0x11
input['EV_SND'] = 0x12
input['EV_REP'] = 0x14
input['EV_FF'] = 0x15
input['EV_PWR'] = 0x16
input['EV_FF_STATUS'] = 0x17
input['EV_MAX'] = 0x1f

# Synchronization events.

input['SYN_REPORT'] = 0
input['SYN_CONFIG'] = 1

# Keys and buttons

input['KEY_RESERVED'] = 0
input['KEY_ESC'] = 1
input['KEY_1'] = 2
input['KEY_2'] = 3
input['KEY_3'] = 4
input['KEY_4'] = 5
input['KEY_5'] = 6
input['KEY_6'] = 7
input['KEY_7'] = 8
input['KEY_8'] = 9
input['KEY_9'] = 10
input['KEY_0'] = 11
input['KEY_MINUS'] = 12
input['KEY_EQUAL'] = 13
input['KEY_BACKSPACE'] = 14
input['KEY_TAB'] = 15
input['KEY_Q'] = 16
input['KEY_W'] = 17
input['KEY_E'] = 18
input['KEY_R'] = 19
input['KEY_T'] = 20
input['KEY_Y'] = 21
input['KEY_U'] = 22
input['KEY_I'] = 23
input['KEY_O'] = 24
input['KEY_P'] = 25
input['KEY_LEFTBRACE'] = 26
input['KEY_RIGHTBRACE'] = 27
input['KEY_ENTER'] = 28
input['KEY_LEFTCTRL'] = 29
input['KEY_A'] = 30
input['KEY_S'] = 31
input['KEY_D'] = 32
input['KEY_F'] = 33
input['KEY_G'] = 34
input['KEY_H'] = 35
input['KEY_J'] = 36
input['KEY_K'] = 37
input['KEY_L'] = 38
input['KEY_SEMICOLON'] = 39
input['KEY_APOSTROPHE'] = 40
input['KEY_GRAVE'] = 41
input['KEY_LEFTSHIFT'] = 42
input['KEY_BACKSLASH'] = 43
input['KEY_Z'] = 44
input['KEY_X'] = 45
input['KEY_C'] = 46
input['KEY_V'] = 47
input['KEY_B'] = 48
input['KEY_N'] = 49
input['KEY_M'] = 50
input['KEY_COMMA'] = 51
input['KEY_DOT'] = 52
input['KEY_SLASH'] = 53
input['KEY_RIGHTSHIFT'] = 54
input['KEY_KPASTERISK'] = 55
input['KEY_LEFTALT'] = 56
input['KEY_SPACE'] = 57
input['KEY_CAPSLOCK'] = 58
input['KEY_F1'] = 59
input['KEY_F2'] = 60
input['KEY_F3'] = 61
input['KEY_F4'] = 62
input['KEY_F5'] = 63
input['KEY_F6'] = 64
input['KEY_F7'] = 65
input['KEY_F8'] = 66
input['KEY_F9'] = 67
input['KEY_F10'] = 68
input['KEY_NUMLOCK'] = 69
input['KEY_SCROLLLOCK'] = 70
input['KEY_KP7'] = 71
input['KEY_KP8'] = 72
input['KEY_KP9'] = 73
input['KEY_KPMINUS'] = 74
input['KEY_KP4'] = 75
input['KEY_KP5'] = 76
input['KEY_KP6'] = 77
input['KEY_KPPLUS'] = 78
input['KEY_KP1'] = 79
input['KEY_KP2'] = 80
input['KEY_KP3'] = 81
input['KEY_KP0'] = 82
input['KEY_KPDOT'] = 83

input['KEY_ZENKAKUHANKAKU'] = 85
input['KEY_102ND'] = 86
input['KEY_F11'] = 87
input['KEY_F12'] = 88
input['KEY_RO'] = 89
input['KEY_KATAKANA'] = 90
input['KEY_HIRAGANA'] = 91
input['KEY_HENKAN'] = 92
input['KEY_KATAKANAHIRAGANA'] = 93
input['KEY_MUHENKAN'] = 94
input['KEY_KPJPCOMMA'] = 95
input['KEY_KPENTER'] = 96
input['KEY_RIGHTCTRL'] = 97
input['KEY_KPSLASH'] = 98
input['KEY_SYSRQ'] = 99
input['KEY_RIGHTALT'] = 100
input['KEY_LINEFEED'] = 101
input['KEY_HOME'] = 102
input['KEY_UP'] = 103
input['KEY_PAGEUP'] = 104
input['KEY_LEFT'] = 105
input['KEY_RIGHT'] = 106
input['KEY_END'] = 107
input['KEY_DOWN'] = 108
input['KEY_PAGEDOWN'] = 109
input['KEY_INSERT'] = 110
input['KEY_DELETE'] = 111
input['KEY_MACRO'] = 112
input['KEY_MUTE'] = 113
input['KEY_VOLUMEDOWN'] = 114
input['KEY_VOLUMEUP'] = 115
input['KEY_POWER'] = 116
input['KEY_KPEQUAL'] = 117
input['KEY_KPPLUSMINUS'] = 118
input['KEY_PAUSE'] = 119

input['KEY_KPCOMMA'] = 121
input['KEY_HANGEUL'] = 122
input['KEY_HANGUEL'] = input['KEY_HANGEUL']
input['KEY_HANJA'] = 123
input['KEY_YEN'] = 124
input['KEY_LEFTMETA'] = 125
input['KEY_RIGHTMETA'] = 126
input['KEY_COMPOSE'] = 127

input['KEY_STOP'] = 128
input['KEY_AGAIN'] = 129
input['KEY_PROPS'] = 130
input['KEY_UNDO'] = 131
input['KEY_FRONT'] = 132
input['KEY_COPY'] = 133
input['KEY_OPEN'] = 134
input['KEY_PASTE'] = 135
input['KEY_FIND'] = 136
input['KEY_CUT'] = 137
input['KEY_HELP'] = 138
input['KEY_MENU'] = 139
input['KEY_CALC'] = 140
input['KEY_SETUP'] = 141
input['KEY_SLEEP'] = 142
input['KEY_WAKEUP'] = 143
input['KEY_FILE'] = 144
input['KEY_SENDFILE'] = 145
input['KEY_DELETEFILE'] = 146
input['KEY_XFER'] = 147
input['KEY_PROG1'] = 148
input['KEY_PROG2'] = 149
input['KEY_WWW'] = 150
input['KEY_MSDOS'] = 151
input['KEY_COFFEE'] = 152
input['KEY_DIRECTION'] = 153
input['KEY_CYCLEWINDOWS'] = 154
input['KEY_MAIL'] = 155
input['KEY_BOOKMARKS'] = 156
input['KEY_COMPUTER'] = 157
input['KEY_BACK'] = 158
input['KEY_FORWARD'] = 159
input['KEY_CLOSECD'] = 160
input['KEY_EJECTCD'] = 161
input['KEY_EJECTCLOSECD'] = 162
input['KEY_NEXTSONG'] = 163
input['KEY_PLAYPAUSE'] = 164
input['KEY_PREVIOUSSONG'] = 165
input['KEY_STOPCD'] = 166
input['KEY_RECORD'] = 167
input['KEY_REWIND'] = 168
input['KEY_PHONE'] = 169
input['KEY_ISO'] = 170
input['KEY_CONFIG'] = 171
input['KEY_HOMEPAGE'] = 172
input['KEY_REFRESH'] = 173
input['KEY_EXIT'] = 174
input['KEY_MOVE'] = 175
input['KEY_EDIT'] = 176
input['KEY_SCROLLUP'] = 177
input['KEY_SCROLLDOWN'] = 178
input['KEY_KPLEFTPAREN'] = 179
input['KEY_KPRIGHTPAREN'] = 180
input['KEY_NEW'] = 181
input['KEY_REDO'] = 182

input['KEY_F13'] = 183
input['KEY_F14'] = 184
input['KEY_F15'] = 185
input['KEY_F16'] = 186
input['KEY_F17'] = 187
input['KEY_F18'] = 188
input['KEY_F19'] = 189
input['KEY_F20'] = 190
input['KEY_F21'] = 191
input['KEY_F22'] = 192
input['KEY_F23'] = 193
input['KEY_F24'] = 194

input['KEY_PLAYCD'] = 200
input['KEY_PAUSECD'] = 201
input['KEY_PROG3'] = 202
input['KEY_PROG4'] = 203
input['KEY_SUSPEND'] = 205
input['KEY_CLOSE'] = 206
input['KEY_PLAY'] = 207
input['KEY_FASTFORWARD'] = 208
input['KEY_BASSBOOST'] = 209
input['KEY_PRINT'] = 210
input['KEY_HP'] = 211
input['KEY_CAMERA'] = 212
input['KEY_SOUND'] = 213
input['KEY_QUESTION'] = 214
input['KEY_EMAIL'] = 215
input['KEY_CHAT'] = 216
input['KEY_SEARCH'] = 217
input['KEY_CONNECT'] = 218
input['KEY_FINANCE'] = 219
input['KEY_SPORT'] = 220
input['KEY_SHOP'] = 221
input['KEY_ALTERASE'] = 222
input['KEY_CANCEL'] = 223
input['KEY_BRIGHTNESSDOWN'] = 224
input['KEY_BRIGHTNESSUP'] = 225
input['KEY_MEDIA'] = 226

input['KEY_SWITCHVIDEOMODE'] = 227
input['KEY_KBDILLUMTOGGLE'] = 228
input['KEY_KBDILLUMDOWN'] = 229
input['KEY_KBDILLUMUP'] = 230

input['KEY_SEND'] = 231
input['KEY_REPLY'] = 232
input['KEY_FORWARDMAIL'] = 233
input['KEY_SAVE'] = 234
input['KEY_DOCUMENTS'] = 235

input['KEY_BATTERY'] = 236

input['KEY_BLUETOOTH'] = 237
input['KEY_WLAN'] = 238

input['KEY_UNKNOWN'] = 240

input['BTN_MISC'] = 0x100
input['BTN_0'] = 0x100
input['BTN_1'] = 0x101
input['BTN_2'] = 0x102
input['BTN_3'] = 0x103
input['BTN_4'] = 0x104
input['BTN_5'] = 0x105
input['BTN_6'] = 0x106
input['BTN_7'] = 0x107
input['BTN_8'] = 0x108
input['BTN_9'] = 0x109

input['BTN_MOUSE'] = 0x110
input['BTN_LEFT'] = 0x110
input['BTN_RIGHT'] = 0x111
input['BTN_MIDDLE'] = 0x112
input['BTN_SIDE'] = 0x113
input['BTN_EXTRA'] = 0x114
input['BTN_FORWARD'] = 0x115
input['BTN_BACK'] = 0x116
input['BTN_TASK'] = 0x117

input['BTN_JOYSTICK'] = 0x120
input['BTN_TRIGGER'] = 0x120
input['BTN_THUMB'] = 0x121
input['BTN_THUMB2'] = 0x122
input['BTN_TOP'] = 0x123
input['BTN_TOP2'] = 0x124
input['BTN_PINKIE'] = 0x125
input['BTN_BASE'] = 0x126
input['BTN_BASE2'] = 0x127
input['BTN_BASE3'] = 0x128
input['BTN_BASE4'] = 0x129
input['BTN_BASE5'] = 0x12a
input['BTN_BASE6'] = 0x12b
input['BTN_DEAD'] = 0x12f

input['BTN_GAMEPAD'] = 0x130
input['BTN_A'] = 0x130
input['BTN_B'] = 0x131
input['BTN_C'] = 0x132
input['BTN_X'] = 0x133
input['BTN_Y'] = 0x134
input['BTN_Z'] = 0x135
input['BTN_TL'] = 0x136
input['BTN_TR'] = 0x137
input['BTN_TL2'] = 0x138
input['BTN_TR2'] = 0x139
input['BTN_SELECT'] = 0x13a
input['BTN_START'] = 0x13b
input['BTN_MODE'] = 0x13c
input['BTN_THUMBL'] = 0x13d
input['BTN_THUMBR'] = 0x13e

input['BTN_DIGI'] = 0x140
input['BTN_TOOL_PEN'] = 0x140
input['BTN_TOOL_RUBBER'] = 0x141
input['BTN_TOOL_BRUSH'] = 0x142
input['BTN_TOOL_PENCIL'] = 0x143
input['BTN_TOOL_AIRBRUSH'] = 0x144
input['BTN_TOOL_FINGER'] = 0x145
input['BTN_TOOL_MOUSE'] = 0x146
input['BTN_TOOL_LENS'] = 0x147
input['BTN_TOUCH'] = 0x14a
input['BTN_STYLUS'] = 0x14b
input['BTN_STYLUS2'] = 0x14c
input['BTN_TOOL_DOUBLETAP'] = 0x14d
input['BTN_TOOL_TRIPLETAP'] = 0x14e

input['BTN_WHEEL'] = 0x150
input['BTN_GEAR_DOWN'] = 0x150
input['BTN_GEAR_UP'] = 0x151

input['KEY_OK'] = 0x160
input['KEY_SELECT'] = 0x161
input['KEY_GOTO'] = 0x162
input['KEY_CLEAR'] = 0x163
input['KEY_POWER2'] = 0x164
input['KEY_OPTION'] = 0x165
input['KEY_INFO'] = 0x166
input['KEY_TIME'] = 0x167
input['KEY_VENDOR'] = 0x168
input['KEY_ARCHIVE'] = 0x169
input['KEY_PROGRAM'] = 0x16a
input['KEY_CHANNEL'] = 0x16b
input['KEY_FAVORITES'] = 0x16c
input['KEY_EPG'] = 0x16d
input['KEY_PVR'] = 0x16e
input['KEY_MHP'] = 0x16f
input['KEY_LANGUAGE'] = 0x170
input['KEY_TITLE'] = 0x171
input['KEY_SUBTITLE'] = 0x172
input['KEY_ANGLE'] = 0x173
input['KEY_ZOOM'] = 0x174
input['KEY_MODE'] = 0x175
input['KEY_KEYBOARD'] = 0x176
input['KEY_SCREEN'] = 0x177
input['KEY_PC'] = 0x178
input['KEY_TV'] = 0x179
input['KEY_TV2'] = 0x17a
input['KEY_VCR'] = 0x17b
input['KEY_VCR2'] = 0x17c
input['KEY_SAT'] = 0x17d
input['KEY_SAT2'] = 0x17e
input['KEY_CD'] = 0x17f
input['KEY_TAPE'] = 0x180
input['KEY_RADIO'] = 0x181
input['KEY_TUNER'] = 0x182
input['KEY_PLAYER'] = 0x183
input['KEY_TEXT'] = 0x184
input['KEY_DVD'] = 0x185
input['KEY_AUX'] = 0x186
input['KEY_MP3'] = 0x187
input['KEY_AUDIO'] = 0x188
input['KEY_VIDEO'] = 0x189
input['KEY_DIRECTORY'] = 0x18a
input['KEY_LIST'] = 0x18b
input['KEY_MEMO'] = 0x18c
input['KEY_CALENDAR'] = 0x18d
input['KEY_RED'] = 0x18e
input['KEY_GREEN'] = 0x18f
input['KEY_YELLOW'] = 0x190
input['KEY_BLUE'] = 0x191
input['KEY_CHANNELUP'] = 0x192
input['KEY_CHANNELDOWN'] = 0x193
input['KEY_FIRST'] = 0x194
input['KEY_LAST'] = 0x195
input['KEY_AB'] = 0x196
input['KEY_NEXT'] = 0x197
input['KEY_RESTART'] = 0x198
input['KEY_SLOW'] = 0x199
input['KEY_SHUFFLE'] = 0x19a
input['KEY_BREAK'] = 0x19b
input['KEY_PREVIOUS'] = 0x19c
input['KEY_DIGITS'] = 0x19d
input['KEY_TEEN'] = 0x19e
input['KEY_TWEN'] = 0x19f

input['KEY_DEL_EOL'] = 0x1c0
input['KEY_DEL_EOS'] = 0x1c1
input['KEY_INS_LINE'] = 0x1c2
input['KEY_DEL_LINE'] = 0x1c3

input['KEY_FN'] = 0x1d0
input['KEY_FN_ESC'] = 0x1d1
input['KEY_FN_F1'] = 0x1d2
input['KEY_FN_F2'] = 0x1d3
input['KEY_FN_F3'] = 0x1d4
input['KEY_FN_F4'] = 0x1d5
input['KEY_FN_F5'] = 0x1d6
input['KEY_FN_F6'] = 0x1d7
input['KEY_FN_F7'] = 0x1d8
input['KEY_FN_F8'] = 0x1d9
input['KEY_FN_F9'] = 0x1da
input['KEY_FN_F10'] = 0x1db
input['KEY_FN_F11'] = 0x1dc
input['KEY_FN_F12'] = 0x1dd
input['KEY_FN_1'] = 0x1de
input['KEY_FN_2'] = 0x1df
input['KEY_FN_D'] = 0x1e0
input['KEY_FN_E'] = 0x1e1
input['KEY_FN_F'] = 0x1e2
input['KEY_FN_S'] = 0x1e3
input['KEY_FN_B'] = 0x1e4

input['KEY_BRL_DOT1'] = 0x1f1
input['KEY_BRL_DOT2'] = 0x1f2
input['KEY_BRL_DOT3'] = 0x1f3
input['KEY_BRL_DOT4'] = 0x1f4
input['KEY_BRL_DOT5'] = 0x1f5
input['KEY_BRL_DOT6'] = 0x1f6
input['KEY_BRL_DOT7'] = 0x1f7
input['KEY_BRL_DOT8'] = 0x1f8

# Relative axes

input['REL_X'] = 0x00
input['REL_Y'] = 0x01
input['REL_Z'] = 0x02
input['REL_RX'] = 0x03
input['REL_RY'] = 0x04
input['REL_RZ'] = 0x05
input['REL_HWHEEL'] = 0x06
input['REL_DIAL'] = 0x07
input['REL_WHEEL'] = 0x08
input['REL_MISC'] = 0x09
input['REL_MAX'] = 0x0f

# Absolute axes

input['ABS_X'] = 0x00
input['ABS_Y'] = 0x01
input['ABS_Z'] = 0x02
input['ABS_RX'] = 0x03
input['ABS_RY'] = 0x04
input['ABS_RZ'] = 0x05
input['ABS_THROTTLE'] = 0x06
input['ABS_RUDDER'] = 0x07
input['ABS_WHEEL'] = 0x08
input['ABS_GAS'] = 0x09
input['ABS_BRAKE'] = 0x0a
input['ABS_HAT0X'] = 0x10
input['ABS_HAT0Y'] = 0x11
input['ABS_HAT1X'] = 0x12
input['ABS_HAT1Y'] = 0x13
input['ABS_HAT2X'] = 0x14
input['ABS_HAT2Y'] = 0x15
input['ABS_HAT3X'] = 0x16
input['ABS_HAT3Y'] = 0x17
input['ABS_PRESSURE'] = 0x18
input['ABS_DISTANCE'] = 0x19
input['ABS_TILT_X'] = 0x1a
input['ABS_TILT_Y'] = 0x1b
input['ABS_TOOL_WIDTH'] = 0x1c
input['ABS_VOLUME'] = 0x20
input['ABS_MISC'] = 0x28
input['ABS_MAX'] = 0x3f

# Switch events

input['SW_LID'] = 0x00               # set = lid shut */
input['SW_TABLET_MODE'] = 0x01       # set = tablet mode */
input['SW_HEADPHONE_INSERT'] = 0x02  # set = inserted */
input['SW_MAX'] = 0x0f

# Misc events

input['MSC_SERIAL'] = 0x00
input['MSC_PULSELED'] = 0x01
input['MSC_GESTURE'] = 0x02
input['MSC_RAW'] = 0x03
input['MSC_SCAN'] = 0x04
input['MSC_MAX'] = 0x07

# LEDs

input['LED_NUML'] = 0x00
input['LED_CAPSL'] = 0x01
input['LED_SCROLLL'] = 0x02
input['LED_COMPOSE'] = 0x03
input['LED_KANA'] = 0x04
input['LED_SLEEP'] = 0x05
input['LED_SUSPEND'] = 0x06
input['LED_MUTE'] = 0x07
input['LED_MISC'] = 0x08
input['LED_MAIL'] = 0x09
input['LED_CHARGING'] = 0x0a
input['LED_MAX'] = 0x0f

# Autorepeat values

input['REP_DELAY'] = 0x00
input['REP_PERIOD'] = 0x01
input['REP_MAX'] = 0x01

# Sounds

input['SND_CLICK'] = 0x00
input['SND_BELL'] = 0x01
input['SND_TONE'] = 0x02
input['SND_MAX'] = 0x07

# IDs.

input['ID_BUS'] = 0
input['ID_VENDOR'] = 1
input['ID_PRODUCT'] = 2
input['ID_VERSION'] = 3

input['BUS_PCI'] = 0x01
input['BUS_ISAPNP'] = 0x02
input['BUS_USB'] = 0x03
input['BUS_HIL'] = 0x04
input['BUS_BLUETOOTH'] = 0x05
input['BUS_VIRTUAL'] = 0x06

input['BUS_ISA'] = 0x10
input['BUS_I8042'] = 0x11
input['BUS_XTKBD'] = 0x12
input['BUS_RS232'] = 0x13
input['BUS_GAMEPORT'] = 0x14
input['BUS_PARPORT'] = 0x15
input['BUS_AMIGA'] = 0x16
input['BUS_ADB'] = 0x17
input['BUS_I2C'] = 0x18
input['BUS_HOST'] = 0x19
input['BUS_GSC'] = 0x1A


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

