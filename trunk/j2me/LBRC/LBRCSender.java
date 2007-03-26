package LBRC;

import javax.microedition.io.Connector;
import javax.microedition.io.StreamConnection;
import java.io.IOException;
import java.io.OutputStream;
import java.io.InputStream;
import org.json.*;

final class LBRCSender implements Runnable {
	// Make the protocol upgradeable 
	// (read: the j2me part announces what version it 
	//  speaks and the python part follows)
	// Transport encoding is UTF-8
	final private int protocol = 0;
    private Thread senderThread;
	private StreamConnection connection;
    private OutputStream output;
    private InputStream input;
    private LBRCSenderController parent;
    private String URL;

	LBRCSender(LBRCSenderController parent, String URL ) {
		senderThread = new Thread(this);
        this.parent = parent;
        this.URL = URL;
		senderThread.start();
	}

	public void sendKey(int keyCode, int mapping) {
		JSONObject keycode = new JSONObject();
		keycode.put("type", "keycode");
		keycode.put("keycode", keyCode);
		keycode.put("mapping", mapping);
		send(keycode);
	}
	
	private void initCall() {
		JSONObject init = new JSONObject();
		init.put("type", "init");
		init.put("protocol", protocol);
		send(init);
	}
	
	private void send(JSONObject message) {
		try {
			String stringified = message.toString() + "\u0000";
			output.write(stringified.getBytes("UTF-8"));
			output.flush();
		} catch (Exception e) {
		    parent.do_alert("Can't send data: " + e, 4000);
            shutdown();
		}		
	}
	
	public void run() {
		try {
			connection = (StreamConnection)Connector.open(this.URL);
			input = connection.openInputStream();
			output = connection.openOutputStream();
			initCall();
		} catch (Exception e) {
            parent.do_alert("Bluetooth Connection Failed", 4000);
            shutdown();
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
		this.parent.remoteServiceClosed();
	}
}
