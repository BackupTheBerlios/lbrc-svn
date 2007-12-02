package LBRC;

import javax.microedition.lcdui.*;

public abstract class LBRCShowModuleCanvas extends Canvas implements LBRCRequestHandler, LBRCShowModule {
	public String name;
	LBRCSenderController parent;
	
	public LBRCShowModuleCanvas(LBRCSenderController parent, String name) {
		this.parent = parent;
		this.name = name; 
	}
	
    public void keyPressed(final int keyCode) {
    	if (parent.sender != null) {
    		parent.sender.sendKey(keyCode, 0);
    		repaint();
    	}
    }
    
    public void keyReleased(final int keyCode) {
    	if (parent.sender != null) {
    		parent.sender.sendKey(keyCode, 1);
    		repaint();
    	}
    }
    
    public String getName() {
    	return this.name; 
    }
}