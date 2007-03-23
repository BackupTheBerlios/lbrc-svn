package LBRC;

import javax.microedition.lcdui.*;

class LBRCFrame extends Canvas  implements CommandListener {
	Command exit;
	Command back;
	private String pressedKey = "No key pressed";
	private LBRC parent;

    LBRCFrame(LBRC parent) {
		this.parent = parent;
		this.exit = new Command("Exit", Command.EXIT, 1);
		this.back = new Command("Back", Command.BACK, 1);
		this.addCommand(this.back);
		this.addCommand(this.exit);
		this.setCommandListener(this);
    }
    
    protected void keyPressed(int keyCode) {
		pressedKey = getKeyName(keyCode);
		parent.sendKey(keyCode,(byte)0);
		repaint();
    }
    
    protected void keyReleased(int keyCode) {
		pressedKey = getKeyName(keyCode);
        parent.sendKey(keyCode,(byte)1);
        repaint();
    }
    
	public void commandAction(Command com, Displayable dis) {
		if (com == exit) {
			this.parent.quit();
		}
		if (com == back) {
			this.parent.close_remote_service();
		}
	} 
    
    protected void paint(Graphics g) {
		g.setColor(255,255,255);
		g.fillRect(0,0,getWidth(), getHeight());
		g.setColor(0,0,0);
		g.drawString(pressedKey, 20, 100, Graphics.TOP| Graphics.LEFT);
	}
}
