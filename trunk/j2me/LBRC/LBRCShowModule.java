package LBRC;

import javax.microedition.lcdui.*;

public abstract class LBRCShowModule extends Canvas implements LBRCRequestHandler {
	public String name;
	LBRCSenderController parent;
	
	public LBRCShowModule(LBRCSenderController parent, String name) {
		this.parent = parent;
		this.name = name; 
	}
	
    protected void keyPressed(final int keyCode) {
    	if (parent.sender != null) {
    		parent.sender.sendKey(keyCode, 0);
    		repaint();
    	}
    }
    
    protected void keyReleased(final int keyCode) {
    	if (parent.sender != null) {
    		parent.sender.sendKey(keyCode, 1);
    		repaint();
    	}
    }
}