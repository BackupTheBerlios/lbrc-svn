package LBRC;

import javax.microedition.lcdui.*;
import org.json.me.*;
import java.util.Vector;

public class LBRCVolumeControl extends LBRCShowModule {
	private Vector elements;
	
	LBRCVolumeControl(LBRCSenderController parent, String name) {
		super(parent, name);
		this.elements = new Vector();
	}
	
	public synchronized void handleRequest(JSONObject obj) throws JSONException {
		if (! obj.getString("type").equals(this.name)) return;
		String command = obj.getString("command");
		if(command.equals("updateVolumes")) {
			JSONArray volumes = obj.getJSONArray("volumeData");
			synchronized(elements) {
				elements.removeAllElements();
				elements.ensureCapacity(volumes.length());
				for(int i=0;i<volumes.length();i++) {
					elements.addElement(volumes.getJSONArray(i));
				}
			}
		}
		this.repaint();
	}
	
	protected void paint(Graphics g) {
		g.setColor(255, 255, 255);
		g.fillRect(0, 0, getWidth(), getHeight());
		int width = g.getClipWidth() - g.getClipX();
		//int height = g.getClipHeight() - g.getClipY();
		g.setColor(0, 0, 0);
		Font f = g.getFont();
		int fh = f.getHeight();
		int space_offset = f.stringWidth(" ");
		synchronized(elements) {
			for(int i = 0; i<elements.size(); i++) {
				JSONArray data = (JSONArray) elements.elementAt(i);
				String vlabel = "";
				int vvalue = 0;
				try {
					vlabel = data.getString(0);
					vvalue = data.getInt(1);
				} catch (JSONException e) {
					continue;
				}
				double sum_offset = i * 3.5 * fh;
				int label_y_offset = (int) (sum_offset + 0.5 * fh);
				int bar_y_offset =  (int) (sum_offset + 2 * fh);
				int bar_width = width * vvalue / 100;
				int bar_height = fh;
				g.setColor(0, 0, 0);
				g.drawString(vlabel, space_offset, label_y_offset, Graphics.TOP|Graphics.LEFT);
				g.setColor(119,83,255);
				g.fillRect(0, bar_y_offset, bar_width, bar_height);
				g.setColor(175,153,255);
				g.fillRect(bar_width, bar_y_offset, width - bar_width, bar_height);	
			}
		}
	}
}
