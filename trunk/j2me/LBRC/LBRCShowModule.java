package LBRC;

import org.json.JSONObject;

public interface LBRCShowModule {
	void handleRequest(JSONObject obj);
    void keyPressed(final int keyCode);  
    void keyReleased(final int keyCode);
    String getName();
}
