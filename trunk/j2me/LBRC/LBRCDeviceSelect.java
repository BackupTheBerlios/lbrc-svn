package LBRC;

import javax.bluetooth.DataElement;
import javax.bluetooth.DeviceClass;
import javax.bluetooth.DiscoveryAgent;
import javax.bluetooth.DiscoveryListener;
import javax.bluetooth.LocalDevice;
import javax.bluetooth.RemoteDevice;
import javax.bluetooth.ServiceRecord;
import javax.bluetooth.UUID;
import javax.microedition.lcdui.Choice;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.List;
import javax.microedition.lcdui.Displayable;

public class LBRCDeviceSelect  implements CommandListener, DiscoveryListener {
	LBRC parent;
	WaitScreen wait_screen;
	List dev_list;
	List serv_list;
	Command exit;
	Command back;
	Command scan;
	Display display;
	java.util.Vector devices;
	java.util.Vector services;
	LocalDevice local;
	DiscoveryAgent agent;
	int state;
	int search;
	
	public LBRCDeviceSelect(LBRC parent) {
		this.parent = parent;
		this.state = 0;
		this.search = 0;
		wait_screen = new WaitScreen();
		display = Display.getDisplay(this.parent);
		dev_list = new List("LBRC - Devices", Choice.IMPLICIT);
		exit = new Command("Exit", Command.EXIT, 1);
		back = new Command("Back", Command.BACK, 1);
		scan = new Command("Scannen", Command.OK, 1);
		
		wait_screen.addCommand(back);
		wait_screen.setCommandListener(this);
		dev_list.addCommand(exit);
		dev_list.addCommand(scan);
		dev_list.setCommandListener(this);
	}
	
	public void show_chooser() {
		this.display.setCurrent(this.dev_list);
	}
	
	public void commandAction(Command com, Displayable dis) {
		if (com == back) {
			this.display.setCurrent(dev_list);
			try {
			if (this.state == 1) {
				local = LocalDevice.getLocalDevice();
				agent = local.getDiscoveryAgent();
				agent.cancelInquiry(this);
			}
			if (this.state == 2){
				local = LocalDevice.getLocalDevice();
				agent = local.getDiscoveryAgent();
				agent.cancelServiceSearch(this.search);
			}
			} catch (javax.bluetooth.BluetoothStateException e) {
				
			}
		}
		if (com == exit) {
			this.parent.destroyApp(false);
			this.parent.notifyDestroyed();
		}
		if (com == scan) {
			FindDevices();
		}
		if (com == List.SELECT_COMMAND) {
			if (dis == dev_list) {
				if (dev_list.getSelectedIndex() >= 0) {
					int[] attributes = { 0x100 }; // the name of the service
					UUID[] uuids = new UUID[1];
					uuids[0] = new UUID(0x1002); // browsable services
					FindServices( attributes,
							      uuids, 
							      (RemoteDevice) devices.elementAt(dev_list.getSelectedIndex()
							     ));
					wait_screen.setTitle("LBRC - Inquiery");
					wait_screen.setAction("Checking for service");
					this.display.setCurrent(wait_screen);
				}
			}
		}
	}
	public void FindDevices() {
		wait_screen.setTitle("LBRC - Scan");
		wait_screen.setAction("Scanning for devices");
		this.display.setCurrent(wait_screen);
		try {
			devices = new java.util.Vector();
			LocalDevice local = LocalDevice.getLocalDevice();
			DiscoveryAgent agent = local.getDiscoveryAgent();
			agent.startInquiry(DiscoveryAgent.GIAC, this);
			this.state = 1;
		} catch (Exception e) {
			this.parent.do_alert("Error in initiating search", 4000);
		}
	}

	public void FindServices(int[] attributes, UUID[] uuids, RemoteDevice device) {
		try {
			services = new java.util.Vector();
			local = LocalDevice.getLocalDevice();
			agent = local.getDiscoveryAgent();
			this.search = agent.searchServices(attributes, uuids, device, this);
			this.state = 2;
		} catch (Exception e) {
			this.parent.do_alert("Error in initiating search", 4000);
		}
	}

	public void deviceDiscovered(RemoteDevice remoteDevice,
			DeviceClass deviceClass) {
		devices.addElement(remoteDevice);
	}

	public void servicesDiscovered(int transID, ServiceRecord[] serviceRecord) {
		for (int x = 0; x < serviceRecord.length; x++)
			services.addElement(serviceRecord[x]);
	}

	public void inquiryCompleted(int param) {
		switch (param) {
		case DiscoveryListener.INQUIRY_COMPLETED: // Inquiry completed normally
			this.dev_list.deleteAll();
			for (int x = 0; x < devices.size(); x++)
				try {
					String device_name = ((RemoteDevice) devices.elementAt(x))
							.getFriendlyName(false);
					this.dev_list.append(device_name, null);
				} catch (Exception e) {
					this.parent.do_alert("Error in adding devices", 4000);
				}
			break;
		case DiscoveryListener.INQUIRY_ERROR: // Error during inquiry
			this.parent.do_alert("Inquiry error", 4000);
			break;
		case DiscoveryListener.INQUIRY_TERMINATED: // Inquiry terminated by
													// agent.cancelInquiry()
			//this.parent.do_alert("Inqury Canceled", 4000);
			break;
		}
		state = 0;
		display.setCurrent(dev_list);
	}

	public void serviceSearchCompleted(int transID, int respCode) {
		state = 0;
		display.setCurrent(dev_list);
		switch (respCode) {
		case DiscoveryListener.SERVICE_SEARCH_COMPLETED:
			for (int x = 0; x < services.size(); x++)
				try {
					ServiceRecord sr = (ServiceRecord) services.elementAt(x);
					DataElement ser_de = sr.getAttributeValue(0x100);
					String service_name = (String) ser_de.getValue();
					if (service_name.equals("LBRC")) {
						this.parent.set_remote_service(sr);
						break;
					}
				} catch (Exception e) {
					this.parent.do_alert("Error in adding services ", 1000);
				}
			break;
		case DiscoveryListener.SERVICE_SEARCH_DEVICE_NOT_REACHABLE:
			this.parent.do_alert("Device not Reachable", 4000);
			break;
		case DiscoveryListener.SERVICE_SEARCH_ERROR:
			this.parent.do_alert("Service serch error", 4000);
			break;
		case DiscoveryListener.SERVICE_SEARCH_NO_RECORDS:
			this.parent.do_alert("LBRC Service not found!", 4000);
			break;
		case DiscoveryListener.SERVICE_SEARCH_TERMINATED:
			//this.parent.do_alert("Inqury Cancled", 4000);
			break;
		}
	}
	
}