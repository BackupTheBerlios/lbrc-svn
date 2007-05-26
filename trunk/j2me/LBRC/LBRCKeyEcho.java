package LBRC;

import javax.microedition.lcdui.*;

public class LBRCKeyEcho extends Canvas {
	private String pressedKeyName = "No key pressed";
	private int pressedKey = 0;
	LBRCSenderController parent;
	
	LBRCKeyEcho(LBRCSenderController parent) {
		this.parent = parent;
	}

    protected void keyPressed(final int keyCode) {
    	if (parent.sender != null) {
    		pressedKeyName = getKeyName(keyCode);
    		pressedKey = keyCode;
    		parent.sender.sendKey(keyCode, 0);
    		repaint();
    	}
    }
    
    protected void keyReleased(final int keyCode) {
    	if (parent.sender != null) {
    		pressedKeyName = getKeyName(keyCode);
    		pressedKey = keyCode;
    		parent.sender.sendKey(keyCode, 1);
    		repaint();
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
