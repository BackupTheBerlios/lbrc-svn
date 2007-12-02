package LBRC;

import javax.microedition.lcdui.*;
import org.json.*;

public class LBRCPresentationControl extends LBRCShowModuleCanvas implements Runnable {
	private boolean visible = false;
	private Thread repaint;
	private int current_slide = 1;
	private long last_time = 0;
	
	public void run() {
		while (true) {
			try {
				Thread.sleep(1000);
			} catch (InterruptedException e) {
			}
			if (visible) this.repaint();
		}
	}
	
	protected void showNotify() {
		visible = true;
	}
	
	protected void hideNotify() {
		visible = false;
	}
	
	LBRCPresentationControl(LBRCSenderController parent, String name) {
		super(parent, name);
		this.repaint = new Thread(this);
		last_time = System.currentTimeMillis();
		this.repaint.start();
	}

    public synchronized void handleRequest(JSONObject obj) {
    	if (! obj.getString("type").equals(this.name)) return;
    	String command = obj.getString("command");
		if (command.equals("changeSlide")) {
			change_slide(obj.getInt("param"));
		} else if (command.equals("setSlide")) {
			set_slide(obj.getInt("param"));
		}
    }
    
    protected void change_slide(int change) {
    	current_slide += change;
    	last_time = System.currentTimeMillis();
    	repaint();
    }
	
    protected void set_slide(int slide) {
    	current_slide = slide;
    	last_time = System.currentTimeMillis();
    	repaint();
    }
    
    private String get_formated_timediff() {
    	int seconds = (int) ((System.currentTimeMillis() - last_time) / 1000);
    	int minutes = (int) seconds / 60;
    	seconds -= 60 * minutes;
    	if (seconds < 10) return Integer.toString(minutes) + ":0" +Integer.toString(seconds);
    	else return Integer.toString(minutes) + ":" + Integer.toString(seconds);
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
		Font description_font = Font.getFont(Font.FACE_SYSTEM, Font.STYLE_PLAIN, Font.SIZE_MEDIUM);
		Font content_font = Font.getFont(Font.FACE_SYSTEM, Font.STYLE_BOLD, Font.SIZE_LARGE);
		
		int description_height = description_font.getHeight();
		int content_height = content_font.getHeight();
		
		g.setFont(description_font);
		String slide = "Slide";
		int slide_width = description_font.stringWidth(slide);
		String time = "Time";
		int time_width = description_font.stringWidth(time);
		
		g.drawString(slide, 
				     (width - slide_width) / 2, 
				     (int) (0.5 * description_height),
				     Graphics.LEFT | Graphics.TOP);
		g.drawString(time,
				     (width - time_width) / 2,
				     (int) (1.5 * description_height + 1.5 * content_height),
				     Graphics.LEFT | Graphics.TOP);
		
		String slide_value = Integer.toString(current_slide);
		int slide_value_width = content_font.stringWidth(slide_value);
		String time_value = get_formated_timediff();
		int time_value_width = content_font.stringWidth(time_value);
		
		g.setFont(content_font);
		g.drawString(slide_value,
					 (width - slide_value_width) / 2,
				     (int)(1.75 * description_height),
				     Graphics.LEFT | Graphics.TOP);
		g.drawString(time_value,
				 (width - time_value_width) / 2,
			     (int)(3.0 * description_height + 1.5 * content_height),
			     Graphics.LEFT | Graphics.TOP);
	}
}
