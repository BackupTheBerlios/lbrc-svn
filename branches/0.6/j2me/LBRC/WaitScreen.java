package LBRC;

import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

public class WaitScreen extends Canvas {
	String action;
	
	public void setAction(String action) {
		this.action = action;
	}
	
	protected void paint(Graphics g) {
		g.setColor(255, 255, 255);
		g.fillRect(0, 0, getWidth(), getHeight());
		int width = g.getClipWidth() - g.getClipX();
		int height = g.getClipHeight() - g.getClipY();
		try {
			Image image = Image.createImage("/res/Blue.png");
			g.drawImage(image, width / 2, height / 2, Graphics.VCENTER | Graphics.HCENTER);
		} catch (Exception e) {
		}
		g.setColor(0, 0, 0);
		Font font = g.getFont();
		String scan = this.action;
		String wait = "Please wait";
		g.drawString(scan, width / 2, height / 4, Graphics.HCENTER | Graphics.BASELINE);
		g.drawString(wait, width / 2, (3 * height) / 4 + font.getHeight(), Graphics.HCENTER | Graphics.BASELINE);
	}	
}
