package LBRC;

import javax.microedition.lcdui.*;

public class LBRCPresentationCompanion extends Canvas implements Runnable {
	private boolean visible = false;
	private Thread repaint;
	private int current_slide = 1;
	private long last_time = 0;
	LBRCSenderController parent;
	
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
	
	LBRCPresentationCompanion(LBRCSenderController parent) {
		this.parent = parent;
		this.repaint = new Thread(this);
		last_time = System.currentTimeMillis();
		this.repaint.start();
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
    	int diff = (int) ((System.currentTimeMillis() - last_time) / 1000);
    	return Integer.toString(diff);
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
		String t = get_formated_timediff();
		g.drawString(time_value,
				 (width - time_value_width) / 2,
			     (int)(3.0 * description_height + 1.5 * content_height),
			     Graphics.LEFT | Graphics.TOP);
	}
}
