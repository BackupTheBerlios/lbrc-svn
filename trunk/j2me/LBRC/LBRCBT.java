package LBRC;

import javax.microedition.io.Connector;
import javax.microedition.io.StreamConnection;
import java.io.IOException;
import java.io.OutputStream;
import java.io.InputStream;
import org.json.*;

final class LBRCBT implements Runnable {
	// Make the protocol upgradeable
	// Transport encoding is UTF-8
	// TODO: Implement check for used protocol
	private static int[] protocols = { 1 };
	private int protocol = 0;
    private Thread senderThread;
	private StreamConnection connection;
    private OutputStream output;
    private InputStream input;
    private LBRC parent;
    private String URL;

	LBRCBT(LBRC parent, String URL ) {
		senderThread = new Thread(this);
        this.parent = parent;
        this.URL = URL;
		senderThread.start();
	}

	private String encodeKeyCode(int keyCode, byte mapping) {
		JSONObject keycode = new JSONObject();
		keycode.put("type", "keycode");
		keycode.put("keycode", keyCode);
		keycode.put("mapping", mapping);
		return keycode.toString() + "\u0000";
	}
	
	public void sendKey(int keyCode, byte mapping) {
		if(output != null){
			try {
			    output.write(encodeKeyCode(keyCode, mapping).getBytes("UTF-8"));
			    output.flush();
			} catch (Exception e) {
			    parent.do_alert("Can't send data: " + e, 4000);
                parent.close_remote_service();
			}
		}
	}
	
	public void run() {
		try {
			connection = (StreamConnection)Connector.open(this.URL);
			input = connection.openInputStream();
			output = connection.openOutputStream();
		} catch (Exception e) {
            parent.do_alert("Bluetooth Connection Failed", 4000);
            parent.close_remote_service();
		}
	}
	
	public void shutdown() {
		try {
			if(input != null) input.close();
			if(output != null) output.close();
			if(connection != null) connection.close();
			input = null;
			output = null;
			connection = null;
		} catch (IOException e) {}
		try {
			senderThread.join();
		} catch (InterruptedException e) {}
	}
}
