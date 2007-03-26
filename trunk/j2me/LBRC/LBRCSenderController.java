package LBRC;

import javax.microedition.lcdui.*;

class LBRCSenderController extends Canvas  implements CommandListener {
	private final static Command exit = new javax.microedition.lcdui.Command("Exit", Command.EXIT, 1);
	private final static Command back = new javax.microedition.lcdui.Command("Back", Command.BACK, 1);
	private String pressedKeyName = "No key pressed";
	private int pressedKey = 0;
	private LBRC parent;
	LBRCSender sender;
	
    LBRCSenderController(final LBRC parent) {
		this.parent = parent;
		this.addCommand(LBRCSenderController.back);
		this.addCommand(LBRCSenderController.exit);
		this.setCommandListener(this);
		this.sender = null;
    }
    
    public void set_connection_url(String url) {
    	this.sender = new LBRCSender(this, url);
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
			this.sender.shutdown();
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
