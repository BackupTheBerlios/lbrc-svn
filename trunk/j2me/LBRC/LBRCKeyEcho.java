package LBRC;

import javax.microedition.lcdui.*;
import org.json.*;

public class LBRCKeyEcho extends LBRCShowModule {
	private String pressedKeyName = "No key pressed";
	private int pressedKey = 0;
	
	LBRCKeyEcho(LBRCSenderController parent, String name) {
		super(parent, name);
	}

    protected void keyPressed(final int keyCode) {
		pressedKeyName = getKeyName(keyCode);
		pressedKey = keyCode;   	
		super.keyPressed(keyCode);
    }
    
    protected void keyReleased(final int keyCode) {
		pressedKeyName = getKeyName(keyCode);
		pressedKey = keyCode;
		super.keyReleased(keyCode);
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
	
	public void handleRequest(JSONObject obj) {}
}
