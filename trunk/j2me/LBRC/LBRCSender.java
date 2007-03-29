package LBRC;

import javax.microedition.io.Connector;
import javax.microedition.io.StreamConnection;
import java.io.IOException;
import java.io.OutputStream;
import java.io.InputStream;
import org.json.*;
import org.json.text.ParseException;

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

	private void handleRequest(JSONObject obj) {
		if (obj.getString("type").equals("listQuery")) {
			// TODO: Make sure only one ListRequest is processed at one time
			parent.doListQuery(obj.getString("title"), obj.getJSONArray("list").getArrayList());
		}
	}
	
	public void sendListReply(int listindex) {
		JSONObject lr = new JSONObject();
		lr.put("type", "listReply");
		lr.put("selectionIndex", listindex);
		send(lr);
	}
	
	public void sendKey(int keyCode, int mapping) {
		JSONObject keycode = new JSONObject();
		keycode.put("type", "keyCode");
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
			if (output != null) {
				String stringified = message.toString() + "\u0000";
				output.write(stringified.getBytes("UTF-8"));
				output.flush();
			}
		} catch (IOException e) {
		    parent.do_alert("Can't send data: " + e, 4000);
            shutdown();
		}		
	}
	
	public void run() {
		try {
			connection = (StreamConnection)Connector.open(this.URL);
			input = connection.openInputStream();
			output = connection.openOutputStream();
		} catch (IOException e) {
            parent.do_alert("Bluetooth Connection Failed", 4000);
            tearDown();
            this.parent.remoteServiceClosed();
            return;
		}
		initCall();
		parent.senderReady();
		try {
			byte[] buffer = new byte[2048];
			int len = 0;
			while(true) {
				final byte in = (byte) input.read();
				if(in != 0) {
					buffer[len] = in;
					len++;
				} else {
					try {
						String string = new String(buffer, 0, len, "UTF-8");
						JSONObject obj = new JSONObject(string);
						handleRequest(obj);
						len = 0;
					} catch (ParseException e) {
						this.parent.do_alert("Received bogus package from server", 4000);
					}
				}
			}
		} 
		catch (IOException e){}
		tearDown();
		this.parent.remoteServiceClosed();
	}
	
	private void tearDown() {
		if(input != null) {
			try {
				input.close();
			} catch(IOException e){}
		}
		if(output != null) {
			try {
				output.close();
			} catch(IOException e){}
		}
		if(connection != null) {
			try {
				connection.close();
			} catch(IOException e){}
		}
		input = null;
		output = null;
		connection = null;
	}

	public void shutdown() {
		tearDown();
	}
}
