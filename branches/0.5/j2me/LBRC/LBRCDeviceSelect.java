package LBRC;

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
	private final static Command exit = new javax.microedition.lcdui.Command("Exit", Command.EXIT, 1);
	private final static Command back = new javax.microedition.lcdui.Command("Back", Command.BACK, 1);
	private final static Command scan = new javax.microedition.lcdui.Command("Scannen", Command.OK, 1);
	LBRC parent;
	WaitScreen waitScreen;
	List deviceDisplayList;
	Display display;
	java.util.Vector devices;
	java.util.Vector services;
	LocalDevice local;
	DiscoveryAgent agent;
	final private UUID lbrc_uuid = new UUID("9c6c8dce954511dca3c10011d8388a56", false);
	int state;
	int search;
	
	public LBRCDeviceSelect(LBRC parent) {
		this.parent = parent;
		this.state = 0;
		this.search = 0;
		waitScreen = new WaitScreen();
		display = Display.getDisplay(this.parent);
		deviceDisplayList = new List("LBRC - Devices", Choice.IMPLICIT);
		
		waitScreen.addCommand(back);
		waitScreen.setCommandListener(this);
		deviceDisplayList.addCommand(exit);
		deviceDisplayList.addCommand(scan);
		deviceDisplayList.setCommandListener(this);
	}
	
	public void showChooser() {
		this.display.setCurrent(this.deviceDisplayList);
	}
	
	public void commandAction(Command com, Displayable dis) {
		if (com == back) {
			this.display.setCurrent(deviceDisplayList);
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
			if (dis == deviceDisplayList) {
				if (deviceDisplayList.getSelectedIndex() >= 0) {
					int[] attributes = { 0x100 }; // the name of the service
					UUID[] uuids = new UUID[] {lbrc_uuid};
					//uuids[0] = new UUID(0x1002); // browsable services
					FindServices( attributes,
							      uuids, 
							      (RemoteDevice) devices.elementAt(deviceDisplayList.getSelectedIndex()
							     ));
					waitScreen.setTitle("LBRC - Inquiery");
					waitScreen.setAction("Checking for service");
					this.display.setCurrent(waitScreen);
				}
			}
		}
	}
	
	public void FindDevices() {
		waitScreen.setTitle("LBRC - Scan");
		waitScreen.setAction("Scanning for devices");
		this.display.setCurrent(waitScreen);
		try {
			devices = new java.util.Vector();
			LocalDevice local = LocalDevice.getLocalDevice();
			DiscoveryAgent agent = local.getDiscoveryAgent();
			agent.startInquiry(DiscoveryAgent.GIAC, this);
			this.state = 1;
		} catch (Exception e) {
			this.parent.do_alert("Error starting search - Bluetooth not enabled?", 5000);
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
			this.deviceDisplayList.deleteAll();
			for (int x = 0; x < devices.size(); x++)
				try {
					String device_name = ((RemoteDevice) devices.elementAt(x))
							.getFriendlyName(false);
					this.deviceDisplayList.append(device_name, null);
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
		display.setCurrent(deviceDisplayList);
	}

	public void serviceSearchCompleted(int transID, int respCode) {
		state = 0;
		display.setCurrent(deviceDisplayList);
		switch (respCode) {
		case DiscoveryListener.SERVICE_SEARCH_COMPLETED:
			for (int x = 0; x < services.size(); x++) {
				ServiceRecord sr = (ServiceRecord) services.elementAt(x);
				this.parent.connectRemoteService(sr);
				break;
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
			this.parent.do_alert("Inqury Canceled", 4000);
			break;
		default:
			this.parent.do_alert("Unknown Response on Service search", 4000);
			break;
		}
	}
	
}