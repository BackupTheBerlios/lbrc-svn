package LBRC;

import java.io.*;
import javax.bluetooth.*;
import javax.microedition.lcdui.Choice;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.List;
import javax.microedition.lcdui.Displayable;

public class LBRCDeviceSelect  implements CommandListener, DiscoveryListener {
	private final static Command exit = new javax.microedition.lcdui.Command("Exit", Command.EXIT, 1);
	private final static Command back = new javax.microedition.lcdui.Command("Back", Command.BACK, 1);
	private final static Command scan = new javax.microedition.lcdui.Command("Find Devices", Command.OK, 1);
	LBRC parent;
	WaitScreen waitScreen;
	List deviceDisplayList;
	Display display;
	java.util.Vector devices;
	java.util.Vector services;
	LocalDevice local;
	DiscoveryAgent agent;
	//final private UUID lbrc_uuid = new UUID("9c6c8dce954511dca3c10011d8388a56", false);
	int state;
	int search;
	
	public LBRCDeviceSelect(LBRC parent) {
		this.parent = parent;
		this.state = 0;
		this.search = 0;
		devices = new java.util.Vector();
		waitScreen = new WaitScreen();
		display = Display.getDisplay(this.parent);
		deviceDisplayList = new List("LBRC - Devices", Choice.IMPLICIT);
		
		waitScreen.addCommand(back);
		waitScreen.setCommandListener(this);
		deviceDisplayList.addCommand(exit);
		deviceDisplayList.addCommand(scan);
		deviceDisplayList.setCommandListener(this);
		
		try {
			LocalDevice local = LocalDevice.getLocalDevice();
			DiscoveryAgent agent = local.getDiscoveryAgent();
			
			RemoteDevice[] btdevices = agent.retrieveDevices(DiscoveryAgent.PREKNOWN);
			
			if (btdevices != null) {
				for (int x = 0; x < btdevices.length; x++) {
					devices.addElement(btdevices[x]);
					String device_name = "";
					try {
						device_name = btdevices[x].getFriendlyName(false);
					} catch (IOException ex) {}
					if (device_name.equals(""))
						device_name = "Unkown: " + btdevices[x].getBluetoothAddress();
					this.deviceDisplayList.append(device_name, null);
				}
			}
		} catch (BluetoothStateException ex) {}
		devices.addElement(null);
		this.deviceDisplayList.append("[Find Devices]", null);
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
					RemoteDevice dev = (RemoteDevice) devices.elementAt(deviceDisplayList.getSelectedIndex());
					int[] attributes = { 0x0000, 0x0001, 0x0004, 0x0100 };
					UUID[] uuids = new UUID[]{ new UUID(0x0003) };
					if (dev != null) {
						FindServices( attributes, uuids, dev);
						waitScreen.setTitle("LBRC - Inquiery");
						waitScreen.setAction("Checking for service");
						this.display.setCurrent(waitScreen);
					} else {
						FindDevices();
					}
				}
			}
		}
	}
	
	public void FindDevices() {
		waitScreen.setTitle("LBRC - Scan");
		waitScreen.setAction("Searching for devices");
		this.display.setCurrent(waitScreen);
		devices.removeAllElements();
		try {
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
			for (int x = 0; x < devices.size(); x++) {
				String device_name = "";
				RemoteDevice dev = (RemoteDevice) devices.elementAt(x);
				try {
					device_name = dev.getFriendlyName(false);
				} catch (IOException ex) {};
				if (device_name.equals(""))
					device_name = "Unkown: " + dev.getBluetoothAddress();
				this.deviceDisplayList.append(device_name, null);
			}
			devices.addElement(null);
			this.deviceDisplayList.append("[Find Devices]", null);
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
				// Do nothing!
				break;
			case DiscoveryListener.SERVICE_SEARCH_DEVICE_NOT_REACHABLE:
				this.parent.do_alert("Device not Reachable", 4000);
				break;
			case DiscoveryListener.SERVICE_SEARCH_ERROR:
				this.parent.do_alert("Service serch error", 4000);
				break;
			case DiscoveryListener.SERVICE_SEARCH_NO_RECORDS:
				this.parent.do_alert("LBRC Service not found! Length of " + 
						             "service list: " + services.size(), 4000);
				break;
			case DiscoveryListener.SERVICE_SEARCH_TERMINATED:
				this.parent.do_alert("Inqury Canceled", 4000);
				break;
			default:
				this.parent.do_alert("Unknown Response on Service search", 4000);
				break;
		}
		for (int x = 0; x < services.size(); x++) {
			ServiceRecord sr = (ServiceRecord) services.elementAt(x);

			String name = (String) sr.getAttributeValue(0x0100).getValue();
			if (name.equals("LBRC")) {
				this.parent.connectRemoteService(sr);
				break;
			}
		}
	}
	
}