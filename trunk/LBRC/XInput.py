"""
The XInput Module translates keycodes from the phone to X Keysyms and
injects them via XTest.
"""
import logging
import gobject
import LBRC.consts as co
from LBRC.Listener import Listener
from Xlib import X, display, XK, error
from Xlib.ext import xtest

class XInput( Listener ):
    """
    The XInput Module translates keycodes from the phone to X Keysyms and
    injects them via XTest.
    """
    def __init__( self, config ):
        """
        @param  config:         configuration data
        @type   config:         dictionary
        """
        Listener.__init__(self, config, "XInput", command_class=X11Event)
        self.invoked = {}
        
    def set_profile( self, config, profile ):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        self.logger.debug("set_profile(%s, %s)" % ( config, profile ) )
        # Stop pending events
        for invoked in self.invoked.values():
            for i in invoked:
                i.stop()
        # Set new profile up
        self.invoked  = {}
        try:
            self._interpret_profile( config, profile )
        except Exception, e:
            self.logger.error("Error while interpreting profile: %s" % e)
    
    def shutdown( self ):
        """
        Stop invoked keycodes and stop them
        """
        for invoked in self.invoked.values():
            for i in invoked:
                i.stop()

    def keycode( self, mapping, keycode ):
        """
        The method maps the incoming keycode and mapping to the associated
        XInput L{Event} objects. For each event the release event (inverted 
        mapping, same keycode) is calculated and checked, whether we invoked
        the original event previously. If there is one, we call the stop method
        on the event.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        integer
        @param  keycode:        keycode received
        @type   keycode:        integer
        """
        self.logger.debug( 'Keycode: %i, Mapping: %i' % ( keycode, mapping ) )
        event_tuple = ( keycode, mapping )

        if mapping == 0:
            release_event_tuple = ( keycode, 1)
        elif mapping == 1:
            release_event_tuple = ( keycode, 0)

        if release_event_tuple in self.invoked:
            self.logger.debug( 'Stopping invoked XInputEvent' )
            for event in self.invoked[release_event_tuple]:
                event.stop()
            del self.invoked[release_event_tuple]

        if event_tuple in self.actions:
            self.logger.debug( 'Invoked XInputEvent' )
            for entry in self.actions[event_tuple]:
                if not event_tuple in self.invoked:
                    self.invoked[event_tuple] = []
                self.invoked[event_tuple].append( entry )
                entry.activate()

