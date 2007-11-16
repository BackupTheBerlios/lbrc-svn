package LBRC;

import java.util.Vector;
import java.lang.StringBuffer;
import javax.microedition.lcdui.*;
import de.enough.polish.util.ArrayList;
import org.json.*;

class LBRCSenderController implements CommandListener {
	private final static Command exit = new javax.microedition.lcdui.Command("Exit", Command.EXIT, 1);
	private final static Command back = new javax.microedition.lcdui.Command("Back", Command.BACK, 1);

	private LBRC parent;
	LBRCSender sender;
	Display display;
	LBRCShowModule[] displays;
	WaitScreen wait_screen;
	List list_query;
	Vector previous = new Vector();
	
    LBRCSenderController(final LBRC parent) {
		this.parent = parent;
		display = Display.getDisplay(this.parent);
		wait_screen = new WaitScreen();
		displays = new LBRCShowModule[3];
		displays[0] = new LBRCKeyEcho(this, "KeyEcho");
		displays[1] = new LBRCPresentationControl(this, "PresentationControl");
		displays[2] = new LBRCVolumeControl(this, "VolumeControl");
		for(int i=0;i<displays.length; i++) {
			displays[i].addCommand(LBRCSenderController.back);
			displays[i].addCommand(LBRCSenderController.exit);
			displays[i].setCommandListener(this);
		}
		previous.addElement(displays[0]);
		this.sender = null;
    }
    
    public void setConnectionUrl(String url) {
    	wait_screen.setTitle("Connecting ...");
    	wait_screen.setAction("Connecting ...");
    	display.setCurrent(wait_screen);
    	sender = new LBRCSender(this, url);
    }
 
    public void doListQuery(String title, ArrayList entries) {
    	list_query = new List(title, Choice.IMPLICIT);
    	for(int i=0;i<entries.size();i++) {
    		list_query.append(entries.get(i).toString(), null);
    	}
    	list_query.addCommand(back);
    	list_query.setCommandListener(this);
    	previous.addElement(display.getCurrent());
    	display.setCurrent(list_query);
    }
    
    public void doDebug(String function, String message) {
    	if (sender != null) {
    		JSONObject debug_query = new JSONObject();
    		debug_query.put("type", "debugMessage");
    		debug_query.put("level", "debug");
    		debug_query.put("function", function);
    		debug_query.put("message", message);
    		sender.send(debug_query);
    	}
    }
    
    protected void senderReady() {
    	display.setCurrent(displays[0]);
    }
    
	public void commandAction(Command com, Displayable dis) {
		if (com == exit) {
			this.parent.quit();
		} else if (com == back) {
			if (list_query == null) {
				sender.shutdown();
			} else {
				sender.sendListReply(-1);
				list_query = null;
				previousModule();
			}
		} else if (com == List.SELECT_COMMAND) {
			if (list_query != null && display.getCurrent() == list_query) {
				sender.sendListReply(list_query.getSelectedIndex());
				list_query = null;
				previousModule();
			}
		}
	} 
    
    protected void remoteServiceClosed() {
    	this.parent.remoteServiceClosed();
    }
    
    protected void do_alert(String message, int timeout) {
    	this.parent.do_alert(message, timeout);
    }
    
    protected synchronized void handleRequest(JSONObject obj) {
    	try {
		if (obj.getString("type").equals("listQuery")) {
			// TODO: Make sure only one ListRequest is processed at one time
			doListQuery(obj.getString("title"), obj.getJSONArray("list").getArrayList());
		} else if (obj.getString("type").equals("displayControl")) {
			String command = obj.getString("command");
			if ( command.equals("showModule")) {
				showModule(obj.getString("param"));
			} else if (command.equals("previousModule")) {
				previousModule();
			} else if (command.equals("hideModule")) {
				hideModule(obj.getString("param"));
			}
		} else {
				for(int i=0;i<displays.length;i++) {
					try {
						displays[i].handleRequest(obj);
					} catch (Exception e) {
						parent.do_alert("Exception in handleRequest (" + displays[i].name + "): " + e.toString(), 5000); 
					}
				}
		}
    	} catch (Exception e) {
    		parent.do_alert("Exception in main-handleRequest: " + e.toString(), 5000);
    	}
	}
    
    protected void hideModule(String module_name) {
    	synchronized(previous) {
    		doDebug("hideModule", "To Hide Module: " + module_name + " (" + getPreviousList() + ")");
	    	if ( ((LBRCShowModule) display.getCurrent()).name.equals(module_name)) {
	    		doDebug("hideModule", "Found and hiding: " + module_name + " (" + getPreviousList() + ")");
	    		previousModule();
	    	} else {
	    		doDebug("hideModule", "Not Found and going through history: " + module_name + " (" + getPreviousList() + ")");
	    		for(int i = previous.size()-1; i>1; i--) {
	    			if (((LBRCShowModule) previous.elementAt(i)).name.equals(module_name)) {
	    				previous.removeElementAt(i);
	    				break;
	    			}
	    		}
	    	}
    	}
    }
    
    protected void showModule(String module_name) {
    	synchronized(previous) {
	    	Displayable next_display = null;
	    	for(int i=0;i<displays.length;i++) {
	    		if (displays[i].name.equals(module_name)) {
	    			next_display = displays[i];
	    			break;
	    		}
	    	}
	    	if(next_display != null) {
	    		doDebug("showModule", "Showing Module: " + module_name + " (" + getPreviousList() + ")");
	    		previous.addElement(display.getCurrent());
	    		display.setCurrent(next_display);
	    		doDebug("showModule", "Shown Module: " + module_name + " (" + getPreviousList() + ")");
	    	} else {
	    		parent.do_alert("Unknown Module requested - Please report Bug!", 10000);
	    	}
    	}
    }
    
    protected void previousModule() {
    	synchronized(previous) {
    		doDebug("previousModule", "Remove Module: (" + getPreviousList() + ")");
    		display.setCurrent((Displayable) previous.lastElement());
    		if ( previous.size() > 1 ) { 
    			String name = "unknown";
    			try {
    				LBRCShowModule last_element = (LBRCShowModule) previous.lastElement();
    				name = last_element.name;
    			} catch (Exception e) {}
    			previous.removeElementAt(previous.size()-1);
    			doDebug("previousModule", "Removed Module from previous: " + name + " (" + getPreviousList() + ")");
    		}
    	}
    }
    
    private String getPreviousList() {
    	synchronized(previous) {
    		StringBuffer return_string = new StringBuffer(); 
    		for(int i=0; i<previous.size();i++){
    			String name = "unkown";
    			try {
    				LBRCShowModule last_element = (LBRCShowModule) previous.elementAt(i);
    				name = last_element.name;
    			} catch (Exception e){}
    			if (i>0) return_string.append(", ");
    			return_string.append(name);
    		}
    		return return_string.toString();
    	}
    }
}
