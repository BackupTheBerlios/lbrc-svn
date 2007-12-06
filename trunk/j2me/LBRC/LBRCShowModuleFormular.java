package LBRC;

import javax.microedition.lcdui.*;

public abstract class LBRCShowModuleFormular extends Form implements LBRCRequestHandler, LBRCShowModule {
	public String name;
	LBRCSenderController parent;
	
	public LBRCShowModuleFormular(LBRCSenderController parent, String name) {
		super(name);
		this.parent = parent;
		this.name = name;
	}
	
    public void keyPressed(final int keyCode) {
    	if (parent.sender != null) {
    		parent.sender.sendKey(keyCode, 0);
    	}
    }
    
    public void keyReleased(final int keyCode) {
    	if (parent.sender != null) {
    		parent.sender.sendKey(keyCode, 1);
    	}
    }
    
    public String getName() {
    	return this.name; 
    }
}