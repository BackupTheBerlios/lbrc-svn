import os, struct, fcntl, time
import os.path as osp
import logging
import gobject
import dbus
import dbus.glib
import time
import LBRC.consts as co
from LBRC import dinterface
from LBRC.config import configValueNotFound
from LBRC.path import path
from LBRC.Listener import Listener

class UinputServiceStartException(Exception): pass

class UinputDispatcher( Listener ):
    """
    The UinputDispatcher translates keycodes from the phone into input events, that are
    injected into the kernel. When the class is instanciated, the uinput device is opened
    and the kernel creates the corresponding device node. Additionally the events are
    also fed into the global event sind /dev/input/events (or where ever the distribution
    descides to place this).
    """
    def __init__( self, config ):
        """
        The method initialises the uinput device and prior to that creates the eventsmap
        from the profiledata. In this process all uinput events are recorded and the
        corresponding eventmasks are set on the uinput device. This means, that all
        uinput events, from any profile have to be present at this point!

        @param  config:         configuration data
        @type   config:         dictionary
        """
        Listener.__init__(self, config, "UInputDispatcher")
        
        self.path = path()
        
        self.invoked = {}
        
        self.uinput_dev = None
        self.uinputbridge = None
        
        self._start_uinput_bridge()
        self._open_uinput_dev()

    def _start_uinput_bridge(self):
        db = dinterface(dbus.SessionBus(), "org.freedesktop.DBus", "/", "org.freedesktop.DBus")
        if not "org.uinputbridge" in db.ListNames() and \
           not "org.uinputbridge" in db.ListActivatableNames():
            gobject.spawn_async([self.path.get_binfile("uinputbridge")],
                                flags=gobject.SPAWN_STDOUT_TO_DEV_NULL | 
                                      gobject.SPAWN_STDERR_TO_DEV_NULL )
            count = 0
            while count < 10:
                count += 1
                if "org.uinputbridge" in db.ListNames():
                    count = 11
                time.sleep(1)
            if count == 10:
                raise UinputServiceStartException()
        self.uinputbridge = dinterface(dbus.SessionBus(), "org.uinputbridge", "/UInputBridge", "org.uinputbridge")

    def _open_uinput_dev( self ):
        """
        We switched from the direct opening of the device to the dbus<->uinput bridge,
        that does the initialisation for us
        """
        device_file = None
        for location in self.config.get_config_item('uinpt-device'):
            if self._check_uinput_dev(location):
                device_file = location
        if not device_file:
            device_file = self._guess_uinput_dev()
        self.uinput_dev = self.uinputbridge.SetupDevice(device_file, 
                                                        "Linux Bluetooth Remote Control", 
                                                        dbus.UInt16(co.input["BUS_BLUETOOTH"]))
 
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
        self._interpret_profile( config, profile )
    
    def shutdown( self ):
        for invoked in self.invoked.values():
            for i in invoked:
                i.stop()
        self.uinputbridge.CloseDevice(self.uinput_dev)

    def _interpret_profile( self, config, profile ):
        """
        Interpret the data from the profile and create appropriate uinput events for each
        configure keycode/mapping tuple in the config an array is created, that holds
        L{Event} objects, that are called, then the corresponding keycode/mapping tuple
        is activated
        
        @param    config:    Source of the profile (system or user)
        @type     config:    String
        @param    profile:   ID of the currently selected Profile
        @type     profile:   String
        """
        self.logger.debug("_interpret_profile(%s, %s)" % ( config, profile ) )
        
        self.init = []
        self.actions = {}
        self.destruct = []

        _actions = None

        try:
            _actions = self.config.get_profile( config, profile, 'UinputDispatcher')['actions']
        except KeyError:
            self.logger.debug("actions section not found")
        except configValueNotFound:
            self.logger.debug("Error fetching config section for %s profile from %s config" % (config, profile))
            
        if _actions:
            for action in _actions:
                self.logger.debug( str( action ) )
                event_tuple = ( int( action['keycode'] ), 0 )
                if not self.actions.has_key( event_tuple ):
                    self.actions[event_tuple] = []
                event = None
                if action['type'] == 'mouseaxis':
                    event = MouseAxisEvent( action ) 
                elif action['type'] == 'mousewheel':
                    event = MouseWheelEvent( action )
                elif action['type'] == 'mousebutton':
                    event = MouseButtonEvent( action )
                elif action['type'] == 'key':
                    event = KeyPressEvent( action )
                event.set_uinput_dev( self.uinput_dev, self.uinputbridge )
                self.actions[event_tuple].append(event)
        else:
            self.logger.debug("No actions were defined")

    def keycode( self, mapping, keycode ):
        """
        The method maps the incoming keycode and mapping to the associated
        uinput L{Event} objects. For each event the release event (inverted mapping,
        same keycode) is calculated and checked, whether we invoked the original
        event previously. If there is one, we call the stop method on the event.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        integer
        @param  keycode:        keycode received
        @type   keycode:        integer
        """
        self.logger.debug( 'Keycode: %i, Mapping: %i' % ( keycode, mapping ) )
        event_tuple = ( keycode, mapping )

        if mapping == 0:
            release_event_tuple = ( keycode, 1 )
        elif mapping == 1:
            release_event_tuple = ( keycode, 0 )

        if release_event_tuple in self.invoked:
            self.logger.debug( 'Stopping invoked UinputEvents' )
            for event in self.invoked[release_event_tuple]:
                event.stop()
            del self.invoked[release_event_tuple]

        if event_tuple in self.actions:
            self.logger.debug( 'Invoked UinputEvents' )
            for entry in self.actions[event_tuple]:
                if not event_tuple in self.invoked:
                    self.invoked[event_tuple] = []
                self.invoked[event_tuple].append( entry )
                entry.activate()
    
    @staticmethod
    def _check_uinput_dev(place):
        """
        Check whether an supplied place is suitable as uinput device. That means,
        that we need read and write permissions on it.
        
        @param    place:    a path to a potential uinput device
        @type     place:    String
        """
        # TODO: add check, that we are faced with a device file
        self.logger.debug( 'Examing %s as uinput device' % ( place, ) )
        if osp.exists( place ):
            if not os.access( place, os.R_OK | os.W_OK ):
                self.logger.warning( '%s looks like a uinput device node, but you lack necessary permissions' % ( place, ) )
            else:
                self.logger.debug( 'Asuming we found a suitable uinput device node: %s' % ( place, ) )
                return True
        else:
            self.logger.debug( 'The place does not exist!' )
        return False

    def _guess_uinput_dev(self):
        """
        Find the uinput device in the system

        First this method checks a few well known places and then desperately search whole /dev hierarchy for devices names
        uinput ...

        @return:    Location of the uinput device
        @rtype:     string
        """
        known_places = ['/dev/input/uinput', '/dev/misc/uinput']
        for place in known_places:
            if self._check_uinput_dev(place):
                return place

        self.logger.debug( 'None of the well known places for uinput device was found to be ok, beginning search' )
        possible_places = []
        for root, dirs, files in os.walk( '/dev' ):
            if 'uinput' in files:
                if not osp.join( root, 'uinput' ) in known_places:
                    place = osp.join( root, 'uinput' )
                    if self._check_uinput_dev(place):
                        self.logger.debug( 'Possible device node: %s' % (place, ) )
                        return place
        self.logger.error( 'No device node found, that looks like a uinput device node - is the kernel module loaded?' )

