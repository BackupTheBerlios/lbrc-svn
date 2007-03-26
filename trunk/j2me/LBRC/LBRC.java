package LBRC;

import javax.bluetooth.ServiceRecord;
import javax.microedition.midlet.*;
import javax.microedition.lcdui.*;

public class LBRC extends MIDlet {
	LBRCDeviceSelect device_select;
	LBRCSenderController control_frame;
	Display display;

    
    public void startApp() {
		this.display = Display.getDisplay(this);
		control_frame = new LBRCSenderController(this);
		device_select = new LBRCDeviceSelect(this);
		device_select.show_chooser();
		device_select.FindDevices();
    }

    public void do_alert(String msg,int time_out){
        if (display.getCurrent() instanceof Alert ){
            ((Alert)display.getCurrent()).setString(msg);
            ((Alert)display.getCurrent()).setTimeout(time_out);
        }else{
            Alert alert = new Alert("LBRC");
            alert.setString(msg);
            alert.setTimeout(time_out);
            display.setCurrent(alert);
        }
    }

	public void connect_remote_service(ServiceRecord sr) {
		control_frame.set_connection_url(sr.getConnectionURL(0, false));
		display.setCurrent(control_frame);
	}    
    
	public void remoteServiceClosed() {
		device_select.show_chooser();
	}
	
    public void quit() {
        destroyApp(false);
        notifyDestroyed();
    }

    public void pauseApp() {}
    public void destroyApp(boolean unconditional) {}

}
