package LBRC;

import javax.microedition.lcdui.*;
import de.enough.polish.util.ArrayList;
import org.json.*;
import org.json.text.ParseException;

class LBRCSenderController implements CommandListener {
	private final static Command exit = new javax.microedition.lcdui.Command("Exit", Command.EXIT, 1);
	private final static Command back = new javax.microedition.lcdui.Command("Back", Command.BACK, 1);

	private LBRC parent;
	LBRCSender sender;
	Display display;
	LBRCKeyEcho key_echo;
	LBRCPresentationCompanion presentation_editor;
	WaitScreen wait_screen;
	List list_query;
	Displayable previous;
	
    LBRCSenderController(final LBRC parent) {
		this.parent = parent;
		display = Display.getDisplay(this.parent);
		wait_screen = new WaitScreen();
		key_echo = new LBRCKeyEcho(this);
		key_echo.addCommand(LBRCSenderController.back);
		key_echo.addCommand(LBRCSenderController.exit);
		key_echo.setCommandListener(this);
		presentation_editor = new LBRCPresentationCompanion(this);
		presentation_editor.addCommand(LBRCSenderController.back);
		presentation_editor.addCommand(LBRCSenderController.exit);
		presentation_editor.setCommandListener(this);		
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
    	previous = display.getCurrent();
    	display.setCurrent(list_query);
    }
    
    protected void senderReady() {
    	display.setCurrent(key_echo);
    }
    
	public void commandAction(Command com, Displayable dis) {
		if (com == exit) {
			this.parent.quit();
		}
		if (com == back) {
			if (display.getCurrent() == key_echo || display.getCurrent() == presentation_editor) {
				sender.shutdown();
			}
			if (list_query != null && display.getCurrent() == list_query) {
				sender.sendListReply(-1);
				display.setCurrent(key_echo);
				list_query = null;
			}
		}
		if (com == List.SELECT_COMMAND) {
			if (list_query != null && display.getCurrent() == list_query) {
				sender.sendListReply(list_query.getSelectedIndex());
				display.setCurrent(previous);
				previous = null;
				list_query = null;
			}
		}
	} 
    
    protected void remoteServiceClosed() {
    	this.parent.remoteServiceClosed();
    }
    
    protected void do_alert(String message, int timeout) {
    	this.parent.do_alert(message, timeout);
    }
    
    protected void handleRequest(JSONObject obj) {
		if (obj.getString("type").equals("listQuery")) {
			// TODO: Make sure only one ListRequest is processed at one time
			doListQuery(obj.getString("title"), obj.getJSONArray("list").getArrayList());
		} else if (obj.getString("type").equals("presentationControl") ) {
			if (obj.getString("command").equals("showModule")) {
				display.setCurrent(presentation_editor);
			} else if (obj.getString("command").equals("hideModule")) {
				display.setCurrent(key_echo);
			} else if (obj.getString("command").equals("changeSlide")) {
				presentation_editor.change_slide(obj.getInt("param"));
			} else if (obj.getString("command").equals("setSlide")) {
				presentation_editor.set_slide(obj.getInt("param"));
			}
		}
			
	}
}
