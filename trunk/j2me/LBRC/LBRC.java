package LBRC;

import javax.bluetooth.ServiceRecord;
import javax.microedition.midlet.*;
import javax.microedition.lcdui.*;

public class LBRC extends MIDlet {
	LBRCDeviceSelect deviceSelect;
	LBRCSenderController interactiveControl;
	Display display;

    public void startApp() {
    	this.display = Display.getDisplay(this);
    	try {
			interactiveControl = new LBRCSenderController(this);
    	}catch (Exception e) {
    		do_alert("Exception in initializing SenderController" + e.toString(), 20000);
    	}
    	try {
			deviceSelect = new LBRCDeviceSelect(this);
			deviceSelect.showChooser();
			//deviceSelect.FindDevices();
    	}catch (Exception e) {
    		do_alert("Exception in Deviceselect: " + e.toString(), 20000);
    	}
    }

    public synchronized void do_alert(String msg,int time_out){
        Alert alert = new Alert("LBRC");
        alert.setString(msg);
        alert.setTimeout(time_out);
        display.setCurrent(alert);
    	try { Thread.sleep(time_out); } catch (Exception f) {};
    }

	public void connectRemoteService(ServiceRecord sr) {
		interactiveControl.setConnectionUrl(sr.getConnectionURL(0, false));
	}    
    
	public void remoteServiceClosed() {
		deviceSelect.showChooser();
	}
	
    public void quit() {
        destroyApp(false);
        notifyDestroyed();
    }

    public void pauseApp() {}
    public void destroyApp(boolean unconditional) {}

}
