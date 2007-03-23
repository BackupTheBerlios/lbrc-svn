package LBRC;

import javax.bluetooth.ServiceRecord;
import javax.microedition.midlet.*;
import javax.microedition.lcdui.*;

public class LBRC extends MIDlet {
	LBRCDeviceSelect device_select;
	Display display;
	LBRCFrame control_frame;
	LBRCBT remoteBT;
    
    public void startApp() {
		this.display = Display.getDisplay(this);
		control_frame = new LBRCFrame(this);
		device_select = new LBRCDeviceSelect(this);
		device_select.show_chooser();
    }

    public void sendKey(int keyCode, byte mapping) {
    	if (remoteBT != null) {
    		remoteBT.sendKey(keyCode, mapping);
    	}
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

	public void set_remote_service(ServiceRecord sr) {
		remoteBT = new LBRCBT(this, 
				   sr.getConnectionURL(0, false));
		display.setCurrent(control_frame);
	}    
    
	public void close_remote_service() {
		remoteBT.shutdown();
		remoteBT = null;
		device_select.show_chooser();
	}
	
    public void quit() {
        destroyApp(false);
        notifyDestroyed();
    }

    public void pauseApp() {}
    public void destroyApp(boolean unconditional) {}

}
