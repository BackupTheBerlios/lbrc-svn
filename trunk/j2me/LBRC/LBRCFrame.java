package LBRC;

import javax.microedition.lcdui.*;

class LBRCFrame extends Canvas  implements CommandListener {
	Command exit;
	Command back;
	private String pressedKeyName = "No key pressed";
	private int pressedKey = 0;
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
		pressedKeyName = getKeyName(keyCode);
		pressedKey = keyCode;
		parent.sendKey(keyCode,(byte)0);
		repaint();
    }
    
    protected void keyReleased(int keyCode) {
		pressedKeyName = getKeyName(keyCode);
		pressedKey = keyCode;
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
}