class Event( object ):
    def __init__( self ):
        # (keycode,mapping) => [callback_id, calls]
        # dictionaries, for handling repeats and cleanups of repeats
        self.logger = logging.getLogger("LBRC.Listener.Event")
        self.repeathandler = []
        self.cleanup = []
        self.commands = []
        self.repeat_freq = 0
        self.repeat_func = None
        self.repeat_commands = []
        self.type = 'Generic Event'

    def set_uinput_dev( self, uinput_dev, uinputbridge ):
        self.uinput_dev = uinput_dev
        self.uinputbridge = uinputbridge

    def _lin_mouse_freq( self, x, n ):
        """
        linear speed up, stopped at 500 (more can't be handled by the mainloop call back)
        """
        freq = x * ( n * 0.75 +1 )
        if freq > 500:
            freq = 500
        return freq

    def _lin_mouse_step( self, x, n ):
        """
        length of stepps for mouse movement
        """
        freq = self._lin_mouse_freq( x, n );
        if( freq < 500 ):
            return 2
        else:
            return 3

    def _const_key( self, x, n ):
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
            self.send_event( command[0], command[1], param )
        self.send_event( co.input['EV_SYN'], co.input['SYN_REPORT'], 0 )

    def send_event( self, event, descriptor, param ):
        """
        Output event to the uinput device => pack the correct structure and write to open device
        For the relevant event ids and types please refer to consts.py

        @param  event:      event type
        @type   event:      int
        @param  descriptor: event id
        @type   descriptor: int
        @param  param:      parameter for the event
        @type   param:      int
        """
        self.logger.debug("%i, %i, %i" % ( event, descriptor, param ) )
        self.uinputbridge.SendEvent(self.uinput_dev, event, descriptor, param)
        #os.write( self.uinput_dev, struct.pack( "LLHHl", time.time(), 0, event, descriptor, param ) )

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

class MouseAxisEvent( Event ):
    def __init__( self, action ):
        Event.__init__( self )
        self.type = 'MouseAxisEvent'
        axis = co.input["REL_" + action['map_to'][1:2]]
        direction = action['map_to'][0:1]
        self.repeat_freq = 10
        self.repeat_func = self._lin_mouse_freq
        if direction == "-":
            self.commands = [( co.input['EV_REL'], axis, lambda x, y: -1 * self._lin_mouse_step( x, y ) )]
        else:
            self.commands = [( co.input['EV_REL'], axis, lambda x, y: self._lin_mouse_step( x, y ) )]

class MouseWheelEvent( Event ):
    def __init__( self, action ):
        Event.__init__( self )
        self.type = 'MouseWheelEvent'
        axis = co.input["REL_" + action['map_to'][1:]]
        direction = action['map_to'][0:1]
        self.repeat_freq = int( action['repeat_freq'] )
        self.repeat_func = lambda x, n: x
        if direction == "-":
            self.commands = [( co.input['EV_REL'], axis, -1 )]
        else:
            self.commands = [( co.input['EV_REL'], axis, 1 )]

class MouseButtonEvent( Event ):
    def __init__( self, action ):
        Event.__init__( self )
        self.type = 'MouseButtonEvent'
        bt = co.input["BTN_" + action['map_to']]
        self.commands = [( co.input['EV_KEY'], bt, 1 )]
        self.cleanup = [( co.input['EV_KEY'], bt, 0 )]

class KeyPressEvent( Event ):
    def __init__( self, action ):
        Event.__init__( self )
        self.type = 'KeyPressEvent'
        for part in action['map_to'].split( "+" ):
            k =  co.input["KEY_" + part]
            self.commands.append( ( co.input['EV_KEY'], k, 1 ) )
            self.repeat_commands.append( ( co.input['EV_KEY'], k, 1 ) )
            self.repeat_commands.insert( 0, ( co.input['EV_KEY'], k, 0 ) )
            self.cleanup.insert( 0, ( co.input['EV_KEY'], k, 0 ) )
            
        if 'repeat_freq' in action:
             self.repeat_freq = int( action['repeat_freq'] )
             self.repeat_func = self._const_key
