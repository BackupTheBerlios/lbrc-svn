import javax.microedition.midlet.*;
import javax.microedition.lcdui.*;
import javax.bluetooth.*;

public class LBRC extends MIDlet implements CommandListener,DiscoveryListener  {
    List main_list;
    List dev_list;
    List serv_list;
    Command exit;
    Command back;
    Display display;
    java.util.Vector devices;
    java.util.Vector services;
    LocalDevice local;
    DiscoveryAgent agent;
    LBRCFrame frame;
    LBRCBT remoteBT;
    
    public void startApp() {
        main_list = new List("Select Operation",Choice.IMPLICIT);   //the main menu
        dev_list  = new List("Select Device",Choice.IMPLICIT);      //the list of devices
        serv_list = new List("Available Services",Choice.IMPLICIT); //the list of services
        exit      = new Command("Exit",Command.EXIT,1);
        back      = new Command("Back",Command.BACK,1);
        display   = Display.getDisplay(this);

        main_list.addCommand(exit);
        main_list.setCommandListener(this);
        dev_list.addCommand(exit);
        dev_list.setCommandListener(this);
        serv_list.addCommand(exit);
        serv_list.addCommand(back);
        serv_list.setCommandListener(this);

        main_list.append("Find Devices",null);
        display.setCurrent(main_list);
    }

    public void sendKey(int keyCode, byte mapping) {
        remoteBT.sendKey(keyCode, mapping);
    }

    public void commandAction(Command com, Displayable dis) {
        if (com == exit){                                              //exit triggered from the main form
            destroyApp(false);
            notifyDestroyed();
        }
        if (com == List.SELECT_COMMAND){
            if (dis == main_list){                                     //select triggered from the main from
                if (main_list.getSelectedIndex() >= 0){                //find devices
                    FindDevices();
                    do_alert("Searching for devices...", Alert.FOREVER);
                }
            }
            if (dis == dev_list){                                       //select triggered from the device list
                if (dev_list.getSelectedIndex() >= 0){                  //find services
                    int[] attributes = {0x100};                         //the name of the service
                    UUID[] uuids     = new UUID[1];
                    uuids[0]         = new UUID(0x1002);                //browsable services
                    FindServices(attributes,uuids,
                            (RemoteDevice)devices.elementAt(dev_list.getSelectedIndex()));
                    do_alert("Inquiring device for services...", Alert.FOREVER);
                }
            }

         }
        if (com == back){
            if (dis == serv_list){                                    //back button is pressed in devices list
                display.setCurrent(dev_list);
            }
        }

    }
    public void FindDevices(){
        try {
            devices              = new java.util.Vector();
            LocalDevice local    = LocalDevice.getLocalDevice();
            DiscoveryAgent agent = local.getDiscoveryAgent();
            agent.startInquiry(DiscoveryAgent.GIAC,this);
        } catch(Exception e) {
            this.do_alert("Error in initiating search" , 4000);
        }
     }
         
    public void FindServices(int[] attributes, UUID[] uuids, RemoteDevice device){
        try{
            services = new java.util.Vector();
            local    = LocalDevice.getLocalDevice();
            agent    = local.getDiscoveryAgent();
            serv_list.deleteAll();                                 //empty the list of services
                                                                   //in case user has pressed back
            agent.searchServices(attributes,uuids,device,this);            
        } catch(Exception e) {
            this.do_alert("Error in initiating search" , 4000);
        }
    }
        
    public void deviceDiscovered(RemoteDevice remoteDevice,DeviceClass deviceClass) {
        devices.addElement(remoteDevice);
    }

    public void servicesDiscovered(int transID,ServiceRecord[] serviceRecord) {
        for (int x = 0; x < serviceRecord.length; x++ )
            services.addElement(serviceRecord[x]);
    }

    public void inquiryCompleted(int param){
        switch (param) {
            case DiscoveryListener.INQUIRY_COMPLETED:    //Inquiry completed normally
                for(int x = 0; x < devices.size(); x++ )
                    try{
                        String device_name = ((RemoteDevice)devices.elementAt(x)).getFriendlyName(false);
                        this.dev_list.append(device_name , null);
                        display.setCurrent(dev_list);
                    } catch (Exception e) {
                        do_alert("Error in adding devices",4000);
                    }
            break;
            case DiscoveryListener.INQUIRY_ERROR:       // Error during inquiry
                this.do_alert("Inqury error" , 4000);
            break;
            case DiscoveryListener.INQUIRY_TERMINATED:  // Inquiry terminated by agent.cancelInquiry()
                this.do_alert("Inqury Canceled" , 4000);
            break;
        }
    }
        
    public void serviceSearchCompleted(int transID, int respCode) {
        switch(respCode) {
            case DiscoveryListener.SERVICE_SEARCH_COMPLETED:
                for(int x = 0; x < services.size(); x++ )
                    try{
                        ServiceRecord sr = (ServiceRecord)services.elementAt(x);
                        DataElement ser_de  = sr.getAttributeValue(0x100);
                        String service_name = (String)ser_de.getValue(); 
                        if(service_name.equals("LBRC")) {
                            frame = new LBRCFrame(this);
                            frame.addCommand(exit);
                            frame.setCommandListener(this);
                            remoteBT =  new LBRCBT(this, sr.getConnectionURL(0, false));
                            display.setCurrent(frame);
                            break;
                        }
                    } catch (Exception e){
                        do_alert("Error in adding services " ,1000);
                    }
            break;
            case DiscoveryListener.SERVICE_SEARCH_DEVICE_NOT_REACHABLE:
                this.do_alert("Device not Reachable" , 4000);
            break;
            case DiscoveryListener.SERVICE_SEARCH_ERROR:
                this.do_alert("Service serch error" , 4000);
            break;
            case DiscoveryListener.SERVICE_SEARCH_NO_RECORDS:
                this.do_alert("No records returned" , 4000);
            break;
            case DiscoveryListener.SERVICE_SEARCH_TERMINATED:
                this.do_alert("Inqury Cancled" , 4000);
            break;
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

    public void quit() {
        destroyApp(false);
        notifyDestroyed();
    }

    public void pauseApp() {}
    public void destroyApp(boolean unconditional) {}

}
