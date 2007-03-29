package LBRC;

import javax.microedition.lcdui.*;

import de.enough.polish.util.ArrayList;

class LBRCSenderController extends Canvas  implements CommandListener {
	private final static Command exit = new javax.microedition.lcdui.Command("Exit", Command.EXIT, 1);
	private final static Command back = new javax.microedition.lcdui.Command("Back", Command.BACK, 1);
	private String pressedKeyName = "No key pressed";
	private int pressedKey = 0;
	private LBRC parent;
	LBRCSender sender;
	Display display;
	WaitScreen wait_screen;
	List list_query;
	
    LBRCSenderController(final LBRC parent) {
		this.parent = parent;
		display = Display.getDisplay(this.parent);
		wait_screen = new WaitScreen();
		this.addCommand(LBRCSenderController.back);
		this.addCommand(LBRCSenderController.exit);
		this.setCommandListener(this);
		this.sender = null;
    }
    
    public void setConnectionUrl(String url) {
    	wait_screen.setTitle("Connecting ...");
    	wait_screen.setAction("");
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
    	display.setCurrent(list_query);
    }
    
    protected void senderReady() {
    	display.setCurrent(this);
    }
    
    protected void keyPressed(final int keyCode) {
    	if (sender != null) {
    		pressedKeyName = getKeyName(keyCode);
    		pressedKey = keyCode;
    		sender.sendKey(keyCode, 0);
    		repaint();
    	}
    }
    
    protected void keyReleased(final int keyCode) {
    	if (sender != null) {
    		pressedKeyName = getKeyName(keyCode);
    		pressedKey = keyCode;
    		sender.sendKey(keyCode, 1);
    		repaint();
    	}
    }
    
	public void commandAction(Command com, Displayable dis) {
		if (com == exit) {
			this.parent.quit();
		}
		if (com == back) {
			if (display.getCurrent() == this) sender.shutdown();
			if (list_query != null && display.getCurrent() == list_query) {
				sender.sendListReply(-1);
				display.setCurrent(this);
				list_query = null;
			}
		}
		if (com == List.SELECT_COMMAND) {
			if (list_query != null && display.getCurrent() == list_query) {
				sender.sendListReply(list_query.getSelectedIndex());
				display.setCurrent(this);
				list_query = null;
			}
		}
	} 
    
    protected void paint(Graphics g) {
		g.setColor(255, 255, 255);
		g.fillRect(0, 0, getWidth(), getHeight());
		int width = g.getClipWidth() - g.getClipX();
		int height = g.getClipHeight() - g.getClipY();
		try {
			Image image = Image.createImage("/res/Blue.png");
			g.drawImage(image, width - 5, height - 5, Graphics.BOTTOM | Graphics.RIGHT);
		} catch (Exception e) {
		}
		g.setColor(0, 0, 0);
		Font f = g.getFont();
		int offset = f.stringWidth(" ");
		String key1 = "Keypress: " + pressedKeyName;
		String key2 = "KeyCode: " + Integer.toString(pressedKey);
		g.drawString(key1, offset, f.getHeight() / 2, Graphics.TOP| Graphics.LEFT);
		g.drawString(key2, offset, f.getHeight() * 2, Graphics.TOP| Graphics.LEFT);
	}
    
    protected void remoteServiceClosed() {
    	this.parent.remoteServiceClosed();
    }
    
    protected void do_alert(String message, int timeout) {
    	this.parent.do_alert(message, timeout);
    }
}