class X11Event( object ): 
    Xdisplay = display.Display()
    XKs = {}
    
    def _init_mouseaxis( self, action ):
        self.type = 'MouseAxisEvent'
        command = lambda stat, dyn: self.Xdisplay.warp_pointer(stat[0] * dyn,
                                                               stat[1] * dyn)
        self.repeat_freq = 10
        self.repeat_func = self.cb_lin_mouse_freq
        
        static = [0, 0]
        
        # TODO: Error check!
        axis = action['map_to']
        
        if "X" in axis:
            static[0] = 1
        if "Y" in axis:
            static[1] = 1
            
        if axis[0] == "-":
            static[0] *= -1
            static[1] *= -1 
        
        self.commands = [( command,
                           static,
                           lambda x, y: self.cb_lin_mouse_step( x, y ) )]

    def _init_mousebutton( self, action):
        """Initialize Mousebutton Commands"""
        self.type = 'MouseButtonEvent'

        command = lambda stat, dyn: xtest.fake_input(self.Xdisplay, 
                                                     stat[0],
                                                     stat[1])
        self.commands = [( command, (X.ButtonPress, action['map_to']), tuple())]
        self.repeat_commands = [
                         ( command, (X.ButtonRelease, action['map_to']), tuple() ),
                         ( command, (X.ButtonPress, action['map_to']), tuple() )
                               ]
        self.cleanup = [( command, (X.ButtonRelease, action['map_to']), tuple())]
            
        if 'repeat_freq' in action:
            self.repeat_freq = int( action['repeat_freq'] )
            if 'repeat_func' in action:
                self.repeat_func = self.cb_lin_mouse_step
            else:
                self.repeat_func = self.cb_const_key

    def _init_keypress( self, action ):
        self.type = 'KeyPressEvent'
        command = lambda stat, dyn: xtest.fake_input(self.Xdisplay, 
                                             stat[0],
                                             stat[1])

        for part in action['map_to'].split( "+" ):
            k = self.XKs[part.lower()]
            k = self.Xdisplay.keysym_to_keycode(k)
            self.commands.append( (command, (X.KeyPress, k), 1 ) )
            self.repeat_commands.append( ( command, (X.KeyPress, k), tuple() ) )
            self.repeat_commands.insert( 0, ( command, 
                                              (X.KeyRelease, k), 
                                              tuple()))
            self.cleanup.insert( 0, ( command, (X.KeyRelease, k), tuple() ) )
            
        if 'repeat_freq' in action:
            self.repeat_freq = int( action['repeat_freq'] )
            self.repeat_func = self.cb_const_key
    
    def __init__( self, parent, action):
        # (keycode,mapping) => [callback_id, calls]
        # dictionaries, for handling repeats and cleanups of repeats
        if not self.XKs:
            for i in dir(XK):
                if i.startswith("XK_") and not callable(i):
                    # pylint: disable-msg=E1101
                    self.XKs[i.lower()[3:]] = XK.__getattribute__(i)
                    # pylint: enable-msg=E1101
        self.logger = logging.getLogger("LBRC.Listener.Event")
        self.repeathandler = []
        self.cleanup = []
        self.commands = []
        self.repeat_freq = 0
        self.repeat_func = lambda x, n: x
        self.repeat_commands = []
        self.type = 'Generic Event'
        self.uinput_dev = None
        self.uinputbridge = None
        if action['type'] == 'mouseaxis':
            self._init_mouseaxis(action)
        elif action['type'] == 'mousebutton':
            self._init_mousebutton(action)
        elif action['type'] == 'key':
            self._init_keypress(action)

    def set_uinput_dev( self, uinput_dev, uinputbridge ):
        self.uinput_dev = uinput_dev
        self.uinputbridge = uinputbridge

    def cb_lin_mouse_freq( self, x, n ):
        """
        linear speed up, stopped at 500 (more can't be handled by the mainloop call back)
        """
        freq = x * ( n * 0.75 +1 )
        if freq > 500:
            freq = 500
        return freq

    def cb_lin_mouse_step( self, x, n):
        """
        length of stepps for mouse movement
        """
        freq = self.cb_lin_mouse_freq( x, n )
        if( freq < 500 ):
            return 2
        else:
            return 3

    def cb_const_key( self, x, n):
        """
        key repeat is only issued, after 1/2 second, after that
        1/20 s
        """
        if n == 0:
            return 2
        return 20

    def _repeater( self ):
        """
        Handle repeats of keystrokes
        """
        repeathandler = self.repeathandler
        repeathandler[1] += 1
        if self.repeat_commands:
            self._send_commands( self.repeat_commands, self.repeat_freq, repeathandler[1] )
        else:
            self._send_commands( self.commands, self.repeat_freq, repeathandler[1] )
        freq = self.repeat_func( self.repeat_freq, repeathandler[1] )
        repeathandler[0] = gobject.timeout_add( int( 1000.0/freq ), self._repeater )
        return False

    def _send_commands( self, commands, freq, calls ):
        """
        Issue the output of the configured events. From the configured frequency,
        passed as C{freq} and the number of calls C{calls}, the param for part
        of the event is calculated, if it is not static.

        The commands are all send into the device and avert that a SYN_REPORT
        event is issued, which flushes the events out.

        @param  commands:   Events to be issued
        @type   commands:   list of list of ints/callables
        @param  freq:       calls per second
        @type   freq:       int
        @param  calls:      calls in this repeat cycle
        @type   calls:      int
        """
        for command in commands:
            param = command[2]
            if callable( param ):
                param = param( freq, calls )
            command[0](command[1], param)
        self.Xdisplay.sync()


    def activate( self ):
        self.logger.debug( "activated: " + self.type )
        self._send_commands( self.commands, 0, 0 )
        if self.repeat_freq:
            self.repeathandler = []
            freq = self.repeat_func( self.repeat_freq, 0 )
            self.repeathandler.append( gobject.timeout_add( int( 1000.0/freq ), self._repeater ) )
            self.repeathandler.append( 0 )

    def stop( self ):
        if self.repeathandler:
            gobject.source_remove( self.repeathandler[0] )
        if self.cleanup:
            self._send_commands( self.cleanup, 0, 0 )


